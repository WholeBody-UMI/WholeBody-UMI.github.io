"""Encode distinct robot recordings for the task carousels.

Usage: python3 scripts/build_demos.py --material ../material
Requires FFmpeg. Originals are preserved. CLIP_WINDOWS defines the requested
source-time edits for Ball Toss and Locomotion Pick-and-Place.
"""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "drawer": [
        "drawer_demo/0810/drawer_success_1-1.mp4",
        "drawer_demo/0810/drawer_success_2-1.mp4",
        "drawer_demo/0810/drawer_success_3-1.mp4",
        "drawer_demo/IMG_4109.mov",
    ],
    "shelf": [
        "shelf_demo/shelf0825_1-1.mp4",
        "shelf_demo/shelf0825_2-1.mp4",
        "shelf_demo/shelf0825_3-1.mp4",
        "shelf_demo/shelf_0825_4-1.mp4",
    ],
    "toss": [
        "tossing/ball_toss_0817_demo1-1.mp4",
        "tossing/toss_0816.mov",
        "tossing/toss_0816_2.mov",
    ],
    "loco-pnp": [
        "Loco-PnP/walk_pnp_0818.MOV",
        "Loco-PnP/IMG_4116.mov",
        "Loco-PnP/walkpnp0902.mov",
        "Loco-PnP/walkpnp0902_2.mov",
    ],
}

# Start and end times in the original recording; None keeps the remainder.
CLIP_WINDOWS = {
    "toss-1": (0, 12),
    "toss-2": (0, 10),
    "toss-3": (0, 12),
    "loco-pnp-1": (15, None),
    "loco-pnp-2": (3, None),
    "loco-pnp-3": (3, None),
    "loco-pnp-4": (0, 24),
}


def duration(path):
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]))


def encode(job):
    source, name = job
    video = ROOT / "static/videos/demos" / f"{name}.mp4"
    poster = ROOT / "static/images/umi-prior/demos" / f"{name}.jpg"
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    start, end = CLIP_WINDOWS.get(name, (0, None))
    seek = ["-ss", str(start)] if start else []
    limit = end - start if end is not None else None
    trim = ["-t", str(limit)] if limit is not None else []
    needs_trim = False
    if name in CLIP_WINDOWS and video.exists():
        expected = duration(source) - start
        if limit is not None:
            expected = min(expected, limit)
        needs_trim = abs(duration(video) - expected) > 0.1
    if not video.exists() or video.stat().st_mtime < source.stat().st_mtime or needs_trim:
        temporary = video.with_suffix(".encoding.mp4")
        subprocess.run([
            *command, *seek, "-i", str(source), "-map", "0:v:0", "-map", "0:a:0?",
            "-vf", "scale=1280:720:force_original_aspect_ratio=decrease:flags=lanczos,"
            "pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30",
            "-c:v", "libx264", "-preset", "medium", "-crf", "21",
            "-threads", "4", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", *trim, str(temporary),
        ], check=True)
        temporary.replace(video)
    # Upgrade older silent exports without another lossy video encode.
    def has_audio(path):
        streams = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=codec_type", "-of", "json", str(path),
        ]))["streams"]
        return bool(streams)

    if has_audio(source) and not has_audio(video):
        temporary = video.with_suffix(".audio.mp4")
        subprocess.run([
            *command, "-i", str(video), *seek, "-i", str(source),
            "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", *trim, str(temporary),
        ], check=True)
        temporary.replace(video)
    subprocess.run([*command, "-i", str(video), "-frames:v", "1", "-vf", "scale=960:540",
                    "-q:v", "3", str(poster)], check=True)
    print(f"Built {name}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--material", type=Path, required=True)
    parser.add_argument("--task", choices=SOURCES, help="Rebuild only one task")
    args = parser.parse_args()
    jobs = [(args.material / "video" / path, f"{task}-{index}")
            for task, sources in SOURCES.items() if args.task is None or task == args.task
            for index, path in enumerate(sources, 1)]
    for source, _ in jobs:
        if not source.is_file():
            parser.error(f"Missing source: {source}")
    (ROOT / "static/videos/demos").mkdir(parents=True, exist_ok=True)
    (ROOT / "static/images/umi-prior/demos").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(encode, jobs))


if __name__ == "__main__":
    main()
