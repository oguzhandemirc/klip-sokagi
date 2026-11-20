#!/usr/bin/env python3
"""Otomatik döngü: Görev Zamanlayıcı 10 dk'da bir çalıştırır (docs/kurulum-thinkpad.md). ONAYLI MOD:
yalnız kullanıcının onayladığı klipler yüklenir (CLAUDE.md kural 5).

Her çalışmada:
 1. Yükle   — data/onayli/sira.txt'deki onaylı yatay videolar → yukle.py (ilk boş Pzt/Çar/Cum 20:00), sonra
              Short'lar → planla.py --gercek (ilk boş 13:00/18:00/21:00); hepsi gizli+planlı.
              uploadLimitExceeded gelirse 30 dk sonra yeniden dener. Başka planla/yeniden_dene çalışıyorsa atlar.
 2. Temizle — yayın saati geçmiş yüklemelerin çıktı .mp4'ü ve (bekleyen başka klip kullanmıyorsa) ham parçası
              silinir; .json/.jpg kalır (aciklama_guncelle.py için).
 3. Keşif   — 30 dk'da bir: hedef yayıncıların son 72 sa'te biten GTA yayınlarından işlenmemiş en tazesini
              gece.py ile işler (sinyal → an → parça → transkript; ayrı süreç, döngüyü bekletmez).
              gece.py zaten çalışıyorsa ya da kanal için bitince.py bekliyorsa atlar. Biten adaylar
              data/inceleme-bekliyor.txt'ye yazılır: Claude inceler, plan yazar, üretir; kullanıcı onaylarsa sira.txt'ye.

sira.txt: satır başına bir mp4 yolu (C:\\shorts'a göre), # ile başlayan satır yorum.
Kullanım: .venv\\Scripts\\python dongu.py [--kuru]   (kuru: hiçbir şey yüklemez/silmez/başlatmaz, ne yapacağını yazar)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from yukle import KAYIT, SAAT_DILIMI, proje_yolu, yasakli_mi

KOK = Path(__file__).resolve().parent
DATA = KOK / "data"
KILIT = DATA / "dongu.kilit"
DURUM = DATA / "dongu-durum.json"
SIRA = DATA / "onayli" / "sira.txt"
INCELEME = DATA / "inceleme-bekliyor.txt"
YUKLEME_ARA = 30 * 60
KESIF_ARA = 30 * 60
TAZE_SAAT = 72
EN_AZ_YAYIN_SN = 3600
EN_AZ_BOS_GB = 5
EN_COK_DENEME = 3
GTA = re.compile(r"gta|grand theft", re.I)


def log(*m):
    print(f"{datetime.now():%m-%d %H:%M}", *m, flush=True)


def calisan_betikler():
    """Çalışan python süreçlerinin komut satırları (gece.py/bitince.py/planla.py çakışmasını önlemek için)."""
    if os.name == "nt":
        komut = ["powershell", "-NoProfile", "-Command",
                 "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | ForEach-Object CommandLine"]
    else:
        komut = ["ps", "-eo", "args"]
    r = subprocess.run(komut, capture_output=True, text=True)
    return [s for s in r.stdout.splitlines() if "python" in s.lower() or s.strip().endswith(".py")]


def kilit_al():
    if KILIT.exists() and time.time() - KILIT.stat().st_mtime < 2 * 3600:
        return False
    KILIT.write_text(str(os.getpid()))
    return True


def yuklenenler():
    if not KAYIT.exists():
        return {}
    return {proje_yolu(k["dosya"]): k for k in map(json.loads, KAYIT.read_text().splitlines())}


# ---------- 1. Yükleme ----------
def yukle(durum, calisan, kuru):
    if not SIRA.exists():
        return
    yuklu = yuklenenler()
    shorts, videolar = [], []
    for satir in SIRA.read_text().splitlines():
        s = satir.strip()
        if not s or s.startswith("#"):
            continue
        yol = KOK / s
        if proje_yolu(yol) in yuklu:
            continue
        if not yol.exists():
            log("✘ sira.txt'deki dosya yok:", s)
            continue
        uzun = "aciklama_son" in json.loads(yol.with_suffix(".json").read_text())
        (videolar if uzun else shorts).append(str(yol))
    if not shorts and not videolar:
        return
    if any("planla.py" in c or "yeniden_dene.py" in c or "yukle.py" in c for c in calisan):
        log(f"yükleme atlandı: başka yükleme süreci çalışıyor ({len(shorts) + len(videolar)} bekliyor)")
        return
    if time.time() - durum.get("sinir_zamani", 0) < YUKLEME_ARA:
        return
    # Yatay videolar önce (saatleri sabit Pzt/Çar/Cum 20:00, kaçarsa 2-3 gün kayar), sonra Short'lar.
    for v in videolar:
        zaman = video_saati(yuklu)
        if kuru:
            log(f"[kuru] yatay video {zaman}: {Path(v).name}")
            continue
        r = subprocess.run([sys.executable, str(KOK / "yukle.py"), v, "--zaman", zaman, "--gercek"],
                           capture_output=True, text=True, cwd=KOK)
        if not sonucu_isle(r, durum, f"yatay {zaman} {Path(v).name}"):
            return
        yuklu = yuklenenler()
    if not shorts:
        return
    if kuru:
        log(f"[kuru] {len(shorts)} onaylı Short planla.py ile yüklenecek:", *(Path(b).name for b in shorts))
        return
    r = subprocess.run([sys.executable, str(KOK / "planla.py"), *shorts, "--gercek"],
                       capture_output=True, text=True, cwd=KOK)
    sonucu_isle(r, durum, "planla.py")


def sonucu_isle(r, durum, ad):
    """Yükleme çıktısını loglar; sınır ya da hata varsa False (sonraki yüklemeler bu tur denenmez)."""
    cikti = r.stdout + r.stderr
    for satir in cikti.splitlines():
        if "✔" in satir or "✘" in satir or re.match(r"\d{4}-\d\d-\d\d \d\d:\d\d ", satir):
            log("  ", satir.strip()[:150])
    if "uploadLimitExceeded" in cikti or "exceeded the number of videos" in cikti:
        durum["sinir_zamani"] = time.time()
        log(f"YouTube günlük yükleme sınırı ({ad}); 30 dk sonra yeniden")
        return False
    if r.returncode:
        log(f"✘ {ad} hata:", cikti[-400:])
        return False
    return True


def video_saati(yuklu):
    """Yatay video için ilk boş Pzt/Çar/Cum 20:00 (en az 1 sa sonrası; docs/strateji.md)."""
    dolu = {datetime.fromisoformat(k["publishAt"]).astimezone(SAAT_DILIMI).strftime("%Y-%m-%d %H:%M")
            for k in yuklu.values() if k.get("publishAt")}
    en_erken = datetime.now(SAAT_DILIMI) + timedelta(hours=1)
    gun = en_erken.date()
    while True:
        aday = datetime.combine(gun, datetime.min.time(), SAAT_DILIMI).replace(hour=20)
        anahtar = aday.strftime("%Y-%m-%d %H:%M")
        if gun.weekday() in (0, 2, 4) and aday > en_erken and anahtar not in dolu:
            return anahtar
        gun += timedelta(days=1)


# ---------- 2. Temizlik ----------
def temizle(kuru):
    yuklu = yuklenenler()
    simdi = datetime.now(SAAT_DILIMI)
    # Yüklenmemiş (bekleyen) kliplerin kullandığı ham parçalar silinmez.
    gerekli = set()
    for meta in (DATA / "hazir").rglob("*.json"):
        if meta.with_suffix(".mp4").exists() and proje_yolu(meta.with_suffix(".mp4")) not in yuklu:
            try:
                m = json.loads(meta.read_text())
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            girdiler = [m.get("girdi")] + [b.get("girdi") for b in m.get("bolumler", []) if isinstance(b, dict)]
            gerekli |= {proje_yolu(g) for g in girdiler if g}
    for yol, k in yuklu.items():
        yayin = datetime.fromisoformat(k["publishAt"]) if k.get("publishAt") else \
            datetime.fromisoformat(k["zaman"]) + timedelta(hours=24)
        if yayin > simdi:
            continue  # yayından önce kullanıcı veto edip yeniden düzenlemek isteyebilir
        cikti = KOK / yol
        silinecek = [cikti] if cikti.exists() else []
        meta = cikti.with_suffix(".json")
        if meta.exists():
            ham = json.loads(meta.read_text()).get("girdi")
            if ham and proje_yolu(ham) not in gerekli and (KOK / proje_yolu(ham)).exists():
                silinecek.append(KOK / proje_yolu(ham))
        for s in silinecek:
            log(("[kuru] silinecek: " if kuru else "🗑 silindi: ") + proje_yolu(s))
            if not kuru:
                s.unlink()


# ---------- 3. Keşif ----------
def gece_bitenleri_bildir(durum, calisan, kuru):
    if any("gece.py" in c or "transkript.py" in c for c in calisan):
        return  # dökümler bitmeden aday sayısı eksik çıkar
    for uuid, b in durum.get("islenen", {}).items():
        if b.get("bildirildi"):
            continue
        adaylar = sorted((DATA / "parca").glob(f"{uuid[:8]}-*.json"))
        if (DATA / "sohbet" / f"kick-{uuid}-anlar.json").exists() and adaylar and not kuru:
            with INCELEME.open("a") as f:
                f.write(f"{datetime.now():%Y-%m-%d %H:%M}  {b['kanal']}  önek {uuid[:8]}  {len(adaylar)} aday  "
                        f"«{b['baslik'][:60]}»\n")
            b["bildirildi"] = True
            log(f"✔ inceleme bekliyor: {b['kanal']} {uuid[:8]} ({len(adaylar)} aday)")


def kesif(durum, calisan, kuru):
    from sinyal import kick_yayinlar
    if time.time() - durum.get("kesif_zamani", 0) < KESIF_ARA:
        return
    if any("gece.py" in c for c in calisan):
        return
    bos = shutil.disk_usage(KOK).free / 1e9
    if bos < EN_AZ_BOS_GB:
        log(f"✘ keşif atlandı: diskte yalnız {bos:.1f} GB boş")
        return
    durum["kesif_zamani"] = time.time()
    ayar = yaml.safe_load((KOK / "config.yaml").read_text()) or {}
    hedefler = ayar.get("hedef_yayincilar", [])
    sinir = set(ayar.get("kesif_kanallari") or [])
    adaylar = []
    for h in hedefler:
        kanal = h.get("kick")
        if not kanal or h.get("vod") != "evet" or yasakli_mi(f"kick.com/{kanal}"):
            continue
        if sinir and kanal not in sinir:
            continue
        if any("bitince.py" in c and kanal in c for c in calisan):
            continue  # yayın bitince bitince.py işleyecek
        try:
            yayinlar = kick_yayinlar(kanal)
        except (RuntimeError, SystemExit) as h_:
            log(f"✘ {kanal} listelenemedi: {h_}")
            continue
        for sira, y in enumerate(yayinlar):
            bitis = y["baslangic_epoch"] + y["sure"]
            if time.time() - bitis > TAZE_SAAT * 3600:
                break
            if y["sure"] < EN_AZ_YAYIN_SN or not GTA.search(y["baslik"]):
                continue
            if (DATA / "sohbet" / f"kick-{y['uuid']}-anlar.json").exists():
                continue
            if durum.get("islenen", {}).get(y["uuid"], {}).get("deneme", 0) >= EN_COK_DENEME:
                continue
            adaylar.append((bitis, kanal, sira, y))
    if not adaylar:
        return
    bitis, kanal, sira, y = max(adaylar, key=lambda a: a[0])  # en taze yayın önce
    log(f"▶ yeni yayın: {kanal}:{sira} «{y['baslik'][:60]}» ({y['sure'] // 3600} sa) → gece.py"
        + (f" (+{len(adaylar) - 1} sırada)" if len(adaylar) > 1 else ""))
    if kuru:
        return
    b = durum.setdefault("islenen", {}).setdefault(y["uuid"], {"kanal": kanal, "baslik": y["baslik"]})
    b["deneme"] = b.get("deneme", 0) + 1
    gece_baslat([f"{kanal}:{sira}"])


def gece_baslat(yayinlar):
    """gece.py'yi döngüden bağımsız süreç olarak başlatır (saatler sürer; yüklemeler beklemesin)."""
    log_dosya = (DATA / "log" / "gece.log").open("a")
    log_dosya.write(f"==== {datetime.now():%Y-%m-%d %H:%M} dongu.py → gece.py {' '.join(yayinlar)}\n")
    log_dosya.flush()
    ek = {}
    if os.name == "nt":
        ek["creationflags"] = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                               | subprocess.CREATE_BREAKAWAY_FROM_JOB)
    else:
        ek["start_new_session"] = True
    ortam = {**os.environ, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1"}
    komut = [sys.executable, str(KOK / "gece.py"), *yayinlar]
    try:
        subprocess.Popen(komut, cwd=KOK, stdout=log_dosya, stderr=subprocess.STDOUT, env=ortam, **ek)
    except OSError:  # iş nesnesi ayrılmaya izin vermiyorsa ayrılmadan başlat
        ek["creationflags"] &= ~subprocess.CREATE_BREAKAWAY_FROM_JOB
        subprocess.Popen(komut, cwd=KOK, stdout=log_dosya, stderr=subprocess.STDOUT, env=ortam, **ek)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kuru", action="store_true")
    a = ap.parse_args()
    if not a.kuru and not kilit_al():
        return
    try:
        durum = json.loads(DURUM.read_text()) if DURUM.exists() else {}
        calisan = calisan_betikler()
        for adim in (lambda: yukle(durum, calisan, a.kuru), lambda: temizle(a.kuru),
                     lambda: gece_bitenleri_bildir(durum, calisan, a.kuru), lambda: kesif(durum, calisan, a.kuru)):
            try:
                adim()
            except Exception as h:  # bir adımın hatası diğerlerini durdurmasın
                log(f"✘ {type(h).__name__}: {str(h)[:300]}")
        if not a.kuru:
            DURUM.write_text(json.dumps(durum, ensure_ascii=False, indent=1))
    finally:
        if not a.kuru:
            KILIT.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
