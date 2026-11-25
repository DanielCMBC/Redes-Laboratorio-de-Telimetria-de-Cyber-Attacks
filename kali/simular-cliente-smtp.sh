#!/bin/bash
# Simula o cliente enviando e-mails para o servidor SMTP do laboratorio
# Executar no Kali: bash simular-cliente-smtp.sh [IP_DO_SERVIDOR]
SRV=${1:-10.200.200.30}
echo "== 1) E-mail legitimo com link"
swaks --server "$SRV" --port 25 --from cliente@empresa-cliente.com --to soc@soclab.local --header "Subject: Relatorio mensal" --body "Segue o link do relatorio: https://empresa-cliente.com/relatorio.pdf" --hide-all && echo "enviado"
echo "== 2) E-mail com anexo"
echo "conteudo de teste" > /tmp/fatura.txt
swaks --server "$SRV" --port 25 --from financeiro@empresa-cliente.com --to analista@soclab.local --header "Subject: Fatura em anexo" --body "Segue a fatura." --attach /tmp/fatura.txt --hide-all && echo "enviado"
echo "== 3) Tentativas de relay (devem ser recusadas)"
for d in gmail.com outlook.com yahoo.com; do
  swaks --server "$SRV" --port 25 --from spammer@malicioso.test --to "vitima@$d" --hide-all >/dev/null 2>&1 || echo "relay para $d recusado"
done
echo "== 4) Enumeracao de usuarios (destinatarios inexistentes)"
for u in admin root teste financeiro rh suporte contato; do
  swaks --server "$SRV" --port 25 --from atacante@malicioso.test --to "$u@soclab.local" --hide-all >/dev/null 2>&1 || echo "$u recusado"
done
echo "== FIM"
