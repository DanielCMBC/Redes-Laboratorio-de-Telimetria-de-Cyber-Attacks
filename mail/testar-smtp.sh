#!/bin/bash
# Testes do servidor SMTP do laboratorio (porta 25)
# Uso: bash testar-smtp.sh [IP_DO_SERVIDOR]
SRV=${1:-10.200.200.30}
MSG=$(mktemp)
printf 'From: cliente@empresa-cliente.com\nTo: soc@soclab.local\nSubject: Teste SOC - link suspeito\n\nOla, acesse http://exemplo-phishing.test/login para validar sua conta.\n' > "$MSG"

echo "== 1) E-mail normal para soc@soclab.local (deve ser ACEITO)"
curl -s --url "smtp://$SRV:25" --mail-from cliente@empresa-cliente.com --mail-rcpt soc@soclab.local --upload-file "$MSG" && echo "OK: aceito"

echo "== 2) Tentativa de RELAY para dominio externo (deve ser RECUSADO)"
curl -s --url "smtp://$SRV:25" --mail-from cliente@empresa-cliente.com --mail-rcpt vitima@gmail.com --upload-file "$MSG" && echo "ERRO: relay aceito" || echo "OK: relay recusado"

echo "== 3) Destinatario inexistente (deve ser RECUSADO)"
curl -s --url "smtp://$SRV:25" --mail-from cliente@empresa-cliente.com --mail-rcpt naoexiste@soclab.local --upload-file "$MSG" && echo "ERRO: aceito" || echo "OK: recusado"
rm -f "$MSG"
