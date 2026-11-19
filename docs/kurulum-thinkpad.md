# ThinkPad (yerel Windows, WSL yok) kurulumu

Hedef: bütün hat (sinyal → an → kesim → düzenleme → yükleme → temizlik) 7/24 açık ThinkPad'de çalışır.
Mac'teki döngüler devirden sonra kapatılır (iki makine aynı anda yüklerse tekrar yükleme olur).
20 Kas 2026'da kuruldu ve doğrulandı (aşağıdaki 3. bölüm). Makine: i5-10310U (4 çekirdek), 16 GB RAM.

## 1. Windows ayarları (yapıldı)
```powershell
winget install --id Python.Python.3.12 -e      # .venv 3.12 olmalı (3.14/3.15'te av derlenmiyor)
winget install --id Gyan.FFmpeg -e             # ffmpeg ≥ 7 gerekir (-/filter_complex); kurulu: 9.0.2
winget install --id Git.Git -e
powercfg /change standby-timeout-ac 0          # prizdeyken uyku yok
powercfg /change hibernate-timeout-ac 0
powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0   # kapak kapanınca hiçbir şey yapma
powercfg /setactive SCHEME_CURRENT
[Environment]::SetEnvironmentVariable("PYTHONUTF8","1","User")    # bkz. Windows farkları
```
Elle: Windows Update "Etkin saatler"i ayarla; Tailscale açık kalsın (paket Taildrop ile `İndirilenler`e gelir).

## 2. Proje (yapıldı)
```powershell
mkdir C:\shorts
tar -xzf $env:USERPROFILE\Downloads\shorts-paket.tar.gz -C C:\shorts --exclude "._*"   # ._* = macOS çöp dosyaları
cd C:\shorts
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt yt-dlp
```
Betikler hep `.venv\Scripts\python betik.py ...` ile çalıştırılır (dokümanlardaki `.venv/bin/python` = Mac).

## 3. Doğrulama (yükleme yapmadan) — 20 Kas 2026 sonuçları
- `.venv\Scripts\python yukle.py --giris` → ✔ Bağlı kanal: Klip Sokağı (@klipsokagi). token.json Mac'ten geldi, tarayıcı açılmadı.
- `.venv\Scripts\python canli.py rraenee` → Kick API çalışıyor (403/Cloudflare yok), ~1,8 sn.
- Kick m3u8'den 12 sn parça kesme (`ffmpeg -ss ... -c copy`): ~11 sn.
- `duzenle.py data\parca\X.mp4 --kamera 1390:144:530:296 --yerlesim tam --sure 10 --cikti ...` →
  10 sn klip **72 sn**'de (medium model, CPU int8) → 1440x2560 60 fps. Mac M4'ten belirgin yavaş:
  30-45 sn'lik klip ≈ 4-6 dk. Whisper medium modeli ilk kullanımda indirilir (~1,5 GB, HF önbelleği).
- `yukle.py data\hazir\hd\03-...mp4` (kuru) → "zaten yüklendi" (Mac kayıtları tanınıyor); `planla.py` kuru da 02/03'ü atlıyor.

## Windows farkları (kodda düzeltildi)
- **Tekrar yükleme kilidi:** `kayit.jsonl` mutlak yol tutuyordu (`/Users/demirci/...`); Windows yolu eşleşmeyince
  02/03 yeniden yüklenebilirdi. `yukle.proje_yolu()` yolları `data/...` biçiminde karşılaştırır;
  `yukle.py`, `planla.py`, `aciklama_guncelle.py` bunu kullanır.
- **Saat dilimi:** Windows'ta sistem tz veritabanı yok → `tzdata` requirements.txt'e eklendi.
- **yt-dlp:** venv etkin değilken `.venv\Scripts` PATH'te değil → `klip_tara.py`, `sinyal_youtube.py`,
  `parca_indir.py` yt-dlp'yi çalışan Python'un yanında arar (`YTDLP`).
- **Kodlama:** betiklerin çoğu `read_text()`/`open()`'ı kodlamasız çağırır; Windows'ta varsayılan cp1254 Türkçe
  UTF-8 JSON'ları bozar. Çözüm kullanıcı ortam değişkeni `PYTHONUTF8=1` (zamanlanmış görevlerde de olmalı).
- Fontlar `C:/Windows/Fonts` (ariblk.ttf, arialbd.ttf) zaten destekleniyordu; `curl` Windows'ta yerleşik.
- Disk: C:'de ~23 GB boş. Kural 9 geçerli: parça indir, yüklenen ham parçaları sil.

## 4. Devir (Mac → ThinkPad) — 20 Kas 2026 00:30 TAMAMLANDI
Mac döngüleri durduruldu; ikinci paket (`DEVIR.md`, kayit.jsonl, sohbet, wtcN adayları) `C:\shorts`'a açıldı.
Yükleme artık YALNIZ ThinkPad'de.

## 5. Görev Zamanlayıcı (`\KlipSokagi\`)
Hepsi `gorev.cmd <log> <betik> ...` ile çalışır (PYTHONUTF8, log `data\log\<log>.log`).
| Görev | Ne | Tetik |
|---|---|---|
| `dongu` | `dongu.py`: onaylı kuyruğu yükle, temizle, yeni yayın keşfi → gece.py | 10 dk'da bir, süresiz |
| `gece` | `gece.py eray:0 tolunayoren:1 wtcn:2` (devirden kalan) | bir kez |
| `bitince_rraenee` | `bitince.py rraenee` (yayın bitince gece.py rraenee:0) | bir kez |

```powershell
Get-ScheduledTask -TaskPath "\KlipSokagi\"                       # durum
Get-Content C:\shorts\data\log\dongu.log -Tail 20                 # log
.venv\Scripts\python dongu.py --kuru                              # ne yapacağını göster, dokunma
```
- **Dikkat:** `Stop-ScheduledTask` yalnız cmd'yi durdurur, Python alt süreçleri yetim kalır →
  `Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? CommandLine -match 'betik.py'` ile bulup `Stop-Process`.
- Görevler "kullanıcı oturum açıkken" çalışır. Windows Update yeniden başlatırsa otomatik oturum açma yoksa döngü
  oturum açılana kadar durur; `dongu` tetiği yeniden başlatmadan sonra kendiliğinden sürer, tek seferlik görevler sürmez
  (dongu keşfi onların işini zaten üstlenir).
- `dongu.py` kilidi `data\dongu.kilit` (2 sa'ten eskiyse yok sayılır); durum `data\dongu-durum.json`.
