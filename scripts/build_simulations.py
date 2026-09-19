"""Prepare simulation videos and posters for the website.

Usage: python3 scripts/build_simulations.py --material ../material
Simulation videos are compressed for browser playback at their original
resolution, frame rate, and duration, without interpolation or motion changes.
"""

import argparse
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "drawer": "sim_demos/drawer0805.mp4",
    "shelf": "sim_demos/shelf0730.mp4",
    "toss": "sim_demos/toss0815.mp4",
    "locomotion-pick-and-place": "sim_demos/walk-pnp-bottle.mp4",
    "squat": "sim_demos/motion_prior_test/01_squat.mp4",
    "dance-step": "sim_demos/motion_prior_test/02_dance_step.mp4",
    "pickup-carry": "sim_demos/motion_prior_test/03_pickup_carry.mp4",
    "jog": "sim_demos/motion_prior_test/04_jog.mp4",
    # Use the revised, smoother source in the material root, not the older test render.
    "diversity-stable": "05_diversity.mp4",
}
MOTION_SAMPLES = {"squat", "dance-step", "pickup-carry", "jog"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--material", type=Path, required=True)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--motion-only", action="store_true", help="Prepare only motion-prior samples")
    selection.add_argument("--only", nargs="+", choices=sorted(SOURCES), help="Prepare selected videos")
    args = parser.parse_args()
    videos = ROOT / "static/videos/simulation"
    posters = ROOT / "static/images/umi-prior/simulation"
    sources = {name: source for name, source in SOURCES.items()
               if (not args.motion_only or name in MOTION_SAMPLES)
               and (not args.only or name in args.only)}
    for source in sources.values():
        if not (args.material / source).is_file():
            parser.error(f"Missing source: {source}")
    videos.mkdir(parents=True, exist_ok=True)
    posters.mkdir(parents=True, exist_ok=True)
    for name, source in sources.items():
        video = videos / f"{name}.mp4"
        temporary = video.with_suffix(".encoding.mp4")
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
        codec = ["-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
                 "-threads", "4", "-g", "60", "-c:a", "aac", "-b:a", "128k"]
        subprocess.run([*command, "-i", str(args.material / source),
                        "-map", "0:v:0", "-map", "0:a:0?", *codec,
                        "-movflags", "+faststart", str(temporary)], check=True)
        temporary.replace(video)
        subprocess.run([*command, "-i", str(video), "-frames:v", "1", "-vf", "scale=960:-2",
                        "-q:v", "3", str(posters / f"{name}.jpg")], check=True)
        print(f"Built {name}", flush=True)


if __name__ == "__main__":
    main()
