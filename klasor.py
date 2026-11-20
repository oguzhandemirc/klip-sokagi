"""Çıktı klasörü düzeni: data/hazir/<yayinci>/<yayin-tarihi>/<shorts|video>/

Yayıncı ve tarih, ham parçanın adındaki yayın önekinden (data/parca/<uuid8>-NN.mp4) sohbet an dosyasıyla
(data/sohbet/kick-<uuid>-anlar.json) bulunur. Tarih yayının İstanbul saatiyle başladığı gündür.
"""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

KOK = Path(__file__).resolve().parent
HAZIR = KOK / "data" / "hazir"
TZ = ZoneInfo("Europe/Istanbul")


def yayin_bilgisi(girdi):
    """Ham parça yolundan (kanal, 'YYYY-AA-GG') döndürür; bulunamazsa None."""
    on_ek = Path(str(girdi).replace("\\", "/")).stem.split("-")[0]
    for anlar in (KOK / "data" / "sohbet").glob(f"kick-{on_ek}*-anlar.json"):
        yayin = json.loads(anlar.read_text(encoding="utf-8"))["yayin"]
        gun = datetime.fromisoformat(yayin["baslangic"]).astimezone(TZ).strftime("%Y-%m-%d")
        return yayin["kanal"], gun
    return None


def cikti_klasoru(girdi, tur):
    """tur: 'shorts' | 'video'. Yayın bulunamazsa ValueError (klasör elle --klasor ile verilmeli)."""
    bilgi = yayin_bilgisi(girdi)
    if not bilgi:
        raise ValueError(f"{girdi} için yayın bulunamadı (data/sohbet/kick-<önek>*-anlar.json yok); --klasor ver.")
    kanal, gun = bilgi
    return HAZIR / kanal / gun / tur
