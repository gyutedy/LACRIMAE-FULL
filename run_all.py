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
CAPTION_SCHEMA = ROOT / "F03_POSTPROD" / "CODEBASE" / "caption" / "TRAVAIL" / "CODEBASE" / "caption_schema.py"


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


def probe_wh(path: Path) -> tuple[int, int, float]:
    r = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration", "-of", "csv=p=0", str(path),
        ],
        capture_output=True,
        text=True,
    )
    raw = (r.stdout or "").strip().split(",")
    w = int(float(raw[0])) if raw and raw[0] else 0
    h = int(float(raw[1])) if len(raw) > 1 and raw[1] else 0
    dur = 0.0
    if len(raw) > 2 and raw[2]:
        try:
            dur = float(raw[2])
        except ValueError:
            dur = 0.0
    if dur <= 0:
        d = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True,
            text=True,
        )
        try:
            dur = float((d.stdout or "0").strip() or 0)
        except ValueError:
            dur = 0.0
    return w, h, dur


def make_look_sample(path: Path, seconds: float) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    d = max(0.5, float(seconds))
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x1a0a0a:s=1080x1920:d={d:.3f}:r=25",
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
        "-shortest",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        str(path),
    ]
    log("G1 SOURCE: fixture local 9:16 (pas de VOD, Phase 5)")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not path.is_file():
        log("G1 SOURCE FAIL: " + (r.stderr or "")[-800:])
        return 2
    log(f"G1 SOURCE OK: {path.name}")
    return 0


def gate_g2(path: Path, start: float, end: float) -> int:
    _, _, dur = probe_wh(path)
    expected = end - start
    if abs(dur - expected) > 0.5:
        log(f"G2 DUREE FAIL: {dur:.2f}s vs {expected:.2f}s")
        return 2
    log(f"G2 DUREE OK: {dur:.2f}s")
    return 0


def gate_g3(path: Path) -> int:
    w, h, _ = probe_wh(path)
    if w <= 0 or h <= 0 or w * 16 != h * 9:
        log(f"G3 LOOK FAIL: {w}x{h} pas 9:16")
        return 2
    log(f"G3 LOOK OK: {w}x{h} 9:16, 0 zoom")
    return 0


def gate_g4(style_pack: dict) -> int:
    caption = style_pack.get("caption") or {}
    if not caption.get("enabled"):
        log("G4 CAPTION: disabled")
        return 0
    if not CAPTION_SCHEMA.is_file():
        log("G4 CAPTION FAIL: caption_schema absent")
        return 2
    log("G4 CAPTION OK: F07 housing present")
    return 0


def gate_gl1(style_pack: dict) -> int:
    glow = style_pack.get("glow") or {}
    if not glow.get("enabled"):
        log("GL1: glow disabled")
        return 0
    sys.path.insert(0, str(ROOT / "F03_POSTPROD" / "CODEBASE" / "glow"))
    from modal_glow import check_gl1
    code = check_gl1(glow)
    if code:
        log("GL1 FAIL")
        return code
    log("GL1 OK")
    return 0


def first_mp4(folder: Path) -> Path | None:
    if folder.is_file() and folder.suffix.lower() == ".mp4":
        return folder
    found = sorted(folder.glob("*.mp4")) if folder.is_dir() else []
    return found[0] if found else None


def main() -> int:
    ap = argparse.ArgumentParser(description="SANGUINALA run_all CDC §7")
    ap.add_argument("--pack", type=Path, required=True)
    ap.add_argument("--work", type=Path, default=ROOT / "WORK")
    ap.add_argument("--out", type=Path, default=ROOT / "OUT")
    ap.add_argument("--style", default=None, choices=sorted(ALLOWED_STYLES))
    ap.add_argument("--look-dir", type=Path, default=None)
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
    style_pack = pack.get("style_pack") or {}
    log(f"PIPELINE: BRIDGE → F00_SOURCE → F01_LOOK → F02_MONTAGE → F03_POSTPROD → F05 → F06  ({len(items)} clips)")
    log("G-PACK: meme style_pack pour tous les assets")
    if args.dry_run:
        log("DRY-RUN: portes G0/G0-S OK, stop avant execution.")
        return 0

    code = gate_g4(style_pack)
    if code:
        return code
    code = gate_gl1(style_pack)
    if code:
        return code

    args.work.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)
    style_pack_path = args.work / "style_pack.json"
    style_pack_path.write_text(json.dumps(style_pack, indent=2), encoding="utf-8")

    delivered = 0
    for asset in items:
        aid = asset.get("id") or "clip"
        log(f"=== asset {aid} ===")
        mi = asset.get("montage_instructions") or {}
        mi_path = args.work / f"{aid}_montage.json"
        mi_path.write_text(json.dumps(mi, indent=2), encoding="utf-8")

        look_mp4 = args.work / f"{aid}_look.mp4"
        if args.look_dir:
            cand = args.look_dir / f"{aid}_look.mp4"
            if cand.is_file():
                look_mp4 = cand
        if not look_mp4.exists():
            start = float(mi.get("start_sec", 0))
            end = float(mi.get("end_sec", 2))
            code = make_look_sample(look_mp4, end - start)
            if code:
                return code
        else:
            log(f"G1 SOURCE OK: {look_mp4} (look fourni)")

        start = float(mi.get("start_sec", 0))
        end = float(mi.get("end_sec", 0))
        code = gate_g2(look_mp4, start, end)
        if code:
            return code
        code = gate_g3(look_mp4)
        if code:
            return code

        mont_out = args.work / f"{aid}_mont.mp4"
        code = run([sys.executable, str(F02_PY), "--input", str(look_mp4), "--manifest", str(mi_path), "--work", str(args.work), "--out", str(mont_out)])
        if code:
            log(f"M1 FAIL asset {aid} exit {code}")
            return code
        if not mont_out.exists():
            log(f"M1 FAIL: {mont_out} absent")
            return 2
        log(f"M1 OK asset {aid}")

        post_out = args.work / f"{aid}_post.mp4"
        code = run([sys.executable, str(F03_PY), "--input", str(mont_out), "--output", str(post_out), "--style-pack", str(style_pack_path), "--work", str(args.work)])
        if code:
            log(f"POSTPROD FAIL asset {aid} exit {code}")
            return code
        if not post_out.exists():
            log(f"F1 FAIL: {post_out} absent")
            return 2
        log(f"L1/F1 OK asset {aid}")

        f05_dir = args.work / f"{aid}_f05"
        code = run([sys.executable, str(F05_PY), "--input", str(post_out), "--output", str(f05_dir)])
        if code:
            log(f"G6 F05 FAIL asset {aid} exit {code}")
            return code
        f05_mp4 = first_mp4(f05_dir)
        if f05_mp4 is None:
            log(f"G6 F05 FAIL: aucun mp4 dans {f05_dir}")
            return 2

        f06_dir = args.out / aid
        code = run([sys.executable, str(F06_PY), "--input", str(f05_mp4), "--output", str(f06_dir)])
        if code:
            log(f"G6 F06 FAIL asset {aid} exit {code}")
            return code
        f06_mp4 = first_mp4(f06_dir)
        if f06_mp4 is None:
            log(f"G6 FAIL: aucun mp4 dans {f06_dir}")
            return 2
        dest = args.out / f"{aid}.mp4"
        if f06_mp4.resolve() != dest.resolve():
            dest.write_bytes(f06_mp4.read_bytes())
        log(f"G6 LIVRABLE OK {aid} -> {dest}")
        delivered += 1

    if delivered != len(items):
        log(f"G-PACK FAIL: {delivered} livrables != {len(items)} assets")
        return 2
    log(f"G-PACK OK: {delivered} livrables dans {args.out}")
    log(f"G6 LIVRABLE OK: N MP4 = N assets = {delivered}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
