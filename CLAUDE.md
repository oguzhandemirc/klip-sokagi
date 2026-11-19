# Klip Sokağı — Shorts Fabrikası · Çalışma Rehberi

> Yeni oturumda sırayla oku: bu dosya → `docs/formuller.md` (neden böyle) → `DURUM.md` (son durum, en yeni üstte).
> Ayrıntılar `docs/` altında; yalnız ilgili aşamaya gelince oku. Başlangıç: 19 Kasım 2026.

## 1. Hedef
Türk Kick/Twitch yayıncılarının (şimdilik GTA 6) yayınlarında **izleyicinin en çok tepki verdiği anları otomatik bulup**
YouTube'a **dikey Shorts** ve **2-5 dk yatay video** olarak planlı yüklemek. Kanal: **Klip Sokağı (@klipsokagi)**.

Kesin kararlar (kullanıcı verdi, yeniden tartışma):
- Kendi oyun kaydımız yok; kaynak başkalarının yayınları. Video bütün indirilmez: önce sinyal, sonra yalnız anlar kesilir.
- Yayıncılardan tek tek izin alınmaz; telif atanlar `yasakli.csv`ye girer ve işlenmez.
- Kredi videodaki küçük yarı saydam yayıncı rozetiyle verilir; açıklamada kaynak satırı/bağlantı yok.
- Sohbet katmanı ve sesli yorum yok (şimdilik). Format kanıtlanmış başarılı örneklerden alınır.
- Başlıklar cesur/clickbait olabilir ama klipte olmayanı vaat etmez. Yayıncı adı (ve yayındaki diğer yayıncılar) yazılır.
- Hedef yayıncılar ve kamera koordinatları `config.yaml`'da.

## 2. Hat ve betikler
```
SİNYAL → AN SEÇ → PARÇA KES → TRANSKRİPT → (Claude inceler, plan yazar) → ÜRET → ONAY → YÜKLE (gizli+planlı) → ÖLÇ
```
| İş | Betik | Not |
|---|---|---|
| Canlı mı / son yayınlar | `canli.py <kanal>`, `sinyal.py <kanal>` | Kick API |
| Sohbet örnekle | `sinyal.py <kanal> --sira N` | 10 sn adım, devam edebilir |
| An seç | `an_sec.py <sohbet.json> --esik-sd 1.5 --aralik 45 --adet 15` | |
| Kes | `parca_indir.py <anlar.json> --adet 15` | m3u8'den |
| Döküm + kare özeti | `transkript.py data/parca/<önek>-*.mp4` | inceleme için |
| Toplu gece hattı | `gece.py kanal:sira ...` / `bitince.py <kanal>` | yükleme yapmaz |
| Short üret | `uretim.py plan.json --klasor data/hazir/hd --kamera x:y:g:y --yerlesim tam` | `duzenle.py` |
| Yatay video | `uzun.py plan-uzun.json` | 2-5 dk + küçük resim |
| Onay sayfası | `onay.py <klasör>` | index.html |
| Yükle | `yukle.py <mp4> --zaman "AAAA-GG-AA SS:DD" --gercek` | kuru çalışma varsayılan |
| Takvime dağıt | `planla.py <mp4>... --gercek` | config `yayin_saatleri` |
| Sınır yeniden dene | `yeniden_dene.py <mp4>...` | uploadLimitExceeded |
| Durum / sil / hemen yayınla | `durum_yt.py`, `sil_yt.py`, `simdi_yayinla.py <id>` | |
| Açıklama güncelle | `aciklama_guncelle.py --gercek` | kural değişince |
| Ek yayıncı | `ek_yayinci.py <Ad> <meta.json>...` | |
| Yayıncı tarama | `klip_tara.py`, `kick_bul.py` | telif göstergesi |

## 3. Çalışma kuralları
1. Kullanıcıya dönük her metin Türkçe. Değişken/dosya adları ASCII. Kullanıcı kod bilmiyor varsay.
2. Betik dosyasını heredoc ile yazma; Write aracıyla yaz, tek satırla çalıştır (gözetimsiz işte izin sorusu çıkmasın). Alt ajana da yaz.
3. Sırlar (`client_secret.json`, `token.json`, `.env`) git dışı; koda, loga, sohbete yazılmaz.
4. `yasakli.csv`deki yayıncı işlenmez. Telif/kaldırma talebi gelirse hemen ekle, kullanıcıya bildir.
5. **İnsan onayı:** kullanıcı onayı olmadan yayın yapılmaz. Gizli+planlı yükleme yayından önce Studio'da görülebilir.
6. Ele: ara sahne ağırlıklı, hikâye sonu/spoiler, hile/mod, sızıntı, cinsel içerik. İlk 7 sn'de grafik şiddet varsa işaretle.
7. Müzik yalnız `muzik/` (CC BY); açıklamada müzik kredisi zorunlu.
8. Yüklenen klibin ham parçasını ve çıktısını yüklemeden sonra silebilirsin (disk).
9. Gelir tahmini yapma; ölçülen veriyle konuş.
10. Oturum sonunda `DURUM.md`'ye (en üste) kısa kayıt düş; kalıcı yeni bilgi `docs/formuller.md`'ye.
11. İki makine aynı anda yükleme yapmasın (tekrar yükleme). Yükleme kaydı `data/yuklendi/kayit.jsonl`.

## 4. Yol haritası
- [x] Sinyal + an seçimi (Kick) · parça kesme · Short düzenleme (HD) · yatay video · başlık/açıklama kuralları
- [x] YouTube API (gizli+planlı yükleme, silme, küçük resim) · kanal kuruldu
- [ ] 7/24 sunucu (ThinkPad, `docs/kurulum-thinkpad.md`) + `dongu.py` otomatik döngü (biten yayın → stok → kota kadar yükle → temizle)
- [ ] Ses zirvesi sinyali · Twitch/YouTube kaynakları · onay sayfasında ✔/✘
- [ ] Analiz (YouTube Analytics) · küfür sansürü · sesli yorum kararı (30. gün)

## 5. Klasörler
```
shorts/
├── CLAUDE.md  DURUM.md  ONBOARDING.md
├── config.yaml            # yayıncılar, kamera koordinatları, yayın saatleri
├── yasakli.csv            # telif atan yayıncılar
├── docs/                  # formuller.md, strateji.md, baslik.md, yukleme.md, kurulum-thinkpad.md, indirme.md, riskler.md
├── marka/                 # logo, afiş, kanal açıklaması
├── muzik/                 # CC BY müzikler
├── *.py                   # betikler (tablo yukarıda)
└── data/                  # sohbet/ parca/ hazir/ yuklendi/ log/ (git dışı)
```
