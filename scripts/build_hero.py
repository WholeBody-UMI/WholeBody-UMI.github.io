"""Build the sticker-free hero from original footage (requires ffmpeg).

Usage: python3 scripts/build_hero.py --material ../material
The four task groups follow the reference GIF: drawer, shelf, toss, loco-PnP.
Each group contains human collection, simulation, and robot execution.
"""

import argparse
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DURATION = 21.94
# Crops are in the original, auto-rotated video coordinates.
SOURCES = [
    ("human_collect/drawer_human.MOV", "crop=1080:1818:0:0"),
    ("sim_demos/drawer0805.mp4", "crop=400:674:320:20"),
    ("video/drawer_demo/0810/drawer_success_3-1.mp4", "crop=632:1064:0:8"),
    ("human_collect/shelf_pnp.MOV", "crop=1080:1818:0:0"),
    ("sim_demos/shelf0730.mp4", "crop=400:674:320:20"),
    ("video/shelf_demo/shelf0825_1-1.mp4", "crop=632:1064:440:8"),
    ("human_collect/toss_human.MOV", "crop=1080:1818:0:0"),
    ("sim_demos/toss0815.mp4", "crop=400:674:320:20"),
    ("video/tossing/ball_toss_0817_demo1-1.mp4", "crop=632:1064:420:8"),
    ("human_collect/loco-pnp_human.MOV", "crop=1080:1818:0:0"),
    ("sim_demos/walk-pnp-bottle.mp4", "crop=400:674:320:20"),
    ("video/Loco-PnP/walk_pnp_0818.MOV", "crop=632:1064:900:8"),
]


def run(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--material", type=Path, required=True)
    args = parser.parse_args()
    video_dir = ROOT / "static/videos"
    image_dir = ROOT / "static/images/umi-prior"
    inputs, filters = [], []
    for index, (source, crop) in enumerate(SOURCES):
        path = args.material / source
        if not path.is_file():
            parser.error(f"Missing source: {path}")
        inputs += ["-stream_loop", "-1", "-i", str(path)]
        filters.append(
            f"[{index}:v]setpts=(PTS-STARTPTS)/1.5,trim=duration={DURATION},"
            f"fps=30,{crop},scale=316:532:flags=lanczos,setsar=1,"
            f"pad=320:540:2:4:color=0xe8edf1,format=yuv420p[v{index}]"
        )
    layout = "|".join(f"{index % 6 * 320}_{index // 6 * 540}" for index in range(12))
    filters.append("".join(f"[v{i}]" for i in range(12)) + f"xstack=inputs=12:layout={layout}[out]")
    desktop = video_dir / "hero-montage.mp4"
    run([*inputs, "-filter_complex", ";".join(filters), "-map", "[out]", "-an",
         "-t", str(DURATION), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-movflags", "+faststart", str(desktop)])
    # Preserve all four triptychs on portrait screens, in reading order.
    mobile = video_dir / "hero-montage-mobile.mp4"
    run(["-i", str(desktop), "-filter_complex",
         "[0:v]split=4[a][b][c][d];"
         "[a]crop=960:540:0:0[a0];[b]crop=960:540:960:0[b0];"
         "[c]crop=960:540:0:540[c0];[d]crop=960:540:960:540[d0];"
         "[a0][b0][c0][d0]vstack=inputs=4,scale=720:1620:flags=lanczos[out]",
         "-map", "[out]", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-movflags", "+faststart", str(mobile)])
    for video, name in [(desktop, "hero-montage-desktop"), (mobile, "hero-montage-mobile")]:
        run(["-i", str(video), "-frames:v", "1", "-q:v", "2", str(image_dir / f"{name}.jpg")])


if __name__ == "__main__":
    main()
