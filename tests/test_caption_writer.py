"""Tests for caption_writer."""

from caption_writer import write_caption


def test_caption_is_german():
    caption = write_caption(
        brand="rebelz-ai",
        platform="ig",
        content_type="educational",
        target_audience="Trockenbauer",
    )
    assert isinstance(caption, str)
    assert len(caption) > 20
    # Should not contain common English words
    for word in ["the", "and", "with", "your"]:
        assert word.lower() not in caption.lower().split()


def test_caption_has_hashtags():
    caption = write_caption(
        brand="johnson-services",
        platform="fb",
        content_type="social_proof",
        target_audience="Betreuer",
    )
    assert "#" in caption


def test_caption_has_cta():
    caption = write_caption(
        brand="johnson-services",
        platform="ig",
        content_type="pain_point",
        target_audience="Studenten die umziehen",
    )
    assert any(kw in caption.lower() for kw in [
        "kontakt", "anruf", "nachricht", "whatsapp", "link", "bio", "jetzt",
    ])
