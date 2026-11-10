#!/usr/bin/env python3
"""F03_POSTPROD orchestrateur : CAPTION → GLOW → LUT → FADE, a tous les clips.

CDC §7.7. S'arrete a la premiere porte en echec.
CAPTION = F07 absorbe (0 modification). GLOW = Modal pattern F07 (Phase 4).
LUT+FADE = lut_apply.py (CDC §7.6).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LUT_APPLY = HERE / "lut" / "lut_apply.py"
GLOW = HERE / "glow" / "modal_glow.py"
CAPTION_DIR = HERE / "caption"


def run(cmd: list[str]) -> int:
    print("POSTPROD:", " ".join(str(c) for c in cmd))
    proc = subprocess.run(cmd)
    return proc.returncode


def apply_one(inp: Path, out: Path, style_pack: dict, work: Path) -> int:
    current = inp
    caption = style_pack.get("caption") or {}
    glow = style_pack.get("glow") or {}
    lut = style_pack.get("lut") or {}
    fade = style_pack.get("fade_out") or {"enabled": True, "mode": "darken", "duration_sec": 1.5}

    if caption.get("enabled"):
        schema = CAPTION_DIR / "TRAVAIL" / "CODEBASE" / "caption_schema.py"
        if not schema.exists():
            print("G4 FAIL: caption_schema absent:", schema)
            return 2
        print("G4: CAPTION present (F07 housing). Application Whisper/Blender = runtime pack.")

    if glow.get("enabled"):
        sys.path.insert(0, str(HERE / "glow"))
        from modal_glow import glow_clip

        glowed = work / (inp.stem + "_glow" + inp.suffix)
        code = glow_clip(current, glow, glowed)
        if code != 0:
            return code
        if glowed.exists():
            current = glowed

    lut_out = out
    cmd = [sys.executable, str(LUT_APPLY), "--input", str(current), "--output", str(lut_out)]
    if lut.get("enabled") and lut.get("cube"):
        cube = Path(lut["cube"])
        if not cube.is_file():
            cube = ROOT / "F03_POSTPROD" / "CODEBASE" / "lut" / "profiles" / lut["cube"]
        cmd += ["--cube", str(cube)]
    if fade.get("enabled", True):
        cmd += ["--fade", fade.get("mode", "darken"), "--fade-duration", str(fade.get("duration_sec", 1.5))]
    return run(cmd)


def main() -> int:
    ap = argparse.ArgumentParser(description="F03_POSTPROD CAPTION→GLOW→LUT→FADE")
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--style-pack", type=Path, default=None)
    ap.add_argument("--work", type=Path, default=Path("WORK"))
    args = ap.parse_args()
    style_pack = {}
    if args.style_pack:
        style_pack = json.loads(args.style_pack.read_text(encoding="utf-8"))
        if "style_pack" in style_pack:
            style_pack = style_pack["style_pack"]
    args.work.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    return apply_one(args.input, args.output, style_pack, args.work)


if __name__ == "__main__":
    sys.exit(main())
