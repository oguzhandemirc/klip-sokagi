#!/usr/bin/env python3
"""An seçimi: sohbet hızı örneklerinden en çok tepki alan anları bulur.

Kullanım:
    python3 an_sec.py data/sohbet/kick-<uuid>.json [--adet 10]

Çıktı: aynı klasörde <ad>-anlar.json ve terminalde özet tablo.
"""
import argparse
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path

EMOTE = re.compile(r"\[emote:\d+:([^\]]+)\]")
BAGLANTI = re.compile(r"https?://|www\.", re.I)
KELIME = re.compile(r"[a-zçğıöşüâîû]+", re.I)
TEKRAR = re.compile(r"(.)\1{2,}")
DOLGU = set("""ve bir bu şu da de ki mi mı mu mü ne abi aga kanka lan ya yaa için ile ama çok
daha gibi var yok ben sen biz siz bana sana beni seni değil diye olan oldu olur şey hadi
the and you that this bro""".split())


def saat(sn):
    s, kalan = divmod(int(sn), 3600)
    d, sn = divmod(kalan, 60)
    return f"{s}:{d:02d}:{sn:02d}"


def sade(kelime):
    """Küçük harfe çevirir, uzatılmış harfleri kısaltır (haaaydi → haydi)."""
    kelime = kelime.replace("I", "ı").replace("İ", "i").lower()
    return TEKRAR.sub(r"\1", kelime)


def gecerli(mesaj):
    _, gonderen, metin, tip = mesaj
    if tip not in ("message", "reply"):
        return False
    return not (gonderen.lower().endswith("bot") or BAGLANTI.search(metin) or metin.startswith("!"))


BOS = set("sa as s a selam selamlar slm merhaba hi hello o".split())
SPONSOR = re.compile(r"yemeksepeti|sponsor|abonelik|abone ol|hediye|bağış|!", re.I)


def bos_mesaj(metin):
    """Tepki taşımayan mesaj: selam seli, sponsor/abonelik sohbeti."""
    duz = sade(EMOTE.sub(" ", metin)).strip(" .!?")
    return duz in BOS or bool(SPONSOR.search(metin))


def hiz(ornek, adim):
    """Örneğin sohbet hızı (mesaj/sn). Sohbet yavaşsa son ADIM saniyedeki mesajlar sayılır."""
    if not ornek["kapsam"]:
        return 0.0
    if ornek["kapsam"] >= adim:
        return sum(1 for m in ornek["mesajlar"] if m[0] > ornek["t"] - adim and gecerli(m)) / adim
    oran = sum(1 for m in ornek["mesajlar"] if gecerli(m)) / max(1, len(ornek["mesajlar"]))
    return ornek["hiz"] * oran


def ozet(mesajlar):
    """Mesajların en sık kelimelerini ve emote'larını döndürür (kişi başına bir kez sayılır)."""
    kelimeler, emoteler, gorulen = Counter(), Counter(), set()
    for _, gonderen, metin, _ in mesajlar:
        for e in set(EMOTE.findall(metin)):
            if (gonderen, e) not in gorulen:
                gorulen.add((gonderen, e))
                emoteler[e] += 1
        for k in {sade(k) for k in KELIME.findall(EMOTE.sub(" ", metin))}:
            if len(k) >= 3 and k not in DOLGU and (gonderen, k) not in gorulen:
                gorulen.add((gonderen, k))
                kelimeler[k] += 1
    return [k for k, _ in kelimeler.most_common(5)], [e for e, _ in emoteler.most_common(2)]


def main():
    ap = argparse.ArgumentParser(description="Sohbet patlamalarından an seçer.")
    ap.add_argument("sohbet")
    ap.add_argument("--adet", type=int, default=10)
    ap.add_argument("--esik-sd", type=float, default=2.0)
    ap.add_argument("--once", type=int, default=25, help="klip patlamadan kaç saniye önce başlar")
    ap.add_argument("--sure", type=int, default=40)
    ap.add_argument("--aralik", type=int, default=90, help="iki an arasındaki en az saniye")
    ap.add_argument("--atla-son", type=int, default=900, help="yayının sonunda atlanacak saniye")
    a = ap.parse_args()

    yol = Path(a.sohbet)
    veri = json.loads(yol.read_text())
    yayin, adim, ornekler = veri["yayin"], veri["adim"], veri["ornekler"]

    # Son dakikalar veda/teşekkür sohbetidir; at.
    ornekler = [o for o in ornekler if o["t"] <= yayin["sure"] - a.atla_son]
    n = len(ornekler)
    # Hız: 25 mesaj aynı saniyeye sığınca sayı uçar; logaritma ile bastırılır.
    # İçeriksiz sel ("sa", tek harf) ve sponsor sohbeti puanı düşürür.
    ham = []
    for o in ornekler:
        mesajlar = [m for m in o["mesajlar"] if gecerli(m)]
        bos = sum(1 for m in mesajlar if bos_mesaj(m[2])) / max(1, len(mesajlar))
        ham.append(math.log1p(hiz(o, adim)) * (1 - 0.8 * bos))
    # Tek örnek gürültülüdür: 3 örneğin (≈30 sn) ortancası alınır, tek örneklik sıçrama elenir.
    duz = [statistics.median(ham[max(0, i - 1):min(n, i + 2)]) for i in range(n)]
    # Yerel taban: ±10 dakikanın ortancası. Puan = tabandan ne kadar yukarıda.
    pencere = max(1, 600 // adim)
    taban = [statistics.median(duz[max(0, i - pencere):i + pencere + 1]) for i in range(n)]
    fark = [d - t for d, t in zip(duz, taban)]
    ort, sd = statistics.mean(fark), statistics.pstdev(fark)
    esik = ort + a.esik_sd * sd

    adaylar = sorted((i for i in range(n) if fark[i] > esik), key=lambda i: -fark[i])
    duz = fark
    secilen = []
    for i in adaylar:
        if all(abs(ornekler[i]["t"] - ornekler[j]["t"]) >= a.aralik for j in secilen):
            secilen.append(i)
        if len(secilen) == a.adet:
            break

    anlar = []
    for sira, i in enumerate(secilen, 1):
        # Patlamanın başı: tepeden geriye doğru hızın eşiğin altına indiği ilk örnek.
        j = i
        while j > 0 and duz[j - 1] > esik and i - j < 6:
            j -= 1
        patlama = ornekler[j]["t"] - adim
        yakin = [m for o in ornekler[max(0, j - 1):i + 2] for m in o["mesajlar"] if gecerli(m)]
        kelimeler, emoteler = ozet(yakin)
        anlar.append({
            "sira": sira,
            "patlama": patlama,
            "baslangic": max(0, patlama - a.once),
            "sure": a.sure,
            "hiz": round(duz[i], 2),
            "puan": round((duz[i] - ort) / sd, 1) if sd else 0,
            "kelimeler": kelimeler,
            "emoteler": emoteler,
        })

    print(f"{yayin['kanal']} | {yayin['baslik']} | {saat(yayin['sure'])}")
    print(f"örnek: {n} ({adim} sn arayla) | puan: ort {ort:.2f}, sd {sd:.2f}, eşik {esik:.2f} | "
          f"eşiği aşan örnek: {len(adaylar)}")
    print()
    print(" #  patlama  klip başı   fark  puan  sohbette öne çıkan")
    for an in anlar:
        print(f"{an['sira']:2d}  {saat(an['patlama']):>7}  {saat(an['baslangic']):>8}  {an["hiz"]:5.2f}  "
              f"{an['puan']:4.1f}  {', '.join(an['kelimeler'])}  [{' '.join(an['emoteler'])}]")

    hedef = yol.with_name(yol.stem + "-anlar.json")
    hedef.write_text(json.dumps({"yayin": yayin, "anlar": anlar}, ensure_ascii=False, indent=1))
    print(f"\n→ {hedef}")


if __name__ == "__main__":
    main()
