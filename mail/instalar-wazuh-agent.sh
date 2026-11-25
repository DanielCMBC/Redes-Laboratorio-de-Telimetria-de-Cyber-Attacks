#!/bin/bash
# Instala o agente Wazuh no Ubuntu_Server e monitora o log do Postfix
# Uso: sudo bash instalar-wazuh-agent.sh
set -e
MANAGER=10.200.200.20
LOGFILE=/home/daniel/soc/mail/logs/mail.log
timeout 5 bash -c "echo > /dev/tcp/$MANAGER/1514" && echo "Wazuh manager acessivel"
cd /tmp
wget -q https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.14.10-1_amd64.deb
WAZUH_MANAGER=$MANAGER WAZUH_AGENT_NAME=smtp-server dpkg -i ./wazuh-agent_4.14.10-1_amd64.deb
if ! grep -q "$LOGFILE" /var/ossec/etc/ossec.conf; then
cat >> /var/ossec/etc/ossec.conf <<EOF
<ossec_config>
  <localfile>
    <log_format>syslog</log_format>
    <location>$LOGFILE</location>
  </localfile>
</ossec_config>
EOF
fi
systemctl daemon-reload
systemctl enable --now wazuh-agent
sleep 15
systemctl is-active wazuh-agent
grep -E "Connected to|mail.log" /var/ossec/logs/ossec.log | tail -4
echo "== AGENTE INSTALADO"
