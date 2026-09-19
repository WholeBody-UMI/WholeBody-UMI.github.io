"""Audit local HTML video references before publishing. Does not modify files."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
VIDEO_SUFFIXES = {".mp4", ".m4v", ".webm", ".mov"}


class MediaReferences(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.paths = set()

    def handle_starttag(self, tag, attrs):
        if tag not in {"video", "source"}:
            return
        for key, value in attrs:
            if key not in {"src", "data-src", "data-mobile-src", "data-desktop-src", "poster",
                           "data-mobile-poster", "data-desktop-poster"} or not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc:
                continue
            path = unquote(url.path)
            base = ROOT if path.startswith("/") else self.page.parent
            self.paths.add((base / path.lstrip("/")).resolve())


def main():
    referenced = set()
    for page in ROOT.glob("*.html"):
        parser = MediaReferences(page)
        parser.feed(page.read_text())
        referenced.update(parser.paths)
    missing = sorted(path for path in referenced if not path.is_file())
    videos = sorted(path for path in referenced if path.suffix.lower() in VIDEO_SUFFIXES)
    existing = [path for path in videos if path.is_file()]
    stored = {path.resolve() for path in (ROOT / "static/videos").rglob("*")
              if path.is_file() and path.suffix.lower() in VIDEO_SUFFIXES}
    unused = sorted(stored - set(videos))
    total = sum(path.stat().st_size for path in existing)
    print(f"Referenced videos: {len(videos)}; total: {total / 1024**2:.1f} MiB")
    for path in sorted(existing, key=lambda p: p.stat().st_size, reverse=True):
        print(f"  {path.stat().st_size / 1024**2:6.1f} MiB  {path.relative_to(ROOT)}")
    for label, paths in (("MISSING media/poster", missing), ("UNUSED video", unused)):
        for path in paths:
            print(f"{label}: {path}")
    large = [path for path in existing if path.stat().st_size > 50 * 1024**2]
    for path in large:
        print(f"REVIEW (>50 MiB): {path}")
    print(f"Missing references: {len(missing)}; unused videos: {len(unused)}; over 50 MiB: {len(large)}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
