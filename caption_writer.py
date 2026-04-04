"""Caption writer — generates German social media captions using Gemini."""

import time
from google import genai
from config import BRANDS, GEMINI_API_KEY


def _get_client():
    return genai.Client(api_key=GEMINI_API_KEY)


def write_caption(
    brand: str,
    platform: str,
    content_type: str,
    target_audience: str,
) -> str:
    """Generate a German caption for a social media post."""
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
