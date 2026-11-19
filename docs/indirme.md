# İndirme yöntemleri (denenmiş)

Buradaki her yöntem 19 Kasım 2026'da bu bilgisayarda (Mac, Apple M4) gerçek yayınlarla denendi.
"Denenmedi" yazanlar dışında hepsi çalıştı. Platformlar sık değişir: bir yöntem bozulursa önce
`yt-dlp`'yi güncelle, sonra bu dosyadaki yedek yola bak.

Temel ilke: **önce sinyal (birkaç MB), sonra yalnız seçilen anların videosu.**
Altı saatlik bir yayını bütün indirmek onlarca GB tutar; diskte ~28 GB boş yer var.

## Özet

| İş | Twitch | Kick | YouTube |
|---|---|---|---|
| Yayın listesi | `yt-dlp --flat-playlist` | Kick'in site API'si | `yt-dlp --flat-playlist` |
| Sohbet | TwitchDownloaderCLI | Kick'in site API'si | `yt-dlp` (yalnız canlı yayın kayıtları) |
| Ek sinyal | Klip izlenmeleri (`yt-dlp`) | yok | Isı verisi (`yt-dlp`) |
| Video parçası | `yt-dlp --download-sections` | `ffmpeg` ile m3u8'den | `yt-dlp --download-sections` |
| API anahtarı | gerekmez | gerekmez | gerekmez |

Gerekli araçlar: `yt-dlp` (sürüm 2026.10.26 denendi), `ffmpeg` (kurulu), `TwitchDownloaderCLI` 1.56.5,
ve YouTube için bir JavaScript çalıştırıcısı (bilgisayarda `node` var, `--js-runtimes node` ile kullanılır).

## Twitch

**Yayın listesi** (kanalın geçmiş yayınları; kimlik, başlık, süre döner):
```bash
yt-dlp --flat-playlist --print "%(id)s | %(title)s | %(duration)s" "https://www.twitch.tv/KANAL/videos?filter=archives"
```

**Sohbet** — TwitchDownloaderCLI (github.com/lay295/TwitchDownloader, CLI sürümü):
```bash
./TwitchDownloaderCLI chatdownload --id VOD_NUMARASI -o chat.json
# yalnız bir aralık: -b 0:10:00 -e 0:15:00
```
Çıktı: `comments[]` → `content_offset_seconds`, `commenter.name`, `message.body`.
Deneme: 5 dakikalık aralık, 67 mesaj, birkaç saniye.

Çalışmayan yollar (deneme sonucu, kullanma):
- `yt-dlp --list-subs`: "has no subtitles" diyor, Twitch sohbetini artık vermiyor.
- `chat-downloader` (Python paketi): Python 3.15'te hata verip çıkıyor, bakımı da durmuş.

**İzleyici klipleri** (izleyicilerin zaten kestiği anlar, izlenme sayısıyla):
```bash
yt-dlp --flat-playlist --print "%(id)s | %(title)s | %(view_count)s | %(url)s" "https://www.twitch.tv/KANAL/clips?range=7d"
```
Eksik: bu liste klibin yayının kaçıncı saniyesinden kesildiğini vermiyor. Onun için Twitch'in resmî
API'si gerekir (`/helix/clips` → `video_id`, `vod_offset`; dev.twitch.tv'den ücretsiz Client ID + Secret).
**Denenmedi**, Faz 2'de doğrulanacak.

**Video parçası:**
```bash
yt-dlp --download-sections "*600-615" -S "res:1080" -o "parca.%(ext)s" "https://www.twitch.tv/videos/VOD_NUMARASI"
```
Deneme: 15 saniye → 14 MB. Yedek yol: `TwitchDownloaderCLI videodownload --id … -b … -e …`.

Notlar: yayın kayıtları kanal türüne göre 7-60 gün sonra silinir, sinyali erken topla.
Abonelere özel kayıtlar oturum anahtarı ister; bunlarla uğraşma.

## Kick

Kick'in resmî API'si (api.kick.com, OAuth + webhook) yalnız **canlı** olayları verir
(sohbet mesajı, yayın başladı/bitti gibi; ayrıntı docs.kick.com, bu oturumda okunmadı) ve yayıncının kendi yetkilendirmesini ister;
geçmiş sohbeti vermez. Geçmiş için sitenin kendi kullandığı, belgelenmemiş uç noktalar kullanılır.
Tarayıcı benzeri `User-Agent` başlığı şart. Hepsi anahtarsız çalıştı.

**Yayın listesi:**
```
GET https://kick.com/api/v2/channels/KANAL_ADI/videos
```
Her kayıt: `session_title`, `start_time`, `duration` (ms), `views`, `channel_id`, `video.uuid`,
`source` (m3u8 adresi), `is_live`. Süresi 0 olan kayıt hâlâ canlıdır, atla.

**Yayın ayrıntısı:** `GET https://kick.com/api/v1/video/UUID` → `livestream.channel_id`, `start_time`, `duration`.

**Sohbet** (iki yol da çalıştı):
```
GET https://kick.com/api/v2/channels/CHANNEL_ID/messages?start_time=2026-11-18T06:37:54.000Z
GET https://kick.com/api/v2/channels/CHANNEL_ID/messages?cursor=MIKROSANIYE
```
- `start_time`: verilen andan sonraki birkaç saniyenin mesajları (denemede 5 mesaj). İleri doğru yürümek için.
- `cursor`: verilen andan **geriye** 25 mesaj, yanıttaki `data.cursor` bir önceki sayfa. Yayın sonundan başa yürü.
- Yayındaki saniye = mesajın `created_at` değeri − yayının `start_time` değeri.
- Bütün sohbet yüzlerce istek demek: istekler arasında kısa bekleme koy, sonucu `data/sohbet/kick-UUID.json` olarak sakla.

**Video parçası** — `yt-dlp`'nin Kick desteği şu an **bozuk** ("NOT_FOUND" veriyor). Bunun yerine
listedeki `source` adresinden doğrudan kes:
```bash
ffmpeg -ss 600 -i "M3U8_ADRESI" -t 40 -c copy parca.mp4
```
Deneme: 1920×1080, sesli, sorunsuz.

Hazır bir Kick sohbet indirme aracı bulunamadı: `kick-dl` yalnız video indiriyor, diğerleri tarayıcı
eklentisi ya da ücretli site. Bu yüzden kendi küçük indiricimizi yazıyoruz (yukarıdaki iki uç nokta yeter).

## YouTube

**"En çok tekrar oynatılan" ısı verisi** — videoda gördüğün grafiğin kendisi, indirme yapmadan gelir:
```bash
yt-dlp --skip-download --print "%(heatmap)j" "VIDEO_ADRESI"
```
Çıktı: 100 nokta, her biri `{"start_time", "end_time", "value"}`; `value` 0-1 arası.
Deneme: 213 saniyelik videoda 100 nokta, her biri 2,14 saniye.
- İlk nokta neredeyse hep 1,0'dır (herkes baştan başlar); ilk %5'i yok say.
- Az izlenen ya da çok yeni videolarda veri olmaz (`heatmap` boş gelir) → ses zirvesine düş.
  19 Kasım gecesi denendi: çıkışın ertesi günü 1,4 M izlenmeli GTA 6 videolarında bile veri yoktu;
  YouTube grafiği birkaç gün sonra açıyor. Yaş sınırlı videolar çerez ister (`--cookies-from-browser chrome`).
- Betik: `python3 sinyal_youtube.py ADRES` → `data/sohbet/youtube-<id>-anlar.json` → `parca_indir.py` (yt-dlp ile keser).
- Çözünürlük videonun %1'i: 3 saatlik videoda bir nokta ≈ 108 saniye. Uzun videoda ısı verisi
  bölgeyi bulur, tam anı o bölgedeki ses zirvesi ya da sohbet belirler.

**Sohbet tekrarı** (yalnız sohbeti açık canlı yayın kayıtlarında):
```bash
yt-dlp --js-runtimes node --skip-download --write-subs --sub-langs live_chat -o yayin "VIDEO_ADRESI"
```
→ `yayin.live_chat.json` (satır başına bir JSON; alanlar `docs/an-bulma.md`'de). **Bu oturumda denenmedi.**

**Video parçası:**
```bash
yt-dlp --js-runtimes node --download-sections "*40-50" -S "res:1080,ext:mp4:m4a" -o "parca.%(ext)s" "VIDEO_ADRESI"
```
Deneme: 10 saniye → 1,8 MB. `--js-runtimes node` olmadan bazı kaliteler eksik kalır.

## Bulunan diğer araçlar

| Araç | Ne | Karar |
|---|---|---|
| TwitchDownloader | Twitch sohbet + video | Kullanılıyor |
| yt-dlp | Liste, parça, ısı verisi | Kullanılıyor |
| Kick resmî API | Canlı olaylar, webhook | Geçmiş için işe yaramaz; ileride canlı izleme için düşünülebilir |
| Streams Charts sohbet indirici | Web sitesi, üç platform | Elle kullanım, otomasyona uymaz |
| Apify "twitch-chat" vb. | Bulut kazıyıcılar | Ücretli, gereksiz |
| OpenShorts (rehber 2) | Konuşmaya göre an seçen hazır araç | Kullanılmıyor: sinyalimiz izleyici tepkisi; ayrıca Docker ve disk yükü |
