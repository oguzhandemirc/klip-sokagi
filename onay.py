#!/usr/bin/env python3
"""Onay sayfası: data/hazir/ içindeki Short'ları tek bir HTML sayfasında listeler.

Her klip için: video, kaynak zamanı, sohbet sinyali, başlık önerileri, açıklama, etiketler, müzik notu.
Sayfa yerel dosyadır, internete gitmez. Tarayıcıda aç: open data/hazir/index.html

Kullanım: python3 onay.py
"""
import html
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
HAZIR = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else KOK / "data" / "hazir"

STIL = """
:root { --bg:#f6f5f2; --kart:#fff; --yazi:#1c1c1c; --soluk:#6b6b6b; --cizgi:#e3e1dc; --vurgu:#0b6e4f; }
@media (prefers-color-scheme: dark) { :root { --bg:#141414; --kart:#1e1e1e; --yazi:#ececec; --soluk:#9a9a9a; --cizgi:#2e2e2e; --vurgu:#4fc29a; } }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--yazi); font:15px/1.5 -apple-system, system-ui, sans-serif; }
header { padding:28px 20px 8px; max-width:1200px; margin:auto; }
h1 { margin:0 0 4px; font-size:22px; }
header p { margin:0; color:var(--soluk); }
main { max-width:1200px; margin:auto; padding:16px 20px 60px; display:grid; gap:20px;
       grid-template-columns:repeat(auto-fill, minmax(340px, 1fr)); }
article { background:var(--kart); border:1px solid var(--cizgi); border-radius:14px; padding:14px; }
video { width:100%; aspect-ratio:9/16; background:#000; border-radius:10px; }
h2 { font-size:16px; margin:12px 0 4px; }
.etiket { display:inline-block; font-size:12px; padding:2px 8px; border-radius:99px; border:1px solid var(--cizgi);
          color:var(--soluk); margin:0 4px 4px 0; }
.etiket.muzik { color:var(--vurgu); border-color:var(--vurgu); }
ol { padding-left:20px; margin:6px 0; }
details { margin-top:8px; color:var(--soluk); }
pre { white-space:pre-wrap; font:13px/1.45 ui-monospace, monospace; background:var(--bg); padding:8px; border-radius:8px; }
.not { color:var(--soluk); font-size:13px; }
"""


def kart(meta_yolu):
    m = json.loads(meta_yolu.read_text())
    video = meta_yolu.with_suffix(".mp4").name
    e = html.escape
    basliklar = "".join(f"<li>{e(b)}</li>" for b in m.get("basliklar", []))
    etiketler = [f'<span class="etiket">{e(x)}</span>' for x in m.get("bilgi", [])]
    if m.get("muzik"):
        etiketler.append(f'<span class="etiket muzik">müzik: {e(m["muzik"])}</span>')
    else:
        etiketler.append('<span class="etiket">müziksiz</span>')
    return f"""
<article>
  <video src="{e(video)}" controls preload="metadata" playsinline></video>
  <h2>{e(m.get("kanca", ""))}</h2>
  <div>{''.join(etiketler)}</div>
  <p class="not">{e(m.get("neden", ""))}</p>
  <strong>Başlık önerileri</strong><ol>{basliklar}</ol>
  <details><summary>Açıklama ve etiketler</summary><pre>{e(m.get("aciklama", ""))}</pre></details>
  <details><summary>Konuşma dökümü</summary><pre>{e(m.get("metin", ""))}</pre></details>
</article>"""


def main():
    metalar = sorted(p for p in HAZIR.glob("*.json") if p.with_suffix(".mp4").exists())
    kartlar = "".join(kart(p) for p in metalar)
    sayfa = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Shorts Onay</title>
<style>{STIL}</style></head><body>
<header><h1>Onay bekleyen Shorts ({len(metalar)})</h1>
<p>Hiçbiri yüklenmedi. Beğendiklerini YouTube uygulamasından yükle; trend sesi orada “Ses ekle” ile ekleyebilirsin.</p></header>
<main>{kartlar}</main></body></html>"""
    hedef = HAZIR / "index.html"
    hedef.write_text(sayfa)
    print(f"{len(metalar)} klip → {hedef}")


if __name__ == "__main__":
    main()
