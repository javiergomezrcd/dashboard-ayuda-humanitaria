#!/usr/bin/env python3
"""Refresca stats.json con cifras agregadas EN VIVO. Lo corre el GitHub Action cada 20 min.

Fuentes (server-side, sin reCAPTCHA, autorizadas por el equipo):
  - localizapacientes.com/api/stats  -> Centro Nacional de Localizacion de Personas
    (hospitales reportando, pacientes registrados). Fuente principal de pacientes.
  - Supabase registro-pacientes       -> respaldo / conteo alternativo.
El CORS de esas APIs bloquea al navegador, pero NO al Action (server-side). Sin captcha.
"""
import datetime
import json
import ssl
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
CTX = ssl.create_default_context()


def _get(url, headers=None, timeout=30):
    h = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return json.loads(r.read().decode("utf-8")), r.headers


out = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}

# 1) Centro Nacional (localizapacientes) — fuente principal de pacientes
try:
    d, _ = _get("https://localizapacientes.com/api/stats")
    out["pacientes"] = d.get("pacientesRegistrados")
    out["hospitales"] = d.get("hospitalesReportando")
    out["fuentePacientes"] = "Centro Nacional de Localizacion de Personas"
except Exception as e:
    print("localizapacientes FALLO:", e)

# 2) Supabase registro-pacientes — respaldo (conteo activos)
try:
    KEY = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdoc3"
           "dvcGFzYXluc2x5Y3BhbGRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI0MDU0MDcsImV4cCI6"
           "MjA5Nzk4MTQwN30.MifuBb6C54KQdhuv_4gMoNAGJl997ycU299OcFeoyzU")
    _, hdrs = _get("https://ghswopasaynslycpaldj.supabase.co/rest/v1/pacientes"
                   "?select=id&deleted_at=is.null&limit=1",
                   headers={"apikey": KEY, "Authorization": f"Bearer {KEY}",
                            "Prefer": "count=exact"})
    rango = hdrs.get("Content-Range", "*/0")
    out["pacientesSupabase"] = int(rango.split("/")[-1]) if "/" in rango else 0
    if "pacientes" not in out:  # si fallo la principal, usa esta
        out["pacientes"] = out["pacientesSupabase"]
except Exception as e:
    print("Supabase FALLO:", e)

with open("stats.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
print(out)
