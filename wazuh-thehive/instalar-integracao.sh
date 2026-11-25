#!/bin/bash
# Instala a integracao Wazuh -> TheHive no Wazuh manager.
# Uso (no Wazuh): sudo bash instalar-integracao.sh   (pede a API key; ela nao aparece na tela)
set -e
read -r -s -p "Cole a API key do usuario wazuh@soclab.local (TheHive) e tecle Enter: " KEY
echo
if [ ${#KEY} -lt 20 ]; then echo "Chave invalida"; exit 1; fi
cd /var/ossec/integrations
cp /tmp/custom-w2thive.py custom-w2thive.py
cp slack custom-w2thive
chown root:wazuh custom-w2thive custom-w2thive.py
chmod 750 custom-w2thive custom-w2thive.py
CONF=/var/ossec/etc/ossec.conf
cp "$CONF" "$CONF.bak-thehive"
if ! grep -q custom-w2thive "$CONF"; then
cat >> "$CONF" <<EOF
<ossec_config>
  <integration>
    <name>custom-w2thive</name>
    <hook_url>http://10.200.200.30:9000</hook_url>
    <api_key>$KEY</api_key>
    <group>postfix,</group>
    <alert_format>json</alert_format>
  </integration>
</ossec_config>
EOF
fi
unset KEY
systemctl restart wazuh-manager
echo "== Integracao Wazuh -> TheHive instalada (alertas do grupo postfix)"
