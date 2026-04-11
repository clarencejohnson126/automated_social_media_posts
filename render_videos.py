#!/usr/bin/env python3
"""
Render videos for a batch using the Remotion project at
  Graph-Growth-Agents/creatives/video-ads/

This is the bridge between the Automated Social Media pipeline and
the existing Remotion compositions. It's called by generate_batch.py
for any post whose media_type == "video".

Mapping (composition_id -> aspect ratio / brand):
  RebelzSocialProof-IG      1080x1080   rebelz-ai   ig
  RebelzSocialProof-FB      1200x630    rebelz-ai   fb
  JohnsonSocialProof-IG     1080x1350   johnson-services   ig
  JohnsonSocialProof-FB     1200x630    johnson-services   fb

Legacy Rebelz IG compositions (1080x1080 only) — used as alternates:
  TimeAnimation, ChatChaos, BeforeAfter

USAGE:
    python3 render_videos.py --brand rebelz-ai --platform ig \\
            --composition RebelzSocialProof-IG \\
            --out batches/2026-04-06/rebelz-ai-ig/post-05.mp4

Or programmatically:
    from render_videos import render_composition
    render_composition("RebelzSocialProof-IG", Path("out.mp4"))
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REMOTION_PROJECT = Path(
    "/Users/clarence/Desktop/AUTOMATED ADS/Graph-Growth-Agents/creatives/video-ads"
)

# brand + platform -> canonical composition id
DEFAULT_COMPOSITIONS = {
    ("rebelz-ai",        "ig"): "RebelzSocialProof-IG",
    ("rebelz-ai",        "fb"): "RebelzSocialProof-FB",
    ("johnson-services", "ig"): "JohnsonSocialProof-IG",
    ("johnson-services", "fb"): "JohnsonSocialProof-FB",
}

# Additional compositions usable as variants (same dimensions)
VARIANTS = {
    ("rebelz-ai", "ig"): [
        "RebelzSocialProof-IG",
        "TimeAnimation",
        "ChatChaos",
        "BeforeAfter",
    ],
    ("rebelz-ai", "fb"): ["RebelzSocialProof-FB"],
    ("johnson-services", "ig"): ["JohnsonSocialProof-IG"],
    ("johnson-services", "fb"): ["JohnsonSocialProof-FB"],
}


def render_composition(composition_id: str, output: Path) -> Path:
    """Render a Remotion composition to the given output path.

    Returns the absolute output path on success, raises on failure.
    """
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "npx", "remotion", "render",
        composition_id,
        str(output),
        "--codec", "h264",
    ]
    print(f"[remotion] rendering {composition_id} -> {output}")
    result = subprocess.run(cmd, cwd=REMOTION_PROJECT, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(
            f"Remotion render failed for {composition_id} "
            f"(exit {result.returncode})"
        )
    if not output.exists():
        raise RuntimeError(f"Remotion reported success but {output} missing")
    print(f"[remotion] ok  {output.stat().st_size / 1024:.0f} KiB")
    return output


def render_for_post(
    brand: str,
    platform: str,
    output: Path,
    variant_index: int = 0,
) -> Path:
    """Render the right composition for a given brand/platform/post.

    variant_index picks between VARIANTS so batches with multiple video
    slots get different content. Falls back to the default composition
    if variant_index is out of range.
    """
    variants = VARIANTS.get((brand, platform), [])
    if not variants:
        raise ValueError(f"No Remotion compositions configured for {brand}/{platform}")
    composition = variants[variant_index % len(variants)]
    return render_composition(composition, output)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--brand", required=True, choices=["rebelz-ai", "johnson-services"])
    p.add_argument("--platform", required=True, choices=["ig", "fb"])
    p.add_argument("--composition", help="override composition id")
    p.add_argument("--variant", type=int, default=0, help="variant index (0-based)")
    p.add_argument("--out", required=True, help="output mp4 path")
    args = p.parse_args()

    out = Path(args.out)
    if args.composition:
        render_composition(args.composition, out)
    else:
        render_for_post(args.brand, args.platform, out, args.variant)


if __name__ == "__main__":
    main()
