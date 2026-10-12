#!/usr/bin/env python3
"""GeoCrimps V2 -- Reels ueber die Instagram-API (Instagram Login) veroeffentlichen.

Ablauf je faelligem Reel (status "ready", nicht "hold", Termin erreicht, hoechstens MAX_LATE_H zu spaet):
  1. Video- und Cover-URL (GitHub Pages) erreichbar?  2. Schon veroeffentlicht? (Schutz vor Doppelposts)
  3. Container anlegen (media_type=REELS)  4. Status abfragen bis FINISHED  5. media_publish
  6. Permalink holen, Quellen-Kommentar setzen  7. v2/reels.json fortschreiben (Commit macht der Workflow)

Modi:  python3 v2/reel_publish.py                 faellige Reels veroeffentlichen
       python3 v2/reel_publish.py --probe [ID]    Probelauf: Container bis FINISHED, NICHT veroeffentlichen
                                                  (ohne ID: naechstes unveroeffentlichtes Reel ohne bestandenen Probelauf)
Umgebung: IG_USER_ID, IG_ACCESS_TOKEN (GitHub-Secrets). Das Token wird nie ausgegeben.
"""
import datetime as dt
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "v2", "reels.json")
GRAPH = "https://graph.instagram.com"
MAX_LATE_H = 6
POLL_S, POLL_MAX_S = 10, 600
UID = os.environ.get("IG_USER_ID", "").strip()
TOK = os.environ.get("IG_ACCESS_TOKEN", "").strip()


def log(msg):
    print(str(msg).replace(TOK, "***") if TOK else msg, flush=True)

def now_utc():
    return dt.datetime.now(dt.timezone.utc)

def api(method, path, **params):
    params["access_token"] = TOK
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        req = urllib.request.Request(f"{GRAPH}/{path}?{data.decode()}")
    else:
        req = urllib.request.Request(f"{GRAPH}/{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            err = json.load(e).get("error", {})
        except Exception:
            err = {}
        raise RuntimeError(f"API-Fehler {e.code} bei {method} {path.split('?')[0]}: "
                           f"Code {err.get('code')}/{err.get('error_subcode')} {err.get('message', '')}".replace(TOK, "***"))

def reachable(url, want_type):
    for attempt in range(10):                 # GitHub Pages braucht nach dem Push ein bis zwei Minuten
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=30) as r:
                ctype = r.headers.get("Content-Type", "")
                if r.status == 200 and ctype.startswith(want_type):
                    return True
                log(f"  {url}: Status {r.status}, Typ {ctype}")
        except Exception as e:
            log(f"  {url}: noch nicht erreichbar ({e.__class__.__name__})")
        time.sleep(30)
    return False

def load():
    with open(QUEUE, encoding="utf-8") as f:
        return json.load(f)

def save(q):
    with open(QUEUE, "w", encoding="utf-8") as f:
        json.dump(q, f, ensure_ascii=False, indent=2)
        f.write("\n")

def marker(item):
    return f"{item['format']} #{item['nr']:02d}"

def already_published(item):
    """Schutz vor Doppelposts: steht ein Post mit derselben Serienmarke schon im Konto?"""
    res = api("GET", f"{UID}/media", fields="id,caption,timestamp,permalink,media_type", limit=10)
    for m in res.get("data", []):
        if marker(item) in (m.get("caption") or ""):
            return m
    return None

def create_container(q, item):
    base = q["pages_base"].rstrip("/") + "/"
    params = dict(media_type="REELS", video_url=base + item["video"], caption=item["caption"],
                  share_to_feed="true", audio_name=item.get("audio_name", "GeoCrimps"))
    if item.get("cover"):
        params["cover_url"] = base + item["cover"]
    res = api("POST", f"{UID}/media", **params)
    return res["id"]

def wait_finished(cid):
    t0 = time.time()
    while time.time() - t0 < POLL_MAX_S:
        st = api("GET", cid, fields="status_code,status")
        code = st.get("status_code")
        log(f"  Container-Status: {code}")
        if code == "FINISHED":
            return True, st
        if code in ("ERROR", "EXPIRED"):
            return False, st
        time.sleep(POLL_S)
    return False, {"status_code": "TIMEOUT"}

def check_urls(q, item):
    base = q["pages_base"].rstrip("/") + "/"
    ok = reachable(base + item["video"], "video/mp4")
    if item.get("cover"):
        ok = ok and reachable(base + item["cover"], "image/")
    return ok

def publish_item(q, item):
    log(f"Reel {item['id']} ({marker(item)}), Termin {item['scheduled']}")
    hit = already_published(item)
    if hit:
        log(f"  Bereits im Konto ({hit.get('permalink')}), wird nur nachgetragen.")
        item.update(status="published", media_id=hit["id"], permalink=hit.get("permalink"),
                    published_at=hit.get("timestamp"))
        return True
    if not check_urls(q, item):
        raise RuntimeError("Video oder Cover unter GitHub Pages nicht erreichbar")
    cid = create_container(q, item)
    ok, st = wait_finished(cid)
    if not ok:
        raise RuntimeError(f"Container nicht fertig: {st}")
    res = api("POST", f"{UID}/media_publish", creation_id=cid)
    mid = res["id"]
    info = api("GET", mid, fields="permalink,timestamp")
    item.update(status="published", media_id=mid, permalink=info.get("permalink"),
                published_at=info.get("timestamp") or now_utc().isoformat(timespec="seconds"))
    log(f"  Veroeffentlicht: {item['permalink']}")
    if item.get("first_comment"):
        try:
            api("POST", f"{mid}/comments", message=item["first_comment"])
            item["first_comment_posted"] = True
            log("  Quellen-Kommentar gesetzt.")
        except RuntimeError as e:              # Kommentar ist nachrangig: Post bleibt gueltig
            item["first_comment_posted"] = False
            log(f"  Quellen-Kommentar fehlgeschlagen: {e}")
    return True

def due(item, t):
    if item.get("status") != "ready" or item.get("hold"):
        return False
    when = dt.datetime.fromisoformat(item["scheduled"])
    return when <= t <= when + dt.timedelta(hours=MAX_LATE_H)

def main():
    if not (UID and TOK):
        log("IG_USER_ID oder IG_ACCESS_TOKEN fehlt."); sys.exit(1)
    q = load()
    if "--probe" in sys.argv:
        i = sys.argv.index("--probe")
        rid = sys.argv[i + 1] if len(sys.argv) > i + 1 else None
        cand = [r for r in q["reels"] if r.get("status") != "published" and (rid is None or r["id"] == rid)]
        if rid is None:                     # ohne ID: naechstes Reel ohne bestandenen Probelauf
            cand = [r for r in cand if (r.get("probe") or {}).get("result") != "FINISHED"] or cand
        if not cand:
            log("Kein Reel fuer den Probelauf gefunden."); sys.exit(1)
        item = cand[0]
        log(f"PROBELAUF fuer {item['id']} ({marker(item)}) -- es wird NICHTS veroeffentlicht.")
        if not check_urls(q, item):
            log("ERGEBNIS: Video/Cover nicht erreichbar."); sys.exit(1)
        cid = create_container(q, item)
        ok, st = wait_finished(cid)
        log(f"ERGEBNIS: {'FINISHED - Instagram nimmt das Video an.' if ok else 'FEHLER ' + json.dumps(st)}")
        item["probe"] = {"at": now_utc().isoformat(timespec="seconds"), "result": st.get("status_code")}
        save(q)
        sys.exit(0 if ok else 1)
    t = now_utc(); done = 0; failed = 0
    for item in q["reels"]:
        if due(item, t):
            try:
                publish_item(q, item); done += 1
            except Exception as e:
                failed += 1
                item["last_error"] = {"at": t.isoformat(timespec="seconds"), "error": str(e)[:300]}
                log(f"  FEHLER: {e}")
            save(q)
    if not done and not failed:
        log("Nichts faellig.")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
