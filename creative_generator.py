"""Creative generator — Gemini image generation with brand-specific prompts.

Rewritten 2026-04-11 after Clarence's feedback that Johnson images were
visually identical (same female caregiver + elderly woman in living room,
repeating). See CLAUDE.md in this directory for the full creative rules.

Core principle: every post in a batch MUST use a DIFFERENT visual scene
category (A–J) AND a different visual style. We enforce this by rotating
categories by post index, not by random.choice() — randomness allowed the
model to converge on the same scene type.
"""

import random
import time
from pathlib import Path
from google import genai
from google.genai import types
from config import BRANDS, GEMINI_API_KEY, BATCHES_DIR


def _get_client():
    return genai.Client(api_key=GEMINI_API_KEY)


# ─────────────────────────────────────────────────────────────────────────
# 10 VISUAL SCENE CATEGORIES (see CLAUDE.md — rotate through these per batch)
# ─────────────────────────────────────────────────────────────────────────
# Each category has Johnson-specific and Rebelz-specific scene prompts.
# The generator picks category by (post_index % 10), so a batch of 10 posts
# gets exactly one of each. Within a category, we pick a variant that
# matches the ICP.

SCENE_CATEGORIES = [
    "A_hero_team_action",
    "B_process_bts",
    "C_transformation",
    "D_human_moment",
    "E_abstract_flatlay",
    "F_data_stats_card",
    "G_text_first_poster",
    "H_environment_regional",
    "I_documentary_flash",
    "J_aerial_topdown",
]

# Human-readable labels passed to Gemini in the prompt. The internal ID
# (e.g. "F_data_stats_card") must NEVER appear in the prompt directly
# because Gemini will sometimes render it as visible text on the image.
CATEGORY_LABELS = {
    "A_hero_team_action":    "Hero-/Team-Aktionsshot",
    "B_process_bts":         "Prozess-/Behind-the-Scenes-Detail",
    "C_transformation":      "Vorher-/Nachher-Transformation",
    "D_human_moment":        "Authentischer menschlicher Moment",
    "E_abstract_flatlay":    "Abstraktes Flatlay / symbolische Komposition",
    "F_data_stats_card":     "Daten-/Statistik-Karte mit großer Zahl",
    "G_text_first_poster":   "Typografie-Poster mit Headline als Hero",
    "H_environment_regional":"Umgebungs-/Stadtansicht mit regionalem Bezug",
    "I_documentary_flash":   "Dokumentarischer Direkt-Blitz-Stil",
    "J_aerial_topdown":      "Drohnen-/Top-Down-Perspektive",
}

# ─────────────────────────────────────────────────────────────────────────
# JOHNSON SERVICES — scenes per category (do NOT reuse the old living-room
# caregiver scene — that's the visual fatigue we're fixing)
# ─────────────────────────────────────────────────────────────────────────

JOHNSON_SCENES = {
    "A_hero_team_action": [
        "Gebrandeter weißer Johnson-Services-Kastenwagen mit blauem Logo steht vor dem Mannheimer Wasserturm zur goldenen Stunde, ein Teammitglied in königsblauem Polo öffnet die Hecktür, kraftvolle Heldenkomposition",
        "Drei-Personen-Team in königsblauen Johnson-Services-Shirts schlägt grinsend ein: Einer hält ein Klemmbrett, der andere trägt einen professionellen Faltkarton, der dritte zeigt ein OK-Zeichen, Ganzkörperporträt vor einem Heidelberger Altbau",
        "Close-Up einer behandschuhten Hand, die mit schwarzem Marker 'KÜCHE – ZERBRECHLICH' auf einen ordentlichen braunen Karton schreibt, im Hintergrund unscharf ein Team bei der Arbeit",
    ],
    "B_process_bts": [
        "Makroaufnahme zweier Hände, die ein filigranes Porzellan-Erinnerungsstück mit gebogenem Kraftpapier umwickeln, warmes goldenes Fensterlicht, dokumentarischer Stil, sehr geringe Schärfentiefe",
        "Bewegungsunschärfe-Aufnahme eines Teams, das einen Karton im Treppenhaus eines Jugendstilhauses weiterreicht, dynamisch, authentisch, leicht körnig",
        "Overhead-Blick auf einen Küchentisch, auf dem jemand professionelle Umzugsmaterialien sortiert: Rollen mit Noppenfolie, blaue Johnson-Services-Kartons, Klebeband, Edding, alles exakt ausgerichtet",
    ],
    "C_transformation": [
        "Vorher/Nachher-Split-Screen (vertikal getrennt durch feine weiße Linie): links ein überfülltes Dachgeschoss mit Staub und Kisten, rechts das gleiche Dachgeschoss komplett leer, frisch gefegt, Sonnenlicht strömt durch die Dachfenster",
        "Vorher/Nachher eines Garagenraums: links vollgestellt mit Gerümpel, rechts blitzsauber und leer, gleicher Kamerawinkel, gleiches Licht",
        "Ein einzelnes Foto: leerer, gefegter Raum mit einem einzigen letzten Karton in der Mitte, durch die Fenster flutet weiches Nachmittagslicht, cinematische Stimmung",
    ],
    "D_human_moment": [
        "Ehrliches Porträt eines Betreuers mittleren Alters (männlich, Sie-Form-Typ) mit sichtbarer Erleichterung im Gesicht, der vor der Tür seines Betreuten steht, natürliches Fensterlicht, dokumentarischer Stil",
        "Junger Student Mitte 20 lacht ehrlich, während er den letzten Karton in einen Kleintransporter in einer Heidelberger Altstadtstraße schiebt, sonniger Vormittag",
        "Elegante ältere Frau Anfang 70 reicht einem Johnson-Services-Teamleiter lächelnd die Hand, Fokus auf den Handschlag, weicher Hintergrund",
    ],
    "E_abstract_flatlay": [
        "Flat Lay von oben auf einem neutralen Leinenhintergrund: ein Bund Schlüssel, eine Umzugscheckliste mit deutschem Text, ein blauer Johnson-Services-Kugelschreiber, eine Tasse schwarzer Kaffee, alles geometrisch angeordnet, magazinreif",
        "Flat Lay von oben: ein Grundriss einer Wohnung, darüber ein Metermaß und ein paar Schlüssel arrangiert, clean minimalistisch auf weißem Holzboden",
        "Symbolisches Bild: eine offene Tür, durch die Licht strömt, und auf der Schwelle ein einzelner kleiner Karton mit dem Wort 'NEUANFANG' drauf",
    ],
    "F_data_stats_card": [
        "Poster-artiges Design: riesige Zahl '147' in fetter DM-Sans auf tiefblauem Hintergrund (#005b8c), darunter kleiner weißer Text 'zufriedene Kunden im Rhein-Neckar-Raum', unten rechts dezentes Johnson-Services-Logo",
        "Statistik-Karte: '48 Stunden' in gewaltiger weißer Schrift auf blauem Grund, darunter 'von Chaos zu leerer Wohnung', schlichtes Grafik-Design",
        "Testimonial-Karte: großes Anführungszeichen, darunter ein kurzes Zitat auf Deutsch ('Schneller als ich dachte. Und sauber.'), Name eines Kunden aus Mannheim, clean Bauhaus-Layout",
    ],
    "G_text_first_poster": [
        "Fetter deutscher Typografie-Poster-Stil: 'ENTRÜMPELUNG IN 48 STUNDEN' in riesiger DM-Sans-Schrift auf limettengrünem Akzent-Hintergrund (#9DFF20), schwarze Schrift, ein einziges kleines blaues Element als Kontrast",
        "Minimaler Poster: 'WIR KÜMMERN UNS UM ALLES.' in weißer Schrift auf tief dunkelblauem Grund, nichts sonst außer dem dezenten Logo unten",
        "Frage-Poster-Stil: 'WOHIN MIT OMAS ALTEM SCHRANK?' in großer bold Schrift auf cremeweißem Grund, darunter winzig 'Wir schon.' mit Logo",
    ],
    "H_environment_regional": [
        "Skyline von Frankfurt am Main in der Dämmerung, im Vordergrund unscharf die Heckklappe eines Johnson-Services-Vans mit sichtbarem Logo, epische Perspektive",
        "Schmale Heidelberger Altstadtgasse am frühen Morgen, ein Johnson-Services-Team trägt Kartons zu einem Haus, authentische Straßenszene",
        "Weite Aufnahme des Mannheimer Wasserturms bei blauer Stunde, im Vordergrund das Johnson-Services-Logo auf einem Fahrzeug, grafisch und regional unverwechselbar",
    ],
    "I_documentary_flash": [
        "Direkter Blitz, nächtliche Straßenszene in Mannheim-Jungbusch, ein Team lädt den letzten Karton in den Van, rohe dokumentarische Ästhetik, leicht gritty",
        "Kandid-Paparazzi-Ästhetik mit hartem Blitz: zwei Teammitglieder stehen rauchend vor einem Frankfurter Altbau, eine ehrliche Pause in einem langen Arbeitstag",
        "Flash-Fotografie im Inneren einer halb geräumten Wohnung, Team in Aktion, wirft scharfe Schatten, roh und echt",
    ],
    "J_aerial_topdown": [
        "Drohnenperspektive direkt von oben auf einen vollständig beladenen Johnson-Services-Van mit offenen Türen, Kartons wie Tetris gepackt, sichtbare regionale Straßenmarkierungen",
        "Bird's-eye-view auf einen leeren Dielenboden eines Raumes mit nur einem Metermaß, einem Schlüsselbund und einem Grundriss — grafisch und minimal",
        "Top-down-Aufnahme eines Stapels sauberer weißer Umzugskartons auf dem Gehweg vor einem Heidelberger Altbau, Sonnenlicht, fast wie eine Installation",
    ],
}

# ─────────────────────────────────────────────────────────────────────────
# REBELZ AI — scenes per category
# ─────────────────────────────────────────────────────────────────────────

REBELZ_SCENES = {
    "A_hero_team_action": [
        "Trockenbauer auf einer Baustelle in Arbeitskleidung, konzentriert, mit einem Tablet in der Hand, im Hintergrund unscharfe Trockenbauwände, Heldenporträt",
        "Elektriker mit Tablet vor einem modernen Sicherungskasten, LEDs glimmen blau, futuristische Atmosphäre",
        "Dachdecker auf einem steilen Dach mit Stadtpanorama, heroische Pose gegen dramatischen Abendhimmel",
    ],
    "B_process_bts": [
        "Makroaufnahme einer präzise gezogenen Fliesenfuge, Wassertropfen perlen ab, hochauflösendes Detail",
        "Nahaufnahme einer Hand, die mit Bleistift und Maßband präzise Maße auf einem Bauplan notiert, warmes Seitenlicht",
        "Farbroller wird über eine halb gestrichene Wand gezogen, cremige Textur, sinnliches Detail",
    ],
    "C_transformation": [
        "Vorher/Nachher einer Wohnzimmerwand: links staubig und unverputzt, rechts frisch gestrichen und elegant",
        "Split-Screen: links ein chaotischer Stapel Papierzettel und Notizen, rechts ein sauberes iPad-Dashboard mit denselben Daten digital erfasst",
        "Vorher/Nachher eines Badezimmers: links alte Fliesen, rechts perfekt verlegtes Mosaik, gleicher Winkel",
    ],
    "D_human_moment": [
        "Ehrliches Porträt eines Dachdeckers mittleren Alters mit Stolz und Erschöpfung im Gesicht nach Feierabend, dokumentarisch",
        "Zwei Handwerker lachen ehrlich auf einer Kaffeepause auf einer Baustelle, echt und warm",
        "Handwerker zeigt seinem Sohn oder Lehrling etwas auf einem Bauplan, lehrende Geste, fokussiert",
    ],
    "E_abstract_flatlay": [
        "Flat Lay von oben: Maßband, Wasserwaage, Bleistift, Notizblock, Kaffee, perfekt geometrisch auf einer Holzfläche",
        "Grafische Komposition: verschiedene Werkzeuge aus der Vogelperspektive, fast wie ein Stillleben, magazinreif",
        "Symbolisches Bild: ein Schlüssel, ein Bauplan und ein Kaffeebecher arrangiert auf einem Tisch, warmer Morgen",
    ],
    "F_data_stats_card": [
        "Poster-Stil: riesige Zahl '12 STUNDEN' in fetter Playfair-Display auf schwarzem Grund, darunter 'pro Woche gespart — dank Rebelz AI', weiß",
        "Statistik-Karte: '68 %' in gewaltiger weißer Schrift, darunter 'weniger Büroarbeit für Trockenbauer', minimal",
        "Testimonial-Karte: großes Zitat, darunter Name eines Handwerksmeisters und sein Gewerk, Bauhaus-Layout",
    ],
    "G_text_first_poster": [
        "Fetter Poster-Stil: 'STUNDENZETTEL? GELÖST.' in riesiger Playfair Display auf tiefschwarzem Grund, weiß",
        "Minimal-Poster: 'NACHTRÄGE VERGESSEN KOSTET €3.400.' in weißer Schrift auf schwarzem Grund, sonst nichts",
        "Frage-Poster: 'WARUM MACHEN SIE IHRE BÜROARBEIT NOCH IMMER HANDSCHRIFTLICH?' bold schwarz auf weiß",
    ],
    "H_environment_regional": [
        "Baustelle in Mannheim bei Dämmerung, im Vordergrund ein Handwerker mit Tablet, im Hintergrund Kräne gegen den Himmel",
        "Frankfurter Bankenviertel-Skyline mit einem Gerüstarbeiter in Hochposition im Vordergrund",
        "Typische deutsche Kleinstadt-Baustelle an einem Altbau, authentisch und regional verankert",
    ],
    "I_documentary_flash": [
        "Direkter Blitz, nächtliche Baustelle, ein Handwerker räumt seine Werkzeuge zusammen, gritty",
        "Flash-Aufnahme im Inneren einer Rohbauwohnung, Team in Aktion, harte Schatten, ungeschönt",
        "Kandid-Stil mit Blitz: ein Elektriker prüft eine Verdrahtung, ehrlich und fokussiert",
    ],
    "J_aerial_topdown": [
        "Drohnenperspektive direkt von oben auf ein Dach, auf dem Dachdecker arbeiten, grafisch klare Komposition",
        "Top-down auf einen Werkzeugkasten, der perfekt organisiert ist, fast wie eine Installation",
        "Bird's-eye auf einen Baustellen-Parkplatz mit Handwerker-Fahrzeugen in Reihe, regional und authentisch",
    ],
}

# ─────────────────────────────────────────────────────────────────────────
# VISUAL TREATMENTS — one per scene (rotated independently)
# ─────────────────────────────────────────────────────────────────────────

TREATMENTS = [
    "goldene Stunde, warmes seitliches Licht",
    "helles Tageslicht, klare Schatten",
    "Studio-Weiß, gleichmäßig ausgeleuchtet",
    "moody dunkel mit einem einzelnen Lichtakzent",
    "leuchtende Farbblöcke im Bauhaus-Stil",
    "monochrom, körniger Film-Look",
    "direkter harter Kamerablitz, dokumentarisch",
    "blaue Stunde / Dämmerung, cinematisch",
]

REGIONAL_CITIES_JOHNSON = [
    "Mannheim", "Heidelberg", "Ludwigshafen", "Weinheim", "Speyer",
    "Frankfurt", "Darmstadt", "Wiesbaden", "Offenbach", "Mainz",
]

# Hard negative constraints — Gemini must NOT produce these
NEGATIVE_CONSTRAINTS_JOHNSON = """
VERMEIDE UNBEDINGT (diese Kompositionen haben zu Creative-Fatigue geführt):
- KEINE junge Pflegerin in blauem Poloshirt mit weißhaariger älterer Frau
- KEINE Szene in einem Wohnzimmer mit Bücherregal und beschrifteten Kartons "FOTOS/BÜCHER/WOHNZIMMER"
- KEIN Stock-Foto-Look von zwei Frauen sortieren Erinnerungsstücke
- KEINE generische Shutterstock-Ästhetik
- KEIN englischer Text im Bild
"""

NEGATIVE_CONSTRAINTS_REBELZ = """
VERMEIDE UNBEDINGT:
- KEIN generischer Bauarbeiter mit Bohrmaschine im Stock-Foto-Stil
- KEIN englischer Text im Bild
- KEIN übertrieben gestellter Werbefoto-Look
"""


def _pick_category(post_index: int) -> str:
    """Scene category is DETERMINED by post index — not random.

    This guarantees that a 10-post batch uses all 10 categories exactly once
    and a 5-post batch uses 5 distinct categories.
    """
    return SCENE_CATEGORIES[(post_index - 1) % len(SCENE_CATEGORIES)]


def _pick_scene(brand: str, category: str, target_audience: str) -> str:
    pool = JOHNSON_SCENES if brand == "johnson-services" else REBELZ_SCENES
    # target_audience could be used to further narrow down in the future
    variants = pool.get(category, [])
    if not variants:
        variants = list(pool.values())[0]
    return random.choice(variants)


def build_image_prompt(
    brand: str,
    platform: str,
    content_type: str,
    target_audience: str,
    post_index: int,
) -> str:
    """Build a Gemini image generation prompt for a specific post.

    post_index (1-based) drives visual category rotation so no two posts
    in a batch end up with the same scene type.
    """
    brand_config = BRANDS[brand]
    fmt = brand_config["formats"]["instagram" if platform == "ig" else "facebook"]

    category = _pick_category(post_index)
    category_label = CATEGORY_LABELS[category]
    scene = _pick_scene(brand, category, target_audience)
    treatment = TREATMENTS[(post_index - 1) % len(TREATMENTS)]

    if brand == "rebelz-ai":
        brand_block = f"""Szene: {scene}
Visuelle Behandlung: {treatment}
Farben: Schwarz (#000000) und Weiß (#FFFFFF). Alles andere ist Akzent.
Branding: Kleines stilisiertes 'R' Logo dezent in einer Ecke.
Text im Bild: Kurze deutsche Headline (max 5 Wörter), bold Playfair Display, groß und selbstbewusst.
Stimme: Formelle Ihr-Form. Direkt, schmerzpunktbezogen.

{NEGATIVE_CONSTRAINTS_REBELZ}
"""
    else:  # johnson-services
        city_hint = random.choice(REGIONAL_CITIES_JOHNSON)
        brand_block = f"""Szene: {scene}
Visuelle Behandlung: {treatment}
Farben: Tiefblau (#005b8c) und Weiß (#FFFFFF), optional Lime-Akzent (#9DFF20).
Branding: Johnson Services Logo dezent aber erkennbar eingebunden.
Text im Bild (falls vorhanden): Kurze deutsche Headline (max 6 Wörter), bold DM Sans.
Regionale Verankerung: Wenn ein Ort im Bild angedeutet werden kann, dann im Raum {city_hint} / Rhein-Neckar oder Rhein-Main.
Stimme: Empathisch, vertrauenswürdig — Zuverlässig, Sauber, Günstig.

{NEGATIVE_CONSTRAINTS_JOHNSON}
"""

    return f"""Erstelle ein einzigartiges, hochwertiges Social-Media-Bild.

Zielformat: {fmt['width']}x{fmt['height']} Pixel ({fmt['style']}).
Visueller Bildtyp: {category_label}
Inhaltstyp: {content_type}
Zielgruppe: {target_audience}

{brand_block}

WICHTIG:
- Das Bild MUSS sich visuell deutlich von den bisherigen Posts unterscheiden.
- Der Bildtyp oben ist Leitfaden — NICHT als Text im Bild darstellen.
- Keine internen Codes, Kategorie-IDs oder Beschriftungen im Bild sichtbar machen.
- Jegliche sichtbaren Textelemente MÜSSEN auf Deutsch sein und aussagekräftig zur Szene passen.
- Authentisch, nicht Stock-Foto-mäßig."""


def generate_image(
    brand: str,
    platform: str,
    content_type: str,
    target_audience: str,
    post_index: int,
    output_path: Path,
) -> bool:
    """Generate a single image using Gemini and save to output_path."""
    client = _get_client()
    prompt = build_image_prompt(brand, platform, content_type, target_audience, post_index)

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
            return generate_image(
                brand, platform, content_type, target_audience, post_index, output_path
            )
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
                post_index=post["index"],
                output_path=output_path,
            )

            if success:
                post["file_path"] = str(output_path.relative_to(batch_dir))
                generated += 1
                print(f"[{generated}/10] Generated {output_path.name} for {account_key}")
                time.sleep(2)  # Rate limit

    print(f"Generated {generated} images total.")
    return batch
