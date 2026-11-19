# Mac → ThinkPad devri (20 Kas 2026 ~00:20)

Mac'teki bütün döngüler DURDURULDU. Bundan sonra yükleme YALNIZ ThinkPad'de yapılır.

## Bu paketle gelenler (ikinci paket)
- Güncel `data/yuklendi/kayit.jsonl` (yüklü: 03 nUaymseybY0 herkese açık; 02 O6oZ-oF1HZk 20 Kas 13:00 planlı).
- `data/sohbet/`: wtcN 19 Kas tamam (`kick-e0ca1c15…`), Eray 18 Kas yarım (`kick-1e73b293….ara.jsonl`, sinyal.py kaldığı yerden sürer).
- `data/parca/e0ca1c15-*.mp4/.json/.jpg`: wtcN'nin 15 adayı (kesildi + transkript + kare özeti). İncelenmedi.
- Yeni/güncel rehberler: `CLAUDE.md` (baştan yazıldı), `docs/formuller.md` (yeni, tüm formüller), `ONBOARDING.md`, `ekip_paketle.sh`.
  Senin Windows düzeltmelerin (yukle.py, planla.py, aciklama_guncelle.py, klip_tara.py, sinyal_youtube.py,
  parca_indir.py, requirements.txt, docs/kurulum-thinkpad.md, DURUM.md) bu pakette YOK; seninkiler geçerli, üzerine yazma.

## Devralınacak işler (sırayla başlat)
1. **Bekleyen yüklemeler (YouTube günlük sınırı, `uploadLimitExceeded`):** kanal "Gelişmiş özellikler" video doğrulaması
   onay bekliyor (~24 sa). 30 dk'da bir dene:
   - `yeniden_dene.py` ile (data/hazir/hd içinden): 05-lucia-kacamadi, 01-berberde-isler-karisti, 04-arka-koltuk-soforleri,
     06-lavabo-tamirinde-misafir, 07-bagaj-kapagi-detayi, 08-gta6-surus-yorumu (bu sırayla; planla.py ilk boş saate koyar;
     saatler 13:00/18:00/21:00).
   - Uzun video: `yukle.py data/hazir/uzun/rraenee-gta6-gun1-en-iyi-anlar.mp4 --zaman "2026-11-20 20:00" --gercek`
     (20:00 geçtiyse bir sonraki Pzt/Çar/Cum 20:00). Küçük resim otomatik eklenir.
2. **RRaenee canlı ("GTA 6 - 2.YAYIN"):** `bitince.py rraenee` — yayın bitince gece.py ile işler. İçinde Elraenn de var
   (`ek_yayinci.py Elraenn ...`).
3. **Gece hattının kalanı:** `gece.py eray:0 tolunayoren:1 wtcn:2` (wtcn:0 bitti).
4. **wtcN adaylarını incele** (data/parca/e0ca1c15-*.json + .jpg): iyi olanlardan HD Short planı yaz, `uretim.py` ile üret;
   yatay 2-5 dk video için `uzun.py`. Onay sayfası (`onay.py`) → kullanıcıya bildir. Kullanıcı onayı olmadan yükleme yok.
5. **dongu.py** (yazılacak, kullanıcı istedi): biten yayınları bul → hepsinden Short + yatay stokla → kota elverdikçe
   gizli+planlı yükle → yüklenenin ham parçasını ve çıktısını sil. Kilit dosyası. Görev Zamanlayıcı 10 dk.
   Onay modeli kullanıcıya soruldu: "yayından ≥ 12 sa önce gizli yükle, beğenmediğini sil (veto)". Cevap gelene kadar onaylı mod.

## Disk
C: 23 GB boş. Ham parçaları (data/parca) ve yüklenmiş çıktıları yüklemeden sonra sil.
