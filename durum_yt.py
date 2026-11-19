#!/usr/bin/env python3
"""Yüklenen videoların YouTube'daki durumu: gizlilik, planlı yayın zamanı, işleme durumu.

Kullanım: .venv/bin/python durum_yt.py            (kayit.jsonl'deki hepsi)
          .venv/bin/python durum_yt.py VIDEO_ID ...
"""
import json
import sys

from yukle import KAYIT, servis

idler = sys.argv[1:] or [json.loads(s)["id"] for s in KAYIT.read_text().splitlines()]
yt = servis()
for i in range(0, len(idler), 50):
    yanit = yt.videos().list(part="snippet,status,processingDetails,contentDetails", id=",".join(idler[i:i + 50])).execute()
    for v in yanit.get("items", []):
        s = v["status"]
        print(f"{v['id']}  {s['privacyStatus']:8} yayın={s.get('publishAt', '-'):25} yükleme={s.get('uploadStatus')}  "
              f"süre={v['contentDetails'].get('duration')}  {v['snippet']['title']}")
