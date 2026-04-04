"""Publisher — posts to Facebook pages and Instagram via Meta Graph API."""

import time
import requests
from pathlib import Path
from config import META_ACCESS_TOKEN

GRAPH_API = "https://graph.facebook.com/v21.0"


def _get_page_access_token(page_id: str) -> str:
    """Get a page-specific access token."""
    resp = requests.get(
        f"{GRAPH_API}/{page_id}",
        params={
            "fields": "access_token",
            "access_token": META_ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def publish_to_facebook(
    page_id: str,
    image_path: str | Path,
    caption: str,
) -> dict:
    """Publish a photo post to a Facebook page."""
    page_token = _get_page_access_token(page_id)
    image_path = Path(image_path)

    with open(image_path, "rb") as f:
        resp = requests.post(
            f"{GRAPH_API}/{page_id}/photos",
            files={"source": (image_path.name, f, "image/png")},
            data={
                "message": caption,
                "access_token": page_token,
            },
        )
    resp.raise_for_status()
    return resp.json()


def publish_video_to_facebook(
    page_id: str,
    video_path: str | Path,
    caption: str,
) -> dict:
    """Publish a video post to a Facebook page."""
    page_token = _get_page_access_token(page_id)
    video_path = Path(video_path)

    with open(video_path, "rb") as f:
        resp = requests.post(
            f"{GRAPH_API}/{page_id}/videos",
            files={"source": (video_path.name, f, "video/mp4")},
            data={
                "description": caption,
                "access_token": page_token,
            },
        )
    resp.raise_for_status()
    return resp.json()


def publish_to_instagram(
    instagram_account_id: str,
    image_url: str,
    caption: str,
) -> dict:
    """Publish a photo to Instagram via Content Publishing API.

    Two-step process:
    1. Create a media container with the image URL
    2. Publish the container

    Note: image_url must be publicly accessible.
    """
    # Step 1: Create container
    resp = requests.post(
        f"{GRAPH_API}/{instagram_account_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": META_ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    container_id = resp.json()["id"]

    # Step 2: Publish
    resp = requests.post(
        f"{GRAPH_API}/{instagram_account_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": META_ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    return resp.json()


def publish_video_to_instagram(
    instagram_account_id: str,
    video_url: str,
    caption: str,
) -> dict:
    """Publish a video (Reel) to Instagram via Content Publishing API."""
    # Step 1: Create video container
    resp = requests.post(
        f"{GRAPH_API}/{instagram_account_id}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": META_ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    container_id = resp.json()["id"]

    # Step 2: Wait for processing, then publish
    for _ in range(30):  # Wait up to 5 minutes
        status_resp = requests.get(
            f"{GRAPH_API}/{container_id}",
            params={
                "fields": "status_code",
                "access_token": META_ACCESS_TOKEN,
            },
        )
        status = status_resp.json().get("status_code")
        if status == "FINISHED":
            break
        time.sleep(10)

    resp = requests.post(
        f"{GRAPH_API}/{instagram_account_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": META_ACCESS_TOKEN,
        },
    )
    resp.raise_for_status()
    return resp.json()


def upload_image_to_facebook_and_get_url(page_id: str, image_path: Path) -> str:
    """Upload image to Facebook (unpublished) to get a public URL for Instagram.

    Returns the public URL of the uploaded image.
    """
    page_token = _get_page_access_token(page_id)

    with open(image_path, "rb") as f:
        resp = requests.post(
            f"{GRAPH_API}/{page_id}/photos",
            files={"source": (image_path.name, f, "image/png")},
            data={
                "published": "false",
                "access_token": page_token,
            },
        )
    resp.raise_for_status()
    photo_id = resp.json()["id"]

    # Get the image URL
    resp = requests.get(
        f"{GRAPH_API}/{photo_id}",
        params={
            "fields": "images",
            "access_token": page_token,
        },
    )
    resp.raise_for_status()
    images = resp.json().get("images", [])
    if images:
        return images[0]["source"]  # Largest image
    raise ValueError(f"No image URL returned for photo {photo_id}")
