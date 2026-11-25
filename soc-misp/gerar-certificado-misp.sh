#!/bin/bash
# Gera o certificado HTTPS autoassinado do MISP (exigido pelo misp-nginx).
# Executar em /home/daniel/soc/misp (projeto oficial: github.com/MISP/misp-docker)
set -e
TMP=$(mktemp -d)
openssl req -x509 -nodes -newkey rsa:2048 -days 730 \
  -subj '/CN=10.200.200.30/O=SOC-Lab' -addext 'subjectAltName=IP:10.200.200.30' \
  -keyout "$TMP/key.pem" -out "$TMP/cert.pem"
# A pasta ssl/ pode pertencer ao root (criada pelo Docker); copiamos via conteiner.
docker run --rm --user 0 -v "$PWD/ssl:/out" -v "$TMP:/in" --entrypoint sh \
  ghcr.io/misp/misp-docker/misp-nginx:latest -c \
  'cp /in/cert.pem /in/key.pem /out/ && chmod 644 /out/cert.pem && chgrp 101 /out/key.pem && chmod 640 /out/key.pem'
rm -rf "$TMP"
docker compose up -d --force-recreate misp-nginx
