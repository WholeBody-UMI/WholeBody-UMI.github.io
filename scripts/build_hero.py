"""Build the anonymous hero with smaller tracked face stickers (requires ffmpeg).

Usage: python3 scripts/build_hero.py --material ../material
The four task groups are drawer, shelf, toss, and loco-PnP. Each group contains
human collection with a face-covering sticker, simulation, and robot execution.
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
STICKER = ROOT / "scripts/assets/anon-cat-sticker.png"
STICKER_WIDTH = 52
STICKER_HEIGHT = round(STICKER_WIDTH * 184 / 195)

# Human head centers sampled once per second from the source footage.
# Coordinates use the 960x540 montage space and are linearly interpolated.
STICKER_TRACKS = [
    [(55, 62), (69, 92), (65, 92), (62, 96), (66, 93), (68, 93),
     (65, 105), (60, 100), (66, 100), (64, 81), (60, 79), (63, 91),
     (58, 100), (62, 89), (64, 91), (66, 86), (65, 91), (64, 92),
     (61, 101), (63, 89), (66, 82), (66, 90), (66, 90)],
    [(550, 65), (568, 85), (570, 95), (572, 101), (569, 96), (572, 84),
     (545, 79), (558, 77), (560, 81), (570, 81), (575, 89), (577, 89),
     (550, 103), (563, 94), (574, 76), (570, 71), (570, 79), (568, 96),
     (552, 101), (555, 101), (569, 96), (575, 91), (575, 91)],
    [(58, 325), (70, 325), (70, 322), (68, 326), (69, 325), (70, 326),
     (70, 324), (72, 328), (68, 328), (70, 330), (66, 332), (70, 328),
     (58, 330), (66, 325), (70, 328), (70, 328), (69, 326), (70, 328),
     (70, 332), (72, 330), (72, 325), (70, 327), (70, 327)],
    [(552, 328), (538, 332), (535, 335), (538, 338), (538, 335), (540, 332),
     (515, 352), (525, 348), (525, 345), (535, 344), (538, 350), (536, 345),
     (508, 340), (522, 340), (530, 340), (523, 338), (535, 335), (535, 340),
     (515, 350), (525, 355), (530, 347), (538, 338), (538, 338)],
]


def run(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def interpolated_expression(values, half_size):
    """Return an FFmpeg expression interpolating keyframes at one-second intervals."""
    expression = f"{values[-1] - half_size:.2f}"
    for second in reversed(range(len(values) - 1)):
        start = values[second] - half_size
        delta = values[second + 1] - values[second]
        segment = f"{start:.2f}+{delta:.2f}*(t-{second})"
        expression = f"if(lt(t,{second + 1}),{segment},{expression})"
    return expression


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
    filters.append("".join(f"[v{i}]" for i in range(12)) + f"xstack=inputs=12:layout={layout}[montage]")
    filters.append(f"[12:v]scale={STICKER_WIDTH}:{STICKER_HEIGHT},split=4[st0][st1][st2][st3]")
    current = "montage"
    for index, track in enumerate(STICKER_TRACKS):
        x = interpolated_expression([point[0] for point in track], STICKER_WIDTH / 2)
        y = interpolated_expression([point[1] for point in track], STICKER_HEIGHT / 2)
        output = f"anonymous{index}"
        filters.append(f"[{current}][st{index}]overlay=x='{x}':y='{y}':eval=frame[{output}]")
        current = output
    filters.extend([
        f"[{current}]split=2[wide][portrait]",
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
