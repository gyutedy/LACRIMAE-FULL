#!/usr/bin/env python3
"""run_all.py — orchestrateur SANGUINALA V1 (CDC §7 / §7.7).

BRIDGE → F00_SOURCE → F01_LOOK → F02_MONTAGE → F03_POSTPROD → F05 → F06.
S'arrete a la premiere porte en echec. Heisenberg n'est jamais appele.
Boucle assets[] : meme style_pack, montage_instructions propre a chaque clip.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALLOWED_STYLES = {"blur", "reframing"}
MAX_SEGMENT = 150.0

BRIDGE_PY = ROOT / "BRIDGE" / "CODEBASE" / "lac_bridge_forge.py"
F00_PY = ROOT / "F00_SOURCE" / "CODEBASE" / "f00_pur.py"
F01_MJS = ROOT / "F01_LOOK" / "CODEBASE" / "render_pictor.mjs"
F02_PY = ROOT / "F02_MONTAGE" / "CODEBASE" / "montage.py"
F03_PY = ROOT / "F03_POSTPROD" / "CODEBASE" / "postprod.py"
F05_PY = ROOT / "F05" / "CODEBASE" / "lac_f05_camouflage.py"
F06_PY = ROOT / "F06_LUTHER" / "CODEBASE" / "lac_f06_luther.py"


def log(msg: str) -> None:
    print(msg, flush=True)


def run(cmd: list[str]) -> int:
    log("RUN: " + " ".join(str(c) for c in cmd))
    return subprocess.run(cmd).returncode


def gate_g0(pack: dict) -> int:
    if pack.get("mode") != "pur":
        log("G0 PACK FAIL: mode != pur")
        return 2
    source = pack.get("source") or {}
    vod = source.get("vod_url")
    assets = pack.get("assets")
    if isinstance(assets, list) and assets:
        if not vod:
            log("G0 PACK FAIL: vod_url absente")
            return 2
        for a in assets:
            mi = a.get("montage_instructions") or {}
            start = float(mi.get("start_sec", -1))
            end = float(mi.get("end_sec", -1))
            if start >= end:
                log(f"G0 PACK FAIL: {a.get('id')} start_sec >= end_sec")
                return 2
            if end - start > MAX_SEGMENT:
                log(f"G0 PACK FAIL: {a.get('id')} segment > {MAX_SEGMENT}s")
                return 2
            if not mi:
                log(f"G0 PACK FAIL: {a.get('id')} montage_instructions absentes")
                return 2
        log(f"G0 PACK OK: {len(assets)} assets")
        return 0
    log("G0 PACK FAIL: assets[] absents")
    return 2


def gate_g0s(pack: dict, style_arg: str | None) -> int:
    sp = pack.get("style_pack") or {}
    style = (style_arg or sp.get("style") or pack.get("montage_style") or "").lower()
    if style not in ALLOWED_STYLES:
        log(f"G0-S STYLE FAIL: {style!r} (blur|reframing only, split_scene = V2+)")
        return 2
    log(f"G0-S STYLE OK: {style}")
    return 0


def assets_of(pack: dict) -> list[dict]:
    return list(pack.get("assets") or [])


def main() -> int:
    ap = argparse.ArgumentParser(description="SANGUINALA run_all CDC §7")
    ap.add_argument("--pack", type=Path, required=True)
    ap.add_argument("--work", type=Path, default=ROOT / "WORK")
    ap.add_argument("--out", type=Path, default=ROOT / "OUT")
    ap.add_argument("--style", default=None, choices=sorted(ALLOWED_STYLES))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    code = gate_g0(pack)
    if code:
        return code
    code = gate_g0s(pack, args.style)
    if code:
        return code

    heisenberg = ROOT / "F04_HEISENBERG"
    if heisenberg.exists():
        log("NOTE: F04_HEISENBERG present hors flux — jamais appele (V1, 0 jump cut).")

    items = assets_of(pack)
    log(f"PIPELINE: BRIDGE → F00_SOURCE → F01_LOOK → F02_MONTAGE → F03_POSTPROD → F05 → F06  ({len(items)} clips)")
    if args.dry_run:
        log("DRY-RUN: portes G0/G0-S OK, stop avant execution.")
        return 0

    args.work.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)
    style_pack_path = args.work / "style_pack.json"
    style_pack_path.write_text(json.dumps(pack.get("style_pack") or {}, indent=2), encoding="utf-8")

    for asset in items:
        aid = asset.get("id") or "clip"
        log(f"=== asset {aid} ===")
        mi_path = args.work / f"{aid}_montage.json"
        mi_path.write_text(json.dumps(asset.get("montage_instructions") or {}, indent=2), encoding="utf-8")

        look_mp4 = args.work / f"{aid}_look.mp4"
        if not look_mp4.exists():
            log(f"G3 LOOK: {look_mp4} absent — F00/F01 a jouer avec VOD (Phase 5/6). Stop.")
            return 2

        mont_out = args.work / f"{aid}_mont.mp4"
        code = run([sys.executable, str(F02_PY), "--input", str(look_mp4), "--manifest", str(mi_path), "--work", str(args.work), "--out", str(mont_out)])
        if code:
            log(f"M1 FAIL asset {aid} exit {code}")
            return code

        post_out = args.work / f"{aid}_post.mp4"
        code = run([sys.executable, str(F03_PY), "--input", str(mont_out if mont_out.exists() else look_mp4), "--output", str(post_out), "--style-pack", str(style_pack_path), "--work", str(args.work)])
        if code:
            log(f"POSTPROD FAIL asset {aid} exit {code}")
            return code

        f05_dir = args.work / f"{aid}_f05"
        code = run([sys.executable, str(F05_PY), "--input", str(post_out), "--output", str(f05_dir)])
        if code:
            log(f"G6 F05 FAIL asset {aid} exit {code}")
            return code

        f06_dir = args.out / aid
        code = run([sys.executable, str(F06_PY), "--input", str(next(f05_dir.glob("*.mp4"), post_out)), "--output", str(f06_dir)])
        if code:
            log(f"G6 F06 FAIL asset {aid} exit {code}")
            return code
        log(f"G6 LIVRABLE OK {aid}")

    log(f"G-PACK OK: {len(items)} livrables dans {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
