#!/usr/bin/env python3
"""GeoCrimps-Kurzbericht (montags): Kennzahlen je veroeffentlichtem Reel aus v2/reels.json.

Holt per Instagram-API (Instagram Login, nur lesend) fuer jedes Reel mit media_id:
  views, reach, likes, comments, shares, saved, total_interactions, ig_reels_avg_watch_time (ms),
  ig_reels_video_view_total_time (ms), reels_skip_rate
und fuer das Konto followers_count und media_count. Daraus die Quoten aus dem Konzept:
  Skip-Rate, Wiedergabequote (Ø Wiedergabe / Laenge des Reels), Shares und Saves pro Reichweite.
Schreibt v2/kennzahlen/<Datum>.md und .json, haengt Zeilen an v2/kennzahlen/verlauf.csv an und
kommentiert das Issue "Kennzahlen: Kurzbericht" mit Erwaehnung von Markus (Mail). Veroeffentlicht nichts.
Hinweis von Meta: Werte koennen bis zu 48 h verzoegert sein; nicht verfuegbare Werte fehlen statt 0.

Umgebung: IG_USER_ID, IG_ACCESS_TOKEN, GITHUB_TOKEN, GITHUB_REPOSITORY.
"""
import csv
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ig_api import IG, GitHub, OWNER_MENTION, REPO, ROOT, berlin, fehlertext, load_json, mask, now_utc  # noqa: E402

METRICS = ["views", "reach", "likes", "comments", "shares", "saved", "total_interactions",
           "ig_reels_avg_watch_time", "ig_reels_video_view_total_time", "reels_skip_rate"]
OUTDIR = os.path.join(ROOT, "v2", "kennzahlen")
ISSUE_TITLE = "Kennzahlen: Kurzbericht"
CSV_COLS = ["datum", "reel", "slug", "format", "ablauf", "tage_online", "views", "reach", "skip_rate_prozent",
            "avg_watch_s", "dauer_s", "wiedergabequote", "likes", "comments", "shares", "saved",
            "shares_pro_reichweite", "saves_pro_reichweite", "followers"]


def value_of(entry):
    if "total_value" in entry:
        return (entry.get("total_value") or {}).get("value")
    vals = entry.get("values") or []
    return vals[0].get("value") if vals else None


def insights(ig, mid):
    """Alle Metriken in einem Aufruf; lehnt Meta einen Namen ab, einzeln nachfragen."""
    ok, res = ig.get(f"{mid}/insights", metric=",".join(METRICS))
    out, missing = {}, []
    if ok:
        for e in res.get("data", []):
            out[e.get("name")] = value_of(e)
    else:
        for m in METRICS:
            ok1, r1 = ig.get(f"{mid}/insights", metric=m)
            if ok1 and r1.get("data"):
                out[m] = value_of(r1["data"][0])
            else:
                missing.append(m if ok1 else f"{m} ({fehlertext(r1)[:80]})")
    for m in METRICS:
        if m not in out and not any(x.startswith(m) for x in missing):
            missing.append(m)
    return out, missing


def parse_ts(ts):
    """Zeitstempel aus der Queue oder von Instagram ("...+0000") lesen."""
    if not ts:
        return None
    ts = str(ts).replace("Z", "+00:00")
    if len(ts) > 5 and ts[-5] in "+-" and ts[-3] != ":":
        ts = ts[:-2] + ":" + ts[-2:]
    t = dt.datetime.fromisoformat(ts)
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def pct(x):
    return "–" if x is None else f"{x:.1f} %"


def num(x):
    return "–" if x is None else f"{x:,}".replace(",", ".")


def main():
    now = now_utc()
    tok = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    uid = os.environ.get("IG_USER_ID", "").strip()
    mask(tok)
    if not tok:
        print("FEHLER: IG_ACCESS_TOKEN fehlt"); sys.exit(1)
    ig = IG(tok, uid)
    ok, acc = ig.get("me", fields="username,followers_count,media_count")
    if not ok:
        print("FEHLER: Konto nicht lesbar: " + fehlertext(acc)); sys.exit(1)
    q = load_json("v2/reels.json", {"reels": []})
    rows, notes = [], []
    posts = []                                    # (Eintrag, Name im Bericht, Dauer oder None) je Post im Konto
    for r in q.get("reels", []):
        for k, old in enumerate(r.get("ersetzt") or []):   # ersetzte Fassungen (Neu-Post) weiter auswerten
            if old.get("media_id"):
                posts.append((dict(r, **old, status="published"), f"{r['id']} (Fassung {old.get('fassung', k + 1)}, ersetzt)",
                              old.get("dauer_s")))
        if r.get("status") == "published" and r.get("media_id"):
            posts.append((r, r["id"], None))
    for r, name, dauer_alt in posts:
        vals, missing = insights(ig, r["media_id"])
        rep = load_json(f"v2/qc/{r['slug']}/bericht.json", {}) or {}
        dauer = dauer_alt or rep.get("dauer_s")
        reach = vals.get("reach")
        avg_ms = vals.get("ig_reels_avg_watch_time")
        avg_s = round(avg_ms / 1000, 2) if isinstance(avg_ms, (int, float)) else None
        skip = vals.get("reels_skip_rate")
        if isinstance(skip, (int, float)) and 0 <= skip <= 1:      # falls als Anteil geliefert
            skip = skip * 100
        def per_reach(x):
            return round(100 * x / reach, 2) if isinstance(x, (int, float)) and reach else None
        pub = parse_ts(r.get("published_at"))
        days = round((now - pub).total_seconds() / 86400, 1) if pub else None
        fmt = f"{r['format']} #{r['nr']:02d}" + (" (alte Fassung)" if name != r["id"] else "")
        row = {"datum": now.date().isoformat(), "reel": name, "slug": r["slug"], "format": fmt,
               "ablauf": r.get("ablauf", ""), "tage_online": days, "views": vals.get("views"), "reach": reach,
               "skip_rate_prozent": round(skip, 1) if isinstance(skip, (int, float)) else None, "avg_watch_s": avg_s,
               "dauer_s": dauer, "wiedergabequote": round(100 * avg_s / dauer, 1) if avg_s and dauer else None,
               "likes": vals.get("likes"), "comments": vals.get("comments"), "shares": vals.get("shares"),
               "saved": vals.get("saved"), "shares_pro_reichweite": per_reach(vals.get("shares")),
               "saves_pro_reichweite": per_reach(vals.get("saved")), "followers": acc.get("followers_count"),
               "permalink": r.get("permalink"), "fehlend": missing}
        rows.append(row)
        if missing:
            notes.append(f"{name}: nicht verfügbar: {', '.join(missing)}")

    os.makedirs(OUTDIR, exist_ok=True)
    prev = None
    olds = sorted(f for f in os.listdir(OUTDIR) if f.endswith(".json") and f[:10] != now.date().isoformat())
    if olds:
        prev = load_json(f"v2/kennzahlen/{olds[-1]}", None)
    fol = acc.get("followers_count")
    dfol = (fol - prev["konto"]["followers_count"]) if prev and isinstance(fol, int) and prev.get("konto", {}).get("followers_count") is not None else None
    stamp = berlin(now)
    md = [f"# GeoCrimps – Kurzbericht vom {stamp:%d.%m.%Y}", "",
          f"Konto @{acc.get('username')}: **{num(fol)} Follower**" + (f" ({dfol:+d} seit {olds[-1][:10]})" if dfol is not None else "")
          + f", {num(acc.get('media_count'))} Beiträge.", "",
          "| Reel | Ablauf | online | Aufrufe | Reichweite | Skip-Rate | Ø Wiedergabe | Wiedergabequote | Shares/Reichw. | Saves/Reichw. | Likes | Komm. |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in rows:
        link = f"[{x['format']}]({x['permalink']})" if x.get("permalink") else x["format"]
        md.append(f"| {link} | {x['ablauf'] or '–'} | {x['tage_online'] if x['tage_online'] is not None else '–'} d | {num(x['views'])} | "
                  f"{num(x['reach'])} | {pct(x['skip_rate_prozent'])} | "
                  f"{('%.1f s' % x['avg_watch_s']) if x['avg_watch_s'] is not None else '–'} von {x['dauer_s'] or '–'} s | "
                  f"{pct(x['wiedergabequote'])} | {pct(x['shares_pro_reichweite'])} | {pct(x['saves_pro_reichweite'])} | "
                  f"{num(x['likes'])} | {num(x['comments'])} |")
    if not rows:
        md.append("| – | | | | | | | | | | | |")
    md += ["", "Lesart: Skip-Rate = Anteil der Aufrufe, die in den ersten 3 s weiterwischen (niedriger ist besser). "
           "Wiedergabequote = Ø Wiedergabedauer geteilt durch die Länge des Reels (über 100 % heißt: wird wiederholt). "
           "Shares und Saves pro Reichweite sind die Quoten, nach denen das Konzept steuert.",
           "Meta liefert Werte mit bis zu 48 h Verzögerung; frische Reels sind deshalb noch unvollständig. "
           "Die Auswertung mit Claude ist alle vier Wochen (nächste laut Konzept: 16.11.2026)."]
    if notes:
        md += ["", "Nicht verfügbar: " + "; ".join(notes)]
    text = "\n".join(md) + "\n"
    day = now.date().isoformat()
    with open(os.path.join(OUTDIR, f"{day}.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    with open(os.path.join(OUTDIR, f"{day}.json"), "w", encoding="utf-8") as fh:
        json.dump({"stand": now.isoformat(timespec="seconds"), "konto": {k: acc.get(k) for k in ("username", "followers_count", "media_count")},
                   "reels": rows}, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    path = os.path.join(OUTDIR, "verlauf.csv")
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLS, extrasaction="ignore")
        if new_file:
            w.writeheader()
        for x in rows:
            w.writerow(x)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(text)

    gh = GitHub(os.environ.get("GITHUB_TOKEN", ""))
    if gh.tok:
        issue = gh.find_open_issue(ISSUE_TITLE)
        if not issue:
            ok, issue = gh.call("POST", f"repos/{REPO}/issues", {
                "title": ISSUE_TITLE,
                "body": "Hier kommt jeden Montag der Kurzbericht mit den Kennzahlen der Reels als Kommentar an. "
                        "Die Dateien liegen unter v2/kennzahlen/ (Tabelle, Rohdaten, Verlauf als CSV)."})
            if not ok:
                print(f"Issue konnte nicht angelegt werden: {issue}")
                issue = None
        if issue:
            gh.call("POST", f"repos/{REPO}/issues/{issue['number']}/comments",
                    {"body": text + f"\n{OWNER_MENTION} Kurzbericht vom {stamp:%d.%m.%Y} (Datei: v2/kennzahlen/{day}.md)."})


if __name__ == "__main__":
    main()
