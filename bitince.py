#!/usr/bin/env python3
"""Canlı yayın bitene kadar bekler (10 dk'da bir bakar), bitince gece.py ile o yayını işler.

Kullanım: .venv/bin/python bitince.py rraenee [--en-cok-saat 14]
"""
import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from sinyal import getir

KOK = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("kanal")
ap.add_argument("--en-cok-saat", type=float, default=14)
a = ap.parse_args()

bitis = time.time() + a.en_cok_saat * 3600
while time.time() < bitis:
    try:
        canli = (getir(f"https://kick.com/api/v2/channels/{a.kanal}", deneme=3) or {}).get("livestream")
    except (RuntimeError, SystemExit):  # getir() ulaşamayınca RuntimeError fırlatır
        canli = True  # bakamadıysak canlı say, sonra yine bak
    if not canli:
        print(f"{datetime.now():%H:%M} {a.kanal} yayını bitti; kaydın oturması için 15 dk bekleniyor", flush=True)
        time.sleep(900)
        subprocess.run([sys.executable, str(KOK / "gece.py"), f"{a.kanal}:0"], cwd=KOK)
        break
    time.sleep(600)
else:
    print("süre doldu, yayın hâlâ canlı", flush=True)
