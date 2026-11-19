#!/usr/bin/env python3
"""Yatay (16:9) kısa video üretir: 2-5 dk, tek hikâye ya da mini derleme.

Her bölümün ilk ~3,5 sn'sinde sol altta başlık şeridi (#n + başlık + bağlam), sürekli olarak sağ üstte
yarı saydam yayıncı rozeti + Klip Sokağı logosu. Bölümler arka arkaya eklenir (giriş kartı yok: ilk saniye aksiyon).
Yanında: küçük resim (1280x720) ve bölüm zaman damgalı açıklama.

Plan (JSON):
{"ad": "rraenee-gta6-gun1", "baslik": "...", "kredi": "kick.com/rraenee", "aciklama": "1-2 cümle",
 "hashtag": ["#GTA6", "#RRaenee"], "kapak_metin": "TEKNEYİ GÖMDÜ", "kapak_bolum": 0, "kapak_sn": 12,
 "bolumler": [{"girdi": "data/parca/X-03.mp4", "bas": 5, "sure": 40, "baslik": "Tekne mangrova gömüldü",
               "baglam": "Görev başarısız olmadan önce…"}]}

Kullanım: .venv/bin/python uzun.py plan-uzun.json [--klasor data/hazir/uzun]
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from duzenle import FONT_KALIN, FONT_NORMAL, KICK_YESIL, tr_buyuk

KOK = Path(__file__).resolve().parent
EN, BOY, FPS = 1920, 1080, 60
SARI = (255, 212, 0)


def serit_png(no, baslik, baglam, yol):
    """Sol alt başlık şeridi: sarı numara kutusu + beyaz başlık + gri bağlam satırı."""
    fb, fk, fn = ImageFont.truetype(FONT_KALIN, 54), ImageFont.truetype(FONT_NORMAL, 34), ImageFont.truetype(FONT_KALIN, 60)
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    gen = int(max(d0.textlength(tr_buyuk(baslik), font=fb), d0.textlength(baglam or "", font=fk))) + 190
    yuk = 150 if baglam else 100
    img = Image.new("RGBA", (EN, yuk), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 0, 40 + gen, yuk], radius=18, fill=(10, 10, 10, 215))
    d.rounded_rectangle([40, 0, 140, yuk], radius=18, fill=SARI)
    d.text((90, yuk / 2), f"{no}", font=fn, fill=(10, 10, 10), anchor="mm")
    d.text((165, 18), tr_buyuk(baslik), font=fb, fill=(255, 255, 255))
    if baglam:
        d.text((167, 92), baglam, font=fk, fill=(200, 200, 200))
    img.save(yol)
    return yuk


def kose_png(kredi, logo, yol):
    """Sağ üst: yarı saydam Kick rozeti + logo."""
    img = Image.new("RGBA", (EN, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_KALIN, 30)
    gen = int(d.textlength(kredi, font=f)) + 95
    cap = 86
    x1 = EN - 40 - cap - 20
    x0 = x1 - gen
    d.rounded_rectangle([x0, 18, x1, 18 + 66], radius=33, fill=(8, 8, 8, 150), outline=KICK_YESIL + (160,), width=4)
    d.rounded_rectangle([x0 + 14, 28, x0 + 60, 74], radius=8, fill=KICK_YESIL + (170,))
    d.text((x0 + 37, 51), "K", font=ImageFont.truetype(FONT_KALIN, 36), fill=(0, 0, 0, 200), anchor="mm")
    d.text((x0 + 75, 51), kredi, font=f, fill=KICK_YESIL + (170,), anchor="lm")
    if logo and Path(logo).exists():
        lg = Image.open(logo).convert("RGBA").resize((cap, cap), Image.LANCZOS)
        m = Image.new("L", (cap, cap), 0)
        ImageDraw.Draw(m).ellipse((0, 0, cap - 1, cap - 1), fill=230)
        img.paste(lg, (EN - 40 - cap, 8), m)
    img.save(yol)


def kapak(kare, metin, logo, yol, kamera=None):
    """1280x720 küçük resim: oyun karesi + (varsa) BÜYÜTÜLMÜŞ yayıncı kamerası sağda + büyük yazı + logo."""
    kaynak = Image.open(kare).convert("RGB")
    im = kaynak.resize((1280, 720), Image.LANCZOS)
    if kamera:
        kx, ky, kg, kyuk = (int(v) for v in kamera.split(":"))
        kam = kaynak.crop((kx, ky, kx + kg, ky + kyuk))
        en = 760
        kam = kam.resize((en, round(en * kyuk / kg)), Image.LANCZOS)
        ImageDraw.Draw(kam).rectangle([0, 0, kam.width - 1, kam.height - 1], outline=SARI, width=8)
        im.paste(kam, (1280 - en - 24, 30))
    alt = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    da = ImageDraw.Draw(alt)
    for y in range(360, 720):  # alttan kararan geçiş
        da.line([(0, y), (1280, y)], fill=(0, 0, 0, int(200 * (y - 360) / 360)))
    im = Image.alpha_composite(im.convert("RGBA"), alt)
    d = ImageDraw.Draw(im)
    boyut = 120
    metin = tr_buyuk(metin)
    while d.textlength(metin, font=ImageFont.truetype(FONT_KALIN, boyut)) > 1180 and boyut > 60:
        boyut -= 6
    f = ImageFont.truetype(FONT_KALIN, boyut)
    d.text((640, 640), metin, font=f, fill=SARI, anchor="ms", stroke_width=8, stroke_fill=(0, 0, 0))
    if logo and Path(logo).exists():
        lg = Image.open(logo).convert("RGBA").resize((110, 110), Image.LANCZOS)
        m = Image.new("L", (110, 110), 0)
        ImageDraw.Draw(m).ellipse((0, 0, 109, 109), fill=255)
        im.paste(lg, (24, 20), m)
    im.convert("RGB").save(yol, quality=92)


def zaman(sn):
    sn = int(sn)
    return f"{sn // 60}:{sn % 60:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--klasor", default="data/hazir/uzun")
    ap.add_argument("--logo", default=str(KOK / "marka" / "logo-B-rozet.png"))
    a = ap.parse_args()
    p = json.loads(Path(a.plan).read_text())
    klasor = KOK / a.klasor
    klasor.mkdir(parents=True, exist_ok=True)
    cikti = klasor / f"{p['ad']}.mp4"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        kose_png(p.get("kredi", ""), a.logo, tmp / "kose.png")
        parcalar, sureler = [], []
        for i, b in enumerate(p["bolumler"], 1):
            yuk = serit_png(i, b["baslik"], b.get("baglam", ""), tmp / f"s{i}.png")
            par = tmp / f"p{i:02d}.mp4"
            filtre = (f"[0:v]scale={EN}:{BOY}:flags=lanczos,fps={FPS},format=yuv420p[v0];"
                      f"[v0][1:v]overlay=0:0[v1];"
                      f"[v1][2:v]overlay=0:{BOY - yuk - 70}:enable='between(t,0.3,3.8)'[v];"
                      f"[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(b.get("bas", 0)), "-t", str(b["sure"]),
                            "-i", b["girdi"], "-i", str(tmp / "kose.png"), "-i", str(tmp / f"s{i}.png"),
                            "-filter_complex", filtre, "-map", "[v]", "-map", "[a]",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-r", str(FPS),
                            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(par)], check=True)
            parcalar.append(par)
            sureler.append(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                                 "-of", "csv=p=0", str(par)], capture_output=True, text=True).stdout))
            print(f"  ✔ bölüm {i}: {b['baslik']} ({sureler[-1]:.0f} sn)", flush=True)
        liste = tmp / "liste.txt"
        liste.write_text("".join(f"file '{x}'\n" for x in parcalar))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(liste),
                        "-c", "copy", "-movflags", "+faststart", str(cikti)], check=True)

        # Küçük resim
        kb = p["bolumler"][p.get("kapak_bolum", 0)]
        kare = tmp / "kare.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(kb.get("bas", 0) + p.get("kapak_sn", 5)),
                        "-i", kb["girdi"], "-frames:v", "1", str(kare)], check=True)
        kapak(kare, p.get("kapak_metin", p["baslik"]), a.logo, cikti.with_suffix(".jpg"), p.get("kamera"))

    # Açıklama: bölüm damgaları (ilki 0:00, en az 3 bölüm ve her biri ≥ 10 sn ise YouTube bölüm yapar)
    t, damga = 0.0, []
    for b, s in zip(p["bolumler"], sureler):
        damga.append(f"{zaman(t)} {b['baslik']}")
        t += s
    aciklama = p.get("aciklama", "") + "\n\n" + "\n".join(damga) + "\n\n" + " ".join(p.get("hashtag", []) + ["#KlipSokağı"])
    cikti.with_suffix(".json").write_text(json.dumps({**p, "aciklama_son": aciklama.strip(), "sure": round(t)},
                                                     ensure_ascii=False, indent=1))
    print(f"→ {cikti} ({zaman(t)})\n{aciklama}")


if __name__ == "__main__":
    main()
