#!/usr/bin/env python3
"""Meta dosyalarına klipte görünen diğer yayıncıları yazar (ek_yayincilar).

Kullanım: python3 ek_yayinci.py Elraenn data/hazir/hd/*.json data/hazir/uzun/x.json
"""
import json
import sys
from pathlib import Path

ad = sys.argv[1]
for yol in map(Path, sys.argv[2:]):
    m = json.loads(yol.read_text())
    m["ek_yayincilar"] = list(dict.fromkeys(m.get("ek_yayincilar", []) + [ad]))
    m.setdefault("ana_yayinci", (m.get("kredi") or "").split("/")[-1].replace("rraenee", "RRaenee"))
    yol.write_text(json.dumps(m, ensure_ascii=False, indent=1))
    print("✔", yol.name, m["ek_yayincilar"])
