#!/usr/bin/env python3
"""POSTPROD/LUT + FADE. L1 : le .cube existe. F1 : fade obligatoire vers la fin (darken ou black)."""
import argparse, subprocess, sys
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--cube", type=Path, default=None)          # optionnel
    ap.add_argument("--fade", default="darken", choices=["darken", "black"])
    ap.add_argument("--fade-duration", type=float, default=1.5) # vers la fin
    args = ap.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    probe = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(args.input)], capture_output=True, text=True)
    dur = float(probe.stdout.strip() or 0)
    audio = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0",
                            "-show_entries", "stream=index", "-of", "csv=p=0", str(args.input)],
                           capture_output=True, text=True)
    filters = []
    if args.cube:
        if not args.cube.exists():
            print("L1 FAIL: cube introuvable:", args.cube); return 2
        filters.append(f"lut3d=file={args.cube}")
    fade_d = min(float(args.fade_duration), max(0.01, dur))
    fade_st = max(0.0, dur - fade_d)
    if args.fade == "black":
        filters.append(f"fade=t=out:st={fade_st:.3f}:d={fade_d:.3f}:color=black")
    else:
        filters.append(f"eq=brightness=-0.15:enable='gte(t,{fade_st:.3f})'")
    vf = ",".join(filters)
    cmd = ["ffmpeg", "-y", "-i", str(args.input), "-vf", vf]
    if (audio.stdout or "").strip():
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-an"]
    cmd += [str(args.output)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("F1/L1 FAIL:", (r.stderr or "")[-2000:])
        return 2
    print("F1/L1 OK:", args.output); return 0

if __name__ == "__main__":
    sys.exit(main())
