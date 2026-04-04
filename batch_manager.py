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
        f"\U0001f4f1 Neue Social-Media-Batch bereit!\n\n"
        f"Zeitraum ab: {batch_date}\n"
        f"Anzahl Posts: {total}\n"
        f"Accounts: Rebelz AI (IG+FB) + Johnson Services (IG+FB)\n\n"
        f"Bitte in Claude Code pr\u00fcfen und freigeben."
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
