"""Autopost — fresh content per cron run, no batches, no git state.

Run: python autopost.py <rebelz-ai|johnson-services>

Flow:
1. Query Meta for last post timestamp on FB + IG.
2. If last post was < MIN_HOURS_BETWEEN_POSTS ago, skip.
3. Derive deterministic rotation index from today's date.
4. Generate image (Gemini) + caption (Gemini) honouring CLAUDE.md iron rules.
5. Publish to FB page and IG account.

Env vars (required):
  {REBELZ|JOHNSON}_META_ACCESS_TOKEN (or META_ACCESS_TOKEN)
  {REBELZ|JOHNSON}_PAGE_ID
  {REBELZ|JOHNSON}_INSTAGRAM_ACCOUNT_ID
  GEMINI_API_KEY
"""

import os
import sys
import tempfile
import time
from datetime import date, datetime, timezone
from pathlib import Path

import requests

from caption_writer import write_caption
from creative_generator import generate_image

BRAND = sys.argv[1] if len(sys.argv) > 1 else None
if BRAND not in ("rebelz-ai", "johnson-services"):
    print("Usage: python autopost.py <rebelz-ai|johnson-services>")
    sys.exit(2)

BRAND_UPPER = "REBELZ" if BRAND == "rebelz-ai" else "JOHNSON"
TOKEN = os.environ.get(f"{BRAND_UPPER}_META_ACCESS_TOKEN") or os.environ.get("META_ACCESS_TOKEN", "")
PAGE_ID = os.environ.get(f"{BRAND_UPPER}_PAGE_ID", "")
IG_ID = os.environ.get(f"{BRAND_UPPER}_INSTAGRAM_ACCOUNT_ID", "")

if not (TOKEN and PAGE_ID and IG_ID):
    print(f"ERROR: missing env vars (TOKEN set={bool(TOKEN)}, PAGE_ID={PAGE_ID!r}, IG_ID={IG_ID!r})")
    sys.exit(1)

GRAPH = "https://graph.facebook.com/v21.0"
MIN_HOURS_BETWEEN_POSTS = 30  # every-2-days cadence that tolerates any post-time-of-day vs fixed daily cron

TELEGRAM_URL = "http://91.98.147.211:9090/send/telegram"
TELEGRAM_AUTH = "bf71c2011c1405018890ad934d2b6d3e16da728761dd1aaf6a38e42835a7da4d"
TELEGRAM_CHAT = "1051747418"


def notify(text: str) -> None:
    """Best-effort push to Clarence's Telegram. Never raises."""
    try:
        requests.post(
            TELEGRAM_URL,
            headers={"Authorization": f"Bearer {TELEGRAM_AUTH}", "Content-Type": "application/json"},
            json={"to": TELEGRAM_CHAT, "message": text},
            timeout=15,
        )
    except Exception as e:
        print(f"notify failed (non-fatal): {e}")

# Fixed reference date so post_index is stable across runs.
POST_INDEX_REF_DATE = date(2026, 4, 22)

ICPS = {
    "rebelz-ai": [
        "Trockenbauer", "Bodenleger", "Elektriker", "Abdichter",
        "Dachdecker", "Maler", "Fliesenleger",
    ],
    "johnson-services": [
        "Betreuer",
        "Erbgemeinschaften",
        "Studenten die umziehen",
        "Junge Familien die umziehen",
        "Kinder die die Wohnung ihrer Eltern auflösen",
    ],
}
CONTENT_TYPES = ["educational", "social_proof", "pain_point", "branded", "engagement"]


def get_page_token(page_id: str) -> str:
    r = requests.get(
        f"{GRAPH}/{page_id}",
        params={"fields": "access_token", "access_token": TOKEN},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def last_post_ts() -> datetime | None:
    """Return the most recent post time across FB + IG, or None."""
    page_token = get_page_token(PAGE_ID)
    times: list[datetime] = []

    fb = requests.get(
        f"{GRAPH}/{PAGE_ID}/posts",
        params={"fields": "created_time", "limit": 1, "access_token": page_token},
        timeout=30,
    )
    if fb.ok and fb.json().get("data"):
        t = fb.json()["data"][0]["created_time"].replace("+0000", "+00:00")
        times.append(datetime.fromisoformat(t))

    ig = requests.get(
        f"{GRAPH}/{IG_ID}/media",
        params={"fields": "timestamp", "limit": 1, "access_token": TOKEN},
        timeout=30,
    )
    if ig.ok and ig.json().get("data"):
        t = ig.json()["data"][0]["timestamp"].replace("+0000", "+00:00")
        times.append(datetime.fromisoformat(t))

    return max(times) if times else None


def publish_fb(page_token: str, image_path: Path, caption: str) -> dict:
    with open(image_path, "rb") as f:
        r = requests.post(
            f"{GRAPH}/{PAGE_ID}/photos",
            files={"source": (image_path.name, f, "image/png")},
            data={"message": caption, "access_token": page_token},
            timeout=120,
        )
    r.raise_for_status()
    return r.json()


def publish_ig(page_token: str, image_path: Path, caption: str) -> dict:
    # Upload unpublished to FB to obtain a public image URL for IG.
    with open(image_path, "rb") as f:
        r = requests.post(
            f"{GRAPH}/{PAGE_ID}/photos",
            files={"source": (image_path.name, f, "image/png")},
            data={"published": "false", "access_token": page_token},
            timeout=120,
        )
    r.raise_for_status()
    photo_id = r.json()["id"]

    r = requests.get(
        f"{GRAPH}/{photo_id}",
        params={"fields": "images", "access_token": page_token},
        timeout=30,
    )
    r.raise_for_status()
    image_url = r.json()["images"][0]["source"]

    r = requests.post(
        f"{GRAPH}/{IG_ID}/media",
        data={"image_url": image_url, "caption": caption, "access_token": TOKEN},
        timeout=60,
    )
    r.raise_for_status()
    container_id = r.json()["id"]

    time.sleep(5)
    r = requests.post(
        f"{GRAPH}/{IG_ID}/media_publish",
        data={"creation_id": container_id, "access_token": TOKEN},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def main() -> None:
    last = last_post_ts()
    now = datetime.now(timezone.utc)
    if last is not None:
        age_h = (now - last).total_seconds() / 3600
        if age_h < MIN_HOURS_BETWEEN_POSTS:
            print(f"[{BRAND}] SKIP — last post {age_h:.1f}h ago (< {MIN_HOURS_BETWEEN_POSTS}h)")
            notify(f"⏭ {BRAND} skip — last post {age_h:.1f}h ago (waiting for {MIN_HOURS_BETWEEN_POSTS}h)")
            return
        print(f"[{BRAND}] Last post {age_h:.1f}h ago — proceeding.")
    else:
        print(f"[{BRAND}] No prior posts found — proceeding.")

    days = (date.today() - POST_INDEX_REF_DATE).days
    post_index = max(1, (days // 2) + 1)
    icps = ICPS[BRAND]
    audience = icps[(post_index - 1) % len(icps)]
    content_type = CONTENT_TYPES[(post_index - 1) % len(CONTENT_TYPES)]
    print(f"[{BRAND}] post_index={post_index} audience={audience!r} content={content_type!r}")

    with tempfile.TemporaryDirectory() as tmp:
        img = Path(tmp) / "post.png"
        print(f"[{BRAND}] Generating image via Gemini...")
        ok = generate_image(
            brand=BRAND,
            platform="ig",  # IG format (1080x1080 / 1080x1350) displays fine on FB too
            content_type=content_type,
            target_audience=audience,
            post_index=post_index,
            output_path=img,
        )
        if not ok or not img.exists() or img.stat().st_size == 0:
            print(f"[{BRAND}] ERROR: image generation failed")
            sys.exit(1)
        print(f"[{BRAND}] Image OK ({img.stat().st_size} bytes)")

        print(f"[{BRAND}] Generating captions...")
        fb_caption = write_caption(BRAND, "fb", content_type, audience, post_index)
        ig_caption = write_caption(BRAND, "ig", content_type, audience, post_index)
        print(f"[{BRAND}] Captions OK ({len(fb_caption)} fb, {len(ig_caption)} ig chars)")

        page_token = get_page_token(PAGE_ID)

        print(f"[{BRAND}] Publishing to Facebook...")
        fb_res = publish_fb(page_token, img, fb_caption)
        print(f"[{BRAND}] FB published: {fb_res}")

        print(f"[{BRAND}] Publishing to Instagram...")
        ig_res = publish_ig(page_token, img, ig_caption)
        print(f"[{BRAND}] IG published: {ig_res}")

    print(f"\n[{BRAND}] SUCCESS fb_post_id={fb_res.get('post_id')} ig_media_id={ig_res.get('id')}")
    notify(
        f"✅ {BRAND} posted to FB+IG\n"
        f"audience: {audience}\n"
        f"content: {content_type}\n"
        f"fb: {fb_res.get('post_id')}\n"
        f"ig: {ig_res.get('id')}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(tb)
        notify(f"❌ {BRAND} autopost FAILED\n{type(e).__name__}: {e}\n\n{tb[-1500:]}")
        raise
