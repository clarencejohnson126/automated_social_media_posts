"""Publish today's scheduled posts. Called by RemoteTrigger daily."""

import json
import os
import sys
import subprocess
import time
from datetime import date
from pathlib import Path

import requests

# RemoteTrigger passes brand as first argument
BRAND = sys.argv[1] if len(sys.argv) > 1 else None
if BRAND not in ("rebelz-ai", "johnson-services"):
    print(f"Usage: python publish_today.py <rebelz-ai|johnson-services>")
    sys.exit(1)

META_ACCESS_TOKEN = os.environ.get(
    f"{'REBELZ' if BRAND == 'rebelz-ai' else 'JOHNSON'}_META_ACCESS_TOKEN",
    os.environ.get("META_ACCESS_TOKEN", ""),
)
GRAPH_API = "https://graph.facebook.com/v21.0"

BRAND_CONFIG = {
    "rebelz-ai": {
        "page_id": os.environ.get("REBELZ_PAGE_ID", "708377165697175"),
        "instagram_id": os.environ.get("REBELZ_INSTAGRAM_ACCOUNT_ID", "17841469414036451"),
    },
    "johnson-services": {
        "page_id": os.environ.get("JOHNSON_PAGE_ID", "333849409814429"),
        "instagram_id": os.environ.get("JOHNSON_INSTAGRAM_ACCOUNT_ID", "17841458145133488"),
    },
}


def find_current_batch() -> Path | None:
    """Find the most recent batch directory."""
    batches_dir = Path("batches")
    if not batches_dir.exists():
        return None
    dirs = sorted(batches_dir.iterdir(), reverse=True)
    for d in dirs:
        if d.is_dir() and (d / "manifest.json").exists():
            return d
    return None


def main():
    today_str = date.today().isoformat()
    config = BRAND_CONFIG[BRAND]
    print(f"Publishing {BRAND} posts for {today_str}")

    batch_dir = find_current_batch()
    if not batch_dir:
        print("No batch found. Skipping.")
        return

    manifest = json.loads((batch_dir / "manifest.json").read_text())
    published_any = False

    for account_key, posts in manifest["accounts"].items():
        if not account_key.startswith(BRAND):
            continue

        for post in posts:
            # Publish any unpublished post whose scheduled_date is today or in the past
            # (backlog catch-up mode — guarantees missed days get published on the next run)
            if post["scheduled_date"] > today_str:
                continue
            if not post["approved"]:
                print(f"  SKIP {account_key} post {post['index']}: not approved")
                continue
            if post["published"]:
                continue  # silent skip — backlog scan hits a lot of these
            if not post["file_path"]:
                print(f"  SKIP {account_key} post {post['index']}: no media file")
                continue

            media_path = batch_dir / post["file_path"]
            if not media_path.exists():
                print(f"  ERROR {account_key} post {post['index']}: file not found: {media_path}")
                continue

            caption = post["caption"] or ""
            platform = post["platform"]
            page_id = config["page_id"]
            ig_id = config["instagram_id"]

            # Get page access token
            resp = requests.get(
                f"{GRAPH_API}/{page_id}",
                params={"fields": "access_token", "access_token": META_ACCESS_TOKEN},
            )
            resp.raise_for_status()
            page_token = resp.json()["access_token"]

            if platform == "fb":
                # Publish to Facebook
                if post["media_type"] == "video":
                    with open(media_path, "rb") as f:
                        resp = requests.post(
                            f"{GRAPH_API}/{page_id}/videos",
                            files={"source": (media_path.name, f, "video/mp4")},
                            data={"description": caption, "access_token": page_token},
                        )
                else:
                    with open(media_path, "rb") as f:
                        resp = requests.post(
                            f"{GRAPH_API}/{page_id}/photos",
                            files={"source": (media_path.name, f, "image/png")},
                            data={"message": caption, "access_token": page_token},
                        )
                resp.raise_for_status()
                print(f"  PUBLISHED {account_key} post {post['index']} to Facebook: {resp.json()}")

            elif platform == "ig" and ig_id:
                if post["media_type"] == "video":
                    # IG video via jsdelivr CDN (repo is public on GitHub)
                    repo_path = f"batches/{batch_dir.name}/{post['file_path']}"
                    video_url = (
                        "https://cdn.jsdelivr.net/gh/clarencejohnson126/"
                        f"automated_social_media_posts@main/{repo_path}"
                    )
                    # Create REELS container
                    resp = requests.post(
                        f"{GRAPH_API}/{ig_id}/media",
                        data={
                            "media_type": "REELS",
                            "video_url": video_url,
                            "caption": caption,
                            "access_token": META_ACCESS_TOKEN,
                        },
                    )
                    resp.raise_for_status()
                    container_id = resp.json()["id"]
                    # Poll container status until FINISHED (videos take time to process)
                    for _ in range(30):
                        time.sleep(5)
                        s = requests.get(
                            f"{GRAPH_API}/{container_id}",
                            params={"fields": "status_code", "access_token": META_ACCESS_TOKEN},
                        ).json()
                        if s.get("status_code") == "FINISHED":
                            break
                        if s.get("status_code") == "ERROR":
                            raise RuntimeError(f"IG video container error: {s}")
                    resp = requests.post(
                        f"{GRAPH_API}/{ig_id}/media_publish",
                        data={"creation_id": container_id, "access_token": META_ACCESS_TOKEN},
                    )
                    resp.raise_for_status()
                    print(f"  PUBLISHED {account_key} post {post['index']} to Instagram (video): {resp.json()}")
                else:
                    # Image: upload to FB as unpublished to get a public URL, then publish on IG
                    with open(media_path, "rb") as f:
                        resp = requests.post(
                            f"{GRAPH_API}/{page_id}/photos",
                            files={"source": (media_path.name, f, "image/png")},
                            data={"published": "false", "access_token": page_token},
                        )
                    resp.raise_for_status()
                    photo_id = resp.json()["id"]

                    resp = requests.get(
                        f"{GRAPH_API}/{photo_id}",
                        params={"fields": "images", "access_token": page_token},
                    )
                    resp.raise_for_status()
                    image_url = resp.json()["images"][0]["source"]

                    resp = requests.post(
                        f"{GRAPH_API}/{ig_id}/media",
                        data={"image_url": image_url, "caption": caption, "access_token": META_ACCESS_TOKEN},
                    )
                    resp.raise_for_status()
                    container_id = resp.json()["id"]

                    time.sleep(5)
                    resp = requests.post(
                        f"{GRAPH_API}/{ig_id}/media_publish",
                        data={"creation_id": container_id, "access_token": META_ACCESS_TOKEN},
                    )
                    resp.raise_for_status()
                    print(f"  PUBLISHED {account_key} post {post['index']} to Instagram (image): {resp.json()}")

            post["published"] = True
            published_any = True

    # Save updated manifest and push
    if published_any:
        (batch_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False)
        )
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"mark {BRAND} posts published for {today_str}"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
        print("Manifest updated and pushed.")
    else:
        print("No posts to publish today.")


if __name__ == "__main__":
    main()
