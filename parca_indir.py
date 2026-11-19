#!/usr/bin/env python3
"""Parça indirme: seçilen anları kaynaktan keser, ham ve dikey (9:16) klip üretir.

Kullanım:
    python3 parca_indir.py data/sohbet/kick-<uuid>-anlar.json [--adet 3]

Çıktı: data/parca/<uuid8>-<sıra>.mp4 (yatay ham kesit)
       data/hazir/<uuid8>-<sıra>-dikey.mp4 (1080x1920, bulanık arka planlı)
"""
import argparse
import json
import subprocess
from pathlib import Path

KOK = Path(__file__).resolve().parent

# Üstte ve altta bulanık arka plan, ortada videonun tamamı: hiçbir şey kırpılmaz.
DIKEY_FILTRE = (
    "[0:v]split[a][b];"
    "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5[arka];"
    "[b]scale=1080:-2[on];"
    "[arka][on]overlay=(W-w)/2:(H-h)/2[v]"
)


def calistir(komut):
    sonuc = subprocess.run(komut, capture_output=True, text=True)
    if sonuc.returncode != 0:
        raise RuntimeError(sonuc.stderr[-500:])


def main():
    ap = argparse.ArgumentParser(description="Seçilen anları keser ve dikey klibe çevirir.")
    ap.add_argument("anlar")
    ap.add_argument("--adet", type=int, default=3)
    ap.add_argument("--pay", type=int, default=10, help="başa ve sona eklenecek saniye")
    ap.add_argument("--dikey", action="store_true", help="basit bulanık arka planlı dikey sürüm de üret")
    a = ap.parse_args()

    veri = json.loads(Path(a.anlar).read_text())
    yayin = veri["yayin"]
    on_ek = yayin["uuid"][:8]
    (KOK / "data" / "parca").mkdir(parents=True, exist_ok=True)
    (KOK / "data" / "hazir").mkdir(parents=True, exist_ok=True)

    for an in veri["anlar"][:a.adet]:
        bas = max(0, an["baslangic"] - a.pay)
        sure = an["sure"] + 2 * a.pay
        ham = KOK / "data" / "parca" / f"{on_ek}-{an['sira']:02d}.mp4"
        dikey = KOK / "data" / "hazir" / f"{on_ek}-{an['sira']:02d}-dikey.mp4"
        print(f"{an['sira']:2d}: {bas} sn'den {sure} sn kesiliyor…", flush=True)
        if not ham.exists() and yayin.get("platform") in ("youtube", "twitch"):
            calistir(["yt-dlp", "--no-warnings", "-q", "--download-sections", f"*{bas}-{bas + sure}",
                      "-S", "res:1080,ext:mp4:m4a", "--remux-video", "mp4", "-o", str(ham), yayin["kaynak"]])
        elif not ham.exists():
            calistir(["ffmpeg", "-v", "error", "-y", "-ss", str(bas), "-i", yayin["kaynak"],
                      "-t", str(sure), "-c", "copy", str(ham)])
        print(f"    → {ham}")
        if not a.dikey:
            continue
        calistir(["ffmpeg", "-v", "error", "-y", "-i", str(ham), "-filter_complex", DIKEY_FILTRE,
                  "-map", "[v]", "-map", "0:a?", "-r", "30", "-c:v", "libx264", "-preset", "veryfast",
                  "-crf", "20", "-c:a", "aac", "-b:a", "160k", str(dikey)])
        print(f"    → {dikey}")


if __name__ == "__main__":
    main()
