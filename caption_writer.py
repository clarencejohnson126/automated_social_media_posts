"""Caption writer — generates German social media captions using Gemini.

Rewritten 2026-04-11 after Clarence's feedback:
- Johnson captions MUST mention Rhein-Neckar and/or Rhein-Main service area
- Johnson captions must only name cities from the whitelist (no Köln, Berlin,
  Hamburg, München etc. — previous generator invented "Familie Schmidt aus
  Köln" which caused inquiries from out-of-area leads)
- Every post in a batch must use a different hook formula (rotated by index)

See CLAUDE.md in this directory for the full rules.
"""

import time
from google import genai
from config import BRANDS, GEMINI_API_KEY


def _get_client():
    return genai.Client(api_key=GEMINI_API_KEY)


HOOK_FORMULAS = [
    {
        "id": "curiosity",
        "label": "Neugier-Hook",
        "example": "Wussten Sie, dass 8 von 10 Haushaltsauflösungen zu teuer bezahlt werden?",
    },
    {
        "id": "story_moment",
        "label": "Story-/Moment-Hook",
        "example": "Letzte Woche in Heidelberg: Herr K. hatte 14 Tage, um die Wohnung seiner Mutter zu räumen.",
    },
    {
        "id": "contrarian",
        "label": "Contrarian-Hook",
        "example": "Entrümpelung muss nicht 3 Wochen dauern. Hier ist, warum.",
    },
    {
        "id": "shock_stat",
        "label": "Schock-Statistik",
        "example": "87 % der Erbgemeinschaften streiten wegen Kleinigkeiten. So vermeiden Sie das.",
    },
    {
        "id": "before_after",
        "label": "Vorher-/Nachher",
        "example": "Vorher: 4 volle Räume. Nachher: leer, gewischt, schlüsselfertig. In 2 Tagen.",
    },
    {
        "id": "direct_question",
        "label": "Direkte Frage",
        "example": "Haben Sie schon einmal einen Umzug zwischen zwei Klausuren geplant?",
    },
    {
        "id": "personal_bts",
        "label": "Persönlich / Behind-the-Scenes",
        "example": "Gestern in Mannheim-Neckarau: 80 Kartons, 2 Teams, ein erleichtertes Lächeln.",
    },
    {
        "id": "scarcity",
        "label": "Knappheit / Dringlichkeit",
        "example": "Nur noch 3 Termine im Mai für Erbgemeinschaften im Rhein-Neckar-Raum.",
    },
    {
        "id": "social_proof",
        "label": "Sozialer Beweis",
        "example": "147 zufriedene Kunden in Mannheim. Das neueste Feedback:",
    },
    {
        "id": "myth_bust",
        "label": "Mythos-Widerlegung",
        "example": "Mythos: Entrümpelung ist Männerarbeit. Realität: Unser Team ist gemischt.",
    },
]


# Cities we actually serve — used to enforce regional specificity
JOHNSON_CITY_WHITELIST = [
    # Rhein-Neckar
    "Mannheim", "Heidelberg", "Ludwigshafen", "Weinheim", "Speyer", "Worms",
    "Schwetzingen", "Viernheim", "Heppenheim", "Bensheim",
    # Rhein-Main
    "Frankfurt", "Darmstadt", "Wiesbaden", "Offenbach", "Hanau", "Mainz",
    "Rüsselsheim", "Bad Homburg",
]

# Cities we explicitly do NOT serve — captions must never mention these
JOHNSON_CITY_BLACKLIST = [
    "Köln", "Berlin", "Hamburg", "München", "Stuttgart", "Leipzig",
    "Dresden", "Düsseldorf", "Nürnberg", "Bremen", "Hannover", "Essen",
    "Dortmund", "Bonn",
]


def _pick_hook(post_index: int) -> dict:
    """Deterministic hook rotation by post index — no repetition within a batch."""
    return HOOK_FORMULAS[(post_index - 1) % len(HOOK_FORMULAS)]


def write_caption(
    brand: str,
    platform: str,
    content_type: str,
    target_audience: str,
    post_index: int,
) -> str:
    """Generate a German caption for a social media post.

    post_index (1-based) drives hook formula rotation so no two posts in a
    batch share the same hook type.
    """
    brand_config = BRANDS[brand]
    platform_name = "Instagram" if platform == "ig" else "Facebook"
    hook = _pick_hook(post_index)

    if brand == "johnson-services":
        region_block = f"""
HARTE REGEL — REGIONALE VERANKERUNG (Johnson Services):
- Der Post MUSS den Service-Raum explizit erwähnen: 'Rhein-Neckar' und/oder 'Rhein-Main'.
- Nenne mindestens EINE konkrete Stadt aus unserer Whitelist:
  {', '.join(JOHNSON_CITY_WHITELIST)}
- VERBOTEN — diese Städte darfst du NICHT nennen (außerhalb unserer Region):
  {', '.join(JOHNSON_CITY_BLACKLIST)}
- Füge eine kurze Standortzeile ein, z.B. '📍 Wir sind im Rhein-Neckar-Raum für Sie da (Mannheim, Heidelberg, Ludwigshafen).'
- Für fiktive Beispiele/Social Proof: nutze realistische deutsche Vornamen + eine Stadt aus der Whitelist.
"""
        cta_block = """
CTA: WhatsApp-Kontakt, johnson-services.de, oder 'Schreiben Sie uns'.
"""
        voice_block = (
            "Tonalität: Empathisch, vertrauenswürdig. "
            + ("Nutze Du-Form (Instagram ist informeller)." if platform == "ig" else "Nutze Sie-Form (Facebook hat ältere Demo).")
        )
        hashtag_hint = (
            "Hashtags (3–5): Mische Service-Tags (#Entrümpelung #Haushaltsauflösung #Umzug), "
            "Region-Tags (#Mannheim #Heidelberg #RheinNeckar oder #Frankfurt #RheinMain), "
            "und ein Branding-Tag (#JohnsonServices)."
        )
    else:  # rebelz-ai
        region_block = ""
        cta_block = """
CTA: 'Kostenloses Erstgespräch' oder 'Jetzt testen' und Link rebelzai.com.
"""
        voice_block = "Tonalität: Direkt, pain-point-first, formelle Ihr-Form. Sprich Handwerks-Gewerke beim Namen an."
        hashtag_hint = (
            "Hashtags (3–5): Mische Gewerk-Tags (#Trockenbauer #Elektriker etc.), "
            "Pain-Tags (#Baustellendoku #Stundenzettel), und #RebelzAI."
        )

    prompt = f"""Du bist ein deutscher Social-Media-Texter für {brand_config['name']}.
Branche: {brand_config['niche']}
Zielgruppe dieses Posts: {target_audience}
Plattform: {platform_name}
Inhaltstyp: {content_type}

HOOK-FORMEL für diesen Post (#{hook['id']} — {hook['label']}):
Der erste Satz MUSS dieser Formel folgen.
Beispiel derselben Formel: "{hook['example']}"
Wichtig: Nicht das Beispiel kopieren — eigene Variante für diese Zielgruppe schreiben.

{region_block}
{voice_block}

Struktur:
1. Hook-Satz (nach der vorgegebenen Formel)
2. 2–4 Sätze Body: Situation malen, empathisch sein ODER Wert rüberbringen
3. Ein konkretes Detail: eine Zahl, ein Zeitraum, ein Ortsbezug
4. Standort-Zeile mit 📍 Emoji (nur Johnson)
5. CTA-Zeile mit 👉 Emoji
6. Eine Leerzeile
7. 3–5 deutsche Hashtags

{cta_block}
{hashtag_hint}

Harte Regeln:
- KEIN einziges englisches Wort (auch nicht in Hashtags)
- Max 150 Wörter für Instagram, 200 für Facebook
- Keine generische Floskel am Anfang — die Hook-Formel ist Pflicht

Gib NUR den fertigen Post-Text zurück, keine Erklärungen, kein Kommentar."""

    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    caption = response.text.strip()

    # Post-validation for Johnson — if no whitelist city was mentioned OR a
    # blacklist city leaked in, raise so the caller can retry.
    if brand == "johnson-services":
        has_whitelist_city = any(c in caption for c in JOHNSON_CITY_WHITELIST)
        has_region_name = "Rhein-Neckar" in caption or "Rhein-Main" in caption
        if not has_whitelist_city or not has_region_name:
            raise ValueError(
                f"Johnson caption missing regional mention "
                f"(whitelist_city={has_whitelist_city}, region={has_region_name}): {caption[:200]}"
            )
        leaked = [c for c in JOHNSON_CITY_BLACKLIST if c in caption]
        if leaked:
            raise ValueError(f"Johnson caption contains blacklisted cities {leaked}: {caption[:200]}")

    return caption


def write_captions_for_batch(batch: dict) -> dict:
    """Generate captions for all posts in a batch."""
    for account_key, posts in batch.items():
        for post in posts:
            if post["caption"] is not None:
                continue
            # Retry up to 3 times if Johnson validation fails
            for attempt in range(3):
                try:
                    caption = write_caption(
                        brand=post["brand"],
                        platform=post["platform"],
                        content_type=post["content_type"],
                        target_audience=post["target_audience"],
                        post_index=post["index"],
                    )
                    post["caption"] = caption
                    break
                except ValueError as e:
                    print(f"  [retry {attempt + 1}/3] {e}")
                    if attempt == 2:
                        raise
            time.sleep(1)  # Rate limit

    return batch
