"""Tests for publisher."""

from unittest.mock import patch, MagicMock
from publisher import _get_page_access_token, publish_to_facebook, publish_to_instagram


def test_get_page_access_token_calls_api():
    with patch("publisher.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            json=lambda: {"access_token": "page_token_123"},
            raise_for_status=lambda: None,
        )
        token = _get_page_access_token("123456")
        assert token == "page_token_123"


def test_publish_to_facebook_photo(tmp_path):
    # Create a fake image file
    fake_image = tmp_path / "test.png"
    fake_image.write_bytes(b"fake png data")

    with patch("publisher.requests.post") as mock_post, \
         patch("publisher._get_page_access_token", return_value="page_tok"):
        mock_post.return_value = MagicMock(
            json=lambda: {"id": "post_789"},
            raise_for_status=lambda: None,
        )
        result = publish_to_facebook(
            page_id="123",
            image_path=str(fake_image),
            caption="Test caption",
        )
        assert result["id"] == "post_789"


def test_publish_to_instagram_two_step():
    with patch("publisher.requests.post") as mock_post:
        # First call: create container, second call: publish
        mock_post.side_effect = [
            MagicMock(json=lambda: {"id": "container_123"}, raise_for_status=lambda: None),
            MagicMock(json=lambda: {"id": "media_456"}, raise_for_status=lambda: None),
        ]
        result = publish_to_instagram(
            instagram_account_id="ig_789",
            image_url="https://example.com/image.png",
            caption="Test IG caption",
        )
        assert result["id"] == "media_456"
        assert mock_post.call_count == 2
