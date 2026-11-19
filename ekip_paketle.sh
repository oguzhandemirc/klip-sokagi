#!/bin/bash
# Ekip arkadaşı için temiz başlangıç paketi: kod + rehberler + ayar + marka + müzik. SIR ve VERİ YOK.
# Kullanım: bash ekip_paketle.sh  → ~/Desktop/klip-sokagi-baslangic.zip
set -e
cd "$(dirname "$0")"
HEDEF="$HOME/Desktop/klip-sokagi-baslangic.zip"
rm -f "$HEDEF"
zip -rq "$HEDEF" . \
  -x '.venv/*' 'araclar/*' 'data/*' 'rehber1/*' 'rehber2/*' '*/__pycache__/*' '__pycache__/*' '*.DS_Store' \
     'token*.json' 'client_secret*.json' '.env' '.git/*' 'plan-sohbetli.json'
mkdir -p /tmp/ks-bos/data/{sohbet,parca,hazir,yuklendi,log}
( cd /tmp/ks-bos && zip -rq "$HEDEF" data )
rm -rf /tmp/ks-bos
unzip -l "$HEDEF" | grep -E "token|client_secret|\.env$" && { echo "SIR VAR, paket silindi"; rm -f "$HEDEF"; exit 1; } || true
ls -lh "$HEDEF"
