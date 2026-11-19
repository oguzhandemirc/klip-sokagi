#!/usr/bin/env python3
"""Toplu üretim: bir plan dosyasındaki her klip için duzenle.py'yi çalıştırır, sonra onay sayfasını yeniler.

Plan (JSON listesi), her öğe:
  {"ad": "01-kaplumbaga", "girdi": "data/parca/X-12.mp4", "bas": 8, "sure": 38,
   "kanca": "...", "kredi": "kick.com/rraenee", "muzik": "muzik/Sneaky_Snitch.mp3" | "",
   "kamera": "1390:144:530:296" (isteğe bağlı),
   "basliklar": [...], "aciklama": "...", "neden": "...", "bilgi": ["3:41:00", "sohbet x6"]}

Kullanım: .venv/bin/python uretim.py plan.json [--klasor data/hazir/kamerali] [--kamera 1390:144:530:296]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("plan")
ap.add_argument("--klasor", default="data/hazir")
ap.add_argument("--kamera", help="plandaki her klibe uygulanacak kamera kutusu x:y:g:y")
ap.add_argument("--yerlesim", default="kutulu", help="kutulu | tam")
ap.add_argument("--sadece", help="yalnız bu ön eklerle başlayan klipler, virgülle: 02,04")
a = ap.parse_args()

klasor = KOK / a.klasor
klasor.mkdir(parents=True, exist_ok=True)
plan = json.loads(Path(a.plan).read_text())
if a.sadece:
    plan = [k for k in plan if k["ad"].startswith(tuple(a.sadece.split(",")))]
for k in plan:
    cikti = klasor / f"{k['ad']}.mp4"
    if cikti.exists():
        print(f"= {k['ad']} zaten var")
        continue
    ek = {x: k[x] for x in ("basliklar", "aciklama", "neden", "bilgi") if x in k}
    komut = [sys.executable, str(KOK / "duzenle.py"), k["girdi"], "--bas", str(k.get("bas", 0)),
             "--sure", str(k.get("sure", 0)), "--kanca", k.get("kanca", ""), "--kredi", k.get("kredi", ""),
             "--ek", json.dumps(ek, ensure_ascii=False), "--cikti", str(cikti)]
    if k.get("kanca_sure"):
        komut += ["--kanca-sure", str(k["kanca_sure"])]
    if k.get("muzik"):
        komut += ["--muzik", k["muzik"]]
    if k.get("sohbet"):
        komut += ["--sohbet", k["sohbet"]]
    kamera = k.get("kamera") or a.kamera
    if kamera:
        komut += ["--kamera", kamera, "--yerlesim", a.yerlesim]
    sonuc = subprocess.run(komut, capture_output=True, text=True)
    print(("✔ " if sonuc.returncode == 0 else "✘ ") + k["ad"], flush=True)
    if sonuc.returncode:
        print(sonuc.stderr[-800:])
subprocess.run([sys.executable, str(KOK / "onay.py"), str(klasor)])
