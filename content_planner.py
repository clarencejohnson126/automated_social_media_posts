"""Content planner — decides what to post, when, and for whom."""

from datetime import date, timedelta
from config import BRANDS, CONTENT_TYPES, POSTS_PER_BATCH, POST_INTERVAL_DAYS


def plan_batch(start_date: date) -> dict[str, list[dict]]:
    """Plan a 2-week batch of posts for all 4 accounts.

    Returns dict keyed by account slug (e.g. 'rebelz-ai-ig')
    with list of 7 post plans each.
    """
    batch = {}

    for brand_key, brand in BRANDS.items():
        for platform in ("ig", "fb"):
            account_key = f"{brand_key}-{platform}"
            posts = []

            for i in range(POSTS_PER_BATCH):
                post_date = start_date + timedelta(days=i * POST_INTERVAL_DAYS)
                content_type = CONTENT_TYPES[i % len(CONTENT_TYPES)]

                # Rotate target audience
                if "icps" in brand:
                    audience = brand["icps"][i % len(brand["icps"])]
                else:
                    audience = brand["trades"][i % len(brand["trades"])]

                # Last post in batch is video, rest are images
                media_type = "video" if i == POSTS_PER_BATCH - 1 else "image"

                fmt = brand["formats"]["instagram" if platform == "ig" else "facebook"]

                posts.append({
                    "index": i + 1,
                    "scheduled_date": post_date.isoformat(),
                    "content_type": content_type["id"],
                    "content_label": content_type["label"],
                    "target_audience": audience,
                    "media_type": media_type,
                    "width": fmt["width"],
                    "height": fmt["height"],
                    "style": fmt["style"],
                    "brand": brand_key,
                    "platform": platform,
                    "approved": False,
                    "published": False,
                    "file_path": None,
                    "caption": None,
                })

            batch[account_key] = posts

    return batch
