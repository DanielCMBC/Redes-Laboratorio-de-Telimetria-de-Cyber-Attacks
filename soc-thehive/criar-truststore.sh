#!/bin/bash
# Faz o TheHive (Java) confiar no certificado autoassinado do MISP.
# Executar em /home/daniel/soc/thehive depois de gerar o certificado do MISP.
set -e
cd /home/daniel/soc/thehive
mkdir -p truststore
docker cp thehive:/usr/lib/jvm/java-11-amazon-corretto/lib/security/cacerts truststore/cacerts
docker run --rm --user 0 \
  -v /home/daniel/soc/thehive/truststore:/ts \
  -v /home/daniel/soc/misp/ssl/cert.pem:/misp.pem:ro \
  --entrypoint keytool strangebee/thehive:5.4 \
  -importcert -noprompt -alias misp-lab -file /misp.pem -keystore /ts/cacerts -storepass changeit
docker compose up -d thehive
