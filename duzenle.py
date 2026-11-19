#!/usr/bin/env python3
"""Düzenleme: ham yatay kesitten altyazılı, kancalı, kredili dikey Short üretir.

Bu bilgisayardaki ffmpeg'de yazı yakma (libass/drawtext) yok; bu yüzden altyazı ve
yazılar Pillow ile saydam PNG olarak çizilip ffmpeg overlay ile bindirilir.

Kullanım (.venv içindeki Python ile):
    .venv/bin/python duzenle.py data/parca/X-01.mp4 --kredi "kick.com/rraenee" --kanca "Kanca yazısı"
    [--model small] [--cikti data/hazir/X-01-short.mp4]

Çıktı: 1080x1920 mp4 + yanında <ad>.json (transkript, kelime zamanları).
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

KOK = Path(__file__).resolve().parent


def font_bul(*adlar):
    """Yazı tipini Mac, Windows (WSL'den /mnt/c) ya da projedeki fonts/ klasöründe arar."""
    yerler = [KOK / "fonts", Path("/System/Library/Fonts/Supplemental"), Path("/Library/Fonts"),
              Path("/mnt/c/Windows/Fonts"), Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/msttcorefonts")]
    for y in yerler:
        for ad in adlar:
            for aday in (y / ad, y / ad.lower()):
                if aday.exists():
                    return str(aday)
    raise SystemExit(f"Yazı tipi yok: {adlar}. fonts/ klasörüne koy.")


FONT_KALIN = font_bul("Arial Black.ttf", "ariblk.ttf")
FONT_NORMAL = font_bul("Arial Bold.ttf", "arialbd.ttf")
G, Y = 1080, 1920
import os
CIHAZ = os.environ.get("WHISPER_CIHAZ", "cpu")

# Yerleşim: üstte kanca, ortada video (biraz yakınlaştırılmış), altta altyazı, en altta kredi.
VIDEO_Y = 560          # videonun üst kenarı
VIDEO_YUKSEKLIK = 760  # 1080 genişlikte 16:9 → 608; 760 için yanlardan kırpılır (yakınlaştırma)
KANCA_Y = 250
ALTYAZI_Y = 1420
KREDI_Y = 1800

# Kameralı yerleşim (--kamera): üstte yayıncı kamerası büyük, altta oyun, en altta altyazı.
K_KREDI_Y = 40
K_KANCA_Y = 110
K_KAMERA_Y = 330        # kamera panelinin üstü; yükseklik genişliğe göre (1080 x en/boy)
K_OYUN_YUKSEKLIK = 720   # oyun paneli yüksekliği (yanlardan kırpılır)
K_ALTYAZI_BOSLUK = 20    # oyun panelinin altından altyazıya

# "tam" yerleşim (--yerlesim tam, --kamera gerekir): boşluk yok; üstte kamera şeridi, altta oyun ekranı
# doldurur, birleşim yerinde Kick rozeti, tek kelimelik büyük altyazı. Çok izlenen klip kanallarındaki biçim.
T_KAMERA_YUKSEKLIK = 540
T_KANCA_Y = T_KAMERA_YUKSEKLIK + 80
T_ALTYAZI_Y = 1430
KICK_YESIL = (83, 252, 24)


def tr_buyuk(metin):
    return metin.replace("i", "İ").replace("ı", "I").upper()


def yazi_png(metin, boyut, font, yol, kutu=False, renk=(255, 255, 255), en=G - 120):
    """Ortalanmış, kenarlıklı yazıyı saydam PNG'ye çizer; gerekirse satırlara böler."""
    f = ImageFont.truetype(font, boyut)
    gecici = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    satirlar, satir = [], ""
    for kelime in metin.split():
        deneme = (satir + " " + kelime).strip()
        if gecici.textlength(deneme, font=f) <= en or not satir:
            satir = deneme
        else:
            satirlar.append(satir)
            satir = kelime
    satirlar.append(satir)
    aralik = int(boyut * 1.18)
    yukseklik = aralik * len(satirlar) + 40
    img = Image.new("RGBA", (G, yukseklik), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if kutu:
        genislik = max(d.textlength(s, font=f) for s in satirlar)
        x0 = (G - genislik) / 2 - 30
        d.rounded_rectangle([x0, 0, G - x0, yukseklik], radius=28, fill=(0, 0, 0, 175))
    for i, s in enumerate(satirlar):
        w = d.textlength(s, font=f)
        d.text(((G - w) / 2, 20 + i * aralik), s, font=f, fill=renk,
               stroke_width=0 if kutu else max(4, boyut // 12), stroke_fill=(0, 0, 0))
    img.save(yol)
    return yukseklik


def rozet_png(metin, yol, boyut=42, seffaf=1.0):
    """Kick rozeti: siyah hap, yeşil kenar, solda yeşil K kutusu, yanında kanal adresi."""
    f = ImageFont.truetype(FONT_KALIN, boyut)
    gecici = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    kutu = int(boyut * 1.5)
    en = int(kutu + 30 + gecici.textlength(metin, font=f) + 40)
    yuk = kutu + 24
    img = Image.new("RGBA", (G, yuk), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0 = (G - en) // 2
    d.rounded_rectangle([x0, 0, x0 + en, yuk - 1], radius=yuk // 2, fill=(8, 8, 8, 235),
                        outline=KICK_YESIL, width=5)
    kx, ky = x0 + 22, 12
    d.rounded_rectangle([kx, ky, kx + kutu, ky + kutu], radius=10, fill=KICK_YESIL)
    fk = ImageFont.truetype(FONT_KALIN, int(kutu * 0.8))
    d.text((kx + kutu / 2, ky + kutu / 2), "K", font=fk, fill=(0, 0, 0), anchor="mm")
    d.line([kx + kutu + 16, ky + 6, kx + kutu + 16, ky + kutu - 6], fill=KICK_YESIL, width=4)
    d.text((kx + kutu + 32, yuk / 2), metin, font=f, fill=KICK_YESIL, anchor="lm")
    if seffaf < 1:
        img.putalpha(img.getchannel("A").point(lambda v: int(v * seffaf)))
    img.save(yol)
    return yuk


def logo_png(kaynak, yol, cap=96, kenar=24):
    """Kanal logosu: G genişliğinde saydam şerit, sağda daire içinde logo (beyaz ince çerçeve)."""
    logo = Image.open(kaynak).convert("RGBA").resize((cap, cap), Image.LANCZOS)
    maske = Image.new("L", (cap, cap), 0)
    ImageDraw.Draw(maske).ellipse((0, 0, cap - 1, cap - 1), fill=255)
    img = Image.new("RGBA", (G, cap + 6), (0, 0, 0, 0))
    x = G - cap - kenar
    ImageDraw.Draw(img).ellipse((x - 3, 0, x + cap + 2, cap + 5), fill=(255, 255, 255, 230))
    img.paste(logo, (x, 3), maske)
    img.save(yol)
    return cap + 6


AD_RENKLERI = [(83, 252, 24), (255, 99, 132), (54, 162, 235), (255, 206, 86), (153, 102, 255),
               (255, 159, 64), (0, 230, 200), (255, 120, 220)]


def sohbet_png(mesajlar, yol, en=660, boyut=34):
    """Son birkaç sohbet mesajını yarı saydam kutuda alt alta çizer (Kick sohbeti görünümü)."""
    f_ad = ImageFont.truetype(FONT_KALIN, boyut)
    f_metin = ImageFont.truetype(FONT_NORMAL, boyut)
    satir_y = int(boyut * 1.45)
    yukseklik = satir_y * len(mesajlar) + 28
    img = Image.new("RGBA", (en, yukseklik), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, en - 1, yukseklik - 1], radius=22, fill=(10, 10, 14, 170))
    for i, m in enumerate(mesajlar):
        y = 14 + i * satir_y
        ad = m["ad"][:16] + ":"
        renk = AD_RENKLERI[sum(map(ord, m["ad"])) % len(AD_RENKLERI)]
        d.text((20, y), ad, font=f_ad, fill=renk, stroke_width=2, stroke_fill=(0, 0, 0))
        x = 20 + d.textlength(ad, font=f_ad) + 12
        metin = m["metin"]
        while metin and x + d.textlength(metin, font=f_metin) > en - 20:
            metin = metin[:-2]
        d.text((x, y), metin, font=f_metin, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(yol)
    return yukseklik


def transkript(ses, model_adi):
    from faster_whisper import WhisperModel
    import wave
    import numpy as np
    # Sesi kendimiz okuyoruz: faster-whisper'ın av sürümüyle uyumsuzluğunu atlatır.
    with wave.open(str(ses)) as w:
        dizi = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    model = WhisperModel(model_adi, device=CIHAZ, compute_type="int8" if CIHAZ == "cpu" else "float16")
    parcalar, _ = model.transcribe(dizi, language="tr", word_timestamps=True, vad_filter=True,
                                   condition_on_previous_text=False)
    kelimeler = []
    for p in parcalar:
        for k in p.words or []:
            metin = k.word.strip()
            if metin:
                kelimeler.append({"metin": metin, "bas": round(k.start, 2), "son": round(k.end, 2),
                                  "olasilik": round(k.probability, 2)})
    return kelimeler


def kaynak_boyut(yol):
    """Girdi videonun (genişlik, yükseklik) pikseli."""
    c = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height", "-of", "csv=p=0", str(yol)], capture_output=True, text=True)
    g, y = c.stdout.strip().split(",")[:2]
    return int(g), int(y)


def gruplar(kelimeler, en_cok=3, en_uzun=1.4):
    """Kelimeleri ekranda birlikte görünecek kısa öbeklere ayırır."""
    sonuc, grup = [], []
    for k in kelimeler:
        if grup and (len(grup) >= en_cok or k["son"] - grup[0]["bas"] > en_uzun
                     or k["bas"] - grup[-1]["son"] > 0.6):
            sonuc.append(grup)
            grup = []
        grup.append(k)
    if grup:
        sonuc.append(grup)
    cikti = []
    for i, g in enumerate(sonuc):
        son = g[-1]["son"] + 0.25
        if i + 1 < len(sonuc):
            son = min(son, sonuc[i + 1][0]["bas"])
        cikti.append({"metin": " ".join(k["metin"] for k in g), "bas": g[0]["bas"], "son": son})
    return cikti


def main():
    ap = argparse.ArgumentParser(description="Ham kesitten dikey Short üretir.")
    ap.add_argument("girdi")
    ap.add_argument("--kanca", default="", help="ilk saniyelerde üstte görünecek yazı")
    ap.add_argument("--kanca-sure", type=float, default=0, help="0 = bütün klip boyunca")
    ap.add_argument("--kredi", default="")
    ap.add_argument("--model", default="medium", help="faster-whisper modeli: small, medium, large-v3")
    ap.add_argument("--bas", type=float, default=0, help="girdide başlangıç saniyesi")
    ap.add_argument("--sure", type=float, default=0, help="0 = sonuna kadar")
    ap.add_argument("--muzik", help="arka plan müziği dosyası (telifsiz olmalı)")
    ap.add_argument("--muzik-seviye", type=float, default=0.18)
    ap.add_argument("--kamera", help='kaynakta yayıncı kamerası "x:y:g:y" (piksel, ör. 1390:144:530:296)')
    ap.add_argument("--yerlesim", choices=["kutulu", "tam"], default="kutulu",
                    help="tam: boşluksuz kamera + oyun (yalnız --kamera ile)")
    ap.add_argument("--sohbet", help="sohbet_katman.py çıktısı: klipte akan sohbet kutusu")
    ap.add_argument("--sohbet-satir", type=int, default=4, help="kutuda aynı anda görünen mesaj")
    ap.add_argument("--logo", default=str(KOK / "marka" / "logo-B-rozet.png"),
                    help="kamera/oyun birleşiminin sağına konan kanal logosu ('' = yok)")
    ap.add_argument("--cozunurluk", type=int, default=1440, help="çıktı genişliği (1080 | 1440); yükseklik 16:9 dikey")
    ap.add_argument("--ek", help="meta dosyasına eklenecek JSON (başlıklar, açıklama vb.)")
    ap.add_argument("--cikti")
    a = ap.parse_args()

    girdi = Path(a.girdi)
    cikti = Path(a.cikti) if a.cikti else KOK / "data" / "hazir" / f"{girdi.stem}-short.mp4"
    cikti.parent.mkdir(parents=True, exist_ok=True)
    kes = ["-ss", str(a.bas)] + (["-t", str(a.sure)] if a.sure else [])

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        ses = tmp / "ses.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *kes, "-i", str(girdi), "-ac", "1", "-ar", "16000",
                        str(ses)], check=True)
        kelimeler = transkript(ses, a.model)
        obekler = gruplar(kelimeler)

        girdiler = ["-i", str(girdi)]
        arka = (f"[a]scale={G}:{Y}:force_original_aspect_ratio=increase,crop={G}:{Y},boxblur=40:6,"
                f"eq=brightness=-0.12[arka]")
        tam = a.yerlesim == "tam" and a.kamera
        if tam:
            kx, ky, kg, kyuk = (int(v) for v in a.kamera.split(":"))
            th = T_KAMERA_YUKSEKLIK
            kh = round(kg * th / G / 2) * 2          # şeridin en/boy oranına uyan kaynak yüksekliği
            kh = min(kh, kyuk)
            oyun_h = Y - th
            kanca_y, kredi_y, altyazi_y = T_KANCA_Y, None, T_ALTYAZI_Y
            src_g, src_y = kaynak_boyut(girdi)
            # Oyun: ekranın GERÇEK ortasından kırp (karakter ortada kalır); kameraya taşarsa sola kaydır.
            ow = round(src_y * G / oyun_h / 2) * 2
            ox = max(0, min(src_g // 2 - ow // 2, kx - ow))
            filtre = [
                "[0:v]split[b][c]",
                # Kameranın üstü (boş duvar) kırpılır, kişiler kalır; 2 kat büyütüldüğü için hafif keskinleştirilir.
                f"[b]crop={kg}:{kh}:{kx}:{ky + kyuk - kh},scale={G}:{th}:flags=lanczos,unsharp=5:5:0.7[kam]",
                f"[c]crop={ow}:{src_y}:{ox}:0,scale={G}:{oyun_h}:flags=lanczos[oyun]",
                "[kam][oyun]vstack[v0]",
            ]
            obekler = gruplar(kelimeler, en_cok=1, en_uzun=0.8)
        elif a.kamera:
            kx, ky, kg, kyuk = (int(v) for v in a.kamera.split(":"))
            kam_yuk = round(G * kyuk / kg / 2) * 2
            oyun_y = K_KAMERA_Y + kam_yuk
            kanca_y, kredi_y = K_KANCA_Y, K_KREDI_Y
            altyazi_y = oyun_y + K_OYUN_YUKSEKLIK + K_ALTYAZI_BOSLUK
            filtre = [
                "[0:v]split=3[a][b][c]", arka,
                f"[b]crop={kg}:{kyuk}:{kx}:{ky},scale={G}:{kam_yuk}[kam]",
                # Oyun: kamera zaten üstte; oyundan kameranın soluna kadar olan alan alınır,
                # genişliğe sığdırılır, üstten-alttan eşit kırpılır.
                f"[c]crop={kx}:ih:0:0,scale={G}:-2,crop={G}:{K_OYUN_YUKSEKLIK}[oyun]",
                f"[arka][kam]overlay=0:{K_KAMERA_Y}[ak]",
                f"[ak][oyun]overlay=0:{oyun_y}[v0]",
            ]
        else:
            kanca_y, kredi_y, altyazi_y = KANCA_Y, KREDI_Y, ALTYAZI_Y
            filtre = [
                "[0:v]split[a][b]", arka,
                f"[b]scale=-2:{VIDEO_YUKSEKLIK},crop={G}:{VIDEO_YUKSEKLIK}[on]",
                f"[arka][on]overlay=0:{VIDEO_Y}[v0]",
            ]
        son_etiket, n = "v0", 1

        def bindir(png, y, bas=None, son=None):
            nonlocal son_etiket, n
            girdiler.extend(["-i", str(png)])
            zaman = f":enable='between(t,{bas:.2f},{son:.2f})'" if bas is not None else ""
            filtre.append(f"[{son_etiket}][{n}:v]overlay=0:{y}{zaman}[v{n}]")
            son_etiket = f"v{n}"
            n += 1

        if a.kanca:
            yazi_png(tr_buyuk(a.kanca), 60 if a.kamera else 70, FONT_KALIN, tmp / "kanca.png", kutu=True)
            if a.kanca_sure:
                bindir(tmp / "kanca.png", kanca_y, 0, a.kanca_sure)
            else:
                bindir(tmp / "kanca.png", kanca_y)
        if a.kredi and tam:
            yuk = rozet_png(a.kredi, tmp / "kredi.png", boyut=24, seffaf=0.6)
            bindir(tmp / "kredi.png", T_KAMERA_YUKSEKLIK - yuk // 2)
        if a.logo and tam:
            yuk = logo_png(a.logo, tmp / "logo.png")
            bindir(tmp / "logo.png", T_KAMERA_YUKSEKLIK - yuk // 2)
        elif a.kredi:
            yazi_png(a.kredi, 40, FONT_NORMAL, tmp / "kredi.png", renk=(235, 235, 235))
            bindir(tmp / "kredi.png", kredi_y)
        if a.sohbet:
            # Her yeni mesajda kutunun o anki hali (son N mesaj) ayrı PNG; bir sonraki mesaja kadar görünür.
            # Kutu oyun panelinin sol altına, altyazının hemen üstüne oturur.
            mesajlar = json.loads(Path(a.sohbet).read_text())
            oyun_alt = (altyazi_y - K_ALTYAZI_BOSLUK) if a.kamera else (VIDEO_Y + VIDEO_YUKSEKLIK)
            for i, m in enumerate(mesajlar):
                durum = mesajlar[max(0, i - a.sohbet_satir + 1):i + 1]
                png = tmp / f"s{i:03d}.png"
                yuk = sohbet_png(durum, png)
                son = mesajlar[i + 1]["t"] if i + 1 < len(mesajlar) else m["t"] + 2.5
                girdiler.extend(["-i", str(png)])
                filtre.append(f"[{son_etiket}][{n}:v]overlay=24:{oyun_alt - yuk - 16}"
                              f":enable='between(t,{m['t']:.2f},{son:.2f})'[v{n}]")
                son_etiket = f"v{n}"
                n += 1
        for i, o in enumerate(obekler):
            png = tmp / f"a{i:04d}.png"
            if tam:
                yazi_png(tr_buyuk(o["metin"]), 112, FONT_KALIN, png)
            else:
                yazi_png(tr_buyuk(o["metin"]), 84, FONT_KALIN, png,
                         renk=(255, 230, 40) if i % 2 else (255, 255, 255))
            bindir(png, altyazi_y, o["bas"], o["son"])

        if a.muzik:
            # Müzik döngüde çalar, konuşma olunca otomatik kısılır (sidechain), klip sonunda söner.
            girdiler.extend(["-stream_loop", "-1", "-i", str(a.muzik)])
            filtre += [
                "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,asplit[konusma][tetik]",
                f"[{n}:a]volume={a.muzik_seviye},aresample=48000[m0]",
                "[m0][tetik]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[m1]",
                "[konusma][m1]amix=inputs=2:duration=first:normalize=0[ses]",
            ]
        else:
            filtre.append("[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[ses]")
        # Son büyütme: YouTube 1440p ve üstü yüklemelere daha iyi kodlama (VP9) veriyor; yerleşim 1080 tabanlı kalır.
        if a.cozunurluk != G:
            filtre.append(f"[{son_etiket}]scale={a.cozunurluk}:{a.cozunurluk * Y // G}:flags=lanczos[vson]")
            son_etiket = "vson"
        betik = tmp / "filtre.txt"
        betik.write_text(";\n".join(filtre))
        # Kesme girdi tarafında yapılır; PNG girdileri tek karedir ve son kareleri tutulur.
        # Kare hızı kaynağınki (Kick 60 fps) korunur.
        komut = ["ffmpeg", "-v", "error", "-y", *kes, *girdiler,
                 "-/filter_complex", str(betik), "-map", f"[{son_etiket}]", "-map", "[ses]",
                 "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(cikti)]
        subprocess.run(komut, check=True)

    meta = cikti.with_suffix(".json")
    ek = json.loads(a.ek) if a.ek else {}
    meta.write_text(json.dumps({"girdi": str(girdi), "kanca": a.kanca, "kredi": a.kredi,
                                "muzik": Path(a.muzik).stem if a.muzik else "",
                                "metin": " ".join(k["metin"] for k in kelimeler),
                                **ek, "obekler": obekler, "kelimeler": kelimeler},
                               ensure_ascii=False, indent=1))
    print(f"→ {cikti}\n  transkript: {' '.join(k['metin'] for k in kelimeler)[:300]}")


if __name__ == "__main__":
    main()
