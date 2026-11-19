#!/usr/bin/env python3
"""YouTube'a yükleme: onaylanmış Short'u planlı (ileri tarihli) olarak yükler.

Güvenlik kilitleri (CLAUDE.md kural 5-6):
  - Varsayılan KURU ÇALIŞMA: yalnız ne yükleneceğini yazar. Gerçek yükleme için --gercek gerekir.
  - Klibin kredisindeki kanal yasakli.csv'deyse (telif atan yayıncı) yükleme reddedilir.
  - Yüklenen her video data/yuklendi/kayit.jsonl'a yazılır; aynı dosya ikinci kez yüklenmez.

Bir kerelik kurulum (kullanıcı yapar, ayrıntı docs/yukleme.md):
  Google Cloud'da proje → YouTube Data API v3 → OAuth istemcisi (Masaüstü) →
  JSON'u proje köküne client_secret.json olarak koy. İlk gerçek çalıştırmada tarayıcı açılır, izin verilir,
  token.json oluşur (ikisi de git dışı).

Kullanım (.venv içindeki Python ile):
    .venv/bin/python yukle.py data/hazir/02-tek-atista-basket.mp4 --baslik 1 --zaman "2026-11-21 19:00"
    .venv/bin/python yukle.py ... --gercek          # gerçekten yükler
    .venv/bin/python yukle.py ... --gizlilik private # zaman vermeden gizli yükler (deneme için)
"""
import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

KOK = Path(__file__).resolve().parent
SIR = KOK / "client_secret.json"
TOKEN = KOK / "token.json"
KAYIT = KOK / "data" / "yuklendi" / "kayit.jsonl"
KAPSAM = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly",   # kanal adını doğrulamak için
          "https://www.googleapis.com/auth/youtube.force-ssl"]  # silme, sabit yorum
SAAT_DILIMI = ZoneInfo("Europe/Istanbul")


def yasakli_mi(kredi):
    """Kredi (ör. kick.com/rraenee) yasakli.csv'deki (telif attığı bilinen) bir kaynak_url ile eşleşiyor mu?"""
    yol = KOK / "yasakli.csv"
    if not yol.exists():
        return None
    anahtar = kredi.lower().removeprefix("https://").removeprefix("www.").strip("/")
    with yol.open() as f:
        for satir in csv.DictReader(f):
            url = (satir.get("kaynak_url") or "").lower().removeprefix("https://").removeprefix("www.").strip("/")
            if url and url == anahtar:
                return satir
    return None


def aciklama_duzenle(metin, ekler=()):
    """Kullanıcı kararı (19 Kas 2026): açıklamada kaynak satırı ve harici bağlantı YOK (kredi videodaki rozette).
    Yalnız müzik kredisi kalır (CC BY lisans şartı), bağlantısız tek satır. Sonda en çok 6 hashtag.
    ekler: klipte görünen diğer yayıncılar (meta "ek_yayincilar"); adları açıklamaya ve hashtag'e girer."""
    satirlar = metin.strip().split("\n")
    kredi = next((s for s in satirlar if s.startswith("Kaynak:")), "")
    etiket = [k for s in satirlar for k in s.split() if s.lstrip().startswith("#") and k.startswith("#")]
    yayinci = re.search(r"Kaynak:\s*([^—–-]+?)\s*[—–-]", kredi)
    muzik = re.search(r'Müzik:\s*"([^"]+)"\s*Kevin MacLeod', metin)
    govde = [s for s in satirlar if s != kredi and not s.lstrip().startswith("#") and not s.startswith("Müzik:")
             and "http" not in s and not s.startswith("Licensed under")]
    if muzik:
        govde += ["", f'Müzik: "{muzik.group(1)}" – Kevin MacLeod (incompetech), CC BY 4.0']
    etiket = [k for k in etiket if k.lower() != "#shorts"]
    if yayinci:
        etiket.insert(1, "#" + re.sub(r"\W", "", yayinci.group(1)))
    for i, e in enumerate(ekler):
        etiket.insert(2 + i, "#" + re.sub(r"\W", "", e))
    etiket.append("#KlipSokağı")
    etiket = list(dict.fromkeys(etiket))
    etiket = etiket[:5] + ["#KlipSokağı"] if len(etiket) > 6 else etiket
    if ekler:
        ana = yayinci.group(1) if yayinci else ""
        govde.insert(0, "👥 " + ", ".join([x for x in [ana, *ekler] if x]) + " birlikte")
        govde.insert(1, "")
    metin = "\n".join(govde).strip()
    metin = re.sub(r"\n{3,}", "\n\n", metin)
    return metin + "\n\n" + " ".join(etiket), [k.lstrip("#") for k in etiket]


def proje_yolu(yol):
    """Kayıttaki yolu makineden bağımsız biçime çevirir (data/hazir/hd/x.mp4).
    kayit.jsonl'de Mac (/Users/...) ve Windows (C:\\shorts\\...) mutlak yolları karışık bulunur."""
    s = str(yol).replace("\\", "/")
    if s.startswith("data/"):
        return s
    i = s.find("/data/")
    return s[i + 1:] if i >= 0 else s


def daha_once_yuklendi(video):
    if not KAYIT.exists():
        return None
    for satir in KAYIT.read_text().splitlines():
        k = json.loads(satir)
        if proje_yolu(k.get("dosya", "")) == proje_yolu(video):
            return k
    return None


def servis():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    kimlik = Credentials.from_authorized_user_file(str(TOKEN), KAPSAM) if TOKEN.exists() else None
    if not kimlik or not kimlik.valid:
        if kimlik and kimlik.expired and kimlik.refresh_token:
            kimlik.refresh(Request())
        else:
            if not SIR.exists():
                raise SystemExit("client_secret.json yok. Kurulum adımları: docs/yukleme.md")
            kimlik = InstalledAppFlow.from_client_secrets_file(str(SIR), KAPSAM).run_local_server(port=0)
        TOKEN.write_text(kimlik.to_json())
    return build("youtube", "v3", credentials=kimlik)


def giris():
    """Yalnız oturum aç (token.json) ve bağlanılan kanalı göster; hiçbir şey yüklemez."""
    yt = servis()
    for k in yt.channels().list(part="snippet", mine=True).execute().get("items", []):
        print(f"✔ Bağlı kanal: {k['snippet']['title']}  ({k['snippet'].get('customUrl', '')})  id={k['id']}")


def main():
    import sys
    if sys.argv[1:] == ["--giris"]:
        return giris()
    ap = argparse.ArgumentParser(description="Onaylı Short'u YouTube'a yükler (varsayılan: kuru çalışma).")
    ap.add_argument("video", help="data/hazir/<ad>.mp4 (yanında <ad>.json olmalı); yalnız giriş için: --giris")
    ap.add_argument("--baslik", type=int, default=1, help="meta'daki kaçıncı başlık önerisi (1-3)")
    ap.add_argument("--baslik-metin", help="öneriler yerine bu başlığı kullan")
    ap.add_argument("--zaman", help='yayın zamanı, İstanbul saati: "2026-11-21 19:00"')
    ap.add_argument("--gizlilik", choices=["private", "unlisted", "public"], default="private",
                    help="zaman verilirse private zorunludur (YouTube planlı yayını böyle yapar)")
    ap.add_argument("--gercek", action="store_true", help="gerçekten yükle")
    a = ap.parse_args()

    video = Path(a.video).resolve()
    meta = json.loads(video.with_suffix(".json").read_text())
    uzun = "aciklama_son" in meta          # uzun.py çıktısı (yatay video)
    baslik = a.baslik_metin or (meta["baslik"] if uzun else meta["basliklar"][a.baslik - 1])
    if len(baslik) > 100:
        raise SystemExit(f"Başlık 100 karakteri aşıyor ({len(baslik)}).")
    if uzun:
        aciklama = meta["aciklama_son"]
        etiketler = [k.lstrip("#") for k in aciklama.split() if k.startswith("#")]
        if meta.get("ek_yayincilar"):
            aciklama = "👥 " + ", ".join([meta.get("ana_yayinci", ""), *meta["ek_yayincilar"]]).strip(", ") \
                + " birlikte\n\n" + aciklama
    else:
        aciklama, etiketler = aciklama_duzenle(meta.get("aciklama", ""), meta.get("ek_yayincilar", []))

    govde = {
        "snippet": {
            "title": baslik,
            "description": aciklama,
            "tags": etiketler,
            "categoryId": "20",            # Gaming
            "defaultLanguage": "tr",
            "defaultAudioLanguage": "tr",
        },
        "status": {
            "privacyStatus": a.gizlilik,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": False,
        },
        # 16 Kasım 2026'dan beri varsayılan false değil; açıkça yazılmalı.
        "paidProductPlacementDetails": {"hasPaidProductPlacement": False},
    }
    if a.zaman:
        zaman = datetime.strptime(a.zaman, "%Y-%m-%d %H:%M").replace(tzinfo=SAAT_DILIMI)
        if zaman <= datetime.now(SAAT_DILIMI):
            raise SystemExit("Yayın zamanı geçmişte.")
        govde["status"]["privacyStatus"] = "private"
        govde["status"]["publishAt"] = zaman.isoformat()

    print(json.dumps(govde, ensure_ascii=False, indent=1))

    # Kilitler: yasak listesi (telif atan yayıncılar) ve tekrar yükleme.
    yasak = yasakli_mi(meta.get("kredi", ""))
    if yasak:
        raise SystemExit(f"✘ '{meta.get('kredi')}' yasakli.csv'de ({yasak.get('neden', '')}): yükleme yapılmaz.")
    onceki = daha_once_yuklendi(video)
    if onceki:
        raise SystemExit(f"✘ Bu dosya zaten yüklendi: https://youtu.be/{onceki['id']}")
    if not a.gercek:
        print("\nKuru çalışma: hiçbir şey yüklenmedi. Gerçek yükleme için --gercek ekle.")
        return

    from googleapiclient.http import MediaFileUpload
    yt = servis()
    istek = yt.videos().insert(part="snippet,status,paidProductPlacementDetails", body=govde,
                               media_body=MediaFileUpload(str(video), mimetype="video/mp4",
                                                          chunksize=8 * 1024 * 1024, resumable=True))
    yanit = None
    while yanit is None:
        durum, yanit = istek.next_chunk()
        if durum:
            print(f"  %{int(durum.progress() * 100)}", flush=True)
    KAYIT.parent.mkdir(parents=True, exist_ok=True)
    with KAYIT.open("a") as f:
        f.write(json.dumps({"dosya": str(video), "id": yanit["id"], "baslik": baslik,
                            "publishAt": govde["status"].get("publishAt"),
                            "zaman": datetime.now(SAAT_DILIMI).isoformat()}, ensure_ascii=False) + "\n")
    print(f"✔ Yüklendi: https://youtu.be/{yanit['id']}  ({govde['status']['privacyStatus']}"
          f"{', yayın ' + a.zaman if a.zaman else ''})")
    kapak = video.with_suffix(".jpg")
    if kapak.exists():  # özel küçük resim (telefon doğrulaması gerekir)
        try:
            yt.thumbnails().set(videoId=yanit["id"], media_body=MediaFileUpload(str(kapak), mimetype="image/jpeg")).execute()
            print("✔ Küçük resim eklendi")
        except Exception as h:
            print(f"✘ Küçük resim eklenemedi: {str(h)[:200]}")


if __name__ == "__main__":
    main()
