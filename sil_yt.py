#!/usr/bin/env python3
"""YAYINLANMAMIŞ (gizli + planlı) yüklemeleri YouTube'dan siler ve kayit.jsonl'dan çıkarır.
Herkese açık ya da planı olmayan videoya dokunmaz.

Kullanım: .venv/bin/python sil_yt.py VIDEO_ID ... --gercek     (id vermezsen kayıttaki hepsi)
"""
import json
import sys

from yukle import KAYIT, servis

gercek = "--gercek" in sys.argv
kayit = [json.loads(s) for s in KAYIT.read_text().splitlines()]
idler = [x for x in sys.argv[1:] if not x.startswith("--")] or [k["id"] for k in kayit]
yt = servis()
durum = {v["id"]: v["status"] for v in yt.videos().list(part="status", id=",".join(idler)).execute()["items"]}
silinen = set()
for i in idler:
    s = durum.get(i, {})
    if s.get("privacyStatus") != "private" or not s.get("publishAt"):
        print(f"= dokunulmadı {i}: {s.get('privacyStatus')}")
        continue
    print(f"{'✘ silindi' if gercek else '(kuru) silinecek'} {i}")
    if gercek:
        yt.videos().delete(id=i).execute()
        silinen.add(i)
KAYIT.write_text("".join(json.dumps(k, ensure_ascii=False) + "\n" for k in kayit if k["id"] not in silinen))
