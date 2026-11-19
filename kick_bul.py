#!/usr/bin/env python3
"""Kick kanal adlarını doğrular: takipçi sayısı, son yayınlar ve kategorileri (GTA 6 oynuyor mu?).

Kullanım: python3 kick_bul.py elraenn tolunayoren ...
"""
import sys

from sinyal import getir

for ad in sys.argv[1:]:
    try:
        k = getir(f"https://kick.com/api/v2/channels/{ad}", deneme=2)
    except SystemExit:
        k = None
    if not k or not k.get("id"):
        print(f"✘ {ad}: bulunamadı")
        continue
    try:
        videolar = getir(f"https://kick.com/api/v2/channels/{ad}/videos", deneme=2) or []
    except SystemExit:
        videolar = []
    kat = [((v.get("categories") or [{}])[0].get("name", "?")) for v in videolar[:15]]
    gta = sum("GTA" in c or "Grand Theft" in c for c in kat)
    print(f"✔ {ad:18} takipçi {k.get('followers_count') or k.get('followersCount')}  "
          f"son {len(kat)} yayın, GTA: {gta}  | {', '.join(dict.fromkeys(kat))[:120]}")
