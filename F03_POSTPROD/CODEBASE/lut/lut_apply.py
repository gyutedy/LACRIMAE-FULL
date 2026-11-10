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

    filters = []
    if args.cube:
        if not args.cube.exists():
            print("L1 FAIL: cube introuvable:", args.cube); return 2
        filters.append(f"lut3d=file={args.cube}")
    # FADE obligatoire vers la fin — assombrit (darken) ou fondu noir (black)
    filters.append(f"fade=t=out:st=0:d={args.fade_duration}:color=black" if args.fade == "black"
                   else f"eq=brightness=-0.15:enable='gte(t,\\({{DUR}}-{args.fade_duration}\\))'")
    vf = ",".join(filters)
    cmd = ["ffmpeg", "-y", "-i", str(args.input)]
    if args.fade == "darken":   # duree totale lue au vol ; black utilise le fade natif
        probe = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                "-of", "csv=p=0", str(args.input)], capture_output=True, text=True)
        dur = float(probe.stdout.strip() or 0)
        vf = vf.replace("{{DUR}}", str(dur))
    cmd += ["-vf", vf, "-c:a", "copy", str(args.output)]
    subprocess.run(cmd, check=True)
    print("F1/L1 OK:", args.output); return 0

if __name__ == "__main__":
    sys.exit(main())
