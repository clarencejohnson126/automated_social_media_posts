"""Tests for content_planner."""

from datetime import date
from content_planner import plan_batch


def test_plan_batch_returns_28_posts():
    batch = plan_batch(start_date=date(2026, 4, 18))
    all_posts = []
    for account_key, posts in batch.items():
        all_posts.extend(posts)
    assert len(all_posts) == 28


def test_plan_batch_has_correct_accounts():
    batch = plan_batch(start_date=date(2026, 4, 18))
    assert set(batch.keys()) == {
        "rebelz-ai-ig", "rebelz-ai-fb",
        "johnson-services-ig", "johnson-services-fb",
    }


def test_each_account_has_7_posts():
    batch = plan_batch(start_date=date(2026, 4, 18))
    for account_key, posts in batch.items():
        assert len(posts) == 7, f"{account_key} has {len(posts)} posts, expected 7"


def test_posts_have_correct_dates():
    batch = plan_batch(start_date=date(2026, 4, 18))
    for account_key, posts in batch.items():
        dates = [p["scheduled_date"] for p in posts]
        expected = ["2026-04-18", "2026-04-20", "2026-04-22", "2026-04-24",
                    "2026-04-26", "2026-04-28", "2026-04-30"]
        assert dates == expected


def test_one_video_per_account():
    batch = plan_batch(start_date=date(2026, 4, 18))
    for account_key, posts in batch.items():
        videos = [p for p in posts if p["media_type"] == "video"]
        assert len(videos) == 1, f"{account_key} has {len(videos)} videos"


def test_johnson_rotates_icps():
    batch = plan_batch(start_date=date(2026, 4, 18))
    icps = [p["target_audience"] for p in batch["johnson-services-ig"]]
    assert len(set(icps)) >= 3


def test_rebelz_rotates_trades():
    batch = plan_batch(start_date=date(2026, 4, 18))
    trades = [p["target_audience"] for p in batch["rebelz-ai-ig"]]
    assert len(set(trades)) >= 3
