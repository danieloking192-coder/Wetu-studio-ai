"""Package validated MP4 renditions into HLS and DASH test outputs."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

PROFILES = (
    ("mobile_saver", 854, 480, 900, 64, "master.mobile_saver_480p.mp4"),
    ("mobile", 1280, 720, 1800, 96, "master.mobile_720p.mp4"),
    ("standard", 1920, 1080, 3500, 128, "master.standard_1080p.mp4"),
)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def package(renditions: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)

    inputs: list[tuple[str, int, int, int, int, Path]] = []
    for name, width, height, video_kbps, audio_kbps, filename in PROFILES:
        path = renditions / filename
        if not path.exists():
            legacy = renditions / f"{name}.mp4"
            if legacy.exists():
                path = legacy
            else:
                raise FileNotFoundError(
                    f"No validated rendition for {name}: expected {path.name}"
                )
        inputs.append((name, width, height, video_kbps, audio_kbps, path))

    hls = output / "hls"
    hls.mkdir(parents=True, exist_ok=True)
    variants = []

    for name, width, height, video_kbps, audio_kbps, path in inputs:
        variant_dir = hls / name
        variant_dir.mkdir(parents=True, exist_ok=True)
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(path),
                "-c",
                "copy",
                "-f",
                "hls",
                "-hls_time",
                "4",
                "-hls_playlist_type",
                "vod",
                "-hls_segment_filename",
                str(variant_dir / "seg_%03d.ts"),
                str(variant_dir / "index.m3u8"),
            ]
        )
        variants.append((name, width, height, video_kbps + audio_kbps))

    lines = ["#EXTM3U", "#EXT-X-VERSION:3"]
    for name, width, height, bandwidth_kbps in variants:
        lines.extend(
            [
                f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth_kbps * 1000},RESOLUTION={width}x{height}",
                f"{name}/index.m3u8",
            ]
        )
    (hls / "master.m3u8").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    dash = output / "dash"
    dash.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y"]
    for _, _, _, _, _, path in inputs:
        cmd.extend(["-i", str(path)])
    for index in range(len(inputs)):
        cmd.extend(["-map", f"{index}:v:0", "-map", f"{index}:a:0"])
    cmd.extend(
        [
            "-c",
            "copy",
            "-adaptation_sets",
            "id=0,streams=v id=1,streams=a",
            "-seg_duration",
            "4",
            "-use_template",
            "1",
            "-use_timeline",
            "1",
            "-f",
            "dash",
            str(dash / "manifest.mpd"),
        ]
    )
    run(cmd)

    return {
        "variants": [item[0] for item in inputs],
        "hls_master": "hls/master.m3u8",
        "dash_manifest": "dash/manifest.mpd",
        "deployment_active": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("renditions", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = package(args.renditions, args.output)
    (args.output / "package_manifest.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print("ADAPTIVE PACKAGE: PASS")


if __name__ == "__main__":
    main()
