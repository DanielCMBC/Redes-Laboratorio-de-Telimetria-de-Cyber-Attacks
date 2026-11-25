#!/usr/bin/env python3
# Integracao Wazuh -> TheHive 5 (episodio 13, atualizado)
# Envia cada alerta do Wazuh como um alerta no TheHive via API v1.
# Argumentos passados pelo Wazuh: <arquivo_do_alerta> <api_key> <hook_url>
import sys, json, datetime, urllib.request, urllib.error

LOG = "/var/ossec/logs/integrations.log"

def log(msg):
    with open(LOG, "a") as f:
        f.write(datetime.datetime.now().isoformat() + " custom-w2thive: " + msg + chr(10))

def main():
    alert_file, api_key, hook_url = sys.argv[1], sys.argv[2].strip(), sys.argv[3].strip()
    with open(alert_file) as f:
        alert = json.load(f)
    rule = alert.get("rule", {})
    agent = alert.get("agent", {})
    data = alert.get("data", {}) or {}
    level = int(rule.get("level", 0))
    severity = 1 if level < 7 else 2 if level < 10 else 3 if level < 13 else 4
    lines = [
        "**Alerta gerado pelo Wazuh**",
        "",
        "- Regra: " + str(rule.get("id")) + " (nivel " + str(level) + ")",
        "- Descricao: " + str(rule.get("description")),
        "- Agente: " + str(agent.get("name")) + " (" + str(agent.get("ip", "-")) + ")",
        "- Horario: " + str(alert.get("timestamp")),
        "",
        "Log original:",
        "",
        "    " + str(alert.get("full_log", ""))[:4000],
    ]
    observables = []
    if data.get("srcip"):
        observables.append({"dataType": "ip", "data": data["srcip"], "message": "IP de origem detectado pelo Wazuh"})
    tags = ["wazuh", "rule:" + str(rule.get("id")), "agent:" + str(agent.get("name"))]
    tags += ["group:" + g for g in rule.get("groups", [])]
    body = {
        "type": "wazuh",
        "source": "wazuh-manager",
        "sourceRef": str(alert.get("id")),
        "title": "[Wazuh] " + str(rule.get("description")),
        "description": chr(10).join(lines),
        "severity": severity,
        "tags": tags,
        "observables": observables,
    }
    req = urllib.request.Request(
        hook_url.rstrip("/") + "/api/v1/alert",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            log("alerta " + str(alert.get("id")) + " enviado ao TheHive: HTTP " + str(r.status))
    except urllib.error.HTTPError as e:
        log("erro HTTP " + str(e.code) + ": " + e.read()[:300].decode(errors="replace"))
    except Exception as e:
        log("erro: " + str(e))

if __name__ == "__main__":
    main()
