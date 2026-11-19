#!/usr/bin/env python3
"""Klip Sokağı kanal görselleri: 3 logo seçeneği (800x800), afiş (2048x1152), önizleme sayfası.

Kullanım: .venv/bin/python marka_uret.py  →  marka/
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

KOK = Path(__file__).resolve().parent
CIKTI = KOK / "marka"
CIKTI.mkdir(exist_ok=True)
from duzenle import FONT_KALIN as KALIN  # taşınabilir yazı tipi
SARI, SIYAH, BEYAZ, KIRMIZI = (255, 212, 0), (17, 17, 17), (255, 255, 255), (235, 40, 50)


def font(boyut):
    return ImageFont.truetype(KALIN, boyut)


def ortala(d, metin, f, y, renk, en):
    g = d.textlength(metin, font=f)
    d.text(((en - g) / 2, y), metin, font=f, fill=renk)


def oynat(d, cx, cy, r, renk):
    d.polygon([(cx - r * 0.6, cy - r), (cx - r * 0.6, cy + r), (cx + r, cy)], fill=renk)


def logo_tabela():
    """A: sarı sokak tabelası, siyah yazı, kırmızı oynat düğmesi."""
    im = Image.new("RGB", (800, 800), SIYAH)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((90, 210, 710, 590), 40, fill=SARI, outline=BEYAZ, width=10)
    ortala(d, "KLİP", font(150), 225, SIYAH, 800)
    ortala(d, "SOKAĞI", font(98), 410, SIYAH, 800)
    d.ellipse((330, 600, 470, 740), fill=KIRMIZI)
    oynat(d, 405, 670, 34, BEYAZ)
    return im


def logo_rozet():
    """B: tam sarı zemin, ortada siyah oynat kutusu, altında yazı."""
    im = Image.new("RGB", (800, 800), SARI)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((280, 150, 520, 330), 46, fill=SIYAH)
    oynat(d, 408, 240, 52, SARI)
    ortala(d, "KLİP", font(160), 345, SIYAH, 800)
    ortala(d, "SOKAĞI", font(86), 535, SIYAH, 800)
    return im


def logo_ks():
    """C: kısa monogram "KS" — küçük boyutta en okunaklı."""
    im = Image.new("RGB", (800, 800), SIYAH)
    d = ImageDraw.Draw(im)
    d.ellipse((60, 60, 740, 740), fill=SARI)
    ortala(d, "KS", font(330), 175, SIYAH, 800)
    d.rounded_rectangle((250, 590, 550, 650), 30, fill=SIYAH)
    oynat(d, 405, 620, 20, SARI)
    return im


def afis():
    """2048x1152; yazılar 1546x423 güvenli alanda (her cihazda görünen orta şerit)."""
    en, boy = 2048, 1152
    im = Image.new("RGB", (en, boy), SIYAH)
    d = ImageDraw.Draw(im)
    # Arka planda eğik sarı-siyah yol şeritleri
    for x in range(-boy, en, 160):
        d.polygon([(x, boy), (x + 70, boy), (x + 70 + boy, 0), (x + boy, 0)], fill=(32, 32, 32))
    gy = (boy - 423) // 2
    d.rectangle((0, gy - 6, en, gy + 423 + 6), fill=SIYAH)
    d.rectangle((0, gy - 14, en, gy - 6), fill=SARI)
    d.rectangle((0, gy + 429, en, gy + 437), fill=SARI)
    ortala(d, "KLİP SOKAĞI", font(150), gy + 50, SARI, en)
    ortala(d, "Yayınların en çok konuşulan anları", font(56), gy + 245, BEYAZ, en)
    ortala(d, "HER GÜN YENİ SHORTS", font(40), gy + 330, (170, 170, 170), en)
    return im


def daire_onizleme(im, boyut):
    """YouTube avatarı daire kırpar; küçük boyutta nasıl göründüğünü gösterir."""
    k = im.resize((boyut, boyut), Image.LANCZOS)
    m = Image.new("L", (boyut, boyut), 0)
    ImageDraw.Draw(m).ellipse((0, 0, boyut, boyut), fill=255)
    zemin = Image.new("RGB", (boyut, boyut), (40, 40, 40))
    zemin.paste(k, (0, 0), m)
    return zemin


def main():
    logolar = {"A-tabela": logo_tabela(), "B-rozet": logo_rozet(), "C-ks": logo_ks()}
    for ad, im in logolar.items():
        im.save(CIKTI / f"logo-{ad}.png")
    afis().save(CIKTI / "afis.png")
    # Önizleme: her logo büyük daire + 88 px + 40 px (yorum/arama boyutu)
    sayfa = Image.new("RGB", (1500, 620), (40, 40, 40))
    d = ImageDraw.Draw(sayfa)
    for i, (ad, im) in enumerate(logolar.items()):
        x = 40 + i * 490
        sayfa.paste(daire_onizleme(im, 360), (x, 40))
        sayfa.paste(daire_onizleme(im, 88), (x + 380, 140))
        sayfa.paste(daire_onizleme(im, 40), (x + 404, 260))
        d.text((x, 440), ad, font=font(48), fill=BEYAZ)
    sayfa.save(CIKTI / "onizleme.png")
    print("✔", CIKTI)


if __name__ == "__main__":
    main()
