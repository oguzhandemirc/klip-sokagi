#!/usr/bin/env python3
"""Planlı (gizli) bir videoyu hemen herkese açık yapar.

Kullanım: .venv/bin/python simdi_yayinla.py VIDEO_ID
"""
import json
import sys

from yukle import KAYIT, servis

vid = sys.argv[1]
yt = servis()
v = yt.videos().list(part="status", id=vid).execute()["items"][0]
s = v["status"]
s.pop("publishAt", None)
s["privacyStatus"] = "public"
s = {k: s[k] for k in ("privacyStatus", "embeddable", "license", "publicStatsViewable",
                       "selfDeclaredMadeForKids", "containsSyntheticMedia") if k in s}
yt.videos().update(part="status", body={"id": vid, "status": s}).execute()
# Kayıttaki yayın zamanını boşalt: planla.py o saati artık dolu saymasın.
satirlar = [json.loads(x) for x in KAYIT.read_text().splitlines()]
for k in satirlar:
    if k["id"] == vid:
        k["publishAt"] = None
KAYIT.write_text("".join(json.dumps(k, ensure_ascii=False) + "\n" for k in satirlar))
print(f"✔ Herkese açık: https://youtube.com/shorts/{vid}")
