#!/usr/bin/env python3
"""plan.json'daki kanca yazılarını bir JSON sözlüğünden ({ad: kanca}) günceller.

Kullanım: python3 kanca_guncelle.py kancalar.json
Videoya gömülü olduğu için değişiklik ancak yeniden üretimle (uretim.py) görünür.
"""
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
yeni = json.loads(Path(sys.argv[1]).read_text())
plan_yolu = KOK / "plan.json"
plan = json.loads(plan_yolu.read_text())
for p in plan:
    if p["ad"] in yeni:
        print(f"{p['ad']}: {p['kanca']!r} → {yeni[p['ad']]!r}")
        p["kanca"] = yeni[p["ad"]]
plan_yolu.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
