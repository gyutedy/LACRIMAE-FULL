#!/usr/bin/env python3
"""CAPTION grave — style `dev11.caption.style.v1` -> ASS -> ffmpeg (libass).

La passe CAPTION de F03_POSTPROD etait declaree `applied: false` (L18) : le
style voyageait, rien n'etait grave. Ce module grave pour de vrai, sans Blender
et sans GPU :

    audio du clip -> mots (whisper, ou transcript fourni)
                  -> cues (1-2 mots, style TikTok)
                  -> fichier .ass (police du depot)
                  -> ffmpeg `ass=` (libass), fonte dans la meme passe que
                     LUT et FADE

Le style ne vient que du codex : taille, place, couleur, contour, motion.
Aucune decision de style ici.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from ffmpeg_bin import FFMPEG  # noqa: E402

FONT_DIR = HERE / "TRAVAIL" / "CODEBASE" / "fonts"
CANVAS = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}
MOTIONS = {"pop-in", "bounce", "slide"}


class CaptionError(RuntimeError):
    """Erreur explicite : la passe ne peut pas etre appliquee, et le dit."""


# ── couleurs / style ─────────────────────────────────────────────────────────

def hex_to_ass(color: str, alpha: int = 0) -> str:
    """#RRGGBB -> &HAABBGGRR (ASS est en BGR, AA=00 opaque, FF transparent)."""
    raw = (color or "").lstrip("#")
    if len(raw) == 3:
        raw = "".join(c * 2 for c in raw)
    if len(raw) != 6:
        raise CaptionError(f"couleur non hexa : {color!r}")
    try:
        r, g, b = (int(raw[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError as exc:
        raise CaptionError(f"couleur non hexa : {color!r}") from exc
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"


def font_name(style: dict) -> str:
    """`Montserrat-ExtraBold.ttf` -> `Montserrat ExtraBold` (nom lisible par libass)."""
    font = str(style.get("font") or "Montserrat-ExtraBold.ttf")
    for ext in (".ttf", ".otf"):
        if font.lower().endswith(ext):
            font = font[: -len(ext)]
    return font.replace("-", " ").strip() or "Montserrat ExtraBold"


def alignment_and_margins(style: dict, canvas: tuple[int, int]) -> tuple[int, int, int]:
    """x_pct -> alignement (1 gauche, 2 centre, 3 droite) + marges en pixels."""
    width, height = canvas
    position = style.get("position") or {}
    x_pct = float(position.get("x_pct", 50))
    y_pct = float(position.get("y_pct", 78))
    size = float(style.get("size", 72))
    if x_pct < 34:
        align, margin_l = 1, int(round(width * x_pct / 100))
    elif x_pct > 66:
        align, margin_l = 3, 0
    else:
        align, margin_l = 2, 0
    margin_v = max(0, int(round(height * (1 - y_pct / 100) - size / 2)))
    return align, margin_l, margin_v


def motion_tags(style: dict, canvas: tuple[int, int]) -> str:
    """Le motion du codex, traduit en overrides ASS."""
    motion = style.get("motion") if style.get("motion") in MOTIONS else "pop-in"
    speed = max(0.25, min(3.0, float(style.get("motion_speed", 1) or 1)))
    fade_in = int(round(90 / speed))
    fade_out = int(round(70 / speed))
    if motion == "bounce":
        return f"\\fad({fade_in},{fade_out})\\fscy125\\t(0,120,\\fscy100)"
    if motion == "slide":
        width, height = canvas
        position = style.get("position") or {}
        x = int(round(width * float(position.get("x_pct", 50)) / 100))
        y = int(round(height * float(position.get("y_pct", 78)) / 100))
        return f"\\fad({fade_in},{fade_out})\\move({x},{y + 60},{x},{y},0,{int(round(160 / speed))})"
    return (
        f"\\fad({fade_in},{fade_out})\\fscx55\\fscy55"
        f"\\t(0,{int(round(140 / speed))},\\fscx100\\fscy100)"
    )


def glow_tag(style: dict) -> str:
    glow = style.get("glow") or {}
    intensity = float(glow.get("intensity", 0) or 0)
    if intensity <= 0:
        return ""
    return f"\\blur{min(4.0, intensity * 1.2):.1f}"


# ── cues ─────────────────────────────────────────────────────────────────────

def _escape(text: str) -> str:
    clean = " ".join(str(text).split())
    return clean.replace("{", "(").replace("}", ")").replace("\\", "/")


def cues_from_words(
    words: list[dict],
    max_words: int = 2,
    max_chars: int = 22,
    max_duration: float = 1.8,
    gap_break: float = 0.6,
) -> list[dict]:
    """Regroupe les mots en cues courtes (style sous-titre social)."""
    cues: list[dict] = []
    group: list[dict] = []

    def flush() -> None:
        if not group:
            return
        cues.append({
            "text": _escape(" ".join(w["word"] for w in group)),
            "start": float(group[0]["start"]),
            "end": max(float(group[-1]["end"]), float(group[0]["start"]) + 0.25),
        })
        group.clear()

    for word in words:
        text = str(word.get("word") or "").strip()
        if not text:
            continue
        if group:
            previous = group[-1]
            too_long = sum(len(w["word"]) + 1 for w in group) + len(text) > max_chars
            too_slow = float(word["start"]) - float(previous["end"]) > gap_break
            too_wide = len(group) >= max_words
            too_tall = float(word["end"]) - float(group[0]["start"]) > max_duration
            if too_long or too_slow or too_wide or too_tall:
                flush()
        group.append({"word": text, "start": float(word["start"]), "end": float(word["end"])})
    flush()
    return cues


# ── ASS ──────────────────────────────────────────────────────────────────────

def build_ass(style: dict, cues: list[dict], canvas_label: str = "9:16") -> str:
    canvas = CANVAS.get(canvas_label, CANVAS["9:16"])
    width, height = canvas
    size = float(style.get("size", 72))
    align, margin_l, margin_v = alignment_and_margins(style, canvas)
    outline = style.get("outline") or {}
    primary = hex_to_ass(style.get("color", "#FFFFFF"))
    outline_color = hex_to_ass(outline.get("color", "#000000"))
    border = float(outline.get("width", 4) or 0)

    header = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        (
            f"Style: Cap,{font_name(style)},{size:g},{primary},{primary},{outline_color},"
            f"&H00000000,-1,0,0,0,100,100,0,0,1,{border:g},0,{align},"
            f"{margin_l},0,{margin_v},1"
        ),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    tags = motion_tags(style, canvas) + glow_tag(style)
    events = [
        f"Dialogue: 0,{_ass_time(c['start'])},{_ass_time(c['end'])},Cap,,0,0,0,,{{{tags}}}{c['text']}"
        for c in cues
    ]
    return "\n".join(header + events) + "\n"


def _ass_time(seconds: float) -> str:
    total = max(0.0, float(seconds))
    hours = int(total // 3600)
    minutes = int((total % 3600) // 60)
    secs = total % 60
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


# ── transcription ────────────────────────────────────────────────────────────

def words_from_transcript(path: Path) -> list[dict]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    words = raw.get("words") if isinstance(raw, dict) else None
    if not words and isinstance(raw, dict):
        words = [
            {"word": item.get("text") or item.get("word"), "start": item.get("start"), "end": item.get("end")}
            for item in (raw.get("segments") or [])
        ]
    if not words:
        raise CaptionError(f"transcript sans mots : {path}")
    return [
        {"word": str(w.get("word") or "").strip(), "start": float(w["start"]), "end": float(w["end"])}
        for w in words
        if w.get("word") and w.get("start") is not None and w.get("end") is not None
    ]


def words_from_whisper(video: Path, model_name: str = "base") -> list[dict]:
    try:
        from faster_whisper import WhisperModel  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - depend de l'env
        raise CaptionError(
            "faster-whisper absent : fournir --transcript ou installer faster-whisper"
        ) from exc
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(str(video), word_timestamps=True, vad_filter=True)
    words: list[dict] = []
    for segment in segments:
        for w in (segment.words or []):
            text = (w.word or "").strip()
            if text:
                words.append({"word": text, "start": float(w.start), "end": float(w.end)})
    if not words:
        raise CaptionError("whisper n'a produit aucun mot (audio muet ?)")
    return words


# ── rendu ────────────────────────────────────────────────────────────────────

def font_file(style: dict) -> Path:
    """La police doit voyager avec le depot : sinon libass retombe en silence."""
    name = str(style.get("font") or "Montserrat-ExtraBold.ttf")
    path = FONT_DIR / name
    if not path.is_file():
        raise CaptionError(
            f"police absente du depot : {name} (attendu dans {FONT_DIR})"
        )
    return path


def check_g4(style: dict) -> int:
    """G4 : taille et place exploitables, sinon refus."""
    size = style.get("size")
    position = style.get("position") or {}
    try:
        size = float(size)
        x_pct = float(position.get("x_pct", 50))
        y_pct = float(position.get("y_pct", 78))
    except (TypeError, ValueError):
        print("G4 FAIL: taille / position illisibles", flush=True)
        return 2
    if not 12 <= size <= 240:
        print(f"G4 FAIL: taille {size} hors 12..240", flush=True)
        return 2
    if not (0 <= x_pct <= 100 and 0 <= y_pct <= 100):
        print(f"G4 FAIL: position ({x_pct},{y_pct}) hors 0..100", flush=True)
        return 2
    return 0


def render(
    video: Path,
    style: dict,
    work: Path,
    transcript: Path | None = None,
    model_name: str = "base",
) -> dict:
    """Retourne la description de la passe : aucun echec silencieux."""
    if check_g4(style) != 0:
        raise CaptionError("style G4 invalide")
    font_file(style)
    work.mkdir(parents=True, exist_ok=True)
    if transcript:
        words, source = words_from_transcript(Path(transcript)), f"transcript:{Path(transcript).name}"
    else:
        words, source = words_from_whisper(Path(video), model_name), f"whisper:{model_name}"
    cues = cues_from_words(words)
    if not cues:
        raise CaptionError("aucun cue exploitable")
    canvas = style.get("canvas", "9:16")
    ass_path = work / f"{Path(video).stem}_cap.ass"
    ass_path.write_text(build_ass(style, cues, canvas), encoding="utf-8")
    return {
        "applied": True,
        "engine": "ass",
        "font": font_file(style).name,
        "source": source,
        "words": len(words),
        "cues": len(cues),
        "ass": str(ass_path),
        "first_cue": cues[0]["text"],
        "last_cue_end": cues[-1]["end"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="CAPTION : grave les sous-titres (ASS/libass)")
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=None, help="ASS a ecrire (defaut: <input>_cap.ass)")
    ap.add_argument("--codex-postprod", type=Path, default=None)
    ap.add_argument("--transcript", type=Path, default=None)
    ap.add_argument("--model", default="base")
    args = ap.parse_args()

    style = {"schema_version": "dev11.caption.style.v1", "size": 72,
             "position": {"x_pct": 50, "y_pct": 78}, "color": "#FFFFFF",
             "outline": {"width": 4, "color": "#000000"}, "canvas": "9:16"}
    if args.codex_postprod:
        codex = json.loads(args.codex_postprod.read_text(encoding="utf-8"))
        style = codex.get("caption") or style

    work = args.output.parent if args.output else args.input.parent
    try:
        info = render(args.input, style, work, args.transcript, args.model)
    except CaptionError as exc:
        print(f"G4/CAPTION FAIL: {exc}", flush=True)
        return 2
    ass_path = Path(info["ass"])
    if args.output:
        ass_path.replace(args.output)
        info["ass"] = str(args.output)
    print(json.dumps(info, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
