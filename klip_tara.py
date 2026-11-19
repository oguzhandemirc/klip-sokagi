#!/usr/bin/env python3
"""Hangi yayıncının klipleri YouTube'da başkaları tarafından bolca paylaşılıyor? (telif tolerans göstergesi)

Her yayıncı için YouTube'da "<ad> shorts" ve "<ad> klip" arar; yayıncının kendisine ait olmayan
kanalları sayar, izlenmeleri toplar. Çok sayıda üçüncü taraf kanalı yüksek izlenmeyle ayaktaysa
yayıncı pratikte klip kanallarına telif atmıyor demektir (kanıt değil, gösterge).

Kullanım: .venv/bin/python klip_tara.py [--adet 40] → data/klip_tara.json + tablo
"""
import argparse
import json
import subprocess
from collections import defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parent
# ad: (arama adı, kendi kanal adında geçen parçalar)
YAYINCILAR = {
    "Eray": ("eray can özkenar", ["eray"]),
    "Jahrein": ("jahrein", ["jahrein"]),
    "Zeon": ("zeon yayın", ["zeon"]),
    "Rammus53": ("rammus53", ["rammus"]),
    "RRaenee": ("rraenee", ["rraenee"]),
    "Atadogann": ("atadogann", ["atadogan"]),
    "Elwind": ("elwind", ["elwind"]),
    "Elraenn": ("elraenn", ["elraenn", "tatlıpatates"]),
    "wtcN": ("wtcn", ["wtcn"]),
    "Tolunay Ören": ("tolunay ören", ["tolunay"]),
    "Pqueen": ("pqueen", ["pqueen"]),
    "Kendine Müzisyen": ("kendine müzisyen", ["kendine müzisyen"]),
    "Mithrain": ("mithrain", ["mithrain"]),
    "Hype": ("hype yayıncı", ["hype"]),
    "Burak Oyunda": ("burak oyunda", ["burak oyunda"]),
}


def ara(sorgu, adet):
    cikti = subprocess.run(["yt-dlp", "--flat-playlist", "-J", f"ytsearch{adet}:{sorgu}"],
                           capture_output=True, text=True, timeout=180)
    if cikti.returncode:
        return []
    return json.loads(cikti.stdout).get("entries", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adet", type=int, default=40)
    a = ap.parse_args()
    sonuc = {}
    for ad, (sorgu, kendi) in YAYINCILAR.items():
        kanallar = defaultdict(lambda: {"video": 0, "izlenme": 0})
        gorulen = set()
        for ek in ("shorts", "klip"):
            for e in ara(f"{sorgu} {ek}", a.adet):
                if e.get("id") in gorulen:
                    continue
                gorulen.add(e.get("id"))
                kanal = e.get("channel") or e.get("uploader") or "?"
                baslik = (e.get("title") or "").lower()
                if not any(p.split()[0] in baslik for p in kendi):  # yayıncıyla ilgisiz sonuç
                    continue
                if any(p in kanal.lower() for p in kendi):
                    kanal = "[KENDİSİ] " + kanal
                kanallar[kanal]["video"] += 1
                kanallar[kanal]["izlenme"] += e.get("view_count") or 0
        ucuncu = {k: v for k, v in kanallar.items() if not k.startswith("[KENDİSİ]")}
        sonuc[ad] = {
            "ucuncu_kanal": len(ucuncu),
            "ucuncu_video": sum(v["video"] for v in ucuncu.values()),
            "ucuncu_izlenme": sum(v["izlenme"] for v in ucuncu.values()),
            "kendi_izlenme": sum(v["izlenme"] for k, v in kanallar.items() if k.startswith("[KENDİSİ]")),
            "en_buyukler": sorted(ucuncu.items(), key=lambda x: -x[1]["izlenme"])[:5],
        }
        r = sonuc[ad]
        print(f"{ad:18} 3.taraf kanal {r['ucuncu_kanal']:3}  video {r['ucuncu_video']:3}  "
              f"izlenme {r['ucuncu_izlenme']:>13,}  | kendi {r['kendi_izlenme']:>12,}", flush=True)
    (KOK / "data" / "klip_tara.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
