#!/usr/bin/env python3
"""Sohbet katmanı: bir klibin zaman aralığındaki seçme sohbet mesajlarını çıkarır (duzenle.py --sohbet için).

Kullanım:
    python3 sohbet_katman.py data/sohbet/kick-<uuid>.json --bas 7223.2 --sure 22 -o data/parca/X-sohbet.json
    (--bas: klibin yayındaki başlangıç saniyesi)

Çıktı: [{"t": klip içi saniye, "ad": "kullanici", "metin": "..."}]
Not: Kick sohbeti örneklenerek indirildi (10 sn'de son 25 mesaj); burada görünen mesajlar gerçek ama hepsi değil.
"""
import argparse
import json
import re
from pathlib import Path

from an_sec import gecerli, bos_mesaj

EMOTE = re.compile(r"\[emote:\d+:([^\]]+)\]")
LINK = re.compile(r"https?://|www\.", re.I)


def temizle(metin):
    metin = EMOTE.sub("", metin)
    metin = re.sub(r"(.)\1{5,}", lambda m: m.group(1) * 5, metin)  # "hahahahahahaha" / "aaaaaaa" kısalt
    metin = " ".join(metin.split())
    return metin[:38] + "…" if len(metin) > 40 else metin


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sohbet")
    ap.add_argument("--bas", type=float, required=True)
    ap.add_argument("--sure", type=float, required=True)
    ap.add_argument("--en-cok", type=int, default=16)
    ap.add_argument("-o", "--cikti", required=True)
    a = ap.parse_args()

    veri = json.loads(Path(a.sohbet).read_text())
    gorulen, adaylar = set(), []
    for o in veri["ornekler"]:
        for m in o["mesajlar"]:
            sn, ad, metin = m[0], m[1], m[2]
            if not (a.bas <= sn <= a.bas + a.sure) or not gecerli(m) or LINK.search(metin):
                continue
            temiz = temizle(metin)
            if len(temiz) < 2 or bos_mesaj(temiz) or (ad, temiz) in gorulen:
                continue
            gorulen.add((ad, temiz))
            adaylar.append({"t": round(sn - a.bas, 2), "ad": ad, "metin": temiz})
    adaylar.sort(key=lambda x: x["t"])
    # Fazlaysa zamana eşit yay: her dilimden bir mesaj (patlama anı yoğun olduğundan doğal olarak öne çıkar).
    if len(adaylar) > a.en_cok:
        adim = len(adaylar) / a.en_cok
        adaylar = [adaylar[int(i * adim)] for i in range(a.en_cok)]
    # Aynı saniyedeki mesajlar okunabilsin diye en az 0,6 sn arayla diz.
    son = -1.0
    for x in adaylar:
        x["t"] = max(x["t"], son + 0.6)
        son = x["t"]
    Path(a.cikti).write_text(json.dumps(adaylar, ensure_ascii=False, indent=1))
    for x in adaylar:
        print(f"{x['t']:5.1f}  {x['ad']}: {x['metin']}")


if __name__ == "__main__":
    main()
