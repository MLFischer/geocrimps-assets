#!/usr/bin/env python3
"""Instagram-Token erneuern und als GitHub-Secret IG_ACCESS_TOKEN zurueckschreiben.

1. GET graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token
   (laut Meta: das Token muss mindestens 24 h alt und noch gueltig sein; das neue gilt 60 Tage ab Erneuerung)
2. Neues Token pruefen: GET /me gehoert zum selben Konto (IG_USER_ID)
3. gh secret set IG_ACCESS_TOKEN mit GH_TOKEN = GH_ADMIN_TOKEN; der Wert geht ueber stdin, nie ins Log
4. v2/status/token.json fortschreiben: erneuert_am, gueltig_bis, ergebnis -- nie das Token selbst

Laeuft im Workflow token-refresh.yml (1. und 15. jedes Monats). Exit 1 bei jedem Fehler; der Waechter meldet ihn.
Umgebung: IG_USER_ID, IG_ACCESS_TOKEN, GH_TOKEN (GH_ADMIN_TOKEN), GITHUB_REPOSITORY.
"""
import datetime as dt
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ig_api import IG, REPO, fehlertext, load_json, mask, now_utc, save_json  # noqa: E402

STATUS = "v2/status/token.json"


def main():
    now = now_utc()
    st = load_json(STATUS, {}) or {}
    st["letzter_versuch"] = now.isoformat(timespec="seconds")
    uid = os.environ.get("IG_USER_ID", "").strip()
    tok = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    mask(tok)

    def fail(msg):
        st.update(ergebnis="fehler", letzter_fehler=msg)
        save_json(STATUS, st)
        print(f"FEHLER: {msg}", flush=True)
        sys.exit(1)

    if not tok:
        fail("Secret IG_ACCESS_TOKEN ist leer")
    if not os.environ.get("GH_TOKEN", "").strip():
        fail("Secret GH_ADMIN_TOKEN fehlt; ohne es kann das neue Token nicht gespeichert werden")

    ok, res = IG(tok, uid).get("refresh_access_token", grant_type="ig_refresh_token")
    if not ok:
        fail("Instagram hat die Erneuerung abgelehnt: " + fehlertext(res))
    new = str(res.get("access_token") or "").strip()
    secs = int(res.get("expires_in") or 0)
    mask(new)
    if not new or secs <= 0:
        fail("Antwort ohne Token oder Laufzeit")

    ok, me = IG(new, uid).get("me", fields="user_id,username")
    if not ok:
        fail("Das neue Token funktioniert nicht: " + fehlertext(me))
    if uid and str(me.get("user_id", "")) != uid:
        fail("Das neue Token gehört zu einem anderen Konto als IG_USER_ID")

    neu_geschrieben = False
    if new != tok:
        p = subprocess.run(["gh", "secret", "set", "IG_ACCESS_TOKEN", "--repo", REPO],
                           input=new, text=True, capture_output=True)
        if p.returncode != 0:
            err = (p.stderr or p.stdout or "").replace(new, "***").replace(tok, "***")
            fail("Secret IG_ACCESS_TOKEN konnte nicht geschrieben werden: " + err.strip()[:200]
                 + " (das alte Token gilt bis zu seinem Ablauf weiter)")
        neu_geschrieben = True

    gueltig_bis = now + dt.timedelta(seconds=secs)
    st.update(ergebnis="ok", letzter_fehler=None, erneuert_am=now.isoformat(timespec="seconds"),
              gueltig_bis=gueltig_bis.isoformat(timespec="seconds"), laufzeit_tage=round(secs / 86400, 1),
              konto="@" + str(me.get("username", "")), secret_neu_geschrieben=neu_geschrieben,
              quelle="Workflow token-refresh.yml")
    save_json(STATUS, st)
    print(f"OK: Token erneuert fuer @{me.get('username')}, gueltig bis {gueltig_bis:%Y-%m-%d %H:%M} UTC "
          f"({'Secret neu geschrieben' if neu_geschrieben else 'gleicher Wert, nur verlaengert'}).", flush=True)


if __name__ == "__main__":
    main()
