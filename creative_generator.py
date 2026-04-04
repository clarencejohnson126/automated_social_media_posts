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
