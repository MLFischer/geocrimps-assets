#!/usr/bin/env python3
"""
GeoCrimps daily Instagram publisher.

Posts the first queue item with "published": false to the Instagram
account @geocrimps via the Instagram Graph API, then marks it published
in queue.json (the workflow commits the change back).

Secrets are read from environment variables (GitHub repo secrets):
  IG_USER_ID       Instagram Business/Creator account ID (numeric)
  IG_ACCESS_TOKEN  Long-lived Page access token with instagram_content_publish

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

GRAPH = "https://graph.facebook.com/v21.0"
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

    # 4) mark published and persist
    item["published"] = True
    item["published_at"] = time.strftime("%Y-%m-%d %H:%M %Z")
    item["media_id"] = media_id
    save_queue(q)
    print("queue.json updated.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        publish()
