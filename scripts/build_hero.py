"""Build the anonymous hero with calibrated head-covering stickers (requires ffmpeg).

Usage: python3 scripts/build_hero.py --material ../material
The four task groups are drawer, shelf, toss, and loco-PnP. Each group contains
human collection with a face-covering sticker, simulation, and robot execution.
"""

import argparse
import json
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
STICKER = ROOT / "scripts/assets/anon-cat-sticker.png"
STICKER_WIDTH = 68
STICKER_HEIGHT = round(STICKER_WIDTH * 184 / 195)
# The opaque cat face lies below/right of the image center; transparent ears
# must not be counted as coverage. Align the human head with that opaque core.
STICKER_ANCHOR = (0.60 * STICKER_WIDTH, 0.62 * STICKER_HEIGHT)
TRACK_FILE = ROOT / "scripts/assets/hero-head-tracks.json"


def run(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def interpolated_expression(keyframes, axis, offset, fps):
    """Interpolate output-frame coordinates, including adjacent frames at cuts.

    Use a balanced expression tree to avoid FFmpeg's expression nesting limit.
    Source-loop jumps have keyframes on both sides and never interpolate across
    an entire sampling interval.
    """
    segments = []
    for start, end in zip(keyframes, keyframes[1:]):
        value = start[axis] + offset
        slope = (end[axis] - start[axis]) * fps / (end[0] - start[0])
        segments.append((end[0] / fps,
                         f"{value:.4f}+{slope:.4f}*(t-{start[0] / fps:.8f})"))
    segments.append((float("inf"), f"{keyframes[-1][axis] + offset:.4f}"))

    def branch(items):
        if len(items) == 1:
            return items[0][1]
        middle = len(items) // 2
        return (f"if(lt(t,{items[middle - 1][0]:.8f}),"
                f"{branch(items[:middle])},{branch(items[middle:])})")

    return branch(segments)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--material", type=Path, required=True)
    args = parser.parse_args()
    video_dir = ROOT / "static/videos"
    image_dir = ROOT / "static/images/umi-prior"
    if not STICKER.is_file():
        parser.error(f"Missing sticker: {STICKER}")
    inputs, filters = [], []
    for index, (source, crop) in enumerate(SOURCES):
        path = args.material / source
        if not path.is_file():
            parser.error(f"Missing source: {path}")
        inputs += ["-stream_loop", "-1", "-i", str(path)]
        filters.append(
            f"[{index}:v]setpts=(PTS-STARTPTS)/1.5,trim=duration={DURATION},"
            f"fps=30,{crop},scale=158:266:flags=lanczos,setsar=1,"
            f"pad=160:270:1:2:color=0xe8edf1,format=yuv420p[v{index}]"
        )
    inputs += ["-loop", "1", "-i", str(STICKER)]
    layout = "|".join(f"{index % 6 * 160}_{index // 6 * 270}" for index in range(12))
    filters.append(f"[12:v]scale={STICKER_WIDTH}:{STICKER_HEIGHT},split=4[st0][st1][st2][st3]")
    track_data = json.loads(TRACK_FILE.read_text())
    tiles = [f"v{i}" for i in range(12)]
    for index, track in enumerate(track_data["tracks"]):
        x = interpolated_expression(track["keyframes"], 1,
                                    -STICKER_ANCHOR[0], track_data["fps"])
        y = interpolated_expression(track["keyframes"], 2,
                                    -STICKER_ANCHOR[1], track_data["fps"])
        output = f"anonymous{index}"
        # Apply within the human tile so stickers cannot cover a neighboring robot.
        filters.append(f"[v{index * 3}][st{index}]overlay=x='{x}':y='{y}':eval=frame[{output}]")
        tiles[index * 3] = output
    filters.append("".join(f"[{tile}]" for tile in tiles) +
                   f"xstack=inputs=12:layout={layout}[montage]")
    filters.extend([
        "[montage]split=2[wide][portrait]",
        "[wide]scale=1280:720:flags=lanczos[desktop]",
        "[portrait]split=4[a][b][c][d]",
        "[a]crop=480:270:0:0[a0]", "[b]crop=480:270:480:0[b0]",
        "[c]crop=480:270:0:270[c0]", "[d]crop=480:270:480:270[d0]",
        "[a0][b0][c0][d0]vstack=inputs=4[mobile]",
    ])
    desktop = video_dir / "hero-montage.mp4"
    mobile = video_dir / "hero-montage-mobile.mp4"
    codec = ["-an", "-t", str(DURATION), "-c:v", "libx264", "-preset", "slow",
             "-crf", "24", "-threads", "4", "-pix_fmt", "yuv420p", "-g", "60",
             "-movflags", "+faststart"]
    # Encode both layouts from the same montage; cap bitrate for network playback.
    desktop_temp = desktop.with_suffix(".encoding.mp4")
    mobile_temp = mobile.with_suffix(".encoding.mp4")
    run([*inputs, "-filter_complex_threads", "4", "-filter_complex", ";".join(filters),
         "-map", "[desktop]", *codec, "-maxrate", "1800k", "-bufsize", "3600k", str(desktop_temp),
         "-map", "[mobile]", *codec, "-maxrate", "1100k", "-bufsize", "2200k", str(mobile_temp)])
    desktop_temp.replace(desktop)
    mobile_temp.replace(mobile)
    for video, name in [(desktop, "hero-montage-desktop"), (mobile, "hero-montage-mobile")]:
        run(["-i", str(video), "-frames:v", "1", "-q:v", "2", str(image_dir / f"{name}.jpg")])


if __name__ == "__main__":
    main()
