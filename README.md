# Whole-Body UMI website

This is a static website; no build step or package installation is required.

```sh
python3 scripts/serve.py
```

Open http://localhost:8765. Use Ctrl+C to stop the server. If that port is
already in use, stop the previous preview or pass `--port 8766`.

Use this server instead of `python3 -m http.server`: it supports HTTP byte-range
requests so videos can seek before downloading completely. Production hosting
should likewise support `Range` requests with `206 Partial Content` responses.

Videos autoplay muted. Use the player's speaker control to enable the original
audio; the sound and volume setting carries over when switching recordings in
the same carousel. Simulation recordings have no source audio.

To regenerate robot recordings and posters from the local source footage:

```sh
python3 scripts/build_demos.py --material ../material
python3 scripts/build_simulations.py --material ../material
```

FFmpeg and FFprobe are required for media preparation, but not for serving.

Motion-prior samples use lighter web encodes with the original frame rate and motion timing. To rebuild only these four files, run `python3 scripts/build_simulations.py --material ../material --motion-only`.

## Video storage and publishing

Keep the final web MP4s and posters in this repository for static hosting:

- `static/videos/demos/`: trimmed real-world demos, including their original audio.
- `static/videos/simulation/`: compressed simulations, including the revised Motion Diversity source.
- `static/videos/hero-montage*.mp4`: desktop and mobile covers.
- `static/images/umi-prior/`: posters and paper figures.

Keep original footage in `../material`, outside this repository. Store long-form
presentation videos on YouTube and add their links or embeds when available.
Short demos continue to use native video controls and carousel navigation.
Commit final exports rather than every intermediate encode. Git retains old
versions of committed videos, so replacing a file does not remove its history.

Before publishing, run this read-only check for missing video/poster references,
unused videos, and individual videos over 50 MiB:

```sh
python3 scripts/check_media.py
```

All simulations are encoded from original sources using H.264 CRF 20, retaining
resolution, frame rate, and timing, with fast-start MP4 metadata. Rebuild only
selected clips with:

```sh
python3 scripts/build_simulations.py --material ../material --only drawer shelf toss locomotion-pick-and-place diversity-stable
```

After replacing a video, update its `?v=` query in `index.html` to refresh browser
caches. Videos preload nothing; hidden carousel slides have no `src` until selected,
and automatic playback pauses outside the viewport. The cover loads only the
desktop or mobile version appropriate to the viewport.

Unused legacy `.m4v` files were archived outside this website at
`../material/website-legacy-videos/`. They are not needed for deployment.
