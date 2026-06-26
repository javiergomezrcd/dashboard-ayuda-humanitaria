#!/usr/bin/env python3
"""Refresca stats.json con el nº de pacientes EN VIVO del registro oficial (Supabase,
sin reCAPTCHA ni CORS-issue). Lo ejecuta el GitHub Action cada 20 min.

Nota: las cifras de DESAPARECIDOS no se actualizan aquí: su API exige reCAPTCHA y no
se debe saltar. Se mantienen como snapshot en la web hasta tener acceso autorizado.
"""
import datetime
import json
import ssl
import urllib.request

SUPA = "https://ghswopasaynslycpaldj.supabase.co/rest/v1/pacientes"
KEY = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdoc3"
       "dvcGFzYXluc2x5Y3BhbGRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI0MDU0MDcsImV4cCI6"
       "MjA5Nzk4MTQwN30.MifuBb6C54KQdhuv_4gMoNAGJl997ycU299OcFeoyzU")
url = SUPA + "?select=id&deleted_at=is.null&limit=1"
req = urllib.request.Request(url, headers={
    "apikey": KEY, "Authorization": f"Bearer {KEY}", "Prefer": "count=exact"})
with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as r:
    rango = r.headers.get("Content-Range", "*/0")  # ej "0-0/393"
pacientes = int(rango.split("/")[-1]) if "/" in rango else 0
out = {"pacientes": pacientes,
       "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
with open("stats.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
print(out)
