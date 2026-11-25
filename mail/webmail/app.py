#!/usr/bin/env python3
# SOCLab WebMail 2000 - interface web simples (estilo Y2K) para o servidor SMTP do laboratorio.
# Envia e-mails via SMTP (porta 25) e le as caixas postais (mbox) do Postfix em modo somente leitura.
import os, html, smtplib, mailbox, email.utils, urllib.parse, re
from email.message import EmailMessage
from email.header import decode_header, make_header
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp")
DOMAIN = "soclab.local"
USERS = ["cliente", "soc", "analista"]
NL = chr(10)

CSS = """
* { box-sizing: border-box; }
body { margin: 0; padding: 16px; font-family: Tahoma, Verdana, 'Trebuchet MS', sans-serif; font-size: 14px; color: #000;
  background: #008080 repeating-linear-gradient(45deg, #007070 0 12px, #008888 12px 24px); }
.win { max-width: 820px; margin: 0 auto; background: #c0c0c0; border: 3px outset #fff; box-shadow: 4px 4px 0 #000; }
.title { background: linear-gradient(90deg, #000080, #1084d0); color: #fff; font-weight: bold; padding: 6px 8px; display: flex; justify-content: space-between; }
.title span.btns b { display: inline-block; width: 18px; height: 16px; margin-left: 2px; background: #c0c0c0; color: #000; border: 2px outset #fff; font-size: 11px; text-align: center; line-height: 12px; }
.logo { text-align: center; padding: 12px 8px 4px; }
.logo h1 { margin: 0; font-family: 'Comic Sans MS', 'Comic Neue', cursive; font-size: 30px; color: #ff00cc;
  text-shadow: 2px 2px 0 #00ffff, 4px 4px 0 #000080; letter-spacing: 1px; }
.logo small { color: #000080; font-weight: bold; }
.marquee { overflow: hidden; white-space: nowrap; background: #000; color: #0f0; font-family: 'Courier New', monospace; border: 2px inset #fff; margin: 8px; }
.marquee span { display: inline-block; padding-left: 100%; animation: scroll 18s linear infinite; }
@keyframes scroll { from { transform: translateX(0); } to { transform: translateX(-100%); } }
.blink { animation: blink 1s steps(2, start) infinite; color: #f00; font-weight: bold; }
@keyframes blink { to { visibility: hidden; } }
nav { display: flex; flex-wrap: wrap; gap: 6px; padding: 4px 8px 8px; }
a.btn, button { font: inherit; font-weight: bold; color: #000; text-decoration: none; background: #c0c0c0; border: 3px outset #fff; padding: 4px 12px; cursor: pointer; }
a.btn:active, button:active { border-style: inset; }
.panel { background: #fff; border: 2px inset #fff; margin: 8px; padding: 12px; }
label { display: block; font-weight: bold; margin-top: 8px; color: #000080; }
input, textarea { width: 100%; font: inherit; padding: 4px; border: 2px inset #fff; background: #ffffe0; }
textarea { min-height: 140px; }
.ok { background: #ccffcc; border: 2px solid #008000; padding: 8px; margin: 8px; }
.err { background: #ffcccc; border: 2px solid #c00000; padding: 8px; margin: 8px; }
table { width: 100%; border-collapse: collapse; }
th { background: #000080; color: #fff; text-align: left; padding: 4px; }
td { border-bottom: 1px dotted #808080; padding: 4px; vertical-align: top; }
details summary { cursor: pointer; color: #0000ee; text-decoration: underline; }
pre { white-space: pre-wrap; word-break: break-word; background: #f0f0f0; border: 1px solid #808080; padding: 6px; font-family: 'Courier New', monospace; }
.warn { color: #c00000; font-weight: bold; }
.foot { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px; padding: 6px 8px 10px; font-size: 11px; }
.badge { background: #000; color: #ff0; border: 2px outset #fff; padding: 2px 6px; font-family: 'Courier New', monospace; }
.construct { height: 10px; margin: 0 8px; background: repeating-linear-gradient(45deg, #ff0 0 10px, #000 10px 20px); }
@media (max-width: 600px) { body { padding: 6px; } .logo h1 { font-size: 22px; } }
"""

VISITS = [1999]


def esc(s):
    return html.escape(str(s if s is not None else ""))


def dec(value):
    try:
        return str(make_header(decode_header(value or "")))
    except Exception:
        return value or ""


def page(title, body):
    VISITS[0] += 1
    nav = "".join('<a class="btn" href="/caixa?u=' + u + '">&#128235; ' + u + '</a>' for u in USERS)
    return ("<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>" + esc(title) + " - SOCLab WebMail 2000</title><style>" + CSS + "</style></head><body>"
            "<div class='win'><div class='title'><span>&#9993; SOCLab WebMail 2000 - " + esc(title) + "</span>"
            "<span class='btns'><b>_</b><b>&#9633;</b><b>x</b></span></div>"
            "<div class='logo'><h1>SOCLab WebMail 2000</h1><small>mail.soclab.local &bull; SMTP porta 25</small></div>"
            "<div class='marquee'><span>*** Bem-vindo ao WebMail do laboratorio SOC! *** Todo e-mail e monitorado pelo Wazuh *** "
            "Nao clique em links suspeitos! *** Relay para dominios externos e BLOQUEADO *** </span></div>"
            "<nav><a class='btn' href='/'>&#9998; Escrever</a>" + nav + "</nav>"
            "<div class='construct'></div>" + body +
            "<div class='foot'><span>&copy; 2000-2026 SOCLab &bull; Melhor visualizado em 800x600</span>"
            "<span class='badge'>Visitantes: " + str(VISITS[0]).zfill(6) + "</span></div></div></body></html>")


def compose(msg=""):
    opts = "".join('<option value="' + u + '@' + DOMAIN + '">' for u in USERS)
    return page("Escrever", msg +
        "<div class='panel'><form method='post' action='/enviar'>"
        "<label for='de'>De:</label><input id='de' name='de' required value='cliente@empresa-cliente.com'>"
        "<label for='para'>Para:</label><input id='para' name='para' list='usuarios' required value='soc@" + DOMAIN + "'>"
        "<datalist id='usuarios'>" + opts + "</datalist>"
        "<label for='assunto'>Assunto:</label><input id='assunto' name='assunto' required value='Ola do cliente!'>"
        "<label for='msg'>Mensagem (pode conter links):</label>"
        "<textarea id='msg' name='msg'>Ola equipe SOC, segue o link: https://empresa-cliente.com/relatorio</textarea>"
        "<p><button type='submit'>&#128228; Enviar via SMTP</button> <span class='blink'>NOVO!</span></p>"
        "</form></div>")


def body_text(m):
    attachments = []
    text = ""
    if m.is_multipart():
        for part in m.walk():
            fn = part.get_filename()
            if fn:
                attachments.append(dec(fn))
            elif part.get_content_type() == "text/plain" and not text:
                text = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
    else:
        payload = m.get_payload(decode=True)
        text = payload.decode(m.get_content_charset() or "utf-8", "replace") if payload else ""
    return text, attachments


def inbox(user):
    path = "/var/mail/" + user
    rows = []
    if os.path.exists(path):
        for m in reversed(list(mailbox.mbox(path))):
            text, att = body_text(m)
            links = re.findall(r"https?://[^ " + NL + "<>]+", text)
            extra = ""
            if links:
                extra += "<p class='warn'>&#9888; Links encontrados (verifique antes de abrir):</p><pre>" + esc(NL.join(links)) + "</pre>"
            if att:
                extra += "<p><b>Anexos:</b> " + esc(", ".join(att)) + "</p>"
            rows.append("<tr><td>" + esc(dec(m.get("From"))) + "</td><td><details><summary>" + esc(dec(m.get("Subject")) or "(sem assunto)") +
                        "</summary><pre>" + esc(text) + "</pre>" + extra + "</details></td><td>" + esc(m.get("Date")) + "</td></tr>")
    table = ("<table><tr><th>De</th><th>Assunto</th><th>Data</th></tr>" + "".join(rows) + "</table>") if rows else "<p>Caixa vazia.</p>"
    return page("Caixa de " + user, "<div class='panel'><h2>&#128235; " + esc(user) + "@" + DOMAIN +
                " (" + str(len(rows)) + " mensagens)</h2>" + table + "</div>")


class Handler(BaseHTTPRequestHandler):
    def send(self, code, content):
        data = content.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(url.query)
        if url.path == "/":
            self.send(200, compose())
        elif url.path == "/caixa" and q.get("u", [""])[0] in USERS:
            self.send(200, inbox(q["u"][0]))
        else:
            self.send(404, page("404", "<div class='err'>Pagina nao encontrada.</div>"))

    def do_POST(self):
        if self.path != "/enviar":
            return self.send(404, page("404", "<div class='err'>Pagina nao encontrada.</div>"))
        n = int(self.headers.get("Content-Length", "0") or 0)
        f = urllib.parse.parse_qs(self.rfile.read(min(n, 100000)).decode("utf-8", "replace"))
        get = lambda k: f.get(k, [""])[0].strip()
        msg = EmailMessage()
        msg["From"] = get("de")
        msg["To"] = get("para")
        msg["Subject"] = get("assunto")
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg["Message-ID"] = email.utils.make_msgid(domain="webmail." + DOMAIN)
        msg.set_content(get("msg") or "(vazio)")
        try:
            with smtplib.SMTP(SMTP_HOST, 25, timeout=15) as s:
                s.ehlo("webmail." + DOMAIN)
                s.send_message(msg)
            note = "<div class='ok'>&#10004; E-mail aceito pelo servidor SMTP para <b>" + esc(get("para")) + "</b>.</div>"
        except smtplib.SMTPRecipientsRefused as e:
            detail = "; ".join(str(code) + " " + r.decode("utf-8", "replace") for code, r in e.recipients.values())
            note = "<div class='err'>&#10008; Servidor recusou o destinatario: " + esc(detail) + "</div>"
        except Exception as e:
            note = "<div class='err'>&#10008; Erro ao enviar: " + esc(e) + "</div>"
        self.send(200, compose(note))

    def log_message(self, fmt, *args):
        print(self.address_string() + " " + (fmt % args), flush=True)


if __name__ == "__main__":
    print("SOCLab WebMail 2000 em http://0.0.0.0:8080 (SMTP: " + SMTP_HOST + ":25)", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
