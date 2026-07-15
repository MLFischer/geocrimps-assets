#!/usr/bin/env python3
"""
GeoCrimps daily Instagram publisher.

Posts the first queue item with "published": false to the Instagram
account @geocrimps via the Instagram Graph API, then marks it published
in queue.json (the workflow commits the change back).

Secrets are read from environment variables (GitHub repo secrets):
  IG_USER_ID              Instagram Business/Creator account ID (numeric)
  IG_ACCESS_TOKEN         Long-lived Instagram access token (content publish)
  BLUESKY_HANDLE          (optional) Bluesky handle, e.g. geocrimps.bsky.social
  BLUESKY_APP_PASSWORD    (optional) Bluesky app password (Settings -> App Passwords)

If the two BLUESKY_* secrets are set, each post is also cross-posted to Bluesky
at the same time. Bluesky cross-posting is best-effort: a Bluesky failure is
logged as a warning but never breaks the Instagram pipeline.

Run modes:
  python publish.py            -> publish the next pending post
  python publish.py --dry-run  -> show what WOULD be posted, call nothing
  python publish.py --check    -> verify token/account works (GET only)
"""
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

# Instagram API with Instagram Login uses the graph.instagram.com host.
GRAPH = "https://graph.instagram.com/v21.0"
QUEUE_FILE = "queue.json"


def _get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _post(url, data):
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def _fail(msg):
    print(f"::error::{msg}")
    sys.exit(1)


# ---------------- Bluesky (AT Protocol) ----------------
BSKY = "https://bsky.social/xrpc"
BSKY_LIMIT = 300  # Bluesky limit is 300 graphemes; approximated with characters.


def _http_json(url, payload, headers=None):
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=hdrs, method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def bluesky_text(caption):
    """Fit the caption into Bluesky's ~300 char limit, filling the budget and
    cutting at the nearest sentence boundary (else a word boundary)."""
    text = caption.strip()
    if len(text) <= BSKY_LIMIT:
        return text
    budget = BSKY_LIMIT - 1  # leave room for the ellipsis
    cut = text[:budget]
    for sep in (". ", "! ", "? ", ".\n", "\n\n", "\n"):
        idx = cut.rfind(sep)
        if idx >= budget * 0.55:  # only if it keeps most of the budget
            return cut[: idx + 1].rstrip() + "…"
    idx = cut.rfind(" ")
    if idx > 0:
        cut = cut[:idx]
    return cut.rstrip() + "…"


def post_bluesky(image_path, text, alt):
    """Best-effort cross-post to Bluesky. Returns the post URI or None."""
    handle = os.environ.get("BLUESKY_HANDLE", "").strip()
    app_pw = os.environ.get("BLUESKY_APP_PASSWORD", "").strip()
    if not handle or not app_pw:
        print("Bluesky: BLUESKY_HANDLE/BLUESKY_APP_PASSWORD not set - skipping.")
        return None
    try:
        sess = _http_json(
            f"{BSKY}/com.atproto.server.createSession",
            {"identifier": handle, "password": app_pw},
        )
        jwt, did = sess["accessJwt"], sess["did"]
        with open(image_path, "rb") as f:
            blob_bytes = f.read()
        req = urllib.request.Request(
            f"{BSKY}/com.atproto.repo.uploadBlob",
            data=blob_bytes,
            headers={"Content-Type": "image/png", "Authorization": f"Bearer {jwt}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            blob = json.loads(r.read().decode("utf-8"))["blob"]
        record = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "langs": ["en"],
            "embed": {
                "$type": "app.bsky.embed.images",
                "images": [{"alt": alt, "image": blob}],
            },
        }
        res = _http_json(
            f"{BSKY}/com.atproto.repo.createRecord",
            {"repo": did, "collection": "app.bsky.feed.post", "record": record},
            {"Authorization": f"Bearer {jwt}"},
        )
        print(f"Bluesky: posted -> {res.get('uri')}")
        return res.get("uri")
    except urllib.error.HTTPError as e:
        print(f"::warning::Bluesky post failed: {e.read().decode('utf-8', 'ignore')}")
    except Exception as e:  # best-effort: never break the Instagram pipeline
        print(f"::warning::Bluesky post error: {e}")
    return None


def load_queue():
    with open(QUEUE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_queue(q):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(q, f, ensure_ascii=False, indent=2)


def creds():
    uid = os.environ.get("IG_USER_ID", "").strip()
    tok = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not uid or not tok:
        _fail("IG_USER_ID and IG_ACCESS_TOKEN must be set as environment variables.")
    return uid, tok


def check():
    uid, tok = creds()
    try:
        info = _get(f"{GRAPH}/{uid}?fields=username,name&access_token={urllib.parse.quote(tok)}")
    except urllib.error.HTTPError as e:
        _fail(f"Token/account check failed: {e.read().decode('utf-8', 'ignore')}")
    print(f"OK - connected to IG account: @{info.get('username')} ({info.get('name')})")


def next_pending(q):
    for item in q["items"]:
        if not item.get("published"):
            return item
    return None


def publish():
    dry = "--dry-run" in sys.argv
    q = load_queue()
    item = next_pending(q)
    if not item:
        print("Nothing to publish - all queue items are marked published.")
        return
    image_url = q["image_base_url"] + item["image"]
    caption = item["caption"]
    print(f"Next post: #{item['post']} - {item['title']}")
    print(f"Image: {image_url}")
    if dry:
        print("--- DRY RUN, nothing sent ---")
        print(caption)
        print("\n--- Bluesky version (<=300 chars) ---")
        print(bluesky_text(caption))
        return

    uid, tok = creds()
    # 1) create media container
    try:
        container = _post(
            f"{GRAPH}/{uid}/media",
            {"image_url": image_url, "caption": caption, "access_token": tok},
        )
    except urllib.error.HTTPError as e:
        _fail(f"Container creation failed: {e.read().decode('utf-8', 'ignore')}")
    cid = container.get("id")
    if not cid:
        _fail(f"No creation id returned: {container}")
    print(f"Container created: {cid}")

    # 2) wait until the container is FINISHED (image fetched & processed)
    for attempt in range(10):
        time.sleep(5)
        st = _get(f"{GRAPH}/{cid}?fields=status_code,status&access_token={urllib.parse.quote(tok)}")
        code = st.get("status_code")
        print(f"  status: {code}")
        if code == "FINISHED":
            break
        if code == "ERROR":
            _fail(f"Container processing error: {st}")
    else:
        _fail("Container never reached FINISHED status.")

    # 3) publish
    try:
        result = _post(
            f"{GRAPH}/{uid}/media_publish",
            {"creation_id": cid, "access_token": tok},
        )
    except urllib.error.HTTPError as e:
        _fail(f"Publish failed: {e.read().decode('utf-8', 'ignore')}")
    media_id = result.get("id")
    print(f"Published! media id: {media_id}")

    # 3b) cross-post to Bluesky (best-effort; never blocks the IG pipeline).
    # item["image"] (e.g. "002.png") sits at the repo root, checked out by CI.
    bsky_uri = post_bluesky(item["image"], bluesky_text(caption), item.get("title", "GeoCrimps"))

    # 4) mark published and persist
    item["published"] = True
    item["published_at"] = time.strftime("%Y-%m-%d %H:%M %Z")
    item["media_id"] = media_id
    if bsky_uri:
        item["bluesky_uri"] = bsky_uri
    save_queue(q)
    print("queue.json updated.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        publish()
