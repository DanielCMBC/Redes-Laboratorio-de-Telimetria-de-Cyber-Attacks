FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN echo "postfix postfix/main_mailer_type string 'Internet Site'" | debconf-set-selections
RUN echo "postfix postfix/mailname string mail.soclab.local" | debconf-set-selections
RUN apt-get update && apt-get install -y --no-install-recommends postfix mailutils ca-certificates && rm -rf /var/lib/apt/lists/*
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 25
CMD ["/entrypoint.sh"]
