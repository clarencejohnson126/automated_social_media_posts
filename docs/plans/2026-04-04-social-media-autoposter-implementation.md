# Social Media Auto-Poster — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automated social media posting every 2 days across 4 accounts (Rebelz AI IG+FB, Johnson Services IG+FB) with bi-weekly batch generation, approval flow, and cloud publishing via RemoteTrigger.

**Architecture:** Local Python modules generate content batches (Gemini images + Remotion video + German captions). Clarence approves in Claude Code. Approved batches pushed to GitHub. Two RemoteTrigger cron jobs on Anthropic's cloud clone the repo daily and publish the next scheduled post via Meta Graph API.

**Tech Stack:** Python 3, google-genai (Gemini), facebook-business SDK, Remotion (Node.js), wacli (WhatsApp), GitHub, RemoteTrigger (Anthropic cloud)

---

### Task 1: Project Setup & Config

**Files:**
- Create: `config.py`
- Create: `requirements.txt`
- Modify: `.env` (already exists)

**Step 1: Create requirements.txt**

```
google-genai>=1.0.0
facebook-business>=21.0.0
python-dotenv>=1.0.0
pydantic-settings>=2.2.0
httpx>=0.27.0
Pillow>=10.0.0
```

**Step 2: Create config.py**

```python
"""Settings for Automated Social Media posting."""

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# --- Meta API ---
META_APP_ID = os.getenv("META_APP_ID", "")
META_APP_SECRET = os.getenv("META_APP_SECRET", "")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")

# --- Rebelz AI ---
REBELZ_PAGE_ID = os.getenv("REBELZ_PAGE_ID", "")
REBELZ_INSTAGRAM_ID = os.getenv("REBELZ_INSTAGRAM_ACCOUNT_ID", "")

# --- Johnson Services ---
JOHNSON_PAGE_ID = os.getenv("JOHNSON_PAGE_ID", "")
JOHNSON_INSTAGRAM_ID = os.getenv("JOHNSON_INSTAGRAM_ACCOUNT_ID", "")

# --- Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --- WhatsApp ---
WHATSAPP_RECIPIENT = os.getenv("WHATSAPP_RECIPIENT", "491621811123")
WACLI_BIN = "/opt/homebrew/bin/wacli"

# --- Business Info ---
REBELZ_WEBSITE = os.getenv("REBELZ_WEBSITE", "https://www.rebelzai.com")
JOHNSON_WEBSITE = os.getenv("JOHNSON_WEBSITE", "https://www.johnson-services.de")
JOHNSON_WHATSAPP = os.getenv("JOHNSON_WHATSAPP", "+491621811123")

# --- Paths ---
BATCHES_DIR = PROJECT_ROOT / "batches"

# --- Posting Schedule ---
POST_INTERVAL_DAYS = 2
POSTS_PER_BATCH = 7  # 7 posts per account per 2-week batch
IMAGES_PER_BATCH = 6
VIDEOS_PER_BATCH = 1

# --- Brand Config ---
BRANDS = {
    "rebelz-ai": {
        "name": "Rebelz AI",
        "page_id": REBELZ_PAGE_ID,
        "instagram_id": REBELZ_INSTAGRAM_ID,
        "post_time_berlin": "19:00",
        "website": REBELZ_WEBSITE,
        "niche": "Handwerk & Bau",
        "trades": [
            "Trockenbauer", "Bodenleger", "Elektriker",
            "Abdichter", "Dachdecker", "Maler", "Fliesenleger",
        ],
        "formats": {
            "instagram": {
                "width": 1080, "height": 1080,
                "style": "square, bold Bauhaus-inspired, heavy branding",
            },
            "facebook": {
                "width": 1200, "height": 630,
                "style": "landscape, text overlay, article/tip style",
            },
        },
        "colors": {"primary": "#000000", "secondary": "#FFFFFF"},
        "font": "Playfair Display",
        "tone": "Direct, pain-point-first, formal German (Ihr-Form)",
    },
    "johnson-services": {
        "name": "Johnson Services",
        "page_id": JOHNSON_PAGE_ID,
        "instagram_id": JOHNSON_INSTAGRAM_ID,
        "post_time_berlin": "09:00",
        "website": JOHNSON_WEBSITE,
        "whatsapp": JOHNSON_WHATSAPP,
        "niche": "Entrümpelung & Umzüge",
        "icps": [
            "Betreuer",
            "Erbgemeinschaften",
            "Studenten die umziehen",
            "Junge Familien die umziehen",
            "Kinder die die Wohnung ihrer Eltern auflösen",
        ],
        "formats": {
            "instagram": {
                "width": 1080, "height": 1350,
                "style": "vertical, lifestyle/emotional imagery, clean modern look",
            },
            "facebook": {
                "width": 1200, "height": 630,
                "style": "landscape, before/after or testimonial format",
            },
        },
        "colors": {"primary": "#005b8c", "secondary": "#FFFFFF", "accent": "#9DFF20"},
        "font": "DM Sans",
        "tone": "Empathetic, trustworthy — Zuverlässig, Sauber, Günstig",
    },
}

CONTENT_TYPES = [
    {"id": "educational", "label": "Wussten Sie schon?", "desc": "Tips, industry insights"},
    {"id": "social_proof", "label": "Kundenerfolg", "desc": "Before/after, testimonials"},
    {"id": "pain_point", "label": "Schmerzpunkt", "desc": "Specific relatable problems"},
    {"id": "branded", "label": "Über uns", "desc": "Company updates, team, behind-the-scenes"},
    {"id": "engagement", "label": "Mitmachen", "desc": "Questions, polls, seasonal content"},
]
```

**Step 3: Install dependencies**

Run: `cd "/Users/clarence/Desktop/AUTOMATED ADS/Automated Social Media" && pip install -r requirements.txt`

**Step 4: Initialize git and push**

Run:
```bash
cd "/Users/clarence/Desktop/AUTOMATED ADS/Automated Social Media"
git init
git remote add origin https://github.com/clarencejohnson126/automated_social_media_posts.git
git add config.py requirements.txt .gitignore docs/
git commit -m "feat: project setup with config, requirements, and design docs"
git branch -M main
git push -u origin main
```

---

### Task 2: Content Planner

**Files:**
- Create: `content_planner.py`
- Create: `tests/test_content_planner.py`

**Step 1: Write the failing test**

```python
"""Tests for content_planner."""

import json
from datetime import date
from content_planner import plan_batch


def test_plan_batch_returns_28_posts():
    batch = plan_batch(start_date=date(2026, 4, 18))
    all_posts = []
    for account_key, posts in batch.items():
        all_posts.extend(posts)
    assert len(all_posts) == 28  # 7 per account × 4 accounts


def test_plan_batch_has_correct_accounts():
    batch = plan_batch(start_date=date(2026, 4, 18))
    assert set(batch.keys()) == {
        "rebelz-ai-ig", "rebelz-ai-fb",
        "johnson-services-ig", "johnson-services-fb",
    }


def test_each_account_has_7_posts():
    batch = plan_batch(start_date=date(2026, 4, 18))
    for account_key, posts in batch.items():
        assert len(posts) == 7, f"{account_key} has {len(posts)} posts, expected 7"


def test_posts_have_correct_dates():
    batch = plan_batch(start_date=date(2026, 4, 18))
    for account_key, posts in batch.items():
        dates = [p["scheduled_date"] for p in posts]
        expected = ["2026-04-18", "2026-04-20", "2026-04-22", "2026-04-24",
                    "2026-04-26", "2026-04-28", "2026-04-30"]
        assert dates == expected


def test_one_video_per_account():
    batch = plan_batch(start_date=date(2026, 4, 18))
    for account_key, posts in batch.items():
        videos = [p for p in posts if p["media_type"] == "video"]
        assert len(videos) == 1, f"{account_key} has {len(videos)} videos"


def test_johnson_rotates_icps():
    batch = plan_batch(start_date=date(2026, 4, 18))
    icps = [p["target_audience"] for p in batch["johnson-services-ig"]]
    # Should have variety, not all the same
    assert len(set(icps)) >= 3


def test_rebelz_rotates_trades():
    batch = plan_batch(start_date=date(2026, 4, 18))
    trades = [p["target_audience"] for p in batch["rebelz-ai-ig"]]
    assert len(set(trades)) >= 3
```

**Step 2: Run test to verify it fails**

Run: `cd "/Users/clarence/Desktop/AUTOMATED ADS/Automated Social Media" && python -m pytest tests/test_content_planner.py -v`
Expected: FAIL (module not found)

**Step 3: Write the implementation**

```python
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
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_content_planner.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add content_planner.py tests/test_content_planner.py
git commit -m "feat: content planner with ICP/trade rotation and scheduling"
```

---

### Task 3: Caption Writer

**Files:**
- Create: `caption_writer.py`
- Create: `tests/test_caption_writer.py`

**Step 1: Write the failing test**

```python
"""Tests for caption_writer."""

from caption_writer import write_caption


def test_caption_is_german():
    caption = write_caption(
        brand="rebelz-ai",
        platform="ig",
        content_type="educational",
        target_audience="Trockenbauer",
    )
    assert isinstance(caption, str)
    assert len(caption) > 20
    # Should not contain common English words
    for word in ["the", "and", "with", "your"]:
        assert word.lower() not in caption.lower().split()


def test_caption_has_hashtags():
    caption = write_caption(
        brand="johnson-services",
        platform="fb",
        content_type="social_proof",
        target_audience="Betreuer",
    )
    assert "#" in caption


def test_caption_has_cta():
    caption = write_caption(
        brand="johnson-services",
        platform="ig",
        content_type="pain_point",
        target_audience="Studenten die umziehen",
    )
    # Should have some call to action
    assert any(kw in caption.lower() for kw in [
        "kontakt", "anruf", "nachricht", "whatsapp", "link", "bio", "jetzt",
    ])
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_caption_writer.py -v`
Expected: FAIL

**Step 3: Write the implementation**

```python
"""Caption writer — generates German social media captions using Gemini."""

import os
from google import genai
from google.genai import types
from config import BRANDS, GEMINI_API_KEY


def _get_client():
    return genai.Client(api_key=GEMINI_API_KEY)


def write_caption(
    brand: str,
    platform: str,
    content_type: str,
    target_audience: str,
) -> str:
    """Generate a German caption for a social media post.

    Args:
        brand: 'rebelz-ai' or 'johnson-services'
        platform: 'ig' or 'fb'
        content_type: one of educational, social_proof, pain_point, branded, engagement
        target_audience: specific ICP or trade name
    """
    brand_config = BRANDS[brand]
    platform_name = "Instagram" if platform == "ig" else "Facebook"

    prompt = f"""Du bist ein deutscher Social-Media-Texter für {brand_config['name']}.
Branche: {brand_config['niche']}
Tonalität: {brand_config['tone']}
Zielgruppe: {target_audience}
Plattform: {platform_name}
Inhaltstyp: {content_type}

Schreibe einen {platform_name}-Post auf Deutsch. KEIN einziges englisches Wort.

Regeln:
- Maximal 150 Wörter für Instagram, 200 Wörter für Facebook
- Beginne mit einem aufmerksamkeitsstarken ersten Satz
- Füge 3-5 relevante deutsche Hashtags am Ende hinzu
- Füge einen Call-to-Action ein (z.B. "Jetzt Kontakt aufnehmen", "Link in Bio", "Schreiben Sie uns")
- {"Nutze Du-Form" if platform == "ig" else "Nutze Sie-Form"}
- Für Johnson Services: Erwähne WhatsApp-Kontakt oder Website johnson-services.de
- Für Rebelz AI: Erwähne kostenlose Erstberatung oder rebelzai.com

Gib NUR den fertigen Post-Text zurück, keine Erklärungen."""

    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text.strip()


def write_captions_for_batch(batch: dict) -> dict:
    """Generate captions for all posts in a batch."""
    import time

    for account_key, posts in batch.items():
        for post in posts:
            if post["caption"] is not None:
                continue
            caption = write_caption(
                brand=post["brand"],
                platform=post["platform"],
                content_type=post["content_type"],
                target_audience=post["target_audience"],
            )
            post["caption"] = caption
            time.sleep(1)  # Rate limit

    return batch
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_caption_writer.py -v`
Expected: ALL PASS (requires GEMINI_API_KEY in .env)

**Step 5: Commit**

```bash
git add caption_writer.py tests/test_caption_writer.py
git commit -m "feat: German caption writer using Gemini"
```

---

### Task 4: Creative Generator (Gemini Images)

**Files:**
- Create: `creative_generator.py`
- Create: `tests/test_creative_generator.py`

**Step 1: Write the failing test**

```python
"""Tests for creative_generator."""

from pathlib import Path
from unittest.mock import patch, MagicMock
from creative_generator import build_image_prompt, generate_image


def test_build_prompt_rebelz_ig():
    prompt = build_image_prompt(
        brand="rebelz-ai",
        platform="ig",
        content_type="educational",
        target_audience="Trockenbauer",
    )
    assert "1080" in prompt
    assert "schwarz" in prompt.lower() or "black" in prompt.lower() or "weiß" in prompt.lower()
    assert "Playfair" in prompt
    assert "Trockenbauer" in prompt


def test_build_prompt_johnson_ig():
    prompt = build_image_prompt(
        brand="johnson-services",
        platform="ig",
        content_type="social_proof",
        target_audience="Betreuer",
    )
    assert "1080" in prompt and "1350" in prompt
    assert "005b8c" in prompt.lower() or "blau" in prompt.lower()
    assert "DM Sans" in prompt


def test_build_prompt_johnson_fb():
    prompt = build_image_prompt(
        brand="johnson-services",
        platform="fb",
        content_type="pain_point",
        target_audience="Erbgemeinschaften",
    )
    assert "1200" in prompt and "630" in prompt
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_creative_generator.py -v`
Expected: FAIL

**Step 3: Write the implementation**

```python
"""Creative generator — Gemini image generation with brand-specific prompts."""

import time
from pathlib import Path
from google import genai
from google.genai import types
from config import BRANDS, GEMINI_API_KEY, BATCHES_DIR


def _get_client():
    return genai.Client(api_key=GEMINI_API_KEY)


def build_image_prompt(
    brand: str,
    platform: str,
    content_type: str,
    target_audience: str,
) -> str:
    """Build a Gemini image generation prompt for a specific post."""
    brand_config = BRANDS[brand]
    fmt = brand_config["formats"]["instagram" if platform == "ig" else "facebook"]
    colors = brand_config["colors"]

    content_descriptions = {
        "educational": "ein informatives Bild mit einem hilfreichen Tipp oder Branchenwissen",
        "social_proof": "ein Vorher-Nachher-Bild oder Kundenerfolg mit professionellem Ergebnis",
        "pain_point": "ein Bild das ein konkretes Problem der Zielgruppe zeigt",
        "branded": "ein Bild das das Unternehmen, Team oder die Marke professionell präsentiert",
        "engagement": "ein ansprechendes Bild das zur Interaktion einlädt",
    }
    content_desc = content_descriptions.get(content_type, content_descriptions["educational"])

    if brand == "rebelz-ai":
        brand_style = f"""Stil: Bauhaus-inspiriertes Design, modern und kraftvoll.
Farben: Hauptsächlich Schwarz (#000000) und Weiß (#FFFFFF), minimalistisch.
Schrift: Playfair Display (elegant, serif).
Branding: Rebelz AI Logo-Element (stilisiertes 'R'), dezent aber sichtbar.
Branche: Handwerk & Bau — Zielgruppe sind {target_audience}.
KEIN englischer Text auf dem Bild. Nur deutscher Text."""
    else:
        brand_style = f"""Stil: Modern, vertrauenswürdig, emotional ansprechend.
Farben: Blau (#005b8c) und Weiß (#FFFFFF), optional Akzent Lime (#9DFF20).
Schrift: DM Sans (clean, sans-serif).
Branding: Johnson Services Logo, professionell und einladend.
Branche: Entrümpelung & Umzüge — Zielgruppe sind {target_audience}.
KEIN englischer Text auf dem Bild. Nur deutscher Text."""

    return f"""Erstelle ein hochwertiges Social-Media-Bild.

Größe: {fmt['width']}x{fmt['height']} Pixel.
Format: {fmt['style']}.

{brand_style}

Inhalt: {content_desc}
Zielgruppe: {target_audience}

Das Bild muss professionell, hochauflösend und sofort als Markeninhalt erkennbar sein.
WICHTIG: Alle Texte auf dem Bild MÜSSEN auf Deutsch sein. KEIN Englisch."""


def generate_image(
    brand: str,
    platform: str,
    content_type: str,
    target_audience: str,
    output_path: Path,
) -> bool:
    """Generate a single image using Gemini and save to output_path."""
    client = _get_client()
    prompt = build_image_prompt(brand, platform, content_type, target_audience)

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(part.inline_data.data)
                    return True

        print(f"WARNING: No image in response for {output_path.name}")
        return False

    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print("Rate limited, waiting 30s...")
            time.sleep(30)
            return generate_image(brand, platform, content_type, target_audience, output_path)
        print(f"ERROR generating {output_path.name}: {e}")
        return False


def generate_images_for_batch(batch: dict, batch_dir: Path) -> dict:
    """Generate all images for a batch. Respects MAX 10 images per day."""
    generated = 0

    for account_key, posts in batch.items():
        account_dir = batch_dir / account_key
        account_dir.mkdir(parents=True, exist_ok=True)

        for post in posts:
            if post["media_type"] != "image":
                continue
            if post["file_path"] is not None:
                continue

            output_path = account_dir / f"post-{post['index']:02d}.png"

            if generated >= 10:
                print(f"HIT 10 IMAGE LIMIT. Remaining images need another session.")
                return batch

            success = generate_image(
                brand=post["brand"],
                platform=post["platform"],
                content_type=post["content_type"],
                target_audience=post["target_audience"],
                output_path=output_path,
            )

            if success:
                post["file_path"] = str(output_path.relative_to(batch_dir))
                generated += 1
                print(f"[{generated}/10] Generated {output_path.name} for {account_key}")
                time.sleep(2)  # Rate limit

    print(f"Generated {generated} images total.")
    return batch
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_creative_generator.py -v`
Expected: Prompt tests PASS (no API calls needed for prompt tests)

**Step 5: Commit**

```bash
git add creative_generator.py tests/test_creative_generator.py
git commit -m "feat: Gemini image generator with brand-specific prompts"
```

---

### Task 5: Batch Manager

**Files:**
- Create: `batch_manager.py`
- Create: `tests/test_batch_manager.py`

**Step 1: Write the failing test**

```python
"""Tests for batch_manager."""

import json
from datetime import date
from pathlib import Path
from batch_manager import create_batch, load_manifest, approve_post, approve_all


def test_create_batch_creates_manifest(tmp_path):
    batch_dir = create_batch(start_date=date(2026, 4, 18), base_dir=tmp_path)
    manifest_path = batch_dir / "manifest.json"
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text())
    assert len(manifest["accounts"]) == 4
    total_posts = sum(len(posts) for posts in manifest["accounts"].values())
    assert total_posts == 28


def test_approve_post(tmp_path):
    batch_dir = create_batch(start_date=date(2026, 4, 18), base_dir=tmp_path)
    approve_post(batch_dir, "rebelz-ai-ig", 1)

    manifest = load_manifest(batch_dir)
    post = manifest["accounts"]["rebelz-ai-ig"][0]
    assert post["approved"] is True


def test_approve_all(tmp_path):
    batch_dir = create_batch(start_date=date(2026, 4, 18), base_dir=tmp_path)
    approve_all(batch_dir)

    manifest = load_manifest(batch_dir)
    for account_key, posts in manifest["accounts"].items():
        for post in posts:
            assert post["approved"] is True, f"{account_key} post {post['index']} not approved"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_batch_manager.py -v`
Expected: FAIL

**Step 3: Write the implementation**

```python
"""Batch manager — creates, loads, and manages content batches."""

import json
import subprocess
from datetime import date
from pathlib import Path
from content_planner import plan_batch
from config import BATCHES_DIR, WACLI_BIN, WHATSAPP_RECIPIENT


def create_batch(start_date: date, base_dir: Path | None = None) -> Path:
    """Create a new batch with manifest.json."""
    if base_dir is None:
        base_dir = BATCHES_DIR

    batch_dir = base_dir / start_date.isoformat()
    batch_dir.mkdir(parents=True, exist_ok=True)

    batch = plan_batch(start_date)

    # Create account subdirectories
    for account_key in batch:
        (batch_dir / account_key).mkdir(exist_ok=True)

    manifest = {
        "batch_date": start_date.isoformat(),
        "created_at": date.today().isoformat(),
        "accounts": batch,
    }

    manifest_path = batch_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    return batch_dir


def load_manifest(batch_dir: Path) -> dict:
    """Load manifest.json from a batch directory."""
    manifest_path = batch_dir / "manifest.json"
    return json.loads(manifest_path.read_text())


def save_manifest(batch_dir: Path, manifest: dict) -> None:
    """Save manifest.json to a batch directory."""
    manifest_path = batch_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))


def approve_post(batch_dir: Path, account_key: str, post_index: int) -> None:
    """Approve a single post by index (1-based)."""
    manifest = load_manifest(batch_dir)
    for post in manifest["accounts"][account_key]:
        if post["index"] == post_index:
            post["approved"] = True
            break
    save_manifest(batch_dir, manifest)


def reject_post(batch_dir: Path, account_key: str, post_index: int) -> None:
    """Reject a single post by index (1-based). Resets file_path and caption."""
    manifest = load_manifest(batch_dir)
    for post in manifest["accounts"][account_key]:
        if post["index"] == post_index:
            post["approved"] = False
            post["file_path"] = None
            post["caption"] = None
            break
    save_manifest(batch_dir, manifest)


def approve_all(batch_dir: Path) -> None:
    """Approve all posts in the batch."""
    manifest = load_manifest(batch_dir)
    for account_key, posts in manifest["accounts"].items():
        for post in posts:
            post["approved"] = True
    save_manifest(batch_dir, manifest)


def mark_published(batch_dir: Path, account_key: str, post_index: int) -> None:
    """Mark a post as published."""
    manifest = load_manifest(batch_dir)
    for post in manifest["accounts"][account_key]:
        if post["index"] == post_index:
            post["published"] = True
            break
    save_manifest(batch_dir, manifest)


def get_next_unpublished(batch_dir: Path, brand: str, target_date: str) -> dict | None:
    """Get the next unpublished approved post for a brand on a specific date."""
    manifest = load_manifest(batch_dir)
    for account_key, posts in manifest["accounts"].items():
        if not account_key.startswith(brand):
            continue
        for post in posts:
            if (post["scheduled_date"] == target_date
                    and post["approved"]
                    and not post["published"]):
                return {**post, "account_key": account_key}
    return None


def send_whatsapp_reminder(batch_dir: Path) -> bool:
    """Send WhatsApp reminder that a new batch is ready for review."""
    manifest = load_manifest(batch_dir)
    total = sum(len(posts) for posts in manifest["accounts"].values())
    batch_date = manifest["batch_date"]

    message = (
        f"📱 Neue Social-Media-Batch bereit!\n\n"
        f"Zeitraum ab: {batch_date}\n"
        f"Anzahl Posts: {total}\n"
        f"Accounts: Rebelz AI (IG+FB) + Johnson Services (IG+FB)\n\n"
        f"Bitte in Claude Code prüfen und freigeben."
    )

    try:
        result = subprocess.run(
            [WACLI_BIN, "send", "text", "--to", WHATSAPP_RECIPIENT, "--message", message],
            capture_output=True, text=True, timeout=60,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("WARNING: Could not send WhatsApp reminder")
        return False


def get_current_batch_dir() -> Path | None:
    """Find the most recent batch directory."""
    if not BATCHES_DIR.exists():
        return None
    dirs = sorted(BATCHES_DIR.iterdir(), reverse=True)
    for d in dirs:
        if d.is_dir() and (d / "manifest.json").exists():
            return d
    return None
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_batch_manager.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add batch_manager.py tests/test_batch_manager.py
git commit -m "feat: batch manager with manifest, approval, and WhatsApp reminder"
```

---

### Task 6: Publisher (Meta Graph API — Organic Posts)

**Files:**
- Create: `publisher.py`
- Create: `tests/test_publisher.py`

**Step 1: Write the failing test**

```python
"""Tests for publisher."""

from unittest.mock import patch, MagicMock
from publisher import _get_page_access_token, publish_to_facebook, publish_to_instagram


def test_get_page_access_token_calls_api():
    with patch("publisher.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            json=lambda: {"access_token": "page_token_123"},
            raise_for_status=lambda: None,
        )
        token = _get_page_access_token("123456")
        assert token == "page_token_123"


def test_publish_to_facebook_photo():
    with patch("publisher.requests.post") as mock_post:
        mock_post.return_value = MagicMock(
            json=lambda: {"id": "post_789"},
            raise_for_status=lambda: None,
        )
        with patch("publisher._get_page_access_token", return_value="page_tok"):
            result = publish_to_facebook(
                page_id="123",
                image_path="/tmp/test.png",
                caption="Test caption",
            )
            assert result["id"] == "post_789"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_publisher.py -v`
Expected: FAIL

**Step 3: Write the implementation**

```python
"""Publisher — posts to Facebook pages and Instagram via Meta Graph API."""

import requests
from pathlib import Path
from config import META_ACCESS_TOKEN, META_APP_ID, META_APP_SECRET

GRAPH_API = "https://graph.facebook.com/v21.0"


def _get_page_access_token(page_id: str) -> str:
    """Get a page-specific access token."""
    resp = requests.get(
        f"{GRAPH_API}/{page_id}",
        params={
            "fields": "access_token",
            "access_token": META_ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def publish_to_facebook(
    page_id: str,
    image_path: str | Path,
    caption: str,
) -> dict:
    """Publish a photo post to a Facebook page.

    Uses the Page Photos API: POST /{page-id}/photos
    """
    page_token = _get_page_access_token(page_id)
    image_path = Path(image_path)

    with open(image_path, "rb") as f:
        resp = requests.post(
            f"{GRAPH_API}/{page_id}/photos",
            files={"source": (image_path.name, f, "image/png")},
            data={
                "message": caption,
                "access_token": page_token,
            },
        )
    resp.raise_for_status()
    return resp.json()


def publish_video_to_facebook(
    page_id: str,
    video_path: str | Path,
    caption: str,
) -> dict:
    """Publish a video post to a Facebook page.

    Uses the Page Videos API: POST /{page-id}/videos
    """
    page_token = _get_page_access_token(page_id)
    video_path = Path(video_path)

    with open(video_path, "rb") as f:
        resp = requests.post(
            f"{GRAPH_API}/{page_id}/videos",
            files={"source": (video_path.name, f, "video/mp4")},
            data={
                "description": caption,
                "access_token": page_token,
            },
        )
    resp.raise_for_status()
    return resp.json()


def publish_to_instagram(
    instagram_account_id: str,
    image_url: str,
    caption: str,
) -> dict:
    """Publish a photo to Instagram via Content Publishing API.

    Two-step process:
    1. Create a media container with the image URL
    2. Publish the container

    Note: image_url must be publicly accessible.
    """
    # Step 1: Create container
    resp = requests.post(
        f"{GRAPH_API}/{instagram_account_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": META_ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    container_id = resp.json()["id"]

    # Step 2: Publish
    resp = requests.post(
        f"{GRAPH_API}/{instagram_account_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": META_ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    return resp.json()


def publish_video_to_instagram(
    instagram_account_id: str,
    video_url: str,
    caption: str,
) -> dict:
    """Publish a video (Reel) to Instagram via Content Publishing API."""
    # Step 1: Create video container
    resp = requests.post(
        f"{GRAPH_API}/{instagram_account_id}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": META_ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    container_id = resp.json()["id"]

    # Step 2: Wait for processing, then publish
    import time
    for _ in range(30):  # Wait up to 5 minutes
        status_resp = requests.get(
            f"{GRAPH_API}/{container_id}",
            params={
                "fields": "status_code",
                "access_token": META_ACCESS_TOKEN,
            },
        )
        status = status_resp.json().get("status_code")
        if status == "FINISHED":
            break
        time.sleep(10)

    resp = requests.post(
        f"{GRAPH_API}/{instagram_account_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": META_ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    return resp.json()


def upload_image_to_facebook_and_get_url(page_id: str, image_path: Path) -> str:
    """Upload image to Facebook (unpublished) to get a public URL for Instagram.

    Returns the public URL of the uploaded image.
    """
    page_token = _get_page_access_token(page_id)

    with open(image_path, "rb") as f:
        resp = requests.post(
            f"{GRAPH_API}/{page_id}/photos",
            files={"source": (image_path.name, f, "image/png")},
            data={
                "published": "false",
                "access_token": page_token,
            },
        )
    resp.raise_for_status()
    photo_id = resp.json()["id"]

    # Get the image URL
    resp = requests.get(
        f"{GRAPH_API}/{photo_id}",
        params={
            "fields": "images",
            "access_token": page_token,
        },
    )
    resp.raise_for_status()
    images = resp.json().get("images", [])
    if images:
        return images[0]["source"]  # Largest image
    raise ValueError(f"No image URL returned for photo {photo_id}")
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_publisher.py -v`
Expected: ALL PASS (mocked)

**Step 5: Commit**

```bash
git add publisher.py tests/test_publisher.py
git commit -m "feat: Meta Graph API publisher for FB pages and IG accounts"
```

---

### Task 7: Integration — Generate & Approve Flow

**Files:**
- Create: `generate_batch.py` (CLI entry point for batch generation)

**Step 1: Write the CLI script**

```python
"""CLI entry point: generate a new content batch."""

import sys
from datetime import date, timedelta
from pathlib import Path
from config import BATCHES_DIR
from batch_manager import create_batch, send_whatsapp_reminder
from caption_writer import write_captions_for_batch
from creative_generator import generate_images_for_batch


def main():
    # Calculate next posting start date (next even day from today)
    today = date.today()
    days_ahead = 2 - (today.toordinal() % 2)
    if days_ahead == 0:
        days_ahead = 2
    start_date = today + timedelta(days=days_ahead)

    print(f"=== Generating batch starting {start_date} ===")
    print(f"Posts will run from {start_date} to {start_date + timedelta(days=12)}")
    print()

    # Step 1: Plan the batch
    print("[1/4] Planning content...")
    batch_dir = create_batch(start_date)
    print(f"  Batch directory: {batch_dir}")

    # Step 2: Generate captions
    print("[2/4] Writing captions (Gemini)...")
    from batch_manager import load_manifest, save_manifest
    manifest = load_manifest(batch_dir)
    manifest["accounts"] = write_captions_for_batch(manifest["accounts"])
    save_manifest(batch_dir, manifest)
    print("  Captions written.")

    # Step 3: Generate images (max 10 per day)
    print("[3/4] Generating images (Gemini, max 10 today)...")
    manifest = load_manifest(batch_dir)
    manifest["accounts"] = generate_images_for_batch(manifest["accounts"], batch_dir)
    save_manifest(batch_dir, manifest)

    # Count remaining
    remaining = sum(
        1 for posts in manifest["accounts"].values()
        for p in posts
        if p["media_type"] == "image" and p["file_path"] is None
    )
    if remaining > 0:
        print(f"  {remaining} images remaining — run again tomorrow.")

    # Step 4: Send WhatsApp reminder
    print("[4/4] Sending WhatsApp reminder...")
    send_whatsapp_reminder(batch_dir)

    print()
    print("=== Done! ===")
    print(f"Review batch in Claude Code: 'show me the batch'")
    print(f"Approve: 'approve batch' or 'approve all'")


if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add generate_batch.py
git commit -m "feat: CLI entry point for batch generation"
```

---

### Task 8: Integration — Publish Script (for RemoteTrigger)

**Files:**
- Create: `publish_today.py` (script that RemoteTrigger runs)

**Step 1: Write the publish script**

This is what runs in the cloud. It must be self-contained since RemoteTrigger clones the repo.

```python
"""Publish today's scheduled posts. Called by RemoteTrigger daily."""

import json
import sys
import subprocess
from datetime import date
from pathlib import Path

# RemoteTrigger passes brand as first argument
BRAND = sys.argv[1] if len(sys.argv) > 1 else None
if BRAND not in ("rebelz-ai", "johnson-services"):
    print(f"Usage: python publish_today.py <rebelz-ai|johnson-services>")
    sys.exit(1)

# Config is embedded by RemoteTrigger prompt — loaded from env vars
import os

META_ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
GRAPH_API = "https://graph.facebook.com/v21.0"

BRAND_CONFIG = {
    "rebelz-ai": {
        "page_id": os.environ.get("REBELZ_PAGE_ID", "708377165697175"),
        "instagram_id": os.environ.get("REBELZ_INSTAGRAM_ACCOUNT_ID", ""),
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
    import requests

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
            if post["scheduled_date"] != today_str:
                continue
            if not post["approved"]:
                print(f"  SKIP {account_key} post {post['index']}: not approved")
                continue
            if post["published"]:
                print(f"  SKIP {account_key} post {post['index']}: already published")
                continue
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
                # Upload to FB first to get public URL for IG
                with open(media_path, "rb") as f:
                    resp = requests.post(
                        f"{GRAPH_API}/{page_id}/photos",
                        files={"source": (media_path.name, f, "image/png")},
                        data={"published": "false", "access_token": page_token},
                    )
                resp.raise_for_status()
                photo_id = resp.json()["id"]

                # Get public URL
                resp = requests.get(
                    f"{GRAPH_API}/{photo_id}",
                    params={"fields": "images", "access_token": page_token},
                )
                resp.raise_for_status()
                image_url = resp.json()["images"][0]["source"]

                # Create IG container
                resp = requests.post(
                    f"{GRAPH_API}/{ig_id}/media",
                    data={"image_url": image_url, "caption": caption, "access_token": META_ACCESS_TOKEN},
                )
                resp.raise_for_status()
                container_id = resp.json()["id"]

                # Publish IG container
                import time
                time.sleep(5)  # Wait for processing
                resp = requests.post(
                    f"{GRAPH_API}/{ig_id}/media_publish",
                    data={"creation_id": container_id, "access_token": META_ACCESS_TOKEN},
                )
                resp.raise_for_status()
                print(f"  PUBLISHED {account_key} post {post['index']} to Instagram: {resp.json()}")

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
```

**Step 2: Commit**

```bash
git add publish_today.py
git commit -m "feat: publish script for RemoteTrigger cloud execution"
```

---

### Task 9: Set Up RemoteTriggers

**Files:** None (API calls only)

**Step 1: Create Johnson Services trigger (09:00 Berlin = 07:00 UTC)**

Use RemoteTrigger create with:
- cron: `3 7 * * *`
- repo: `https://github.com/clarencejohnson126/automated_social_media_posts`
- environment: `env_01UNNVABcgo5t1tm35HUeZao`
- prompt: Install requests, set env vars from .env, run `python publish_today.py johnson-services`

**Step 2: Create Rebelz AI trigger (19:00 Berlin = 17:00 UTC)**

Use RemoteTrigger create with:
- cron: `3 17 * * *`
- repo: `https://github.com/clarencejohnson126/automated_social_media_posts`
- prompt: Install requests, set env vars from .env, run `python publish_today.py rebelz-ai`

**Step 3: Test both triggers with manual run**

Use RemoteTrigger `run` action to test each trigger once.

---

### Task 10: Push Everything to GitHub & Final Test

**Step 1: Push all code to GitHub**

```bash
cd "/Users/clarence/Desktop/AUTOMATED ADS/Automated Social Media"
git add -A
git commit -m "feat: complete social media auto-poster system"
git push origin main
```

**Step 2: Generate a test batch**

```bash
python generate_batch.py
```

**Step 3: Verify batch structure**

Check that `batches/` directory has the expected structure with manifest.json, images, and captions.

**Step 4: Approve and push**

In Claude Code: "approve all" → push to GitHub.

**Step 5: Manual trigger test**

Run both RemoteTriggers manually to verify they can clone, read manifest, and post.
