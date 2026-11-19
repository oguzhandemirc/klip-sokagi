# Kanal stratejisi (Klip Sokağı)

Araştırma: 19 Kasım 2026. [R] resmî YouTube, [İ] ikincil, [A] anekdot. Kaynak listesi en altta.

## Sıklık ve saat
- İlk 30 gün **günde 1-2 Short**, arada ≥ 8 saat. Güçlü an yoksa atma; zayıf klip doldurma yapma.
- Yükleme sayısı tek başına erişimi artırmıyor/azaltmıyor (Todd Sherman [R]); düşük kalite toplu yükleme zarar verir.
  vidIQ (367 bin yeni kanal [İ]): video başına medyan izlenme sıklıkla değişmiyor; sıklık yalnız "piyango bileti" sayısını artırır.
- Silip yeniden yükleme yapma (spam sinyali).
- Taze kayıt avantajı: yayından 24-72 saat içinde klip çıkar [İ].
- Saat: kayırılan saat yok [R]. Başlangıç 18:00-22:00 TSİ; 2-3 hafta sonra Studio "izleyicileriniz ne zaman YouTube'da" kartına göre ayarla.

## Özgünlük (en kritik risk)
- 1 Eki 2026: Shorts akışı, başkasının videosunu "önemli değişiklik olmadan" toplayan kanalları daha az dağıtıyor [R].
  Şablon düzenleme (yerleşim + altyazı + kanca) ve ekranı sadece betimleyen seslendirme **sayılmıyor** [İ, Rene Ritchie aktarımı].
- YPP "reused content": anlatısız an kolajı reddedilir; **yayıncı izni olsa bile** [R].
- Sayılan: kendi yorumun/sesin, hikâyeleştirme, klipten klibe değişen kurgu, seri anlatısı.
- 1 Şub 2027'den yeni YPP başvurusu: 90 günde 20 M nitelikli Shorts izlenmesi ya da 8.000 saat [R].

## Kanca, süre, döngü
- Tepki zirvesinden 0,5-1 sn önce başla; intro/logo yok. Kanca yazısı ≤ 5-6 kelime, ilk 2 sn.
- Hedef süre 20-35 sn (en çok 40).
- Döngü: son kare ilk kareye bağlansın; sonda "abone ol" yok. Her tekrar görüntüleme sayılır [R].
- Ölçü: Studio "izlemeye devam eden / kaydırıp geçen" oranı, kanca türüne göre etiketlenip karşılaştırılır.

## Başlık, açıklama, hashtag
- Başlık: ilk 40 karakterde yayıncı adı + cesur ama klipte olan vaat (bkz. `docs/baslik.md`).
- Açıklama ilk satır kredi: `🎥 Kaynak: <Yayıncı> – kick.com/<kanal>`, sonra 1-2 cümle bağlam, sonda 3-5 hashtag
  (`#GTA6 #<Yayıncı> #KlipSokağı`). `#shorts` gereksiz. 60+ hashtag hepsini geçersiz kılar [R].
- Shorts açıklamasındaki bağlantı tıklanmaz ama kredi olarak yazılır.

## Diğer
- Her Short'a "ilgili video" bağla (aynı yayıncının sonraki klibi) [R]; yayıncı başına oynatma listesi.
- Sabitlenmiş yorum: soru + kredi bağlantısı.
- Eşikler: 14. gün izlemeye devam oranı düşükse kancayı değiştir; 30. gün 20+ klipten hiçbiri 10 bini geçmediyse
  ve "Shorts akışı" trafiği düzse → özgünlük katmanını zorunlu yap.

## Kaynaklar
- https://support.google.com/youtube/blog/470890423/prioritizing-original-content-on-shorts?hl=en
- https://ppc.land/re-uploaded-shorts-lose-reach-as-youtube-favours-original-clips/
- https://support.google.com/youtube/answer/1311392?hl=en
- https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/
- https://blog.youtube/creator-and-artist-stories/debunking-common-myths-about-youtube-shorts/
- https://vidiq.com/research/youtube-first-10-videos-study/
- https://techcrunch.com/2025/03/26/youtube-is-changing-how-youtube-shorts-views-are-counted
- https://support.google.com/youtube/answer/6390658?hl=en

## İşletme planı (19 Kas 2026, kullanıcıyla)
- Shorts: günde 3 (13:00/18:00/21:00), 20-35 sn, en güçlü önce; yayından 24-72 sa içinde.
- Yatay video: 2-5 dk (kullanıcı), haftada 3 (Pzt/Çar/Cum 20:00). Tür: tek hikâye (2-3 dk) ya da mini derleme (4-6 an).
  Shorts anlarını kapsayabilir ama en az yarısı yeni an olmalı; her Short "ilgili video" ile o yatay videoya bağlanır.
- Kaynak önceliği: o gün canlı/yeni yayın > büyük yayıncı (RRaenee, Eray, Elraenn) > diğerleri. Ek yayıncı adları her yere.
- Başlık testi: yarısı yayıncı önde, yarısı GTA 6 önde; meta "baslik_turu" ile etiketlenir, 14. gün karşılaştırılır.
- Günlük döngü: 09:00 dünün yayınları → aday (gece.py) → Claude seçer/üretir → onay sayfası → kullanıcı ✔ → planla.py.
- Ölçüm: 7. gün ilk bakış; 14. gün kanca/başlık/saat; 30. gün özgünlük kararı (sesli katman gerekir mi).
