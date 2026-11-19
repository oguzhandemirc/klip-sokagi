#!/usr/bin/env python3
"""Sinyal toplama: bir yayının sohbet hızını video indirmeden ölçer.

Şimdilik yalnız Kick destekli. Bütün sohbeti indirmek yerine yayın boyunca her ADIM saniyede
bir örnek alır (o andan önceki son 25 mesaj) ve bu 25 mesajın kaç saniyeye yayıldığından
sohbet hızını hesaplar. Kick çok istek atılınca engellediği (429) için yavaş ve kaldığı
yerden devam edebilir biçimde çalışır.

Kullanım:
    python3 sinyal.py KANAL_ADI               # kanalın yayınlarını listeler
    python3 sinyal.py KANAL_ADI --sira 0      # listedeki 0 numaralı yayını örnekler

Çıktı: data/sohbet/kick-<uuid>.json
"""
import argparse
import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parent
SOHBET_KLASORU = KOK / "data" / "sohbet"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

_kilit = threading.Lock()
_bekle_kadar = [0.0]   # 429 gelince bütün iş parçacıkları bu ana kadar bekler


def getir(url, deneme=12):
    """Adresi curl ile çeker, JSON döndürür. Engellenince herkesi bekletip yeniden dener."""
    kod = "?"
    for i in range(deneme):
        kalan = _bekle_kadar[0] - time.time()
        if kalan > 0:
            time.sleep(kalan)
        sonuc = subprocess.run(
            ["curl", "-s", "-m", "30", "-A", UA, "-H", "Accept: application/json",
             "-w", "\n%{http_code}", url],
            capture_output=True, text=True).stdout
        govde, _, kod = sonuc.rpartition("\n")
        if kod == "200":
            try:
                return json.loads(govde)
            except json.JSONDecodeError:
                pass
        with _kilit:
            _bekle_kadar[0] = max(_bekle_kadar[0], time.time() + (30 if kod == "429" else 3) * (i + 1))
    raise RuntimeError(f"İndirilemedi ({kod}): {url}")


def kick_yayinlar(kanal):
    """Kanalın bitmiş yayınlarını döndürür (en yeni başta)."""
    yayinlar = []
    for v in getir(f"https://kick.com/api/v2/channels/{kanal}/videos"):
        if not v.get("duration") or v.get("is_live"):
            continue
        baslangic = datetime.strptime(v["start_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        yayinlar.append({
            "platform": "kick",
            "kanal": kanal,
            "uuid": v["video"]["uuid"],
            "kanal_id": v["channel_id"],
            "baslik": v.get("session_title") or "",
            "baslangic": baslangic.isoformat(),
            "baslangic_epoch": baslangic.timestamp(),
            "sure": v["duration"] // 1000,
            "izlenme": v.get("views"),
            "kaynak": v["source"],
        })
    return yayinlar


def kick_ornek(yayin, t):
    """Yayının t. saniyesinden önceki son 25 mesajı alır; hızı (mesaj/sn) hesaplar."""
    imlec = int((yayin["baslangic_epoch"] + t) * 1_000_000)
    veri = getir(f"https://kick.com/api/v2/channels/{yayin['kanal_id']}/messages?cursor={imlec}").get("data") or {}
    sayfa = veri.get("messages") or []
    eski = int(veri.get("cursor") or 0)
    kapsam = (imlec - eski) / 1e6 if eski else None
    mesajlar = []
    for m in sayfa:
        zaman = datetime.strptime(m["created_at"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        mesajlar.append([int(zaman.timestamp() - yayin["baslangic_epoch"]),
                         (m.get("sender") or {}).get("username") or "",
                         m.get("content") or "", m.get("type") or ""])
    hiz = len(sayfa) / kapsam if kapsam and kapsam > 0 else 0.0
    return {"t": t, "kapsam": kapsam, "hiz": round(hiz, 3), "mesajlar": mesajlar}


def kick_ornekle(yayin, adim, atla_bas, is_parcacigi, ara_dosya):
    """Yayın boyunca örnek toplar. Ara sonuçları dosyaya yazar; yeniden çalıştırınca devam eder."""
    ornekler = {}
    if ara_dosya.exists():
        for satir in ara_dosya.read_text().splitlines():
            o = json.loads(satir)
            ornekler[o["t"]] = o
    zamanlar = [t for t in range(atla_bas + adim, yayin["sure"] + 1, adim) if t not in ornekler]
    toplam = len(zamanlar) + len(ornekler)

    def calis(t):
        o = kick_ornek(yayin, t)
        with _kilit:
            ornekler[t] = o
            with ara_dosya.open("a") as f:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
            if len(ornekler) % 100 == 0:
                print(f"  {len(ornekler)}/{toplam} örnek", file=sys.stderr, flush=True)

    with ThreadPoolExecutor(is_parcacigi) as havuz:
        list(havuz.map(calis, zamanlar))
    return [ornekler[t] for t in sorted(ornekler)]


def main():
    ap = argparse.ArgumentParser(description="Kick yayınının sohbet hızını örnekler.")
    ap.add_argument("kanal", help="Kick kanal adı (adresteki ad)")
    ap.add_argument("--sira", type=int, help="listedeki yayın numarası")
    ap.add_argument("--adim", type=int, default=10, help="örnekler arası saniye")
    ap.add_argument("--atla-bas", type=int, default=600, help="yayının başında atlanacak saniye")
    ap.add_argument("--is-parcacigi", type=int, default=3)
    a = ap.parse_args()

    yayinlar = kick_yayinlar(a.kanal)
    if a.sira is None:
        for i, y in enumerate(yayinlar):
            saat, dk = divmod(y["sure"] // 60, 60)
            print(f"{i:2d} | {y['baslangic'][:16]} | {saat}s {dk:02d}dk | {y['izlenme']:>8} izlenme | {y['baslik'][:50]}")
        return

    yayin = yayinlar[a.sira]
    print(f"Yayın: {yayin['baslik']} | {yayin['baslangic'][:16]} | {yayin['sure']} sn", flush=True)
    SOHBET_KLASORU.mkdir(parents=True, exist_ok=True)
    hedef = SOHBET_KLASORU / f"kick-{yayin['uuid']}.json"
    ara_dosya = hedef.with_suffix(".ara.jsonl")
    basla = time.time()
    ornekler = kick_ornekle(yayin, a.adim, a.atla_bas, a.is_parcacigi, ara_dosya)
    hedef.write_text(json.dumps({"yayin": yayin, "adim": a.adim, "ornekler": ornekler}, ensure_ascii=False))
    ara_dosya.unlink()
    print(f"{len(ornekler)} örnek, {time.time() - basla:.0f} sn → {hedef}")


if __name__ == "__main__":
    main()
