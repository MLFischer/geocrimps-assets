#!/usr/bin/env python3
"""Gemeinsame Helfer fuer Token-Erneuerung, Waechter und Kennzahlen (nicht fuer reel_publish.py).

Instagram-API mit Instagram Login (graph.instagram.com) und GitHub-REST-API, nur Standardbibliothek.
Tokens werden nie ausgegeben: Fehlermeldungen werden bereinigt, in GitHub Actions werden neue Werte maskiert.
"""
import datetime as dt
import json
import os
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.instagram.com"
GH_API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
REPO = os.environ.get("GITHUB_REPOSITORY", "MLFischer/geocrimps-assets")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER_MENTION = "@MLFischer"


def now_utc():
    return dt.datetime.now(dt.timezone.utc)


def berlin(t):
    """Datum/Zeit fuer Meldungen in Berliner Zeit (Sommer-/Winterzeit ueber zoneinfo)."""
    try:
        from zoneinfo import ZoneInfo
        return t.astimezone(ZoneInfo("Europe/Berlin"))
    except Exception:                                   # Fallback ohne Zeitzonendaten
        return t.astimezone(dt.timezone(dt.timedelta(hours=1)))


def mask(*values):
    """In GitHub Actions: Werte fuer alle folgenden Log-Ausgaben dieses Jobs maskieren."""
    for v in values:
        if v and os.environ.get("GITHUB_ACTIONS"):
            print(f"::add-mask::{v}", flush=True)


def load_json(rel, default=None):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(rel, data):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


class IG:
    """Lesende/schreibende Aufrufe gegen graph.instagram.com; Rueckgabe (ok, daten_oder_fehler)."""

    def __init__(self, token, uid=""):
        self.tok = (token or "").strip()
        self.uid = (uid or "").strip()

    def clean(self, text):
        text = str(text or "")
        return text.replace(self.tok, "***") if self.tok else text

    def get(self, path, **params):
        params["access_token"] = self.tok
        url = f"{GRAPH}/{path}?{urllib.parse.urlencode(params)}"
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return True, json.load(r)
        except urllib.error.HTTPError as e:
            try:
                err = json.load(e).get("error", {})
            except Exception:
                err = {}
            return False, {"http": e.code, "code": err.get("code"), "subcode": err.get("error_subcode"),
                           "message": self.clean(err.get("message", ""))[:240]}
        except Exception as e:                          # Netzfehler
            return False, {"http": None, "code": None, "message": type(e).__name__}


def fehlertext(err):
    return f"Code {err.get('code')}/{err.get('subcode')} (HTTP {err.get('http')}): {err.get('message', '')}".strip()


class GitHub:
    """Minimaler Client fuer die GitHub-REST-API mit einem Token (GITHUB_TOKEN oder GH_ADMIN_TOKEN)."""

    def __init__(self, token):
        self.tok = (token or "").strip()

    def call(self, method, path, body=None, want_headers=False):
        url = path if path.startswith("http") else f"{GH_API}/{path.lstrip('/')}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if self.tok:
            req.add_header("Authorization", f"Bearer {self.tok}")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                res = json.loads(raw) if raw else {}
                return (True, res, dict(r.headers)) if want_headers else (True, res)
        except urllib.error.HTTPError as e:
            msg = e.read()[:300].decode("utf-8", "replace")
            out = {"http": e.code, "message": msg}
            return (False, out, {}) if want_headers else (False, out)
        except Exception as e:
            out = {"http": None, "message": type(e).__name__}
            return (False, out, {}) if want_headers else (False, out)

    def find_open_issue(self, title_prefix):
        ok, issues = self.call("GET", f"repos/{REPO}/issues?state=open&per_page=50")
        if not ok:
            return None
        for it in issues:
            if "pull_request" not in it and it.get("title", "").startswith(title_prefix):
                return it
        return None
