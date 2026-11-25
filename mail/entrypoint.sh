#!/bin/bash
# Servidor SMTP do laboratorio SOC (Postfix) - porta 25
set -e
postconf -e "myhostname=mail.soclab.local"
postconf -e "mydomain=soclab.local"
postconf -e 'myorigin=$mydomain'
postconf -e 'mydestination=$myhostname, localhost.$mydomain, localhost, $mydomain'
postconf -e "inet_interfaces=all"
postconf -e "inet_protocols=ipv4"
postconf -e "mynetworks=127.0.0.0/8"
postconf -e "smtpd_relay_restrictions=permit_mynetworks, reject_unauth_destination"
postconf -e "smtpd_helo_required=yes"
postconf -e "disable_vrfy_command=yes"
postconf -e 'smtpd_banner=$myhostname ESMTP'
postconf -e "message_size_limit=20480000"
postconf -e "maillog_file=/var/log/postfix/mail.log"
for u in cliente soc analista; do
  id "$u" >/dev/null 2>&1 || useradd -m -s /usr/sbin/nologin "$u"
done
mkdir -p /var/log/postfix
newaliases
echo "Postfix iniciando em mail.soclab.local:25"
exec postfix start-fg
