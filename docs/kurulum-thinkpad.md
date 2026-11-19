# ThinkPad (Windows + WSL2) kurulumu

Hedef: bütün hat (sinyal → an → kesim → düzenleme → yükleme → temizlik) 7/24 açık ThinkPad'de çalışır.
Mac'teki döngüler devirden sonra kapatılır (iki makine aynı anda yüklerse tekrar yükleme olur).

## 1. Kullanıcı yapar (Windows tarafı, ~20 dk)
1. PowerShell'i **Yönetici** olarak aç: `wsl --install -d Ubuntu` → bilgisayarı yeniden başlat → Ubuntu kullanıcı adı/şifre belirle.
2. Güç ayarları: uyku **Hiçbir zaman**, "kapak kapatılınca" **Hiçbir şey yapma** (prizdeyken).
3. Windows Update'in gece yeniden başlatmasını sınırla (Etkin saatler) — yeniden başlarsa döngü cron ile kendini toparlar.
4. Tailscale açık olsun (paket Taildrop ile gelecek → Windows `İndirilenler`).

## 2. Ubuntu (WSL) içinde — Claude Code oturumu yapar
```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip ffmpeg git curl
curl -fsSL https://claude.ai/install.sh | bash        # Claude Code
mkdir -p ~/shorts && cd ~/shorts
tar -xzf /mnt/c/Users/<WINDOWS_KULLANICI>/Downloads/shorts-paket.tar.gz
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/pip install yt-dlp
.venv/bin/python -c "import duzenle; print(duzenle.FONT_KALIN)"   # /mnt/c/Windows/Fonts/ariblk.ttf olmalı
.venv/bin/python yukle.py --giris   # token.json geldiyse tarayıcı açmadan "Bağlı kanal: Klip Sokağı" yazar
```
Not: WSL içinde ffmpeg'in sürümü farklı olabilir; `duzenle.py` `-/filter_complex` (ffmpeg ≥ 7) kullanır.
`ffmpeg -version` 7'den küçükse: `sudo add-apt-repository ppa:ubuntuhandbook1/ffmpeg7 && sudo apt install ffmpeg`
ya da statik derleme (johnvansickle.com) kullan.

## 3. Doğrulama (yükleme yapmadan)
- `.venv/bin/python canli.py rraenee` → Kick API çalışıyor mu (WSL'den 403 gelirse Kick Cloudflare'i; User-Agent sinyal.py'de).
- `.venv/bin/python duzenle.py data/... --kamera 1390:144:530:296 --yerlesim tam --sure 10 --cikti /tmp/deneme.mp4`
  → bir klip üretebiliyor mu, süre ölç.

## 4. Devir (Mac → ThinkPad)
1. Mac'te çalışan döngüleri durdur (gece.py, bitince.py, yeniden_dene.py, uzun yükleme döngüsü).
2. Mac'teki güncel `data/yuklendi/kayit.jsonl`, `data/sohbet/` ve yeni HD çıktılar ThinkPad'e kopyalanır (ikinci paket).
3. ThinkPad'de döngüler başlatılır; cron kurulur (bkz. `docs/strateji.md` İşletme planı).

## 5. Otomatik döngü (cron, ThinkPad)
`crontab -e`:
```
*/10 * * * * cd ~/shorts && .venv/bin/python dongu.py >> data/log/dongu.log 2>&1
```
`dongu.py` (yazılacak): biten yayınları bulur → hepsini stoklar → yükleme kotası elverdikçe gizli+planlı yükler
→ yüklenen dosyaları temizler. Aynı anda iki kopya çalışmasın diye kilit dosyası kullanır.
