#!/usr/bin/env python3
"""YouTube günlük yükleme sınırına takılan klipleri, sınır açılana kadar aralıklarla yeniden dener.
planla.py zaten yüklenenleri atlar ve ilk boş saati seçer.

Kullanım (klip klasöründen): python yeniden_dene.py 05-x.mp4 01-y.mp4 ... [--aralik 1800] [--deneme 36]
"""
import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("videolar", nargs="+")
ap.add_argument("--aralik", type=int, default=1800)
ap.add_argument("--deneme", type=int, default=36)
a = ap.parse_args()

for i in range(a.deneme):
    r = subprocess.run([sys.executable, str(KOK / "planla.py"), *a.videolar, "--gercek"], capture_output=True, text=True)
    cikti = r.stdout + r.stderr
    for satir in cikti.splitlines():
        if "✔" in satir or "uploadLimitExceeded" in satir:
            print(datetime.now().strftime("%H:%M"), satir.strip()[:120], flush=True)
    if "uploadLimitExceeded" not in cikti:
        print("bitti", flush=True)
        break
    time.sleep(a.aralik)
