# Riskler ve para kazanma kuralları

Hukuki tavsiye değildir. Politikalar değişir; büyük adımlardan önce kaynağından doğrula.
2026 tarihli maddeler iki kaynak rehberden alındı, bu oturumda ayrıca doğrulanmadı.

## Kendi kaydımız olmadığı için durum

Bütün içerik başkalarına ait. Bu, iki rehberin de "en riskli" dediği yol. Kanalın yaşaması
üç şeye bağlı: **izin**, **dönüşüm** ve **spoiler/şiddet kurallarına uymak**.

## 1. Yayıncı izni

- Yayın, yayıncının telif içeriğidir. İzinsiz yükleme telif şikâyetine, 3 aktif ihtar kanalın kapanmasına yol açar.
- İzin yolları:
  - Doğrudan anlaşma ("resmî klipçi", gelir paylaşımı). Şablon: `izin-mesaji.md`.
  - Yayıncının açık "klip serbest" kuralı (ekran görüntüsünü sakla).
  - Ücretli klip kampanyaları (yayıncı izlenme başına öder; izin zaten vardır).
- Kayıt: `yasakli.csv` (telif atanlar, işlenmez). 19 Kas 2026: kullanıcı tek tek izin almama kararı verdi; risk kullanıcıda.
- YouTube videoları için de aynısı geçerli: video sahibinin izni gerekir.

## 2. YouTube "yeniden kullanılmış içerik"

- Para kazanamaz: başkasının içeriğini anlatı eklemeden kesip yüklemek, az anlatılı klip derlemeleri.
- Para kazanabilir: yorum, açıklama, hikâyeleştirme, anlamlı kurgu eklenmiş içerik.
- Değerlendirme kanal bazında: ham klip kanalı bütün kanalın gelirini kaybettirir.
- 1 Ekim 2026 Shorts güncellemesi (rehber 1): anlamlı değişiklik olmadan yeniden yüklenen içeriğin erişimi düşürülüyor.
- Sonuç: `docs/an-bulma.md` 6. bölümdeki dönüşüm katmanı zorunlu. Altyazı ve kanca tek başına
  yetmeyebilir; **Türkçe yorum/anlatım katmanı** (yazılı bağlam ya da seslendirme) eklemek en güçlü önlem.
  Aynı kalıpta seri üretim de "özgün olmayan içerik" sayılabilir.

## 3. Rockstar / Take-Two

- Ticari olmayan paylaşıma genelde itiraz etmiyor; para kazanılan kullanım bu hoşgörünün dışında, kaldırma hakkı saklı.
- Kesin kaldırılanlar: hikâye sonu ve büyük spoiler, ara sahneler (tek başına ya da derleme),
  oyun içi TV/gösterilerin tek başına yüklenmesi, hile/mod tanıtımı, sızıntı.
- Oyun radyosundaki lisanslı şarkılar Content ID'ye takılabilir.

## 4. Şiddet kuralı (Eylül 2026, rehber 1)

Grafik oyun şiddeti videonun ilk 7 saniyesindeyse reklam geliri yok. Kanca şiddet değil, merak/tepki olsun.

## 5. YPP eşikleri ve gelir

- 1.000 abone + 90 günde 10 milyon geçerli Shorts izlenmesi (ya da 12 ayda 4.000 saat uzun video).
- Shorts geliri düşüktür. Asıl gelir çoğu zaman klip kampanyaları ve yayıncı anlaşmalarıdır.

## 6. YouTube Data API

- Günlük kota sınırlı; yükleme pahalı bir işlemdir (günde birkaç yükleme). Güncel rakamı dokümandan doğrula.
- Denetlenmemiş API projesiyle yüklenen video gizli kalır → denetim başvurusunu erken yap.

## 7. Teknik kırılganlık

- Kick uç noktaları belgelenmemiş; haber vermeden değişebilir ya da engellenebilir.
- `yt-dlp` sık bozulur ve güncellenir (Kick desteği şu an bozuk).
- Çok hızlı istek atmak IP engeline yol açar; isteklere bekleme koy.

## Kaynaklar

- Rockstar video politikası: https://support.rockstargames.com/articles/7bNaeoMFTV0iUDGhStTXvz/policy-on-posting-copyrighted-material
- YouTube para kazanma politikaları: https://support.google.com/youtube/answer/1311392
- Rehber 1 kaynağı: https://kisiselgelisimpartisi.com/rehber/sohbet-klip/oku
- Rehber 2 kaynağı: https://ecakan.com/tr/rehberler/uzun-videonu-ucretsiz-kisa-kliplere-cevir
- TwitchDownloader: https://github.com/lay295/TwitchDownloader
