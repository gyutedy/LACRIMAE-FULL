#!/usr/bin/env python3
"""F03_POSTPROD orchestrateur — piloté par `REVIEW/codex_postprod.json`.

Ordre GRAVÉ (PP2) : GLOW → CAPTION → LUT → FADE.

- GLOW   : `glow/modal_glow.py::glow_clip` (ffmpeg pur, Modal inutile en local/CI).
           La zone des sous-titres (bas 22 %) n'est jamais floutée.
- CAPTION: le codex porte le style `dev11.caption.style.v1`. La gravure réelle
           demande une séquence PNG rendue par Blender (runtime Modal) : sans
           elle, la passe est **déclarée non appliquée** dans le rapport, jamais
           silencieuse.
- LUT    : `lut/lut_apply.py --profile <nom>` (profils ATOM-IC, traduits en
           filtres ffmpeg) ou `--cube` pour une vraie LUT 3D.
- FADE   : `lut_apply.py --fade/--fade-duration`, vers la fin, obligatoire (F1).
           LUT et FADE partent dans la même passe ffmpeg (filtres ordonnés
           lut → fade) : une seule ré-encode par clip.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LUT_APPLY = HERE / "lut" / "lut_apply.py"
CAPTION_DIR = HERE / "caption"
REPORT_SCHEMA = "sanguinala.postprod.report.v1"
PP2_ORDER = ["glow", "caption", "lut", "fade"]


def log(msg: str) -> None:
    print(f"POSTPROD: {msg}", flush=True)


def run(cmd: list[str]) -> int:
    print("POSTPROD:", " ".join(str(c) for c in cmd), flush=True)
    proc = subprocess.run(cmd)
    return proc.returncode


def load_codex(path: Path) -> dict:
    """Charge et valide le codex. PP1 : non signé = post-prod refusée (exit 2)."""
    sys.path.insert(0, str(ROOT / "tools"))
    import codex as codex_mod

    try:
        return codex_mod.load_postprod_codex(path, require_validated=True)
    except codex_mod.CodexError as exc:
        for err in exc.errors or [str(exc)]:
            print(f"PP1 FAIL: {err}", flush=True)
        raise SystemExit(exc.code)


def check_pp2(codex: dict) -> int:
    order = list(codex.get("order") or [])
    if order != PP2_ORDER:
        print(f"PP2 FAIL: ordre {order} != {PP2_ORDER} (sous-titres floutés)", flush=True)
        return 2
    log("PP2 OK: ordre glow -> caption -> lut -> fade")
    return 0


def legacy_style_pack_to_codex(style_pack: dict) -> dict:
    """Ancien style_pack (pack) -> forme codex, pour ne rien casser."""
    glow = dict(style_pack.get("glow") or {})
    glow.setdefault("enabled", bool(glow))
    glow.setdefault("mode", "scene")
    glow.setdefault("sigma", 12)
    glow.setdefault("opacity", 0.35)
    lut = dict(style_pack.get("lut") or {})
    lut.setdefault("enabled", bool(lut))
    lut.setdefault("profile", "hdr_imperator")
    fade = dict(style_pack.get("fade_out") or {})
    return {
        "schema_version": "sanguinala.postprod.codex.v1",
        "order": PP2_ORDER,
        "caption": dict(style_pack.get("caption") or {}),
        "glow": glow,
        "lut": lut,
        "fade_out": {
            "mode": fade.get("mode", "darken"),
            "duration_sec": float(fade.get("duration_sec", 1.5)),
        },
        "validated_by_magos": style_pack.get("validated_by_magos", True),
    }


def apply_one(inp: Path, out: Path, codex: dict, work: Path) -> dict:
    steps: list[dict] = []
    current = inp
    glow = codex.get("glow") or {}
    lut = codex.get("lut") or {}
    fade = codex.get("fade_out") or {}
    caption = codex.get("caption") or {}

    # ── 1. GLOW ──────────────────────────────────────────────────────────────
    if glow.get("enabled"):
        sys.path.insert(0, str(HERE / "glow"))
        from modal_glow import glow_clip

        glowed = work / (inp.stem + "_glow" + inp.suffix)
        code = glow_clip(current, glow, glowed)
        if code != 0:
            steps.append({"step": "glow", "applied": False, "returncode": code})
            return {"qa_pass": False, "steps": steps, "output": None}
        if glowed.exists():
            current = glowed
        steps.append({
            "step": "glow", "applied": True, "file": glowed.name,
            "mode": glow.get("mode", "scene"),
            "sigma": float(glow.get("sigma", 12)),
            "opacity": float(glow.get("opacity", 0.35)),
            "caption_zone_preserved": True,
        })
    else:
        steps.append({"step": "glow", "applied": False, "reason": "disabled dans le codex"})

    # ── 2. CAPTION ───────────────────────────────────────────────────────────
    if caption:
        schema = CAPTION_DIR / "TRAVAIL" / "CODEBASE" / "caption_schema.py"
        schema_ok = schema.exists()
        steps.append({
            "step": "caption",
            "applied": False,
            "reason": (
                "sequence PNG Blender absente (runtime Modal) : style conserve, "
                "aucun sous-titre grave dans ce run"
            ),
            "style_id": caption.get("id"),
            "schema_ok": schema_ok,
        })
        log(
            f"G4 CAPTION: style {caption.get('id')} porté par le codex, "
            "non gravé (séquence Blender absente) — déclaré dans le rapport"
        )
    else:
        steps.append({"step": "caption", "applied": False, "reason": "aucun caption dans le codex"})

    # ── 3+4. LUT puis FADE (même passe ffmpeg, filtres ordonnés) ─────────────
    cmd = [sys.executable, str(LUT_APPLY), "--input", str(current), "--output", str(out)]
    if lut.get("enabled"):
        cube = lut.get("cube")
        if cube:
            cube_path = Path(cube)
            if not cube_path.is_file():
                cube_path = HERE / "lut" / "profiles" / cube
            cmd += ["--cube", str(cube_path)]
            lut_mode = f"cube:{cube_path.name}"
        else:
            profile = lut.get("profile") or "hdr_imperator"
            cmd += ["--profile", str(profile)]
            lut_mode = f"profile:{profile}"
        steps.append({"step": "lut", "applied": True, "mode": lut_mode})
    else:
        steps.append({"step": "lut", "applied": False, "reason": "disabled dans le codex"})

    cmd += [
        "--fade", fade.get("mode", "darken"),
        "--fade-duration", str(fade.get("duration_sec", 1.5)),
    ]
    steps.append({
        "step": "fade", "applied": True,
        "mode": fade.get("mode", "darken"),
        "duration_sec": float(fade.get("duration_sec", 1.5)),
    })

    code = run(cmd)
    if code != 0:
        return {"qa_pass": False, "steps": steps, "output": None}
    return {
        "qa_pass": out.is_file(),
        "steps": steps,
        "output": str(out),
        "lut_fade_single_pass": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="F03_POSTPROD GLOW→CAPTION→LUT→FADE (codex_postprod)")
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--codex-postprod", type=Path, default=None,
                    help="REVIEW/codex_postprod.json (PP1 vérifiée)")
    ap.add_argument("--style-pack", type=Path, default=None,
                    help="legacy : style_pack du pack, utilisé si aucun codex")
    ap.add_argument("--work", type=Path, default=Path("WORK"))
    ap.add_argument("--report", type=Path, default=None,
                    help="rapport JSON (défaut : <work>/postprod_report.json)")
    args = ap.parse_args()

    if args.codex_postprod:
        codex = load_codex(args.codex_postprod)
        log(f"codex : {args.codex_postprod}")
    elif args.style_pack and args.style_pack.is_file():
        style_pack = json.loads(args.style_pack.read_text(encoding="utf-8"))
        if "style_pack" in style_pack:
            style_pack = style_pack["style_pack"]
        codex = legacy_style_pack_to_codex(style_pack)
        log(f"legacy : {args.style_pack} (aucun codex fourni)")
    else:
        print("PP1 FAIL: ni --codex-postprod ni --style-pack", flush=True)
        return 2

    code = check_pp2(codex)
    if code:
        return code

    args.work.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    result = apply_one(args.input, args.output, codex, args.work)
    report = {
        "schema_version": REPORT_SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input": str(args.input),
        "output": result.get("output"),
        "order": codex.get("order"),
        "qa_pass": bool(result.get("qa_pass")),
        "steps": result.get("steps"),
        "lut_fade_single_pass": result.get("lut_fade_single_pass", False),
    }
    report_path = args.report or (args.work / "postprod_report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log(f"rapport : {report_path}")
    return 0 if report["qa_pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
