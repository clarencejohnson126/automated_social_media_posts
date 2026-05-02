# Automated Social Media — Creative Fundamentals

This file is auto-loaded whenever Claude works in this directory. It encodes the
strategic rules that the image/caption generators must follow. Written after
Clarence's 2026-04-11 feedback that the Johnson posts were visually identical
(same female caregiver + elderly woman + living room + boxes, over and over)
and missing regional context.

## The fundamental problem

**Creative fatigue kills organic reach.** If every post looks the same, the
algorithm stops showing them and the audience stops engaging. You cannot go
viral by posting variations of the same image. The single biggest lever for
organic traction is VARIETY — different visuals, different hooks, different
moments, different angles on the same core value prop.

**One clear message per post, but every post must look and feel different
from the last.**

## IRON RULES (never break)

1. **Visual diversity within a batch is non-negotiable.** No two posts in the
   same batch may use the same scene, the same characters, the same location
   type, the same composition, or the same treatment. If you're about to
   generate "young female caregiver + elderly woman in a living room" for the
   second time, STOP and pick a different scene category.

2. **Regional specificity for Johnson Services is non-negotiable.** Every
   Johnson caption MUST mention the service area. Use `Rhein-Neckar` and/or
   `Rhein-Main` explicitly, and name at least one real city from the whitelist
   below. This filters out inquiries from regions we cannot serve.

3. **City whitelist for Johnson Services.** When naming a city (for social
   proof, testimonials, location tags, etc.) you may ONLY use:
   - **Rhein-Neckar**: Mannheim, Heidelberg, Ludwigshafen, Weinheim, Speyer,
     Worms, Schwetzingen, Viernheim, Heppenheim, Bensheim
   - **Rhein-Main**: Frankfurt, Darmstadt, Wiesbaden, Offenbach, Hanau, Mainz,
     Rüsselsheim, Bad Homburg
   - **NEVER use**: Köln, Berlin, Hamburg, München, Stuttgart, Leipzig,
     Dresden, Düsseldorf, Nürnberg, Bremen, or any city outside the two
     metropolitan regions above. If a previous caption used an invalid city
     (the old ones used "Köln"), that was a bug — fix it.

4. **ICP rotation.** Each brand has multiple ICPs. Every batch must rotate
   through them — never generate two posts in a row targeting the same ICP.
   - Johnson: Betreuer, Erbgemeinschaften, Studenten, junge Familien, Kinder
     die die Wohnung ihrer Eltern auflösen
   - Rebelz: Trockenbauer, Bodenleger, Elektriker, Abdichter, Dachdecker,
     Maler, Fliesenleger

5. **German only.** Zero English words in any caption, image text, or
   hashtag. Address construction trades by name, formal Ihr-Form for Rebelz,
   Du-Form for Johnson Instagram (warmer), Sie-Form for Johnson Facebook
   (older demo).

6. **Budget discipline.** MAX 10 Gemini images per day. If you need more,
   split across days. Never shotgun 60 variants — pick the 10 best concepts.

7. **No stock-photo feel.** If the prompt would produce something that could
   come from Shutterstock, rewrite it. Specificity beats genericness every
   time.

## Hook formulas — rotate through all of these

Every caption has a hook (first line / first 5 words). Posts in the same
batch must use DIFFERENT hook formulas. Here are the 10 proven categories —
tag each caption with which one it's using to prevent accidental repetition:

| # | Formula | German example |
|---|---------|----------------|
| 1 | Curiosity | "Wussten Sie, dass 8 von 10 Haushaltsauflösungen zu teuer bezahlt werden?" |
| 2 | Story/Moment | "Letzte Woche in Heidelberg: Herr K. hatte 14 Tage, um die Wohnung seiner Mutter zu räumen." |
| 3 | Contrarian | "Entrümpelung muss nicht 3 Wochen dauern. Hier ist, warum." |
| 4 | Shock stat | "87 % der Erbgemeinschaften streiten wegen Kleinigkeiten. So vermeiden Sie das." |
| 5 | Vorher/Nachher | "Vorher: 4 volle Räume. Nachher: leer, gewischt, schlüsselfertig. In 2 Tagen." |
| 6 | Direct question | "Haben Sie schon einmal einen Umzug zwischen zwei Klausuren geplant?" |
| 7 | Personal/BTS | "Gestern in Mannheim-Neckarau: 80 Kartons, 2 Teams, ein erleichtertes Lächeln." |
| 8 | Scarcity | "Nur noch 3 Termine im Mai für Erbgemeinschaften im Rhein-Neckar-Raum." |
| 9 | Social proof | "147 zufriedene Kunden in Mannheim. Das neueste Feedback:" |
| 10 | Myth-bust | "Mythos: Entrümpelung ist Männerarbeit. Realität: Unser Team ist gemischt." |

## Visual scene categories — rotate within a batch

**Every post in a batch MUST use a different scene category.** In a 10-post
batch, use 10 different categories. Never repeat.

| # | Category | What it looks like |
|---|----------|--------------------|
| A | Hero / team action | Van with branded sign, team mid-work, crew portrait |
| B | Process / BTS | Macro of hands wrapping a vase, labelling a box, motion blur |
| C | Transformation | Before/after split screen, empty-vs-full, chaos-to-order |
| D | Human moment | Customer handshake, emotional smile, one face in natural light |
| E | Abstract / flat lay | Supplies arranged geometrically, symbolic composition |
| F | Data / stats card | Bold number card, testimonial card, price transparency |
| G | Text-first poster | Bold German typography as the hero element |
| H | Environment / regional | Skyline, landmark, street, Rhein bridge, Altstadt |
| I | Documentary flash | Direct flash, nighttime, candid, paparazzi-style |
| J | Aerial / top-down | Drone view, bird's eye of packed truck, flat overhead |

**Explicit negative constraint for Johnson:** Do NOT generate "young female
caregiver in blue shirt sitting with a white-haired elderly woman in a
bookshelf-lined living room surrounded by boxes labelled FOTOS / BÜCHER /
UMZUG." That is the exact repeating scene we are replacing. Zero tolerance
for it in new creative.

## Johnson caption structure template

Every Johnson caption follows this skeleton (with a different hook formula each time):

```
[Hook — one of the 10 formulas]

[2–4 sentences of body: paint the situation, empathize, or drop the value]

[Concrete proof or specific detail — a number, a timeframe, a location]

📍 Wir sind für Sie da im [Rhein-Neckar | Rhein-Main | Rhein-Neckar und Rhein-Main] Raum — [name 1–3 real cities from the whitelist].

👉 [CTA — johnson-services.de or "schreiben Sie uns"]

#Entrümpelung #[Region-Tag] #[ICP-Tag] #[ContentType-Tag] #JohnsonServices
```

Region tags to use: `#Mannheim`, `#Heidelberg`, `#RheinNeckar`, `#Ludwigshafen`,
`#Frankfurt`, `#Darmstadt`, `#RheinMain`, `#Wiesbaden`, `#Offenbach`.

## Rebelz caption structure template

```
[Hook addressing a specific trade by name — "Als Trockenbauer kennen Sie das..."]

[Pain point → consequence → better way, 2–4 sentences, formal Ihr-Form]

[Concrete Rebelz AI benefit — hours saved, fewer errors, a specific feature]

👉 Kostenloses Erstgespräch: rebelzai.com

#[Trade] #Baustellendoku #RebelzAI #[AngleTag]
```

## Quality checklist — run this before shipping any new batch

Before committing any new batch to git, walk through this list:

- [ ] Every caption has a DIFFERENT hook formula (no two #3 Contrarian in a row)
- [ ] Every post uses a DIFFERENT visual scene category (A–J)
- [ ] Every ICP appears at most twice per batch
- [ ] Every Johnson caption mentions Rhein-Neckar or Rhein-Main explicitly
- [ ] Every Johnson caption names at least one city from the whitelist
- [ ] Zero invalid cities anywhere (grep for Köln/Berlin/Hamburg/München)
- [ ] Zero English words anywhere (grep for obvious English tokens)
- [ ] No "young female caregiver + elderly woman in living room" scene
- [ ] Each image has a clearly different composition (top-down vs side, macro
  vs wide, etc.)
- [ ] Every caption ends with a CTA and 3–5 relevant hashtags

## Why this matters

Clarence's business depends on first paying customers. Johnson Services is
the priority because it's closer to revenue. Every repeating image is a lost
chance to hook someone new. Every missing region mention is an inbound
inquiry from someone we can't serve — that wastes Clarence's time. Every
generic hook is a post the algorithm won't push.

**Do not generate creative that you would scroll past.**
