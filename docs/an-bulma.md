# An bulma ve klip üretme şartnamesi

Amaç: bir yayın ya da video için, **video indirmeden**, puanlı bir an listesi çıkarmak;
sonra yalnız o anları kesip Shorts'a çevirmek.

## 1. Ortak sohbet kaydı

Üç platformun sohbeti tek biçime çevrilir: `saniye`, `gonderen`, `metin`, `bildirim_mi`.

- **Twitch** (`chat.json`): `comments[]` → `content_offset_seconds`, `commenter.name`, `message.body`;
  `message.user_notice_params.msg-id` doluysa bildirim.
- **Kick**: `created_at − start_time` = saniye; `type` değeri `message` ya da `reply` değilse bildirim;
  `[emote:123:KEKW]` → emote adı.
- **YouTube** (`.live_chat.json`, satır başına bir JSON): zaman `replayChatItemAction.videoOffsetTimeMsec`;
  mesaj `actions[].addChatItemAction.item`; `liveChatTextMessageRenderer` normal mesaj
  (metin `message.runs[].text`, gönderen `authorName.simpleText`); diğer tipler bildirim; zamanı 0 olanlar atlanır.

## 2. Sohbet patlaması

1. Ele: adı `bot` ile bitenler, abonelik/hediye/baskın bildirimleri, bağlantı içeren mesajlar, `!komut`lar.
2. 15 saniyelik dilimlere böl, mesajları say.
3. Eşik = ortalama + 2 × standart sapma. Her kanalın kendi temposuna uyar.
4. Eşiği aşan dilimleri yoğunluğa göre sırala; birbirine 60 saniyeden yakın olanlardan yalnız en yoğunu kalır.
5. Sohbet geç tepki verir: klip patlamadan **25 saniye önce** başlar, **40 saniye** sürer.
6. Eşik dilim başına 5 mesajın altındaysa yayın çok sakin; sohbet sinyaline güvenme.

Puan = (dilimdeki mesaj − ortalama) / standart sapma.

Tepki türü ipucu: dilimde en çok geçen kelime ya da 2-3 kelimelik ifade klibin çalışma adı olur
(emote, kahkaha, küfür, tek harf, dolgu kelimeler elenir). Kahkaha emote'u ağırlıklı dilim "komik",
şaşkınlık ağırlıklı dilim "şok" diye etiketlenir; başlık yazarken kullanılır.

## 3. YouTube ısı verisi

1. 100 noktayı al; videonun ilk %5'ini yok say.
2. Yerel tepe noktalarını bul (iki komşusundan yüksek ve değeri ≥ 0,5 olanlar).
3. Kısa videoda (nokta ≤ 15 saniye) tepe noktasının kendisi andır.
4. Uzun videoda tepe yalnız bölgeyi gösterir: o bölgenin sesini indir, en yüksek ses zirvesini an kabul et.

Puan = tepe değeri (0-1) × 3, böylece sohbet puanıyla aynı ölçeğe yaklaşır.

## 4. Yardımcı sinyaller

- **Twitch klip izlenmesi:** aynı ana denk gelen izleyici klibi varsa puana `log10(izlenme)` eklenir.
- **Ses zirvesi:** ffmpeg `ebur128` ile anlık ses yüksekliği; yayıncının bağırdığı/güldüğü yerler.
  Yalnız seçilen bölgelerin sesi indirilir, bütün yayının değil.

Toplam puan = sinyallerin ağırlıklı toplamı; ağırlıklar `config.yaml`'da. En yüksek N an seçilir (varsayılan 10).
Çıktı: `data/sohbet/<kaynak>-anlar.json` (saniye, puan, sinyaller, çalışma adı, tepki türü).

## 5. Parça indirme

Seçilen her an için başlangıç − 5 sn ve bitiş + 5 sn payıyla kaynak kesilir (`docs/indirme.md`).
Çıktı: `data/parca/<kaynak>-<sıra>.mp4`.

## 6. Düzenleme (dönüşümün kalbi)

Ham kesit yüklenmez; her klip şunları taşır:

- **Yerleşim:** üstte yayıncı kamerası, altta oyun (1080×1920). Kamera koordinatları yayıncı başına
  `config.yaml`'da. Kamerası olmayan kaynakta ortadan kırpma + bulanık arka plan.
- **Altyazı:** faster-whisper (Türkçe) → kelime zamanlı, büyük ve kalın; ffmpeg ile yakılır.
- **Kanca yazısı:** ilk 1-2 saniyede ne olacağını merak ettiren kısa cümle.
- **Bağlam:** gerekiyorsa tek satır açıklama ("3 saattir bu görevi deniyor").
- **Kredi:** köşede yayıncı adı.
- **Ses:** loudnorm ile dengeleme. Oyun radyosunda lisanslı şarkı çalıyorsa klibi işaretle.
- **Süre:** 20-45 saniye hedef.

Sorun işaretleri (onay ekranında gösterilir): ilk 7 saniyede grafik şiddet, ara sahne ağırlıklı kesit,
hikâye sonu ipucu, radyo müziği.

## 7. Metin

Transkript + sohbet ifadeleri + tepki türü → Claude API: 3 Türkçe başlık (≤ 60 karakter, yalan değil),
açıklama (kaynak kredisi ve bağlantısıyla), 3-5 etiket. `data/hazir/<klip>.json`'a yazılır.

## 8. Onay ve yükleme

- Onay: yerel bir HTML sayfası; her klip için izle, ✔ / ✘, başlık seç. Onaylanan `data/onayli/`'ya geçer.
- Yükleme: YouTube Data API v3, `privacyStatus=private` + `publishAt` ile planlı yayın.
  API denetimi bitene kadar videolar gizli kalır; YouTube Studio'dan elle yayına alınır.
- Günde 1-3 Shorts, Türkiye akşam saatleri.
