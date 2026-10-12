#!/usr/bin/env python3
"""Setup-Check V2: prueft das Instagram-Token, ohne etwas zu veroeffentlichen.

Liest IG_USER_ID und IG_ACCESS_TOKEN aus der Umgebung (GitHub-Secrets),
ruft nur lesende Endpunkte auf und haengt das Ergebnis an result.md an.
Das Token wird nie ausgegeben; Fehlermeldungen werden davon bereinigt.
Exit-Code 1, sobald eine Pruefung fehlschlaegt.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.instagram.com"
UID = os.environ.get("IG_USER_ID", "").strip()
TOK = os.environ.get("IG_ACCESS_TOKEN", "").strip()
OUT = "result.md"
rows = []


def clean(text):
    text = str(text or "")
    if TOK:
        text = text.replace(TOK, "***")
    return text.replace("|", "/").replace("\n", " ")[:180]


def get(path, **params):
    params["access_token"] = TOK
    url = f"{GRAPH}/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return True, json.load(resp)
    except urllib.error.HTTPError as exc:
        try:
            err = json.load(exc).get("error", {})
        except Exception:
            err = {}
        return False, {"code": err.get("code"), "message": clean(err.get("message"))}
    except Exception as exc:  # network error etc.
        return False, {"code": None, "message": clean(type(exc).__name__)}


def row(check, ok, detail):
    rows.append(f"| {check} | {'OK' if ok else 'FEHLT'} | {clean(detail)} |")
    return ok


def fail_text(err):
    code = err.get("code")
    hint = {190: "Token abgelaufen oder ungueltig", 10: "Recht fehlt", 200: "Recht fehlt"}.get(code, "Fehler")
    return f"{hint} (Code {code}): {err.get('message', '')}"


def main():
    all_ok = True
    if not TOK:
        row("Token vorhanden", False, "Secret IG_ACCESS_TOKEN ist leer")
        return False
    ok, me = get("me", fields="user_id,username")
    if not ok:
        row("Token gueltig (instagram_business_basic)", False, fail_text(me))
        return False
    row("Token gueltig (instagram_business_basic)", True, f"Konto @{me.get('username')}")
    same = str(me.get("user_id", "")) == UID
    all_ok &= row("IG_USER_ID passt zum Token", same, "passt" if same else "Secret IG_USER_ID gehoert zu einem anderen Konto")
    uid = str(me.get("user_id") or UID)

    ok, lim = get(f"{uid}/content_publishing_limit", fields="quota_usage")
    all_ok &= row("Veroeffentlichen (instagram_business_content_publish)", ok,
                  f"heutige API-Posts: {(lim.get('data') or [{}])[0].get('quota_usage', '?')}" if ok else fail_text(lim))

    ok, media = get(f"{uid}/media", fields="id,media_type,timestamp", limit=1)
    items = media.get("data", []) if ok else []
    if not items:
        row("Letzter Post lesbar", False, fail_text(media) if not ok else "keine Posts gefunden")
        return False
    mid = items[0]["id"]
    row("Letzter Post lesbar", True, f"{items[0].get('media_type')} vom {str(items[0].get('timestamp', ''))[:10]}")

    ok, ins = get(f"{mid}/insights", metric="reach")
    all_ok &= row("Kennzahlen (instagram_business_manage_insights)", ok, "Reichweite abrufbar" if ok else fail_text(ins))

    ok, com = get(f"{mid}/comments", fields="id", limit=1)
    all_ok &= row("Kommentare (instagram_business_manage_comments)", ok, "Kommentare abrufbar" if ok else fail_text(com))
    return all_ok


if __name__ == "__main__":
    result = main()
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write("\n## Instagram-Token\n\n| Pruefung | Status | Detail |\n|---|---|---|\n")
        fh.write("\n".join(rows) + "\n")
    print("\n".join(rows))
    sys.exit(0 if result else 1)
