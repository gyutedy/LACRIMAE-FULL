#!/usr/bin/env python3
"""F03_POSTPROD/glow/preview_glow.py — endpoint preview : 1 frame + params → PNG, temps réel (curseur).

Pattern F07. CDC §7.2. GL2 : preview validée sur frame → style_pack.glow consolidé → N clips.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from modal_glow import check_gl1, glow_clip


def preview_frame(frame: Path, params: dict, out_png: Path) -> int:
    code = check_gl1(params)
    if code != 0:
        return code
    out_png = Path(out_png)
    if out_png.suffix.lower() != ".png":
        out_png = out_png.with_suffix(".png")
    return glow_clip(Path(frame), params, out_png)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--mode", choices=["scene", "subject"], default="scene")
    ap.add_argument("--sigma", type=float, default=12)
    ap.add_argument("--opacity", type=float, default=0.35)
    a = ap.parse_args()
    sys.exit(preview_frame(a.frame, {"mode": a.mode, "sigma": a.sigma, "opacity": a.opacity}, a.out))
