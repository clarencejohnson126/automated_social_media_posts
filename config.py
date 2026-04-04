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
POSTS_PER_BATCH = 7
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
