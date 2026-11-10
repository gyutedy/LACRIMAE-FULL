#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GLOW = HERE.parent
sys.path.insert(0, str(GLOW))

from modal_glow import check_gl1, glow_clip  # noqa: E402
from preview_glow import preview_frame  # noqa: E402


def test_gl1_ok_defaults():
    assert check_gl1({"mode": "scene", "sigma": 12, "opacity": 0.35}) == 0
    assert check_gl1({"mode": "subject", "sigma": 4, "opacity": 0}) == 0
    assert check_gl1({"mode": "scene", "sigma": 30, "opacity": 0.6}) == 0


def test_gl1_rejects_sigma():
    assert check_gl1({"mode": "scene", "sigma": 99, "opacity": 0.35}) == 2
    assert check_gl1({"mode": "scene", "sigma": 3.99, "opacity": 0.35}) == 2
    assert check_gl1({"mode": "scene", "sigma": 30.01, "opacity": 0.35}) == 2


def test_gl1_rejects_opacity_and_mode():
    assert check_gl1({"mode": "scene", "sigma": 12, "opacity": 0.9}) == 2
    assert check_gl1({"mode": "scene", "sigma": 12, "opacity": -0.01}) == 2
    assert check_gl1({"mode": "split_scene", "sigma": 12, "opacity": 0.35}) == 2


def _make_clip(path: Path, with_caption_bar: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if with_caption_bar:
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=0x140a0a:s=180x320:d=0.4:r=10",
            "-f", "lavfi", "-i", "color=c=white:s=180x70:d=0.4:r=10",
            "-filter_complex", "overlay=0:250",
            "-pix_fmt", "yuv420p",
            str(path),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=0x140a0a:s=180x320:d=0.4:r=10",
            "-pix_fmt", "yuv420p",
            str(path),
        ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0 and path.is_file(), (r.stderr or "")[-500:]


def _mean_rgb(png: Path, y0: int, y1: int) -> tuple[float, float, float]:
    from PIL import Image
    im = Image.open(png).convert("RGB")
    w, h = im.size
    px = im.load()
    n = 0
    s = [0, 0, 0]
    for y in range(max(0, y0), min(h, y1)):
        for x in range(w):
            r, g, b = px[x, y]
            s[0] += r
            s[1] += g
            s[2] += b
            n += 1
    return (s[0] / n, s[1] / n, s[2] / n)


def test_preview_png_scene(tmp_path: Path | None = None):
    work = tmp_path or (HERE / "_work")
    work.mkdir(parents=True, exist_ok=True)
    clip = work / "scene.mp4"
    png = work / "scene.png"
    _make_clip(clip)
    code = preview_frame(clip, {"mode": "scene", "sigma": 12, "opacity": 0.35}, png)
    assert code == 0, "GL2 preview scene"
    assert png.is_file() and png.stat().st_size > 0


def test_preview_png_subject(tmp_path: Path | None = None):
    work = tmp_path or (HERE / "_work")
    work.mkdir(parents=True, exist_ok=True)
    clip = work / "subject.mp4"
    png = work / "subject.png"
    _make_clip(clip, with_caption_bar=False)
    code = preview_frame(clip, {"mode": "subject", "sigma": 12, "opacity": 0.35}, png)
    assert code == 0, "GL2 preview subject (rigid mat if rembg absent)"
    assert png.is_file() and png.stat().st_size > 0


def test_gl2_does_not_bleach_caption_band(tmp_path: Path | None = None):
    work = tmp_path or (HERE / "_work")
    work.mkdir(parents=True, exist_ok=True)
    clip = work / "caption.mp4"
    png = work / "caption.png"
    _make_clip(clip, with_caption_bar=True)
    code = preview_frame(clip, {"mode": "scene", "sigma": 18, "opacity": 0.6}, png)
    assert code == 0
    cap = _mean_rgb(png, 250, 320)
    mid = _mean_rgb(png, 80, 180)
    assert cap[0] > 200, cap
    assert mid[0] < 80, mid


def test_glow_clip_mp4(tmp_path: Path | None = None):
    work = tmp_path or (HERE / "_work")
    work.mkdir(parents=True, exist_ok=True)
    clip = work / "in.mp4"
    out = work / "out.mp4"
    _make_clip(clip)
    code = glow_clip(clip, {"mode": "scene", "sigma": 12, "opacity": 0.35}, out)
    assert code == 0 and out.is_file()


def test_preview_cli_gl1_fail(tmp_path: Path | None = None):
    work = tmp_path or (HERE / "_work")
    work.mkdir(parents=True, exist_ok=True)
    clip = work / "cli.mp4"
    _make_clip(clip)
    r = subprocess.run(
        [sys.executable, str(GLOW / "preview_glow.py"), "--frame", str(clip), "--out", str(work / "x.png"), "--sigma", "99"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 2


if __name__ == "__main__":
    work = HERE / "_work"
    work.mkdir(parents=True, exist_ok=True)
    tests = [
        test_gl1_ok_defaults,
        test_gl1_rejects_sigma,
        test_gl1_rejects_opacity_and_mode,
        lambda: test_preview_png_scene(work),
        lambda: test_preview_png_subject(work),
        lambda: test_gl2_does_not_bleach_caption_band(work),
        lambda: test_glow_clip_mp4(work),
        lambda: test_preview_cli_gl1_fail(work),
    ]
    failed = 0
    for t in tests:
        name = getattr(t, "__name__", "lambda")
        try:
            t()
            print("OK", name)
        except Exception as e:
            failed += 1
            print("FAIL", name, e)
    sys.exit(2 if failed else 0)
