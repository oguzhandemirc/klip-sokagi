#!/usr/bin/env python3
"""Kick kanalları şu an canlı mı, son kayıt ne zaman? Kullanım: python3 canli.py rraenee eray ..."""
import sys

from sinyal import getir

for ad in sys.argv[1:]:
    k = getir(f"https://kick.com/api/v2/channels/{ad}", deneme=3) or {}
    c = k.get("livestream")
    if c:
        print(f"🔴 {ad}: CANLI — başladı {c.get('created_at', '')[:16]} | {c.get('session_title', '')[:60]} | "
              f"{(c.get('categories') or [{}])[0].get('name', '')} | izleyici {c.get('viewer_count')}")
    else:
        print(f"⚪ {ad}: canlı değil")
    v = (getir(f"https://kick.com/api/v2/channels/{ad}/videos", deneme=3) or [])[:1]
    for x in v:
        print(f"   son kayıt: {x.get('start_time', x.get('created_at', ''))[:16]} | {x.get('session_title', '')[:60]}")
