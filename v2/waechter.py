#!/usr/bin/env python3
"""GeoCrimps-Waechter: Gesundheitscheck der Reel-Automatik. Veroeffentlicht nichts, aendert keine Reels.

Prueft
  1. Instagram-Token: gueltig (GET /me), Ablauf laut v2/status/token.json, letzte Erneuerung erfolgreich
  2. GH_ADMIN_TOKEN: Ablaufdatum (Kopfzeile github-authentication-token-expiration)
  3. Queue v2/reels.json: verpasste Termine, last_error, fehlender Quellen-Kommentar
  4. Puffer: jeder Termin der naechsten 120 h hat ein Reel mit status "ready", bestandenem Probelauf
     und erreichbarem Video und Cover (GitHub Pages)
  5. Fehlgeschlagene Workflow-Laeufe der letzten 26 h
Meldet Fehler als GitHub-Issue "Waechter: ..." mit Erwaehnung von Markus (Mail). Ist alles wieder in Ordnung,
schliesst er das Issue. Ergebnis ohne Geheimnisse in v2/status/waechter.json und in der Lauf-Zusammenfassung.

Umgebung: IG_USER_ID, IG_ACCESS_TOKEN, GH_ADMIN_TOKEN, GITHUB_TOKEN, GITHUB_REPOSITORY.
WAECHTER_TESTALARM=1 erzeugt einen Testfehler (prueft die Benachrichtigung). WAECHTER_OFFLINE=1: ohne Netz (lokaler Test).
"""
import datetime as dt
import hashlib
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ig_api import (IG, GitHub, OWNER_MENTION, REPO, berlin, fehlertext, load_json, mask,  # noqa: E402
                    now_utc, save_json)

STATUS = "v2/status/waechter.json"
TITLE = "Wächter: "
WINDOW_H = 120             # so weit im Voraus muss ein fertiges Reel bereitstehen (Produktion So/Mi: 5-6 Tage vorher)
MISSED_AFTER_MIN = 75      # so lange nach dem Termin gilt ein nicht veroeffentlichtes Reel als verpasst
MAX_LATE_H = 6             # wie reel_publish.py: so lange darf nachgeholt werden
TOKEN_WARN_D = 20          # Instagram-Token: Alarm, wenn weniger Tage uebrig
GH_TOKEN_WARN_D = 30       # GH_ADMIN_TOKEN: Alarm, wenn weniger Tage uebrig
OFFLINE = os.environ.get("WAECHTER_OFFLINE") == "1"

fehler, hinweise, geprueft = [], [], []


def fmt(t):
    return berlin(t).strftime("%a %d.%m. %H:%M").replace("Mon", "Mo").replace("Tue", "Di").replace("Wed", "Mi") \
        .replace("Thu", "Do").replace("Fri", "Fr").replace("Sat", "Sa").replace("Sun", "So")


def parse(ts):
    """Zeitstempel aus Queue, Plan oder von Instagram ("...+0000") lesen."""
    ts = str(ts).replace("Z", "+00:00")
    if len(ts) > 5 and ts[-5] in "+-" and ts[-3] != ":":
        ts = ts[:-2] + ":" + ts[-2:]
    t = dt.datetime.fromisoformat(ts)
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def reachable(url, want):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as r:
            return r.status == 200 and r.headers.get("Content-Type", "").startswith(want)
    except Exception:
        return False


def check_instagram(now):
    tok = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    uid = os.environ.get("IG_USER_ID", "").strip()
    mask(tok)
    if OFFLINE:
        geprueft.append("Instagram-Token: nicht geprüft (offline)")
    elif not tok:
        fehler.append("Instagram-Token fehlt: Secret IG_ACCESS_TOKEN ist leer.")
    else:
        ok, me = IG(tok, uid).get("me", fields="user_id,username")
        if not ok:
            fehler.append("Instagram-Token ungültig, nichts kann erscheinen: " + fehlertext(me))
        elif uid and str(me.get("user_id")) != uid:
            fehler.append("Instagram-Token gehört nicht zum Konto in IG_USER_ID.")
        else:
            geprueft.append(f"Instagram-Token gültig (@{me.get('username')})")
    st = load_json("v2/status/token.json", {}) or {}
    if st.get("ergebnis") == "fehler":
        fehler.append(f"Letzte Token-Erneuerung fehlgeschlagen ({str(st.get('letzter_versuch', ''))[:16]} UTC): "
                      f"{st.get('letzter_fehler')}")
    if st.get("gueltig_bis"):
        left = (parse(st["gueltig_bis"]) - now).total_seconds() / 86400
        geprueft.append(f"Instagram-Token laut Statusdatei gültig bis {parse(st['gueltig_bis']):%d.%m.%Y} "
                        f"(noch {left:.0f} Tage)")
        if left < TOKEN_WARN_D:
            fehler.append(f"Instagram-Token läuft am {parse(st['gueltig_bis']):%d.%m.%Y} ab; "
                          "die automatische Erneuerung hat offenbar nicht geklappt.")
    else:
        hinweise.append("Kein Ablaufdatum des Instagram-Tokens bekannt (v2/status/token.json).")


def check_github_token(now):
    tok = os.environ.get("GH_ADMIN_TOKEN", "").strip()
    if OFFLINE:
        geprueft.append("GH_ADMIN_TOKEN: nicht geprüft (offline)")
        return
    if not tok:
        fehler.append("Secret GH_ADMIN_TOKEN fehlt: Die Token-Erneuerung kann das Instagram-Token nicht speichern.")
        return
    ok, _, headers = GitHub(tok).call("GET", f"repos/{REPO}", want_headers=True)
    if not ok:
        fehler.append("GH_ADMIN_TOKEN wird von GitHub abgelehnt (abgelaufen oder ohne Zugriff auf das Repo).")
        return
    exp = {k.lower(): v for k, v in headers.items()}.get("github-authentication-token-expiration", "")
    if not exp:
        geprueft.append("GH_ADMIN_TOKEN gültig, ohne Ablaufdatum")
        return
    t = dt.datetime.strptime(exp.replace(" UTC", "").strip()[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
    left = (t - now).total_seconds() / 86400
    geprueft.append(f"GH_ADMIN_TOKEN gültig bis {t:%d.%m.%Y} (noch {left:.0f} Tage)")
    if left < GH_TOKEN_WARN_D:
        fehler.append(f"GH_ADMIN_TOKEN läuft am {t:%d.%m.%Y} ab. Bitte auf GitHub einen neuen "
                      "fine-grained Token nur für geocrimps-assets mit Schreibrecht auf Secrets anlegen und als "
                      "Secret GH_ADMIN_TOKEN speichern; sonst endet danach die Token-Erneuerung.")


def check_queue(now):
    q = load_json("v2/reels.json", {"reels": []})
    plan = load_json("v2/themenplan.json", {"slots": []})
    reels = {r["id"]: r for r in q.get("reels", [])}
    base = q.get("pages_base", "").rstrip("/") + "/"
    for r in reels.values():
        if r.get("status") == "published":
            pub = parse(r["published_at"]) if r.get("published_at") else None
            if r.get("first_comment") and r.get("first_comment_posted") is False and pub and now - pub < dt.timedelta(days=3):
                fehler.append(f"{r['id']} ({r['format']} #{r['nr']:02d}) ist online, aber der Quellen-Kommentar fehlt.")
            continue
        when = parse(r["scheduled"])
        tag = f"{r['id']} ({r['format']} #{r['nr']:02d}, Termin {fmt(when)})"
        if r.get("last_error"):
            le = r["last_error"]
            fehler.append(f"{tag}: letzter Fehler {str(le.get('at', ''))[:16]} UTC: {le.get('error')}")
        if r.get("status") == "ready" and not r.get("hold") and now - when > dt.timedelta(minutes=MISSED_AFTER_MIN) \
                and now - when < dt.timedelta(days=7):
            late = (now - when).total_seconds() / 3600
            nach = ("Nachholen geht noch bis " + fmt(when + dt.timedelta(hours=MAX_LATE_H))
                    + ": v2/publish.trigger ändern oder Claude Bescheid geben." if late < MAX_LATE_H
                    else "Für einen neuen Termin scheduled in v2/reels.json ändern oder Claude Bescheid geben.")
            fehler.append(f"Termin verpasst: {tag} ist nicht veröffentlicht. {nach}")
    n_ok = 0
    for s in plan.get("slots", []):
        when = parse(s["termin"])
        if not (now < when <= now + dt.timedelta(hours=WINDOW_H)):
            continue
        tag = f"Termin {fmt(when)} ({s['format']}, Post {s.get('post')})"
        rid = s.get("reel")
        r = reels.get(rid) if rid else None
        if not r:
            fehler.append(f"{tag}: noch kein Reel. Die geplante Produktion (So und Mi 07:41) ist offenbar nicht "
                          "gelaufen oder abgebrochen.")
            continue
        if r.get("hold"):
            hinweise.append(f"{tag}: {rid} ist angehalten (hold) und erscheint nicht.")
            continue
        if r.get("status") == "review":
            fehler.append(f"{tag}: {rid} wartet auf deine Freigabe (status review)"
                          + (f": {r['last_error'].get('error')}" if r.get("last_error") else "."))
            continue
        if r.get("status") != "ready":
            continue
        if (r.get("probe") or {}).get("result") != "FINISHED":
            fehler.append(f"{tag}: Probelauf für {rid} fehlt oder ist fehlgeschlagen ({(r.get('probe') or {}).get('result')}).")
        if OFFLINE:
            n_ok += 1
            continue
        bad = [k for k, want in (("video", "video/mp4"), ("cover", "image/")) if r.get(k) and not reachable(base + r[k], want)]
        if bad:
            fehler.append(f"{tag}: {', '.join(bad)} von {rid} unter GitHub Pages nicht erreichbar.")
        else:
            n_ok += 1
    geprueft.append(f"Puffer: {n_ok} Termin(e) in den nächsten {WINDOW_H} h fertig und erreichbar")
    future = [parse(s["termin"]) for s in plan.get("slots", []) if parse(s["termin"]) > now]
    if future and max(future) - now < dt.timedelta(days=10):
        hinweise.append(f"Themenplan reicht nur bis {fmt(max(future))}; die Produktion legt neue Termine selbst an.")


def check_runs(now, gh):
    if OFFLINE:
        geprueft.append("Workflow-Läufe: nicht geprüft (offline)")
        return
    since = (now - dt.timedelta(hours=26)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ok, res = gh.call("GET", f"repos/{REPO}/actions/runs?created=>{since}&per_page=60")
    if not ok:
        hinweise.append(f"Workflow-Läufe nicht lesbar (HTTP {res.get('http')}).")
        return
    bad = [w for w in res.get("workflow_runs", [])
           if w.get("conclusion") in ("failure", "timed_out", "startup_failure") and not w.get("name", "").startswith("Wächter")]
    for w in bad:
        fehler.append(f"Workflow \"{w.get('name')}\" ist am {fmt(parse(w['created_at']))} fehlgeschlagen: {w.get('html_url')}")
    geprueft.append(f"Workflow-Läufe der letzten 26 h: {res.get('total_count', 0)}, davon fehlgeschlagen: {len(bad)}")


def report(now):
    lines = [f"Stand: {fmt(now)} (Berliner Zeit)", ""]
    if fehler:
        lines += ["**Handlungsbedarf**", ""] + [f"- {f}" for f in fehler] + [""]
    if hinweise:
        lines += ["**Hinweise**", ""] + [f"- {h}" for h in hinweise] + [""]
    lines += ["**Geprüft**", ""] + [f"- {g}" for g in geprueft]
    return "\n".join(lines)


def main():
    now = now_utc()
    gh = GitHub(os.environ.get("GITHUB_TOKEN", ""))
    if os.environ.get("WAECHTER_TESTALARM") == "1":
        fehler.append("Testalarm: Claude prüft, ob dich die Meldung des Wächters per Mail erreicht. "
                      "Nichts zu tun; der nächste normale Lauf schließt dieses Issue.")
    check_instagram(now)
    check_github_token(now)
    check_queue(now)
    check_runs(now, gh)
    body = report(now)
    print(body)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write("## Wächter\n\n" + body + "\n")

    old = load_json(STATUS, {}) or {}
    fp = hashlib.sha1("\n".join(sorted(fehler)).encode()).hexdigest()[:12] if fehler else ""
    issue_no = old.get("issue")
    if not OFFLINE:
        issue = gh.find_open_issue(TITLE)
        foot = (f"\n\n{OWNER_MENTION} Diese Meldung kommt vom automatischen Gesundheitscheck der Reels. "
                "Sobald alles passt, schließt der Wächter das Issue selbst. Was zu tun ist: v2/PRODUKTION.md, Abschnitt 11.")
        if fehler and not issue:
            ok, res = gh.call("POST", f"repos/{REPO}/issues",
                              {"title": TITLE + f"{len(fehler)} Punkt(e) brauchen Aufmerksamkeit", "body": body + foot})
            issue_no = res.get("number") if ok else None
            print(f"Issue angelegt: #{issue_no}" if ok else f"Issue konnte nicht angelegt werden: {res}")
        elif fehler and issue and fp != old.get("fingerprint"):
            gh.call("POST", f"repos/{REPO}/issues/{issue['number']}/comments", {"body": "Neuer Stand:\n\n" + body + foot})
            gh.call("PATCH", f"repos/{REPO}/issues/{issue['number']}",
                    {"title": TITLE + f"{len(fehler)} Punkt(e) brauchen Aufmerksamkeit"})
            issue_no = issue["number"]
        elif not fehler and issue:
            gh.call("POST", f"repos/{REPO}/issues/{issue['number']}/comments",
                    {"body": "Alles wieder in Ordnung, der Wächter schließt dieses Issue.\n\n" + body})
            gh.call("PATCH", f"repos/{REPO}/issues/{issue['number']}", {"state": "closed", "state_reason": "completed"})
            issue_no = None
        elif fehler and issue:
            issue_no = issue["number"]
        else:
            issue_no = None
    new = {"fehler": fehler, "hinweise": hinweise, "geprueft": geprueft, "fingerprint": fp, "issue": issue_no}
    keep = ("fehler", "hinweise", "fingerprint", "issue")          # taegliche Zahlen allein loesen keinen Commit aus
    if {k: old.get(k) for k in keep} != {k: new[k] for k in keep} or not old:
        new["stand"] = now.isoformat(timespec="seconds")
        save_json(STATUS, new)
    sys.exit(0)


if __name__ == "__main__":
    main()
