#!/usr/bin/env python3
"""Ham parçaların konuşmasını yazıya döker (kelime zamanlı) ve inceleme için kare sayfası çıkarır.

Kullanım: .venv/bin/python transkript.py data/parca/13c4146d-*.mp4
Çıktı: her parçanın yanında <ad>.json (kelimeler) ve <ad>.jpg (6 karelik özet).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from duzenle import transkript

for yol in map(Path, sys.argv[1:]):
    hedef = yol.with_suffix(".json")
    if hedef.exists():
        continue
    with tempfile.TemporaryDirectory() as tmp:
        ses = Path(tmp) / "ses.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(yol), "-ac", "1", "-ar", "16000", str(ses)],
                       check=True)
        kelimeler = transkript(ses, "small")
    # 10 saniyede bir kare, 3x2 ızgara
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(yol), "-vf",
                    "fps=1/10,scale=480:-2,tile=3x2", "-frames:v", "1", str(yol.with_suffix(".jpg"))], check=True)
    satirlar, satir, bas = [], [], 0
    for k in kelimeler:
        if not satir:
            bas = k["bas"]
        satir.append(k["metin"])
        if k["metin"][-1:] in ".?!" or len(satir) > 12:
            satirlar.append(f"[{bas:5.1f}] {' '.join(satir)}")
            satir = []
    if satir:
        satirlar.append(f"[{bas:5.1f}] {' '.join(satir)}")
    hedef.write_text(json.dumps({"kelimeler": kelimeler, "satirlar": satirlar}, ensure_ascii=False, indent=1))
    print(f"✔ {yol.name}: {len(kelimeler)} kelime", flush=True)
