"""Tests for batch_manager."""

import json
from datetime import date
from pathlib import Path
from batch_manager import create_batch, load_manifest, approve_post, approve_all, reject_post, mark_published, get_next_unpublished


def test_create_batch_creates_manifest(tmp_path):
    batch_dir = create_batch(start_date=date(2026, 4, 18), base_dir=tmp_path)
    manifest_path = batch_dir / "manifest.json"
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text())
    assert len(manifest["accounts"]) == 4
    total_posts = sum(len(posts) for posts in manifest["accounts"].values())
    assert total_posts == 28


def test_approve_post(tmp_path):
    batch_dir = create_batch(start_date=date(2026, 4, 18), base_dir=tmp_path)
    approve_post(batch_dir, "rebelz-ai-ig", 1)

    manifest = load_manifest(batch_dir)
    post = manifest["accounts"]["rebelz-ai-ig"][0]
    assert post["approved"] is True


def test_approve_all(tmp_path):
    batch_dir = create_batch(start_date=date(2026, 4, 18), base_dir=tmp_path)
    approve_all(batch_dir)

    manifest = load_manifest(batch_dir)
    for account_key, posts in manifest["accounts"].items():
        for post in posts:
            assert post["approved"] is True, f"{account_key} post {post['index']} not approved"


def test_reject_post(tmp_path):
    batch_dir = create_batch(start_date=date(2026, 4, 18), base_dir=tmp_path)
    approve_post(batch_dir, "rebelz-ai-ig", 1)
    reject_post(batch_dir, "rebelz-ai-ig", 1)

    manifest = load_manifest(batch_dir)
    post = manifest["accounts"]["rebelz-ai-ig"][0]
    assert post["approved"] is False
    assert post["file_path"] is None
    assert post["caption"] is None


def test_mark_published(tmp_path):
    batch_dir = create_batch(start_date=date(2026, 4, 18), base_dir=tmp_path)
    approve_post(batch_dir, "rebelz-ai-ig", 1)
    mark_published(batch_dir, "rebelz-ai-ig", 1)

    manifest = load_manifest(batch_dir)
    post = manifest["accounts"]["rebelz-ai-ig"][0]
    assert post["published"] is True


def test_get_next_unpublished(tmp_path):
    batch_dir = create_batch(start_date=date(2026, 4, 18), base_dir=tmp_path)
    approve_all(batch_dir)

    post = get_next_unpublished(batch_dir, "rebelz-ai", "2026-04-18")
    assert post is not None
    assert post["scheduled_date"] == "2026-04-18"
    assert post["approved"] is True

    # Non-existent date
    post = get_next_unpublished(batch_dir, "rebelz-ai", "2099-01-01")
    assert post is None
