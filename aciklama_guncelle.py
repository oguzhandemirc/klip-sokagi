#!/usr/bin/env python3
"""Yüklenmiş videoların açıklamasını yukle.aciklama_duzenle'nin güncel kuralıyla yeniden yazar.

Kullanım: .venv/bin/python aciklama_guncelle.py [--gercek]   (kayit.jsonl'deki hepsi)
"""
import json
import sys

from yukle import KAYIT, KOK, aciklama_duzenle, proje_yolu, servis

gercek = "--gercek" in sys.argv
yt = servis()
for satir in KAYIT.read_text().splitlines():
    k = json.loads(satir)
    meta = json.loads((KOK / proje_yolu(k["dosya"])).with_suffix(".json").read_text())
    aciklama, etiketler = aciklama_duzenle(meta.get("aciklama", ""), meta.get("ek_yayincilar", []))
    v = yt.videos().list(part="snippet", id=k["id"]).execute()["items"][0]
    sn = v["snippet"]
    yeni = {"title": sn["title"], "categoryId": sn["categoryId"], "description": aciklama, "tags": etiketler,
            "defaultLanguage": sn.get("defaultLanguage", "tr")}
    print(f"--- {k['id']}\n{aciklama}\n")
    if gercek:
        yt.videos().update(part="snippet", body={"id": k["id"], "snippet": yeni}).execute()
        print("✔ güncellendi")
