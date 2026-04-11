"""CLI entry point: generate a new content batch."""

import sys
from datetime import date, timedelta
from pathlib import Path
from config import BATCHES_DIR
from batch_manager import create_batch, send_whatsapp_reminder, load_manifest, save_manifest
from caption_writer import write_captions_for_batch
from creative_generator import generate_images_for_batch
from render_videos import render_for_post


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

    # Step 4: Render videos via Remotion (one variant per video slot per account)
    print("[4/5] Rendering videos (Remotion)...")
    manifest = load_manifest(batch_dir)
    for account_key, posts in manifest["accounts"].items():
        video_slots = [p for p in posts if p["media_type"] == "video"]
        for variant_index, p in enumerate(video_slots):
            brand = p["brand"]
            platform = p["platform"]
            out_rel = f"{account_key}/post-{p['index']:02d}.mp4"
            out_abs = batch_dir / out_rel
            if out_abs.exists():
                print(f"  skip {out_rel} (exists)")
                p["file_path"] = out_rel
                continue
            try:
                render_for_post(brand, platform, out_abs, variant_index)
                p["file_path"] = out_rel
            except Exception as e:
                print(f"  ❌ failed {out_rel}: {e}")
    save_manifest(batch_dir, manifest)

    # Step 5: Send WhatsApp reminder
    print("[5/5] Sending WhatsApp reminder...")
    send_whatsapp_reminder(batch_dir)

    print()
    print("=== Done! ===")
    print(f"Review batch in Claude Code: 'show me the batch'")
    print(f"Approve: 'approve batch' or 'approve all'")


if __name__ == "__main__":
    main()
