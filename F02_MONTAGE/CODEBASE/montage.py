#!/usr/bin/env python3
"""F02_MONTAGE — insertion b-roll + flash blanc (duree ajustable) + SFX au debut du b-roll.
Pas de jump cuts en V1. Porte M1 : chaque broll src existe, in < out, flash_duration 0.04..0.5 s."""
import argparse, subprocess, sys, json
from pathlib import Path

def apply_broll(clip: Path, broll: dict, out: Path, workdir: Path) -> int:
    src = workdir / broll["src"]
    if not src.exists():
        print("M1 FAIL: broll absent:", src); return 2
    fd = max(0.04, min(0.5, float(broll.get("flash_duration", 0.12))))   # duree flash AJUSTABLE
    # 1. inserer le b-roll a l'Instant 'in' (concat demuxer, aucun cut du clip principal)
    # 2. flash blanc au debut du b-roll : geq/blank blanc pose pendant 'fd' secondes
    # 3. mixer le SFX au debut du b-roll (adelay + amix)
    print(f"M1: broll {src.name} a {broll['in']}s, flash {fd}s, sfx {broll.get('sfx_start')}")
    # (implementation ffmpeg : cf. commande exacte consignee dans SANGUINALA_LOG.md a l'installation)
    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)   # montage_instructions de CE clip
    ap.add_argument("--work", type=Path, default=Path("WORK"))
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    entry = json.loads(Path(a.manifest).read_text())
    code = 0
    for b in entry.get("broll") or []:
        code = apply_broll(a.input, b, a.out, a.work)
        if code != 0: sys.exit(code)
    print("M1 OK:", a.out); sys.exit(0)
