# Social Media Auto-Poster — Design Document

**Date**: 2026-04-04
**Author**: Clarence + Claude
**Status**: Approved

## Goal

Fully automated social media posting every 2 days across 4 accounts (Rebelz AI IG + FB, Johnson Services IG + FB). Batch-generated every 2 weeks, approved once, then auto-published via cloud cron.

## Accounts

| Brand | Platform | Page/Account ID | Post Time (Berlin) | Format |
|-------|----------|----------------|---------------------|--------|
| Rebelz AI | Instagram | TBD (needs linking) | 19:00 | 1080x1080 square, black/white, Playfair Display, Bauhaus |
| Rebelz AI | Facebook | 708377165697175 | 19:00 | 1200x630 landscape, black/white, text-heavy tips |
| Johnson Services | Instagram | 17841458145133488 | 09:00 | 1080x1350 vertical, blue (#005b8c)/white, DM Sans, lifestyle |
| Johnson Services | Facebook | 333849409814429 | 09:00 | 1200x630 landscape, blue/white, before/after or testimonial |

## Architecture

Two-phase system with GitHub repo (`clarencejohnson126/automated_social_media_posts`) as bridge between local generation and cloud publishing.

### Phase 1: Batch Generation (local, every 2 weeks)

Triggered manually in Claude Code. Generates 28 posts (7 per account).

```
content_planner.py
  → Picks 7 content types per account (rotate A-E: educational, social proof, pain-point, mixed, other)
  → Johnson Services: rotates ICPs (Betreuer, Erbgemeinschaften, Studenten, junge Familien, Kinder/Eltern)
  → Rebelz AI: rotates Handwerk trades (Trockenbauer, Bodenleger, Elektriker, etc.)

creative_generator.py
  → Gemini (gemini-3.1-flash-image-preview) generates 6 images per account (24 total)
  → Brand-specific prompts per format style
  → MAX 10 Gemini images per day (spread across 3 days if needed)

video_generator.py
  → Remotion renders 1 video per account (4 total)
  → Brand-matched style

caption_writer.py
  → German captions, hashtags, CTAs
  → Johnson: empathetic, trustworthy tone
  → Rebelz: direct, pain-point-first tone

batch_manager.py
  → Creates manifest.json with schedule, captions, file paths
  → Sends WhatsApp reminder via wacli
```

**Output structure:**
```
batches/2026-04-18/
├── manifest.json
├── rebelz-ai-ig/
│   ├── post-01.png ... post-06.png
│   └── post-07.mp4
├── rebelz-ai-fb/
│   ├── post-01.png ... post-06.png
│   └── post-07.mp4
├── johnson-services-ig/
│   ├── post-01.png ... post-06.png
│   └── post-07.mp4
└── johnson-services-fb/
    ├── post-01.png ... post-06.png
    └── post-07.mp4
```

### Phase 2: Approval & Push to GitHub

1. Clarence opens Claude Code, says "show batch" or "approve batch"
2. Claude shows each post (image + caption + scheduled date)
3. Clarence approves all or rejects specific posts
4. Rejected posts regenerated, re-approved
5. manifest.json updated with `"approved": true` per post
6. Approved batch pushed to GitHub repo

### Phase 3: Daily Publisher (RemoteTrigger, Anthropic cloud)

Two RemoteTrigger cron jobs on Anthropic's cloud infrastructure:

| Trigger | Cron (UTC) | Schedule (Berlin) | Action |
|---------|------------|-------------------|--------|
| johnson-services-publisher | `3 7 * * *` | Daily 09:03 | Publish next approved Johnson post to FB + IG |
| rebelz-ai-publisher | `3 17 * * *` | Daily 19:03 | Publish next approved Rebelz post to FB + IG |

Each trigger:
1. Clones the GitHub repo
2. Reads manifest.json from current batch
3. Finds the next post scheduled for today
4. Checks approval status — skip if not approved
5. Uploads image/video to Meta via Graph API
6. Creates organic post on FB page + IG account
7. Commits manifest update (marks post as "published") and pushes

**Environment**: Anthropic Cloud (env_01UNNVABcgo5t1tm35HUeZao)
**Repo**: https://github.com/clarencejohnson126/automated_social_media_posts
**Credentials**: Embedded in trigger prompt (private to Clarence's Anthropic account)

## Content Types (A-E Rotation)

- **A) Educational** — tips, industry insights, "Wussten Sie schon?"
- **B) Social proof** — before/after, testimonials, project showcases
- **C) Pain-point** — specific relatable problems
- **D) Mixed/branded** — company updates, team, behind-the-scenes
- **E) Engagement** — questions, polls, seasonal content

## Branding

### Rebelz AI
- Colors: Black + White
- Font: Playfair Display
- Niche: Handwerk & Bau only
- Tone: Direct, pain-point-first, formal German (Ihr-Form)
- Trades: Trockenbauer, Bodenleger, Elektriker, Abdichter, Dachdecker, Maler, Fliesenleger

### Johnson Services
- Colors: Blue (#005b8c) + White, accent lime (#9DFF20)
- Font: DM Sans
- Tone: Empathetic, trustworthy — "Zuverlässig, Sauber, Günstig"
- ICPs: Betreuer, Erbgemeinschaften, Studenten, junge Familien, Kinder die Eltern-Wohnung auflösen
- Website: johnson-services.de

## Modules

| Module | Purpose |
|--------|---------|
| `content_planner.py` | Content type + ICP/trade rotation per batch |
| `creative_generator.py` | Gemini image prompts with 4 brand styles |
| `video_generator.py` | Remotion render wrapper (1 video per account) |
| `caption_writer.py` | German captions, hashtags, CTAs |
| `batch_manager.py` | Manifest creation, approval tracking, WhatsApp reminders |
| `publisher.py` | Meta Graph API: FB page posts + IG content publishing |
| `config.py` | Settings, tokens, page IDs, IG account IDs from .env |

## Prerequisites

- [ ] Link @rebelz_ai Instagram to Rebelz AI Facebook page in Meta Business Suite
- [ ] Verify Meta token has `pages_manage_posts` and `instagram_basic` permissions
- [x] Create GitHub repo (clarencejohnson126/automated_social_media_posts)

## Constraints

- MAX 10 Gemini images per day (spread batch generation across 3 days if needed)
- ALL content 100% German
- No Docker/K8s — local generation, cloud cron for publishing
- Budget: €0 (organic posts only, no boost)
