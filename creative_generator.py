"""Creative generator — Gemini image generation with brand-specific prompts."""

import time
from pathlib import Path
from google import genai
from google.genai import types
from config import BRANDS, GEMINI_API_KEY, BATCHES_DIR


def _get_client():
    return genai.Client(api_key=GEMINI_API_KEY)


import random

# Visual variety pools — each post gets a DIFFERENT scene/style combo
_REBELZ_SCENES = {
    "Trockenbauer": [
        "Nahaufnahme von Händen die präzise eine Gipskartonplatte zuschneiden, Staub in der Luft, dramatisches Seitenlicht",
        "Fertiger Raum mit perfekt verputzten Wänden, warmes Licht fällt durch ein Fenster, der Handwerker lehnt stolz an der Wand",
        "Vogelperspektive auf einen Grundriss mit Werkzeug und Tablet daneben, flache Komposition, minimalistisch",
        "Zwei Handwerker besprechen einen Plan auf einer Baustelle, einer zeigt auf ein Tablet, professionelle Teamarbeit",
    ],
    "Bodenleger": [
        "Detailaufnahme von elegant verlegtem Parkettboden mit Spiegelung, künstlerische Perspektive von unten",
        "Vorher-Nachher Split: links alter kaputter Boden, rechts frisch verlegtes Parkett, scharfe Trennlinie",
        "Handwerker kniet auf fertigem Boden und prüft die Qualität, Fokus auf seine prüfenden Hände",
        "Verschiedene Bodenbeläge als Muster angeordnet wie ein Kunstwerk, Flatlay-Stil von oben",
    ],
    "Elektriker": [
        "Modernes Smart-Home Panel an der Wand, blaue LED-Lichter, futuristisch und clean",
        "Sauberer Sicherungskasten nach der Arbeit, alles perfekt beschriftet, professionelle Ordnung",
        "Elektriker mit Tablet steuert Gebäudeautomation, Bildschirm leuchtet, moderne Technologie",
        "Kabelstränge kunstvoll und ordentlich verlegt, fast wie ein Kunstwerk, Makro-Aufnahme",
    ],
    "Abdichter": [
        "Flachdach bei Sonnenuntergang, frische Abdichtung glänzt, dramatischer Himmel",
        "Nahaufnahme einer perfekten Naht bei einer Kellerabdichtung, Wassertropfen perlen ab",
        "Handwerker arbeitet auf einem Dach mit Stadtpanorama im Hintergrund, epische Perspektive",
        "Querschnitt-Illustration einer Gebäudeabdichtung, technisch aber visuell ansprechend",
    ],
    "Dachdecker": [
        "Dachlandschaft von oben, verschiedene Ziegel in Mustern, grafisch und ästhetisch",
        "Handwerker auf einem Dach mit Bergpanorama im Hintergrund, heroische Pose",
        "Nahaufnahme von Dachziegeln mit Regentropfen, die perfekt abperlen, Makro-Fotografie",
        "Historisches vs. modernes Dach nebeneinander, Kontrast zwischen Tradition und Innovation",
    ],
    "Maler": [
        "Farbfächer und Pinsel arrangiert als Flatlay, eine Hand wählt eine Farbe, elegant",
        "Halb gestrichene Wand: vorher grau, nachher leuchtend, dramatischer Farbkontrast",
        "Nahaufnahme von Farbroller auf frischer Wand, cremige Textur, sinnliches Detail",
        "Fertig gestrichener Raum mit perfekten Kanten und Linien, Sonnenlicht fällt herein",
    ],
    "Fliesenleger": [
        "Mosaik-Muster in einem luxuriösen Badezimmer, elegante Perspektive",
        "Nahaufnahme einer perfekten Fuge, geometrische Perfektion, minimalistisch",
        "Handwerker schneidet präzise eine Fliese mit einer Nassschneidemaschine, Wasser spritzt",
        "Fertiges Badezimmer mit aufwändigem Fliesenmuster, Magazin-Qualität",
    ],
}

_JOHNSON_SCENES = {
    "Betreuer": [
        "Leerer, sauberer Raum nach einer Entrümpelung mit Sonnenlicht, Neuanfang-Stimmung",
        "Freundlicher Helfer übergibt Schlüssel an eine erleichterte ältere Person, warmherzige Szene",
        "Ordentlich sortierte Umzugskartons mit Beschriftung, alles organisiert und professionell",
        "Team in blauen Shirts trägt vorsichtig Möbel die Treppe hinunter, Teamwork",
    ],
    "Erbgemeinschaften": [
        "Altes Haus wird ausgeräumt, Mix aus Nostalgie und Aufbruch, warmes Licht",
        "Alte Fotos und Erinnerungsstücke sorgfältig in Kisten verpackt, respektvoller Umgang",
        "Leeres Zimmer mit Sonnenlicht und einem letzten Umzugskarton, poetische Stimmung",
        "Professionelles Team vor einem Haus, bereit zum Anpacken, vertrauenswürdig",
    ],
    "Studenten die umziehen": [
        "Junger Mensch in neuem WG-Zimmer, erste Kiste wird ausgepackt, Vorfreude",
        "Kleintransporter vor einem Altbau, Umzugshelfer tragen Kartons, urbane Szene",
        "Chaotisches vs. aufgeräumtes Zimmer Split-Screen, humorvoller Kontrast",
        "Studentin sitzt glücklich auf dem Boden ihrer neuen leeren Wohnung, Smartphone in der Hand",
    ],
    "junge Familien": [
        "Familie steht vor neuem Haus mit Umzugskartons, Kind hält Teddy, glücklicher Moment",
        "Kinderzimmer wird eingerichtet, bunte Kisten, fröhliche Atmosphäre",
        "Eltern und Kind malen zusammen die Wand im neuen Zuhause, familiärer Moment",
        "Umzugshelfer tragen Kinderbett ins Haus, Familie schaut dankbar zu",
    ],
    "Kinder die Eltern-Wohnung auflösen": [
        "Erwachsenes Kind packt sorgsam Erinnerungsstücke ein, emotionaler aber positiver Moment",
        "Leere Wohnung mit letztem Karton und einem Bilderrahmen, würdevoller Abschied",
        "Professioneller Helfer berät eine Person mittleren Alters, einfühlsam und kompetent",
        "Altes Möbelstück wird vorsichtig auf einen LKW geladen, sorgfältiger Umgang",
    ],
}

_REBELZ_VISUAL_STYLES = [
    "Hochkontrast Schwarz-Weiß, körnige Textur wie analoges Film-Foto",
    "Clean minimalistisch, viel Weißraum, ein starkes zentrales Element",
    "Dramatisches Chiaroscuro-Licht, tiefe Schatten, ein Highlight",
    "Grafisch-geometrisch, Bauhaus-Linien überlagert auf Foto, modern",
    "Dokumentar-Stil, authentisch, wie aus einem Architektur-Magazin",
    "Duotone Schwarz-Weiß mit einem einzelnen farbigen Akzent-Element",
]

_JOHNSON_VISUAL_STYLES = [
    "Warm und einladend, weiches natürliches Licht, Lifestyle-Fotografie",
    "Clean und professionell, helle Farben, vertrauenswürdig",
    "Emotional und nahbar, Fokus auf Gesichter und Momente",
    "Modern und frisch, klare Linien, positive Energie",
    "Dokumentar-Stil aber freundlich, echte Situationen, authentisch",
    "Magazin-Qualität, perfekt inszeniert aber natürlich wirkend",
]


def build_image_prompt(
    brand: str,
    platform: str,
    content_type: str,
    target_audience: str,
) -> str:
    """Build a Gemini image generation prompt for a specific post."""
    brand_config = BRANDS[brand]
    fmt = brand_config["formats"]["instagram" if platform == "ig" else "facebook"]

    if brand == "rebelz-ai":
        scenes = _REBELZ_SCENES.get(target_audience, list(_REBELZ_SCENES.values())[0])
        scene = random.choice(scenes)
        style = random.choice(_REBELZ_VISUAL_STYLES)
        brand_style = f"""Szene: {scene}
Visueller Stil: {style}
Farben: Schwarz (#000000) und Weiß (#FFFFFF).
Branding: Kleines stilisiertes 'R' Logo in einer Ecke, dezent.
Text auf dem Bild: Kurze deutsche Headline (max 5 Wörter), groß und bold, Playfair Display Schrift.
Optional: Eine kurze Subline (max 8 Wörter).
KEIN englischer Text. KEIN generischer Stock-Foto-Look. Muss einzigartig und markant sein."""
    else:
        scenes = _JOHNSON_SCENES.get(target_audience, list(_JOHNSON_SCENES.values())[0])
        scene = random.choice(scenes)
        style = random.choice(_JOHNSON_VISUAL_STYLES)
        brand_style = f"""Szene: {scene}
Visueller Stil: {style}
Farben: Blau (#005b8c) und Weiß (#FFFFFF), optional Akzent Lime (#9DFF20).
Branding: Johnson Services dezent eingebunden.
Text auf dem Bild: Kurze deutsche Headline (max 6 Wörter), DM Sans Schrift, bold.
Optional: Eine kurze Subline.
KEIN englischer Text. Echte, authentische Szene — KEIN generischer Stock-Foto-Look."""

    return f"""Erstelle ein einzigartiges Social-Media-Bild.

Größe: {fmt['width']}x{fmt['height']} Pixel.
Format: {fmt['style']}.

{brand_style}

Zielgruppe: {target_audience}
Content-Typ: {content_type}

WICHTIG: Das Bild muss sich DEUTLICH von typischen Handwerker-Stock-Fotos unterscheiden.
Keine generischen Bauarbeiter-mit-Bohrmaschine Bilder. Sei kreativ und überraschend.
Alle Texte auf dem Bild MÜSSEN auf Deutsch sein."""


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
