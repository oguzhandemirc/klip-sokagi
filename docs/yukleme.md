# YouTube'a yükleme

Araştırma: 19 Kasım 2026 (resmî developers.google.com sayfaları). Betik: `yukle.py`.

## Yol: resmî YouTube Data API v3 (`videos.insert`)
- Ücretsiz. Yükleme kendi kotasında: **günde 100 yükleme** (1 Haziran 2026'dan beri ayrı kova).
- **2 Kasım 2026:** doğrulanmamış (audit edilmemiş) API projelerinin yüklemeleri artık "private"a kilitlenmiyor.
  Kişisel kullanımda audit gerekmeyebilir → **ilk gerçek yüklemeyle doğrula** (private + publishAt).
- Planlı yayın: `privacyStatus=private` + `publishAt` (betik `--zaman "YYYY-AA-GG SS:DD"`, İstanbul saati).
- Shorts sayılma: dikey/kare ve ≤ 3 dk. Bizim 1080x1920, 20-40 sn uygun.
- 16 Kasım 2026'dan beri `hasPaidProductPlacement` açıkça `false` yazılmalı (betik yazıyor).
- API'de "reused content" bayrağı yok; özgünlük yükleme sonrası değerlendiriliyor (bkz. `docs/baslik.md`).

Elenenler: `youtube-upload` (bakımsız), Upload-Post (ücretsiz plan ayda 10), tarayıcı otomasyonu (kırılgan, hesap riski).

## Bir kerelik kurulum (kullanıcı yapar, ~15 dk)
1. Yüklenecek YouTube kanalını hazırla (yayıncıyı taklit etmeyen ad ve görsel).
2. https://console.cloud.google.com → üstteki proje seçici → **New Project**.
3. **APIs & Services → Library** → "YouTube Data API v3" → **Enable**.
4. https://console.cloud.google.com/auth/overview → **Get started**: App name, destek e-postası, Audience **External**, iletişim e-postası.
5. https://console.cloud.google.com/auth/audience → **Test users → Add users** → kanalın bağlı olduğu Gmail.
6. https://console.cloud.google.com/auth/clients/create → **Desktop app** → Create → **Download JSON** →
   proje köküne `client_secret.json` adıyla koy (git dışı, kimseyle paylaşma).
7. Uygulama **Testing**'te kalır ("Publish app" alan adı + gizlilik sayfası ister; gerek yok). Bedeli: giriş 7 günde düşer →
   `python yukle.py --giris` (30 sn). Girişte kanal listesinden doğru kanalı seç; "doğrulanmamış uygulama" uyarısında
   **Advanced → Go to … (unsafe)**; 3 izin kutusunun hepsini işaretle.
8. YouTube Studio → Ayarlar → Kanal → Özellik uygunluğu: telefon doğrulaması (özel küçük resim) + Gelişmiş özellikler
   (günlük yükleme sınırı yükselir; yeni kanalda ~10/gün, silinenler dahil).

## Kullanım
```bash
.venv/bin/python yukle.py data/hazir/02-tek-atista-basket.mp4 --baslik 1 --zaman "2026-11-21 19:00"          # kuru çalışma
.venv/bin/python yukle.py data/hazir/02-tek-atista-basket.mp4 --baslik 1 --zaman "2026-11-21 19:00" --gercek # yükler
```
Kilitler: kredideki kanal `yasakli.csv`'deyse reddeder; aynı dosyayı iki kez yüklemez
(`data/yuklendi/kayit.jsonl`); `--gercek` olmadan hiçbir şey göndermez.
