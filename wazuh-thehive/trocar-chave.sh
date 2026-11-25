#!/bin/bash
# Troca a API key do TheHive usada pela integracao Wazuh -> TheHive.
# Uso (no Wazuh): sudo bash trocar-chave.sh   (a chave nao aparece na tela)
set -e
read -r -s -p "Cole a API key do usuario wazuh@soclab.local (TheHive) e tecle Enter: " KEY
echo
echo "Chave recebida: ${#KEY} caracteres, comeca com ${KEY:0:2}"
if [ ${#KEY} -lt 20 ]; then echo "Chave invalida"; exit 1; fi
CONF=/var/ossec/etc/ossec.conf
cp "$CONF" "$CONF.bak-chave"
NEWKEY="$KEY" python3 - "$CONF" <<'PYEOF'
import os, re, sys
p = sys.argv[1]
t = open(p).read()
t = re.sub(r"(<name>custom-w2thive</name>(?:(?!</integration>).)*?<api_key>)[^<]*(</api_key>)", lambda m: m.group(1) + os.environ["NEWKEY"] + m.group(2), t, flags=re.S)
open(p, "w").write(t)
PYEOF
unset KEY NEWKEY
systemctl restart wazuh-manager
echo "== Chave trocada e Wazuh reiniciado"
