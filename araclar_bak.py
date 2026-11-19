#!/usr/bin/env python3
"""Yardımcı: örnek dosyasında verilen saniye çevresindeki mesajları gösterir.

Kullanım: python3 araclar_bak.py data/sohbet/kick-X.json 3:51:00 [--genislik 30] [--adet 25]
"""
import argparse
import json


def sn(metin):
    p = [int(x) for x in metin.split(":")]
    while len(p) < 3:
        p.insert(0, 0)
    return p[0] * 3600 + p[1] * 60 + p[2]


ap = argparse.ArgumentParser()
ap.add_argument("dosya")
ap.add_argument("zaman")
ap.add_argument("--genislik", type=int, default=30)
ap.add_argument("--adet", type=int, default=25)
a = ap.parse_args()
t = sn(a.zaman)
veri = json.load(open(a.dosya))
gorulen = set()
for o in veri["ornekler"]:
    if abs(o["t"] - t) <= a.genislik:
        print(f"--- örnek t={o['t']} hız={o['hiz']}")
        for m in o["mesajlar"][:a.adet]:
            anahtar = (m[0], m[1], m[2])
            if anahtar not in gorulen:
                gorulen.add(anahtar)
                print(f"  {m[0]:6d} {m[1][:14]:14s} {m[3][:7]:7s} {m[2][:70]}")
