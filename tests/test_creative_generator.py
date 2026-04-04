"""Tests for creative_generator."""

from creative_generator import build_image_prompt


def test_build_prompt_rebelz_ig():
    prompt = build_image_prompt(
        brand="rebelz-ai",
        platform="ig",
        content_type="educational",
        target_audience="Trockenbauer",
    )
    assert "1080" in prompt
    assert "Playfair" in prompt
    assert "Trockenbauer" in prompt


def test_build_prompt_johnson_ig():
    prompt = build_image_prompt(
        brand="johnson-services",
        platform="ig",
        content_type="social_proof",
        target_audience="Betreuer",
    )
    assert "1080" in prompt and "1350" in prompt
    assert "DM Sans" in prompt


def test_build_prompt_johnson_fb():
    prompt = build_image_prompt(
        brand="johnson-services",
        platform="fb",
        content_type="pain_point",
        target_audience="Erbgemeinschaften",
    )
    assert "1200" in prompt and "630" in prompt


def test_build_prompt_rebelz_fb():
    prompt = build_image_prompt(
        brand="rebelz-ai",
        platform="fb",
        content_type="branded",
        target_audience="Maler",
    )
    assert "1200" in prompt and "630" in prompt
    assert "Maler" in prompt
    assert "Playfair" in prompt
