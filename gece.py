#!/usr/bin/env python3
"""Gece toplu hattı: birden çok yayın için sinyal → an seç → parça kes → transkript (yükleme YOK).

Her yayın sırayla işlenir (Kick istek sınırı yüzünden paralel değil). Biten adım atlanır, kaldığı yerden sürer.
Sonuç: data/parca/<uuid8>-NN.mp4 + .json (transkript) + .jpg (kare özeti); özet data/log/gece-<tarih>.txt

Kullanım: .venv/bin/python gece.py wtcn:0 eray:0 tolunayoren:1 wtcn:2 [--adet 15 --esik-sd 1.5 --aralik 45]
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
PY = sys.executable


def calistir(komut, log):
    log.write(f"\n$ {' '.join(komut)}\n")
    log.flush()
    r = subprocess.run(komut, capture_output=True, text=True, cwd=KOK)
    log.write(r.stdout[-3000:] + r.stderr[-1500:])
    log.flush()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("yayinlar", nargs="+", help="kanal:sira (sinyal.py listesindeki sıra)")
    ap.add_argument("--adet", type=int, default=15)
    ap.add_argument("--esik-sd", type=float, default=1.5)
    ap.add_argument("--aralik", type=int, default=45)
    a = ap.parse_args()
    (KOK / "data" / "log").mkdir(parents=True, exist_ok=True)
    log = (KOK / "data" / "log" / f"gece-{datetime.now():%Y%m%d-%H%M}.txt").open("w")

    for y in a.yayinlar:
        kanal, sira = y.split(":")
        bas = datetime.now()
        print(f"{bas:%H:%M} ▶ {kanal} #{sira}: sohbet örnekleniyor", flush=True)
        r = calistir([PY, "sinyal.py", kanal, "--sira", sira], log)
        sohbet = next((s.split("→")[-1].strip() for s in r.stdout.splitlines() if "kick-" in s and ".json" in s), None)
        if not sohbet:
            # sinyal.py çıktısında yol yoksa en yeni sohbet dosyası
            sohbet = str(max((KOK / "data" / "sohbet").glob("kick-*[0-9a-f].json"), key=lambda p: p.stat().st_mtime))
        sohbet = sohbet if Path(sohbet).is_absolute() else str(KOK / sohbet)
        if r.returncode or not Path(sohbet).exists():
            print(f"   ✘ sinyal başarısız (log'a bak)", flush=True)
            continue
        r = calistir([PY, "an_sec.py", sohbet, "--adet", str(a.adet), "--esik-sd", str(a.esik_sd),
                      "--aralik", str(a.aralik)], log)
        anlar = Path(sohbet).with_name(Path(sohbet).stem + "-anlar.json")
        if r.returncode or not anlar.exists():
            print("   ✘ an seçimi başarısız", flush=True)
            continue
        n = len(json.loads(anlar.read_text())["anlar"])
        print(f"   {n} an bulundu, kesiliyor", flush=True)
        calistir([PY, "parca_indir.py", str(anlar), "--adet", str(a.adet)], log)
        on_ek = json.loads(anlar.read_text())["yayin"]["uuid"][:8]
        parcalar = sorted(str(p) for p in (KOK / "data" / "parca").glob(f"{on_ek}-*.mp4"))
        print(f"   {len(parcalar)} parça, transkript çıkarılıyor", flush=True)
        calistir([PY, "transkript.py", *parcalar], log)
        print(f"   ✔ {kanal} bitti ({(datetime.now() - bas).seconds // 60} dk), önek {on_ek}", flush=True)
    print("TÜMÜ BİTTİ", flush=True)


if __name__ == "__main__":
    main()
