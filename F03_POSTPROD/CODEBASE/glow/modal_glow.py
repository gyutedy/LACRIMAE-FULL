#!/usr/bin/env python3
"""F03_POSTPROD/glow/modal_glow.py — fonction Modal : frame/clip + params → frame/clip glowed.

Pattern F07 : F03_POSTPROD/CODEBASE/caption/TRAVAIL/CODEBASE/modal_app.py
Implementation GPU = Phase 4. Signature CDC §7.2 seulement.

Parametres : { "mode": "scene"|"subject", "sigma": 12, "opacity": 0.35 }
Bornes GL1 : sigma 4–30, opacite 0–0.6.
"""
from __future__ import annotations

from pathlib import Path

GL1_SIGMA = (4.0, 30.0)
GL1_OPACITY = (0.0, 0.6)


def check_gl1(params: dict) -> int:
    mode = params.get("mode", "scene")
    if mode not in ("scene", "subject"):
        print("GL1 FAIL: mode", mode)
        return 2
    sigma = float(params.get("sigma", 12))
    opacity = float(params.get("opacity", 0.35))
    if not (GL1_SIGMA[0] <= sigma <= GL1_SIGMA[1]):
        print("GL1 FAIL: sigma", sigma)
        return 2
    if not (GL1_OPACITY[0] <= opacity <= GL1_OPACITY[1]):
        print("GL1 FAIL: opacity", opacity)
        return 2
    return 0


def glow_clip(frame_or_clip: Path, params: dict, out: Path) -> int:
    code = check_gl1(params)
    if code != 0:
        return code
    print("GLOW stub Phase 2 (Phase 4 = Modal pattern F07):", frame_or_clip, "->", out, params)
    return 0
