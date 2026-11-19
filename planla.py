#!/usr/bin/env python3
"""Onaylı klipleri yayın saatlerine dağıtıp yukle.py ile gizli + planlı yükler.

Saatler config.yaml'daki yayin_saatleri (docs/strateji.md: günde 1-2, arada ≥ 8 sa).
Yüklenmiş klipleri ve dolu saatleri data/yuklendi/kayit.jsonl'dan bilir; ilk boş saatten devam eder.

Kullanım:
  .venv/bin/python planla.py data/hazir/tam/01-x.mp4 data/hazir/tam/03-y.mp4 ...   # kuru: takvimi gösterir
  .venv/bin/python planla.py ... --gercek                                          # yükler
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

KOK = Path(__file__).resolve().parent
KAYIT = KOK / "data" / "yuklendi" / "kayit.jsonl"
TZ = ZoneInfo("Europe/Istanbul")


def saatler():
    m = re.search(r"^yayin_saatleri:\s*\[(.*?)\]", (KOK / "config.yaml").read_text(), re.M)
    return sorted(s.strip().strip('"') for s in m.group(1).split(","))


def dolu_ve_yuklu():
    dolu, yuklu = set(), set()
    if KAYIT.exists():
        for s in KAYIT.read_text().splitlines():
            k = json.loads(s)
            yuklu.add(k["dosya"])
            if k.get("publishAt"):
                dolu.add(datetime.fromisoformat(k["publishAt"]).astimezone(TZ).strftime("%Y-%m-%d %H:%M"))
    return dolu, yuklu


def bos_saatler(dolu, en_erken):
    gun = en_erken.date()
    while True:
        for s in saatler():
            aday = datetime.strptime(f"{gun} {s}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
            anahtar = aday.strftime("%Y-%m-%d %H:%M")
            if aday > en_erken and anahtar not in dolu:
                yield anahtar
        gun += timedelta(days=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("videolar", nargs="+")
    ap.add_argument("--gercek", action="store_true")
    a = ap.parse_args()
    dolu, yuklu = dolu_ve_yuklu()
    # En erken: 1 saat sonrası (YouTube işleme süresi payı) ve son dolu saatten sonrası.
    en_erken = datetime.now(TZ) + timedelta(hours=1)
    if dolu:
        en_erken = max(en_erken, max(datetime.strptime(d, "%Y-%m-%d %H:%M").replace(tzinfo=TZ) for d in dolu))
    slot = bos_saatler(dolu, en_erken)
    for v in a.videolar:
        yol = str(Path(v).resolve())
        if yol in yuklu:
            print(f"= {Path(v).name} zaten yüklü, atlandı")
            continue
        zaman = next(slot)
        baslik = json.loads(Path(v).with_suffix(".json").read_text())["basliklar"][0]
        print(f"{zaman}  {Path(v).name}  «{baslik}»", flush=True)
        if a.gercek:
            r = subprocess.run([sys.executable, str(KOK / "yukle.py"), v, "--zaman", zaman, "--gercek"],
                               capture_output=True, text=True)
            print("   " + (r.stdout.strip().splitlines() or ["?"])[-1] if r.returncode == 0 else "   ✘ " + r.stderr[-400:],
                  flush=True)
            if r.returncode:
                break
    if not a.gercek:
        print("\nKuru çalışma. Yüklemek için --gercek ekle.")


if __name__ == "__main__":
    main()
