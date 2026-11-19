# Başlık ve kanca stratejisi

Araştırma: 19 Kasım 2026. Reddit'e erişilemedi; kaynaklar resmî YouTube sayfaları + uygulayıcı blogları
(çıkarları var) + birkaç büyük ilişkisel veri çalışması. Türkçe pazara özgü kaynak bulunamadı.

## Ne biliyoruz
- **Akışta asıl filtre kanca**, başlık değil: "izlenen / kaydırılan" oranı. Kanca ilk saniyede, ekranda yazılı,
  3-7 kelime. Başlık oynatıcının altında küçük görünür, mobilde ~40 karakterde kesilir; asıl rolü arama ve kanal sayfası.
- Oyun nişinde kısa başlık ve BÜYÜK HARF vurgusu olumlu, soru biçimi zayıf, emoji nötr (18 bin kanallık ilişkisel veri).
  Tamamı büyük harf bazı kaynaklara göre spam sinyali → tek kelimelik vurgu.
- `#Shorts` etiketi etkisiz (17 bin videoluk veri). 2-3 özel hashtag açıklamada yeter.
- **Clickbait sınırı (resmî):** vaat edilen şey klipte yoksa "yanıltıcı meta veri" → kaldırma/ihtar.
  Cesur olabilir, yalan olamaz.
- Shorts'ta başlık A/B testi **yok** (resmî). Ölçmek için `analiz.py`'de başlık kalıbı etiketlenecek.

## Kurallar
1. Yayıncı adı + GTA 6 + somut olay + tek açık uç. Anahtar bilgi ilk 40 karakterde, toplam 20-50 karakter.
2. BÜYÜK HARF yalnız 1-2 kelimede.
3. Kanca ve başlık aynı vaadi verir.
4. Aynı yayının kliplerinde kalıp çeşitlenir.

Şablonlar: `[Yayıncı] GTA 6'da [olay], sohbet çıldırdı` · `[Yayıncı] bunu beklemiyordu: GTA 6 [olay]` ·
`GTA 6'da [olay] mı oldu? [Yayıncı]'nın tepkisi`

## En büyük risk: özgünlük (başlıktan önemli)
1 Ekim 2026 (ikincil kaynaklar, resmî metin birebir okunamadı): YouTube, ağırlıkla başkalarının videolarını
yeniden yükleyen kanalların Shorts dağıtımını azaltıyor. Yalnız altyazı/kesim/şablon düzenleme "özgün katkı"
sayılmıyor; yayıncı izni bunu çözmüyor. → Kanala yorum, bağlam ya da özgün kurgu katmanı gerekiyor
(ör. Türkçe anlatım/yorum sesi, "sohbet ne dedi" katmanı, derleme/karşılaştırma formatları).
