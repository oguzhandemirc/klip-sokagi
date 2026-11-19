#!/usr/bin/env python3
"""Başlık önerilerini plan.json'da ve data/hazir/*.json meta dosyalarında günceller.

Kullanım: python3 baslik_guncelle.py basliklar_cesur.json
Video yeniden üretilmez; yalnız başlıklar değişir. Ardından onay.py sayfayı yeniler.
"""
import json
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent


def main():
    yeni = json.loads(Path(sys.argv[1]).read_text())
    plan_yolu = KOK / "plan.json"
    plan = json.loads(plan_yolu.read_text())
    for p in plan:
        if p["ad"] in yeni:
            p["basliklar"] = yeni[p["ad"]]
    plan_yolu.write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    for ad, basliklar in yeni.items():
        meta = KOK / "data" / "hazir" / f"{ad}.json"
        if meta.exists():
            m = json.loads(meta.read_text())
            m["basliklar"] = basliklar
            meta.write_text(json.dumps(m, ensure_ascii=False, indent=1))
            print(f"✔ {ad}: {basliklar[0]}")
        else:
            print(f"✘ {ad}: meta yok")
    subprocess.run([sys.executable, str(KOK / "onay.py")], check=True)


if __name__ == "__main__":
    main()
