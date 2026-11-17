#!/usr/bin/env python3
"""run_all.py — orchestrateur SANGUINALA V1 (CDC §7 / §7.7).

F03_PREVIEW (W1/T1, JSON review) AVANT le moteur.
Puis BRIDGE → F00_SOURCE → F01_LOOK → F02_MONTAGE → F03_POSTPROD
(CAPTION F07 preview s1 → GLOW → LUT → FADE) → F05 → F06.
S'arrete a la premiere porte en echec. Heisenberg n'est jamais appele.
Boucle assets[] : meme style_pack, montage_instructions propre a chaque clip.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# L1 (AUDIT_V1) : la console Windows est en cp1252 et ne sait pas encoder
# les caracteres comme la fleche "->" utilisee dans les logs. Sans ceci, le
# script crashe APRES les portes G0/G0-S vertes : on croit que le pack est
# refuse alors que c'est l'encodage. On force l'UTF-8 avec repli tolerant.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent
ALLOWED_STYLES = {"blur", "reframing"}
MAX_SEGMENT = 150.0

sys.path.insert(0, str(ROOT / "tools"))
from ffmpeg_bin import FFMPEG, FFPROBE, FFMPEG_TOOLS_DIR  # noqa: E402  (AUDIT_V1 L10)

BRIDGE_PY = ROOT / "BRIDGE" / "CODEBASE" / "lac_bridge_forge.py"
F00_PY = ROOT / "F00_SOURCE" / "CODEBASE" / "f00_pur.py"
F01_MJS = ROOT / "F01_LOOK" / "CODEBASE" / "render_pictor.mjs"
F02_PY = ROOT / "F02_MONTAGE" / "CODEBASE" / "montage.py"
F03_PY = ROOT / "F03_POSTPROD" / "CODEBASE" / "postprod.py"
F05_PY = ROOT / "F05" / "CODEBASE" / "lac_f05_camouflage.py"
F06_PY = ROOT / "F06_LUTHER" / "CODEBASE" / "lac_f06_luther.py"
CAPTION_SCHEMA = ROOT / "F03_POSTPROD" / "CODEBASE" / "caption" / "TRAVAIL" / "CODEBASE" / "caption_schema.py"
CAPTION_STYLE = ROOT / "F03_POSTPROD" / "CODEBASE" / "caption" / "OUT" / "style.json"
CAPTION_PREVIEW = ROOT / "F03_POSTPROD" / "CODEBASE" / "caption" / "PREVIEW" / "CODEBASE"
F03_PREVIEW = ROOT / "F03_PREVIEW" / "CODEBASE"
REVIEW_JSON = ROOT / "REVIEW" / "codex.json"
CODEX_RENDER = ROOT / "REVIEW" / "codex_render.json"
CONVERT_MJS = ROOT / "tools" / "convert_pur_pack.mjs"
RENDER_PICTOR = ROOT / "F01_LOOK" / "CODEBASE" / "render_pictor.mjs"


def log(msg: str) -> None:
    print(msg, flush=True)


def run(cmd: list[str]) -> int:
    log("RUN: " + " ".join(str(c) for c in cmd))
    return subprocess.run(cmd).returncode


def gate_g0(pack: dict) -> int:
    """G0 PACK — accepte les deux formes reellement produites.

    - pack MARK1 (PERTURABO) : `mode: mark1`, bornes A PLAT sur l'asset
      (`asset.start_sec` / `asset.end_sec`).
    - pack PUR adapte : `mode: pur`, bornes dans
      `asset.montage_instructions.segment`.

    Avant ce correctif, seule une troisieme forme (mode pur + assets[] avec
    montage_instructions a plat) passait : aucun producteur ne l'ecrit, donc
    un pack MARK1 valide etait refuse avec le mauvais message (L13).
    """
    mode = pack.get("mode")
    if mode not in ("pur", "mark1"):
        log(f"G0 PACK FAIL: mode={mode!r} (attendu 'pur' ou 'mark1')")
        return 2
    source = pack.get("source") or {}
    vod = source.get("vod_url")
    assets = pack.get("assets")
    if not (isinstance(assets, list) and assets):
        log("G0 PACK FAIL: assets[] absents (un pack mono-clip se rend par"
            " BRIDGE + F00_SOURCE, pas par run_all)")
        return 2
    if not vod:
        log("G0 PACK FAIL: vod_url absente")
        return 2
    for a in assets:
        mi = a.get("montage_instructions") or {}
        seg = mi.get("segment") or {}
        start = a.get("start_sec", seg.get("start_sec", mi.get("start_sec")))
        end = a.get("end_sec", seg.get("end_sec", mi.get("end_sec")))
        if start is None or end is None:
            log(f"G0 PACK FAIL: {a.get('id')} bornes absentes"
                " (start_sec/end_sec ni a plat ni dans montage_instructions.segment)")
            return 2
        start, end = float(start), float(end)
        if start >= end:
            log(f"G0 PACK FAIL: {a.get('id')} start_sec >= end_sec")
            return 2
        if end - start > MAX_SEGMENT:
            log(f"G0 PACK FAIL: {a.get('id')} segment > {MAX_SEGMENT}s")
            return 2
    log(f"G0 PACK OK: {mode} — {len(assets)} assets")
    return 0


def gate_g0s(pack: dict, style_arg: str | None, codex_style: str | None = None) -> int:
    sp = pack.get("style_pack") or {}
    # Trois formes reelles : codex (il commande), --style, pack MARK1 (asset_mode).
    style = (
        style_arg
        or codex_style
        or sp.get("style")
        or pack.get("asset_mode")
        or pack.get("montage_style")
        or ""
    ).lower()
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
            FFPROBE, "-v", "error", "-select_streams", "v:0",
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
            [FFPROBE, "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True,
            text=True,
        )
        try:
            dur = float((d.stdout or "0").strip() or 0)
        except ValueError:
            dur = 0.0
    return w, h, dur


def seconds_to_hms(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def is_fixture_vod(url: str) -> bool:
    return not url or url.rstrip("/").endswith("/videos/0")


def download_segment(vod_url: str, start: float, end: float, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    raw = dest.parent / (dest.stem + ".raw.mp4")
    cmd = [
        "yt-dlp",
        "--download-sections", f"*{seconds_to_hms(start)}-{seconds_to_hms(end)}",
        "--force-keyframes-at-cuts",
        "-f", "bv*[height<=720]+ba/b",
        "--no-playlist",
    ]
    # yt-dlp cherche `ffmpeg` dans le PATH pour les sections : il ne le trouve
    # pas ici (L10). Et il exige ffmpeg + ffprobe dans le MEME dossier
    # (ffmpeg_bin.tools_dir resout ce dossier).
    if FFMPEG_TOOLS_DIR:
        cmd += ["--ffmpeg-location", FFMPEG_TOOLS_DIR]
    cmd += ["-o", str(raw), vod_url]
    log("G1 SOURCE: yt-dlp segment " + seconds_to_hms(start) + " -> " + seconds_to_hms(end))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not raw.is_file():
        log("G1 SOURCE FAIL yt-dlp: " + ((r.stderr or r.stdout or "")[-800:]))
        return 2
    expected = max(0.5, end - start)
    trim = [
        FFMPEG, "-y", "-i", str(raw), "-t", f"{expected:.3f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", str(dest),
    ]
    t = subprocess.run(trim, capture_output=True, text=True)
    if t.returncode != 0 or not dest.is_file():
        log("G1 SOURCE FAIL trim: " + (t.stderr or "")[-800:])
        return 2
    log(f"G1 SOURCE OK: {dest.name}")
    return 0


def build_manifest(pack: Path, out: Path, codex: Path | None, packs_out: Path) -> int:
    """BRIDGE : pack (+ codex_render) -> manifest PUR. Le codex commande, le pack fournit."""
    node = shutil.which("node")
    if not node:
        log("BRIDGE FAIL: node introuvable")
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [node, str(CONVERT_MJS), "--pack", str(pack), "--out", str(out), "--packs-out", str(packs_out)]
    if codex:
        cmd += ["--codex-render", str(codex)]
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    for line in (r.stdout or "").splitlines():
        if line.strip():
            log(line.rstrip())
    if r.returncode != 0:
        log("BRIDGE FAIL: " + ((r.stderr or r.stdout or "")[-900:]))
        return 2
    return 0


def render_look(manifest: Path, index: int, clips_dir: Path, out_dir: Path, watermarks: Path) -> int:
    """P2 LOOK : le moteur Remotion dessine (titre du pack + logo du codex, 0 zoom)."""
    node = shutil.which("node")
    if not node:
        log("G3 LOOK FAIL: node introuvable")
        return 2
    log(f"P2 LOOK entry {index}: moteur Remotion → {out_dir.name}")
    cmd = [
        node, str(RENDER_PICTOR),
        "--manifest", str(manifest),
        "--clips", str(clips_dir),
        "--out", str(out_dir),
        "--watermarks", str(watermarks),
        "--entry", str(index),
    ]
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        log("G3 LOOK FAIL (P2 moteur, entry %d): %s" % (index, ((r.stdout or "")[-700:] + (r.stderr or "")[-500:])))
        return 2
    for line in (r.stdout or "").splitlines():
        if line.strip().startswith(("  [ok]", "  logo", "  [..]")):
            log(line.rstrip())
    return 0


def segment_of(asset: dict) -> dict:
    """MARK1 : bornes a plat sur l'asset. PUR : montage_instructions.segment. Les deux."""
    if isinstance(asset.get("montage_instructions"), dict):
        return asset["montage_instructions"]
    seg = {}
    for key in ("start_sec", "end_sec"):
        if asset.get(key) is not None:
            seg[key] = asset[key]
    return seg

def make_look_sample(path: Path, seconds: float) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    d = max(0.5, float(seconds))
    cmd = [
        FFMPEG, "-y",
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


def gate_g4(style_pack: dict, require_preview: bool) -> int:
    caption = style_pack.get("caption") or {}
    if not caption.get("enabled"):
        log("G4 CAPTION: disabled")
        return 0
    if not CAPTION_SCHEMA.is_file():
        log("G4 CAPTION FAIL: caption_schema absent")
        return 2
    preview_app = CAPTION_PREVIEW / "src" / "App.jsx"
    if not preview_app.is_file():
        log("G4 CAPTION FAIL: F07 PREVIEW App.jsx absent")
        return 2
    if CAPTION_STYLE.is_file():
        log(f"G4 CAPTION OK: F07 PREVIEW branchee, s1={CAPTION_STYLE}")
        return 0
    if require_preview:
        log("G4 CAPTION FAIL: F07 PREVIEW non validee (caption/OUT/style.json absent)")
        return 2
    log("G4 CAPTION: F07 housing + PREVIEW presente, style.json absent (degrade, Whisper/Blender runtime)")
    return 0


def gate_w1r(codex_path: Path, require: bool) -> int:
    """W1-R : le codex render commande le moteur. Refus si absent/invalide."""
    sys.path.insert(0, str(ROOT / "tools"))
    import codex as codex_mod

    if not codex_path.is_file():
        if require:
            log(f"W1-R FAIL: codex render absent ({codex_path})")
            return 2
        log(f"W1-R: codex render absent ({codex_path}) — style declare par le pack")
        return 0
    try:
        loaded = codex_mod.load_render_codex(codex_path, require_validated=require)
    except codex_mod.CodexError as exc:
        log(str(exc))
        for err in exc.errors:
            log(f"    - {err}")
        return exc.code
    log(f"W1-R OK: {codex_path.name} (style={loaded['style']}, logo={'on' if loaded['logo'].get('enabled') else 'off'})")
    if loaded.get("validated_by_magos") is not True:
        log("W1-R: validated_by_magos=false — rendu autorise en local, refuse en CI")
    return 0


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def codex_style_of(codex_path: Path) -> str | None:
    """Style declare par le codex (il commande), sans le valider : gate_w1r le fera."""
    if not codex_path.is_file():
        return None
    try:
        return str(load_json(codex_path).get("style") or "") or None
    except (OSError, ValueError):
        return None


def merge_review(style_pack: dict, review_path: Path) -> dict:
    """Legacy (REVIEW/codex.json). En V1 le codex ne fusionne plus ici :
    codex_render est projete par le BRIDGE, codex_postprod par F03_POSTPROD."""
    return style_pack


def merge_caption_style(style_pack: dict) -> dict:
    if not CAPTION_STYLE.is_file():
        return style_pack
    s1 = load_json(CAPTION_STYLE)
    merged = dict(style_pack)
    cap = dict(merged.get("caption") or {})
    cap["enabled"] = True
    cap["style"] = s1.get("id") or cap.get("style") or "s1"
    cap["s1"] = s1
    merged["caption"] = cap
    log("G4: caption.s1 fusionne depuis F07 OUT/style.json")
    return merged


def stage_f03_preview(pack_path: Path, look_mp4: Path | None) -> None:
    public = F03_PREVIEW / "public"
    public.mkdir(parents=True, exist_ok=True)
    dest_pack = public / "pack.json"
    dest_pack.write_bytes(pack_path.read_bytes())
    log(f"F03_PREVIEW stage: {dest_pack}")
    if look_mp4 and look_mp4.is_file():
        clips = public / "clips"
        clips.mkdir(parents=True, exist_ok=True)
        dest = clips / look_mp4.name
        dest.write_bytes(look_mp4.read_bytes())
        log(f"F03_PREVIEW stage clip: {dest}")


def stage_f07_preview(look_mp4: Path | None) -> None:
    public = CAPTION_PREVIEW / "public"
    public.mkdir(parents=True, exist_ok=True)
    if look_mp4 and look_mp4.is_file():
        dest = public / "target.mp4"
        dest.write_bytes(look_mp4.read_bytes())
        log(f"F07 PREVIEW stage clip: {dest}")
    if CAPTION_STYLE.is_file():
        dest_s = public / "style.json"
        dest_s.write_bytes(CAPTION_STYLE.read_bytes())
        log(f"F07 PREVIEW stage s1: {dest_s}")


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
    ap.add_argument("--review", type=Path, default=REVIEW_JSON, help="legacy (REVIEW/codex.json), ignore en V1")
    ap.add_argument("--codex-render", type=Path, default=CODEX_RENDER, help="codex qui commande le moteur (style, look, titre, logo)")
    ap.add_argument("--watermarks", type=Path, default=None, help="dossier du PNG watermark (defaut : dossier du pack)")
    ap.add_argument("--preview-stage", action="store_true", help="clip de reference + stage F03_PREVIEW et F07 PREVIEW, stop")
    ap.add_argument("--require-previews", action="store_true", help="W1/G4 FAIL si JSON review / style.json absents")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    code = gate_g0(pack)
    if code:
        return code
    code = gate_g0s(pack, args.style, codex_style_of(args.codex_render))
    if code:
        return code

    heisenberg = ROOT / "F04_HEISENBERG"
    if heisenberg.exists():
        log("NOTE: F04_HEISENBERG present hors flux — jamais appele (V1, 0 jump cut).")

    items = assets_of(pack)
    style_pack = pack.get("style_pack") or {}
    style_pack = merge_review(style_pack, args.review)
    style_pack = merge_caption_style(style_pack)
    log("PIPELINE: BRIDGE (codex_render) → F00_SOURCE → F01_LOOK (P2 moteur) → F02_MONTAGE → F03_POSTPROD (F07 CAPTION → GLOW → LUT → FADE) → F05 → F06")
    log(f"G-PACK: meme codex pour tous les assets ({len(items)} clips)")
    if args.dry_run:
        log("DRY-RUN: portes G0/G0-S OK, stop avant execution.")
        return 0

    code = gate_w1r(args.codex_render, args.require_previews and not args.preview_stage)
    if code:
        return code
    code = gate_g4(style_pack, args.require_previews and not args.preview_stage)
    if code:
        return code
    code = gate_gl1(style_pack)
    if code:
        return code

    args.work.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)
    style_pack_path = args.work / "style_pack.json"
    style_pack_path.write_text(json.dumps(style_pack, indent=2), encoding="utf-8")

    # BRIDGE : une seule projection codex pour tous les clips. Le codex fixe
    # style/look/titre/logo ; le pack fournit texte, bornes et PNG.
    manifest_path = args.work / "pur_manifest.json"
    code = build_manifest(
        args.pack,
        manifest_path,
        args.codex_render if args.codex_render.is_file() else None,
        args.work / "PUR",
    )
    if code:
        return code
    watermarks_dir = args.watermarks or args.pack.parent
    log(f"G3 LOOK: moteur Remotion (manifest={manifest_path.name}, watermark={watermarks_dir})")
    stage_f03_preview(args.pack, None)

    delivered = 0
    ref_id = pack.get("reference_asset") or (items[0].get("id") if items else None)
    for index, asset in enumerate(items):
        aid = asset.get("id") or "clip"
        log(f"=== asset {aid} ===")
        mi = segment_of(asset)
        mi_path = args.work / f"{aid}_montage.json"
        mi_path.write_text(json.dumps(mi, indent=2), encoding="utf-8")

        look_mp4 = args.work / f"pur_{aid}_look.mp4"
        src_mp4 = args.work / f"pur_{aid}.mp4"
        if args.look_dir:
            cand = args.look_dir / f"{aid}_look.mp4"
            if cand.is_file():
                look_mp4 = cand
        start = float(mi.get("start_sec", 0))
        end = float(mi.get("end_sec", 2))
        vod_url = (pack.get("source") or {}).get("vod_url") or ""
        if not look_mp4.exists():
            if is_fixture_vod(vod_url):
                code = make_look_sample(look_mp4, end - start)
                if code:
                    return code
                src_mp4 = look_mp4
            else:
                code = download_segment(vod_url, start, end, src_mp4)
                if code:
                    return code
                # P2 : le moteur dessine (titre pack + logo codex). Plus de blur ffmpeg.
                code = render_look(manifest_path, index, args.work, args.work, watermarks_dir)
                if code:
                    return code
        else:
            log(f"G1 SOURCE OK: {look_mp4} (look fourni)")
            if not src_mp4.exists():
                src_mp4 = look_mp4

        code = gate_g2(src_mp4, start, end)
        if code:
            return code
        code = gate_g3(look_mp4)
        if code:
            return code

        if aid == ref_id:
            stage_f03_preview(args.pack, look_mp4)
            stage_f07_preview(look_mp4)
            if args.preview_stage:
                log("PREVIEW STAGE OK: F03_PREVIEW public/pack.json + clip")
                log("PREVIEW STAGE OK: F07 PREVIEW public/target.mp4")
                log("Operateur: cd F03_PREVIEW/CODEBASE && npm ci && npm run dev   (port 5174)")
                log("Operateur: cd F03_POSTPROD/CODEBASE/caption/PREVIEW/CODEBASE && npm ci && npm run dev   (port 5173)")
                log("Valider: Export codex -> REVIEW/codex_render.json + REVIEW/codex_postprod.json")
                log("Valider: Save s1 -> F03_POSTPROD/CODEBASE/caption/OUT/style.json")
                log("Puis relancer run_all SANS --preview-stage")
                return 0

        if aid == ref_id and (style_pack.get("glow") or {}).get("enabled"):
            preview_png = args.work / f"{aid}_glow_preview.png"
            glow = style_pack["glow"]
            prev = [
                sys.executable,
                str(ROOT / "F03_POSTPROD" / "CODEBASE" / "glow" / "preview_glow.py"),
                "--frame", str(look_mp4),
                "--out", str(preview_png),
                "--mode", str(glow.get("mode", "scene")),
                "--sigma", str(glow.get("sigma", 12)),
                "--opacity", str(glow.get("opacity", 0.35)),
            ]
            code = run(prev)
            if code or not preview_png.is_file():
                log("GL2 FAIL: preview frame")
                return 2
            log(f"GL2 OK: preview {preview_png.name}")

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
