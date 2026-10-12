#!/usr/bin/env python3
"""
GeoCrimps daily publisher — Instagram + Bluesky, independently.

Supports single-image posts AND carousels: if an item has an "images" list, it is
published as an Instagram carousel (children + carousel container) and a Bluesky
multi-image post (max 4). Items with only "image" keep the old single-image path.

Each platform advances on its own: a failure on one (e.g. Instagram temporarily
blocking API access) never stops the other. Per-platform progress is tracked in
queue.json via `published_ig` and `published_bsky`. The workflow commits the
updated queue even when the run is flagged as failed (if: always()), so a
platform that DID succeed is never re-posted.

Secrets (GitHub repo secrets, read from the environment):
  IG_USER_ID              Instagram Business/Creator account ID (numeric)
  IG_ACCESS_TOKEN         Long-lived Instagram access token (content publish)
  BLUESKY_HANDLE          Bluesky handle, e.g. geocrimps.bsky.social
  BLUESKY_APP_PASSWORD    Bluesky app password (Settings -> App Passwords)

Run modes:
  python publish.py                 -> publish the next pending post per platform
  python publish.py --dry-run       -> show what WOULD be posted, call nothing
  python publish.py --check         -> verify the IG token/account works (GET only)
  python publish.py --bluesky 1,2   -> post the given posts to Bluesky ONLY
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
        raise RuntimeError("IG_USER_ID and IG_ACCESS_TOKEN must be set as environment variables.")
    return uid, tok


def media_list(item):
    """Image filenames for an item, carousel-aware. `images` (list) wins over `image`."""
    imgs = item.get("images")
    if imgs:
        return list(imgs)
    return [item["image"]]


# ---------------- Instagram ----------------
def _wait_finished(cid, tok):
    """Poll a media container until it reaches FINISHED, or raise."""
    for _ in range(10):
        time.sleep(5)
        st = _get(f"{GRAPH}/{cid}?fields=status_code,status&access_token={urllib.parse.quote(tok)}")
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code == "ERROR":
            raise RuntimeError(f"container processing error: {st}")
    raise RuntimeError("container never reached FINISHED status")


def _ig_child(uid, tok, image_url):
    """Create one carousel child container (no caption). Returns its id."""
    try:
        child = _post(
            f"{GRAPH}/{uid}/media",
            {"image_url": image_url, "is_carousel_item": "true", "access_token": tok},
        )
    except urllib.error.HTTPError as e:
        raise RuntimeError("child container: " + e.read().decode("utf-8", "ignore"))
    cid = child.get("id")
    if not cid:
        raise RuntimeError(f"no child id returned: {child}")
    return cid


def ig_publish(item, base):
    """Create the media container(s), wait for processing, publish. Single image or
    carousel depending on item['images']. Returns the published media id or raises."""
    uid, tok = creds()
    imgs = media_list(item)

    if len(imgs) == 1:
        try:
            container = _post(
                f"{GRAPH}/{uid}/media",
                {"image_url": base + imgs[0], "caption": item["caption"], "access_token": tok},
            )
        except urllib.error.HTTPError as e:
            raise RuntimeError("container creation: " + e.read().decode("utf-8", "ignore"))
        parent_id = container.get("id")
        if not parent_id:
            raise RuntimeError(f"no creation id returned: {container}")
        _wait_finished(parent_id, tok)
    else:
        child_ids = [_ig_child(uid, tok, base + fn) for fn in imgs]
        for ccid in child_ids:
            _wait_finished(ccid, tok)
        try:
            parent = _post(
                f"{GRAPH}/{uid}/media",
                {
                    "media_type": "CAROUSEL",
                    "children": ",".join(child_ids),
                    "caption": item["caption"],
                    "access_token": tok,
                },
            )
        except urllib.error.HTTPError as e:
            raise RuntimeError("carousel container: " + e.read().decode("utf-8", "ignore"))
        parent_id = parent.get("id")
        if not parent_id:
            raise RuntimeError(f"no carousel id returned: {parent}")
        _wait_finished(parent_id, tok)

    try:
        result = _post(
            f"{GRAPH}/{uid}/media_publish",
            {"creation_id": parent_id, "access_token": tok},
        )
    except urllib.error.HTTPError as e:
        raise RuntimeError("publish: " + e.read().decode("utf-8", "ignore"))
    mid = result.get("id")
    if not mid:
        raise RuntimeError(f"no media id returned: {result}")
    return mid


def check():
    try:
        uid, tok = creds()
        info = _get(f"{GRAPH}/{uid}?fields=username,name&access_token={urllib.parse.quote(tok)}")
    except (RuntimeError, urllib.error.HTTPError) as e:
        detail = e.read().decode("utf-8", "ignore") if isinstance(e, urllib.error.HTTPError) else str(e)
        _fail(f"Token/account check failed: {detail}")
    print(f"OK - connected to IG account: @{info.get('username')} ({info.get('name')})")


# ---------------- Bluesky (AT Protocol) ----------------
BSKY = "https://bsky.social/xrpc"
BSKY_LIMIT = 300  # Bluesky limit is 300 graphemes; approximated with characters.
BSKY_MAX_IMAGES = 4


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


def post_bluesky(image_paths, text, alt):
    """Post one crimp to Bluesky (1-4 images). Returns the post URI, or None on failure."""
    handle = os.environ.get("BLUESKY_HANDLE", "").strip()
    app_pw = os.environ.get("BLUESKY_APP_PASSWORD", "").strip()
    if not handle or not app_pw:
        print("Bluesky: BLUESKY_HANDLE/BLUESKY_APP_PASSWORD not set - skipping.")
        return None
    if isinstance(image_paths, str):
        image_paths = [image_paths]
    image_paths = image_paths[:BSKY_MAX_IMAGES]
    try:
        sess = _http_json(
            f"{BSKY}/com.atproto.server.createSession",
            {"identifier": handle, "password": app_pw},
        )
        jwt, did = sess["accessJwt"], sess["did"]
        images_embed = []
        for idx, path in enumerate(image_paths, start=1):
            with open(path, "rb") as f:
                blob_bytes = f.read()
            req = urllib.request.Request(
                f"{BSKY}/com.atproto.repo.uploadBlob",
                data=blob_bytes,
                headers={"Content-Type": "image/png", "Authorization": f"Bearer {jwt}"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                blob = json.loads(r.read().decode("utf-8"))["blob"]
            slide_alt = alt if len(image_paths) == 1 else f"{alt} (slide {idx})"
            images_embed.append({"alt": slide_alt, "image": blob})
        record = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "langs": ["en"],
            "embed": {
                "$type": "app.bsky.embed.images",
                "images": images_embed,
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
    except Exception as e:
        print(f"::warning::Bluesky post error: {e}")
    return None


# ---------------- per-platform progress ----------------
def ig_done(it):
    # fall back to the legacy `published` flag for items created before per-platform tracking
    return bool(it.get("published_ig", it.get("published")))


def bsky_done(it):
    return bool(it.get("published_bsky"))


def next_for(q, done_fn):
    for it in q["items"]:
        if not done_fn(it):
            return it
    return None


def publish():
    dry = "--dry-run" in sys.argv
    q = load_queue()
    base = q.get("image_base_url", "")
    ig_item = next_for(q, ig_done)
    bsky_item = next_for(q, bsky_done)

    if not ig_item and not bsky_item:
        print("Nothing to publish - all items done on both platforms.")
        return

    if dry:
        print("--- DRY RUN, nothing sent ---")
        if ig_item:
            print(f"Instagram next: #{ig_item['post']} - {ig_item['title']} ({len(media_list(ig_item))} img)")
        if bsky_item:
            print(f"Bluesky next:   #{bsky_item['post']} - {bsky_item['title']} ({len(media_list(bsky_item))} img)")
            print("--- Bluesky text ---")
            print(bluesky_text(bsky_item["caption"]))
        return

    failures = []

    # --- Instagram (independent) ---
    if ig_item:
        try:
            mid = ig_publish(ig_item, base)
            ig_item["published_ig"] = True
            ig_item["published"] = True  # legacy compat
            ig_item["media_id"] = mid
            if not ig_item.get("published_at"):
                ig_item["published_at"] = time.strftime("%Y-%m-%d %H:%M %Z")
            print(f"Instagram: published #{ig_item['post']} (media {mid})")
        except Exception as e:
            failures.append(f"Instagram #{ig_item['post']}: {e}")
            print(f"::warning::Instagram failed for #{ig_item['post']}: {e}")

    # --- Bluesky (independent) ---
    if bsky_item:
        uri = post_bluesky(
            media_list(bsky_item), bluesky_text(bsky_item["caption"]), bsky_item.get("title", "GeoCrimps")
        )
        if uri:
            bsky_item["published_bsky"] = True
            bsky_item["bluesky_uri"] = uri
            print(f"Bluesky: published #{bsky_item['post']}")
        else:
            failures.append(f"Bluesky #{bsky_item['post']}")

    save_queue(q)
    print("queue.json updated.")

    if failures:
        # Exit non-zero so the run is flagged (and the maintainer is notified),
        # but the queue is already saved and committed by the workflow's
        # `if: always()` step, so the platform that succeeded is not re-posted.
        _fail("Some platforms failed: " + " | ".join(failures))


def backfill_bluesky(ids):
    """Post the given posts (by number) to Bluesky ONLY - no Instagram. Marks
    published_bsky=true and saves the queue so the daily run won't re-post them."""
    q = load_queue()
    by_id = {it["post"]: it for it in q["items"]}
    ok = True
    for pid in ids:
        pid = pid.strip().zfill(3)
        it = by_id.get(pid)
        if not it:
            print(f"::warning::post {pid} not found in queue")
            ok = False
            continue
        uri = post_bluesky(media_list(it), bluesky_text(it["caption"]), it.get("title", "GeoCrimps"))
        if uri:
            it["published_bsky"] = True
            it["bluesky_uri"] = uri
            print(f"#{pid} posted to Bluesky: {uri}")
        else:
            print(f"::error::Bluesky post for #{pid} failed")
            ok = False
    save_queue(q)
    print("queue.json updated.")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    if "--bluesky" in sys.argv:
        i = sys.argv.index("--bluesky")
        ids = sys.argv[i + 1].split(",") if len(sys.argv) > i + 1 else []
        backfill_bluesky(ids)
    elif "--check" in sys.argv:
        check()
    else:
        publish()
