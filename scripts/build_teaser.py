"""Replace the four stickered human panels in the website's SVG teaser.

Usage: python3 scripts/build_teaser.py --material ../material
Uses original video frames; keeps the SVG layout, labels, simulation, and robot panels.
"""

import argparse
import base64
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
# Existing embedded-image IDs, source video, timestamp, and vertical crop origin.
PANELS = {
    "source-5": ("drawer_human.MOV", 7, 570),
    "source-14": ("shelf_pnp.MOV", 5, 480),
    "source-23": ("toss_human.MOV", 1, 100),
    "source-32": ("loco-pnp_human.MOV", 0, 70),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--material", type=Path, required=True)
    args = parser.parse_args()
    folder = ROOT / "static/images/umi-prior"
    ET.register_namespace("", SVG)
    ET.register_namespace("xlink", XLINK)
    tree = ET.parse(folder / "wb-umi-teaser.svg")
    changed = set()
    for image in tree.iter(f"{{{SVG}}}image"):
        identifier = image.get("id")
        if identifier not in PANELS:
            continue
        source, timestamp, top = PANELS[identifier]
        width, height = int(image.get("width")), int(image.get("height"))
        crop_height = round(1080 * height / width / 2) * 2
        frame = subprocess.check_output([
            "ffmpeg", "-v", "error", "-ss", str(timestamp),
            "-i", str(args.material / "human_collect" / source), "-frames:v", "1",
            "-vf", f"crop=1080:{crop_height}:0:{top},scale={width}:{height}:flags=lanczos",
            "-c:v", "mjpeg", "-q:v", "2", "-f", "image2pipe", "-",
        ])
        image.set(f"{{{XLINK}}}href", "data:image/jpeg;base64," + base64.b64encode(frame).decode())
        changed.add(identifier)
    if changed != set(PANELS):
        raise ValueError(f"Unexpected SVG structure; matched panels: {changed}")
    tree.write(folder / "wb-umi-teaser-clean.svg", encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
