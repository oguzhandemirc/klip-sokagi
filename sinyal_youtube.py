#!/usr/bin/env python3
"""YouTube sinyali: "en çok tekrar oynatılan" ısı verisinden an seçer (video indirmeden).

Kullanım:
    python3 sinyal_youtube.py "https://www.youtube.com/watch?v=..." [--adet 5] [--sure 40]

Çıktı: data/sohbet/youtube-<id>-anlar.json (parca_indir.py ile aynı biçim).
Not: az izlenen ya da çok yeni videolarda ısı verisi olmaz.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
# venv etkin değilse (Windows'ta .venv\Scripts PATH'te olmaz) yt-dlp'yi çalışan Python'un yanında ara.
YTDLP = shutil.which("yt-dlp") or str(Path(sys.executable).with_name("yt-dlp"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("adres")
    ap.add_argument("--adet", type=int, default=5)
    ap.add_argument("--sure", type=int, default=40)
    ap.add_argument("--esik", type=float, default=0.5, help="tepe, ilk yüzde 5 dışındaki en yüksek değerin en az bu oranı olmalı")
    a = ap.parse_args()

    cikti = subprocess.run([YTDLP, "--js-runtimes", "node", "--no-warnings", "--skip-download",
                            "--dump-single-json", a.adres], capture_output=True, text=True, check=True).stdout
    bilgi = json.loads(cikti)
    isi = bilgi.get("heatmap") or []
    if not isi:
        raise SystemExit("Bu videoda ısı verisi yok (az izlenmiş ya da yeni).")
    sure = bilgi["duration"]
    deger = [n["value"] for n in isi]
    atla = max(1, len(isi) // 20)      # ilk %5: herkes baştan başlar
    tepeler = [i for i in range(atla, len(isi))
               if deger[i] >= a.esik * max(deger[atla:]) and deger[i] >= deger[i - 1] and (i + 1 == len(isi) or deger[i] >= deger[i + 1])]
    tepeler.sort(key=lambda i: -deger[i])

    anlar, secilen = [], []
    for i in tepeler:
        orta = (isi[i]["start_time"] + isi[i]["end_time"]) / 2
        if any(abs(orta - s) < a.sure for s in secilen):
            continue
        secilen.append(orta)
        baslangic = max(0, int(orta - a.sure / 2))
        anlar.append({"sira": len(anlar) + 1, "patlama": int(orta), "baslangic": baslangic, "sure": a.sure,
                      "puan": round(deger[i] * 3, 2), "isi": round(deger[i], 3),
                      "nokta_genisligi": round(isi[i]["end_time"] - isi[i]["start_time"], 1)})
        if len(anlar) == a.adet:
            break

    yayin = {"platform": "youtube", "kanal": bilgi.get("channel") or bilgi.get("uploader"),
             "uuid": bilgi["id"], "baslik": bilgi.get("title", ""), "sure": sure,
             "izlenme": bilgi.get("view_count"), "kaynak": bilgi.get("webpage_url", a.adres)}
    hedef = KOK / "data" / "sohbet" / f"youtube-{bilgi['id']}-anlar.json"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(json.dumps({"yayin": yayin, "anlar": anlar}, ensure_ascii=False, indent=1))
    print(f"{yayin['kanal']} | {yayin['baslik']} | {sure} sn | nokta: {len(isi)} × {sure / len(isi):.1f} sn")
    for an in anlar:
        print(f"  {an['sira']}. {an['patlama'] // 60}:{an['patlama'] % 60:02d}  ısı {an['isi']}")
    print(f"→ {hedef}")


if __name__ == "__main__":
    main()
