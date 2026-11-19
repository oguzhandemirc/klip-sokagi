# Klip Sokağı'na hoş geldin 👋

Bu klasör, Türk yayıncıların GTA 6 yayınlarından **en çok tepki alan anları otomatik bulup** YouTube Shorts'a
ve kısa yatay videolara çeviren bir hattır. Formülleri bulmak 2 gün sürdü; hepsi burada yazılı, sen uğraşmayacaksın.

## İlk 15 dakika
1. Bilgisayarında Python 3.12, ffmpeg (sürüm 7 ya da üstü) ve Claude Code kurulu olsun.
2. Bu klasörde terminal aç ve `claude` yaz. İlk mesajın:
   > "CLAUDE.md, docs/formuller.md ve DURUM.md'yi oku. Ortamımı kur (.venv, requirements.txt, yt-dlp) ve kontrol et."
3. Claude kurulumu yapar, yazı tipini ve ffmpeg'i kontrol eder.

**Windows'taysan** Claude'a ayrıca söyle: "PYTHONUTF8=1 kullanıcı ortam değişkenini ayarla (Türkçe JSON'lar bozulmasın),
tzdata kurulu olsun, yt-dlp'yi .venv içinden çağır." Yazı tipi otomatik `C:\Windows\Fonts\ariblk.ttf` bulunur.

## Neye ihtiyacın var (hesaplar)
| Ne | Gerekli mi | Nereden |
|---|---|---|
| Claude Code hesabı | Evet | claude.ai |
| YouTube kanalı + Google Cloud OAuth (`client_secret.json`) | Yalnız yükleme yapacaksan | `docs/yukleme.md` (≈ 15 dk) |
| Kick / Twitch hesabı | Hayır | Kick'in açık API'si kullanılıyor |
| Anthropic API anahtarı (`.env`) | Hayır (ileride tam otomasyon için) | `.env.example` |

## YouTube'a bağlanmak (gerekirse)
Giriş dosyaları (`client_secret.json`, `token.json`) bu klasörde **yok**; güvenlik için paylaşılmaz.
- Aynı kanala yükleyeceksen: dosyaları Oğuzhan'dan güvenli yoldan (Tailscale/elden) al. **Aynı anda iki bilgisayardan yükleme yapma.**
- Kendi kanalını açacaksan: `docs/yukleme.md`'deki Google Cloud adımlarını izle (≈ 15 dk), sonra `python yukle.py --giris`.

## Günlük iş (Claude'a söyleyeceklerin)
| İstek | Claude ne yapar |
|---|---|
| "RRaenee canlı mı, son yayınlar ne?" | `canli.py` / `sinyal.py` |
| "wtcN'nin son GTA yayınından aday çıkar" | `gece.py wtcn:0` → sohbet tarar, 15 an keser, döker |
| "Adaylara bak, en iyi 8'ini Short yap" | dökümleri ve kareleri inceler, `plan.json` yazar, `uretim.py` ile HD üretir |
| "Bu yayından 3 dakikalık video yap" | `uzun.py` ile yatay video + küçük resim |
| "Onaylılarımı takvime koy" | `planla.py` ile gizli + planlı yükler |
| "Yüklenenlerin durumu?" | `durum_yt.py` |

## Bilmen gereken 5 şey
1. **Format sabit ve kanıtlı:** üstte kamera, altta ortadan kırpılmış oyun, tek kelimelik büyük altyazı, kısa kanca, küçük rozet + logo. Değiştirmeden önce `docs/formuller.md`.
2. **Başlık:** yayıncı adı + cesur ama klipte gerçekten olan bir vaat, ≤ 45 karakter. Yayında başka yayıncı varsa onun adı da.
3. **Telif:** `yasakli.csv`deki yayıncılar işlenmez. Telif gelirse oraya ekle.
4. **YouTube sınırı:** yeni kanal günde ~10 video yükleyebilir (silinenler dahil). Çok silip yükleme yapma.
5. **Hiçbir şey onaysız yayınlanmaz;** her şey önce gizli + planlı yüklenir.

Sorun olursa: önce `DURUM.md`'nin üstüne bak (son ne yapıldı), sonra Claude'a sor.
