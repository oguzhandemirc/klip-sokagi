# Formüller ve tuzaklar (19-20 Kasım 2026'da deneyerek bulundu)

Bu dosya "neden böyle" sorusunun cevabıdır. Bir ayarı değiştirmeden önce burayı oku.

## 1. An bulma (sohbet patlaması)
- Kick sohbetini bütün indirmek 429 (istek sınırı) yer. `sinyal.py` her 10 sn'de bir **son 25 mesajı** örnekler;
  3 iş parçacığı, 429'da herkes bekler, `.ara.jsonl` ile kaldığı yerden devam eder. 8 saatlik yayın ≈ 1-2 saat.
- Puan (`an_sec.py`): `log(mesaj/sn) × (1 − 0,8 × boş mesaj oranı)` → 3 örnek ortancası → ±10 dk yerel ortancadan fark.
  Eşik ort + k·sd. **k=2 çok sıkı** (8 sa'te 32 an); **k=1,5 + aralık 45 sn** önerilen (≈60 aday).
- Son 15 dk (veda) ve ilk 10 dk atlanır. "sa", tek harf, sponsor/komut (!kazan, !wraith) mesajları boş sayılır.
- **Sohbet puanı ≠ klip değeri.** Geri sayım, "buradayız chat" selamları, sponsor anları yüksek puan alır → içerik elemesi şart
  (transkript + 6 karelik özet `.jpg` ile Claude inceler).
- Yayın başı/sonu, ara sahne, cinsel içerik (striptiz kulübü) → ele.

## 2. Short formatı ("tam" yerleşim, kanıtlanmış örnek: yayincitepkileri kanalı)
- 1440x2560, 60 fps, x264 crf 18 preset slow (YouTube 1440p+ yüklemeye VP9 verir → daha net). Yerleşim 1080 tabanlı hesaplanır, en son büyütülür.
- Üstte kamera şeridi 1080x540 (kameranın üstündeki boş duvar kırpılır), altta oyun 1080x1380.
- **Oyun ekranın GERÇEK ortasından kırpılır** (kameranın solundaki alanın ortası değil — karakter kayıyordu, mini harita giriyordu).
- Kamera 2x büyür → lanczos + `unsharp=5:5:0.7`.
- Birleşim çizgisinde küçük (24 pt) %60 saydam Kick rozeti; sağda Klip Sokağı logosu.
- Kanca yazısı ≤ 5-6 kelime, oyunun üstünde; altyazı **tek kelime**, 112 pt beyaz.
- **Sohbet katmanı YOK** (başarılı Shorts'ta yok). Sesli yorum şimdilik yok (kullanıcı kararı).
- 20-35 sn; tepkiden 0,5-1 sn önce başla; intro/logo animasyonu yok.
- Yayıncı kamera koordinatı yayıncıya özel: `config.yaml → yayincilar.<ad>.kamera` (RRaenee: 1390:144:530:296).
  Yeni yayıncıda bir kareden ölç ve config'e yaz.

## 3. Yatay video (2-5 dk)
- `uzun.py`: 1920x1080 60 fps; her bölümün ilk 3,5 sn'sinde sol alt şerit (#n + başlık + bağlam); sağ üst rozet + logo.
- Küçük resim: oyun karesi + **büyütülmüş yayıncı kamerası** (yüzler görünmeli) + 2-3 kelime sarı yazı. En iyi tepki karesini seç.
- Açıklamada bölüm damgaları (0:00 ile başlar, ≥ 3 bölüm, her biri ≥ 10 sn → YouTube bölüm yapar).
- Ham derleme "reused content" riskidir → her anın bağlam satırı ve anlatı sırası şart.

## 4. Başlık / açıklama
- Başlık ≤ ~40-45 karakter (mobilde kesilir), yayıncı adı + cesur ama **klipte olan** vaat, 1-2 kelime BÜYÜK, 1 emoji.
  Örnek: "RRaenee tekneyi ağaçlara GÖMDÜ 😂 GTA 6". Klipte olmayanı vaat etme (kaldırma/ceza).
- Yarı yarıya yayıncı önde / GTA 6 önde dene (Shorts'ta A/B yok; etiketle ve karşılaştır).
- Açıklama: 1-2 cümle bağlam; **kaynak satırı ve harici bağlantı YOK** (kredi videodaki rozet); müzik varsa CC BY satırı;
  sonda ≤ 6 hashtag (`#GTA6 #<Yayıncı> #<EkYayıncı> ... #KlipSokağı`), `#Shorts` gereksiz.
- Yayında başka yayıncı varsa (ör. RRaenee + Elraenn) adı açıklama/etiket/hashtag'e (yatayda başlığa da): meta `ek_yayincilar`.

## 5. Yayıncı seçimi ve telif
- Tek tek izin alınmıyor (kullanıcı kararı). Gösterge: YouTube'da o yayıncının kliplerini paylaşan çok sayıda 3. taraf kanal
  ayakta mı (`klip_tara.py`). Bol: RRaenee, Eray, Elraenn, Tolunay Ören, Kendine Müzisyen, wtcN, Elwind.
- Telif atan → `yasakli.csv` (Mithrain). Telif/kaldırma gelirse hemen ekle.
- Müzik: yalnız Kevin MacLeod CC BY (`muzik/`), açıklamada kredi zorunlu. Trend müzik dosyası ekleme (Content ID).

## 6. YouTube API tuzakları
- Kurulum: Google Cloud projesi → YouTube Data API v3 → Google Auth Platform (External) → Desktop istemci → `client_secret.json`.
  "Publish app" için Branding'de alan adı/gizlilik sayfası istenir → **Testing'te kal**, kendini test kullanıcısı ekle;
  token 7 günde düşer → `yukle.py --giris` (30 sn).
- Kapsamlar: youtube.upload + youtube.readonly + youtube.force-ssl (silme, sabit yorum).
- Planlı yayın: `privacyStatus=private` + `publishAt`. Doğrulanmamış projede bile çalıştı (19 Kas 2026).
- **Kanalın günlük yükleme sınırı** (API kotasından ayrı): yeni kanalda ~10/gün; **silinen videolar da sayılır**.
  Telefon doğrulaması + "Gelişmiş özellikler" (video selfie / kimlik, ~24 sa) sınırı yükseltir. Hata: `uploadLimitExceeded` → `yeniden_dene.py`.
- Özel küçük resim (thumbnails.set) telefon doğrulaması ister.
- Yüklenmiş videonun dosyası değiştirilemez: sil + yeniden yükle (`sil_yt.py` yalnız gizli+planlıları siler).
- `hasPaidProductPlacement=false` açıkça yazılmalı (16 Kas 2026'dan beri).

## 7. Strateji (ayrıntı `docs/strateji.md`)
- Shorts günde 3 (13:00/18:00/21:00), en güçlüsü önce; yayından 24-72 sa içinde. Yatay haftada 3, 20:00.
- 1 Eki 2026'dan beri Shorts akışı yeniden yükleme kanallarını kısıyor → 30. günde izlenme düşükse sesli yorum katmanını konuş.
- Gelir tahmini yapma; ölç.

## 8. Ortam
- Python 3.12 `.venv` (3.15'te av derlenmiyor). ffmpeg ≥ 7 (`-/filter_complex`). Mac'teki ffmpeg'de libass/drawtext yok →
  bütün yazılar Pillow PNG + overlay.
- Yazı tipi: Arial Black/Bold; `duzenle.font_bul` Mac, Windows ve `fonts/` klasörüne bakar.
- faster-whisper medium CPU (small hatalı). Whisper İngilizce küfrü "S**T" diye kendisi sansürler; Türkçe küfür sansürsüz (yapılacak).
- Döküm klipten 15 sn ÖNCE başlar, kelimeler sonra klibe kaydırılır; `no_speech_threshold=None` (VAD sessizliği zaten atar).
  Neden: < 30 sn klip tek pencere; oyun içi İngilizce diyalogla açılınca pencere "konuşma yok" sayılıp düşüyor ya da
  sıcaklık örneklemesine geçip yalnız İngilizceyi yazıyordu (wtcN 03, 20 Kas 2026).
- Kamera solda (wtcN) → oyun ortadan kırpılır, kameradan sağa kaydırılır; sağda (RRaenee) → sola. Koordinatlar config.yaml.
- ThinkPad (i5-10310U) hızı: 30-40 sn HD Short ≈ 4,5 dk; 2:46 yatay video ≈ 20 dk.
- Komut kuralı: betik dosyasını heredoc ile yazma, Write aracıyla yaz, tek satırla çalıştır (izin sorusu çıkıp gece iş durmasın).
