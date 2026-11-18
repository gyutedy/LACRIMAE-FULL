"""CAPTION : style du codex -> ASS -> pixels graves (L18).

Le point de ces tests n'est pas la beaute du texte : c'est que le style du codex
(taille, place, couleur, contour, motion) atterrisse dans le .ass, et que la
gravure change vraiment l'image.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
F03 = HERE.parent
ROOT = F03.parent.parent
sys.path.insert(0, str(F03 / "caption"))
sys.path.insert(0, str(F03 / "lut"))
sys.path.insert(0, str(ROOT / "tools"))

import ass_render  # noqa: E402
from ffmpeg_bin import FFMPEG  # noqa: E402

STYLE = {
    "schema_version": "dev11.caption.style.v1",
    "id": "s1",
    "font": "Montserrat-ExtraBold.ttf",
    "position": {"x_pct": 50, "y_pct": 78},
    "size": 72,
    "color": "#FFFFFF",
    "outline": {"width": 4, "color": "#000000"},
    "glow": {"intensity": 1.2, "color": "#FFFFFF"},
    "motion": "pop-in",
    "motion_speed": 1,
    "canvas": "9:16",
}

WORDS = [
    {"word": w, "start": round(0.2 + i * 0.32, 2), "end": round(0.48 + i * 0.32, 2)}
    for i, w in enumerate("She lost fifty thousand dollars on a bet today".split())
]


class TestCouleurs:
    def test_hexa_vers_ass(self):
        assert ass_render.hex_to_ass("#FFFFFF") == "&H00FFFFFF"
        assert ass_render.hex_to_ass("#FFD700") == "&H0000D7FF"      # BGR
        assert ass_render.hex_to_ass("#F00") == "&H000000FF"
        assert ass_render.hex_to_ass("#000000", alpha=0x40) == "&H40000000"

    def test_hexa_invalide_refuse(self):
        with pytest.raises(ass_render.CaptionError):
            ass_render.hex_to_ass("rouge")
        with pytest.raises(ass_render.CaptionError):
            ass_render.hex_to_ass("#GGGGGG")


class TestPlace:
    def test_centre(self):
        align, margin_l, margin_v = ass_render.alignment_and_margins(STYLE, (1080, 1920))
        assert align == 2
        assert margin_l == 0
        assert margin_v == 386          # 1920*0.22 - 36

    def test_gauche_et_droite(self):
        left = dict(STYLE, position={"x_pct": 10, "y_pct": 78})
        right = dict(STYLE, position={"x_pct": 90, "y_pct": 78})
        assert ass_render.alignment_and_margins(left, (1080, 1920))[0] == 1
        assert ass_render.alignment_and_margins(left, (1080, 1920))[1] == 108
        assert ass_render.alignment_and_margins(right, (1080, 1920))[0] == 3

    def test_remonte_avec_y_pct(self):
        bas = dict(STYLE, position={"x_pct": 50, "y_pct": 90})
        haut = dict(STYLE, position={"x_pct": 50, "y_pct": 60})
        # y_pct petit = plus haut = marge basse plus grande
        assert (
            ass_render.alignment_and_margins(bas, (1080, 1920))[2]
            < ass_render.alignment_and_margins(haut, (1080, 1920))[2]
        )


class TestCues:
    def test_deux_mots_par_cue(self):
        cues = ass_render.cues_from_words(WORDS)
        assert len(cues) == 5
        assert cues[0]["text"] == "She lost"
        assert cues[0]["start"] == pytest.approx(0.2)
        assert all(len(c["text"].split()) <= 2 for c in cues)

    def test_le_silence_coupe(self):
        words = [
            {"word": "un", "start": 0.0, "end": 0.3},
            {"word": "deux", "start": 1.5, "end": 1.8},
        ]
        cues = ass_render.cues_from_words(words)
        assert len(cues) == 2

    def test_mot_long_seul(self):
        cues = ass_render.cues_from_words([{"word": "incomprehensibilite", "start": 0, "end": 1}])
        assert len(cues) == 1
        assert cues[0]["text"] == "incomprehensibilite"

    def test_accolades_ne_cassent_pas_l_ass(self):
        cues = ass_render.cues_from_words([{"word": "a{b}c\\d", "start": 0, "end": 1}])
        assert "{" not in cues[0]["text"]
        assert "\\" not in cues[0]["text"]

    def test_duree_minimale(self):
        cues = ass_render.cues_from_words([{"word": "hop", "start": 1.0, "end": 1.0}])
        assert cues[0]["end"] - cues[0]["start"] >= 0.25


class TestAssFile:
    def test_entete_et_style(self):
        ass = ass_render.build_ass(STYLE, ass_render.cues_from_words(WORDS), "9:16")
        assert "PlayResX: 1080" in ass
        assert "PlayResY: 1920" in ass
        assert "Montserrat ExtraBold" in ass
        assert ",72," in ass                     # la taille du codex
        assert ",2,0,0,386,1" in ass             # alignement centre + marge
        assert "&H00FFFFFF" in ass               # couleur du codex
        assert "&H00000000" in ass               # contour noir
        assert ass.count("Dialogue:") == 5

    def test_motion_pop_in(self):
        tags = ass_render.motion_tags(STYLE, (1080, 1920))
        assert "\\fad(" in tags
        assert "\\fscx55" in tags
        assert "\\t(0,140,\\fscx100" in tags

    def test_motion_bounce_et_slide(self):
        bounce = ass_render.motion_tags(dict(STYLE, motion="bounce"), (1080, 1920))
        slide = ass_render.motion_tags(dict(STYLE, motion="slide"), (1080, 1920))
        assert "\\fscy125" in bounce
        assert "\\move(" in slide

    def test_glow_devient_un_flou(self):
        assert ass_render.glow_tag(STYLE) == "\\blur1.4"
        assert ass_render.glow_tag(dict(STYLE, glow={"intensity": 0})) == ""

    def test_temps_ass(self):
        assert ass_render._ass_time(0) == "0:00:00.00"
        assert ass_render._ass_time(61.5) == "0:01:01.50"
        assert ass_render._ass_time(3661.25) == "1:01:01.25"


class TestPoliceEtPorte:
    def test_police_du_depot(self):
        assert ass_render.font_file(STYLE).name == "Montserrat-ExtraBold.ttf"

    def test_police_absente_refusee(self):
        with pytest.raises(ass_render.CaptionError):
            ass_render.font_file(dict(STYLE, font="Comic-Sans.ttf"))

    def test_g4_taille_hors_bornes(self):
        assert ass_render.check_g4(dict(STYLE, size=400)) == 2
        assert ass_render.check_g4(dict(STYLE, size=72)) == 0

    def test_transcript_sans_mots(self, tmp_path):
        path = tmp_path / "t.json"
        path.write_text('{"words": []}', encoding="utf-8")
        with pytest.raises(ass_render.CaptionError):
            ass_render.words_from_transcript(path)


def _clip(path: Path, seconds: float = 1.2) -> None:
    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"color=c=0x203040:s=360x640:d={seconds}:r=30",
        "-f", "lavfi", "-i", f"sine=frequency=300:duration={seconds}",
        "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
        str(path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0 and path.is_file(), (res.stderr or "")[-400:]


def _bright_in_band(png: Path, y0: float, y1: float) -> int:
    from PIL import Image  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    img = np.asarray(Image.open(png).convert("L")).astype(int)
    height = img.shape[0]
    band = img[int(height * y0):int(height * y1)]
    return int((band > 200).sum())


class TestGravure:
    """Le vrai test de L18 : des pixels de texte apparaissent, et la-bas seulement."""

    def test_render_puis_burn(self, tmp_path):
        clip = tmp_path / "in.mp4"
        _clip(clip)
        transcript = tmp_path / "t.json"
        transcript.write_text(
            '{"words": [{"word": "She", "start": 0.1, "end": 0.5}, '
            '{"word": "lost", "start": 0.55, "end": 0.95}]}',
            encoding="utf-8",
        )
        info = ass_render.render(clip, STYLE, tmp_path / "work", transcript=transcript)
        assert info["applied"] is True
        assert info["cues"] == 1
        assert info["font"] == "Montserrat-ExtraBold.ttf"
        ass_path = Path(info["ass"])
        assert ass_path.is_file() and "Dialogue:" in ass_path.read_text(encoding="utf-8")

        # la gravure passe par la vraie passe LUT/FADE (une seule re-encode)
        burned = tmp_path / "burned.mp4"
        cmd = [
            sys.executable, str(F03 / "lut" / "lut_apply.py"),
            "--input", str(clip), "--output", str(burned),
            "--profile", "hdr_imperator", "--fade", "darken", "--fade-duration", "0.2",
            "--ass", str(ass_path), "--fontsdir", str(ass_render.FONT_DIR),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        assert res.returncode == 0, (res.stdout or "")[-600:] + (res.stderr or "")[-400:]

        shot = tmp_path / "shot.png"
        subprocess.run([FFMPEG, "-y", "-ss", "0.3", "-i", str(burned), "-frames:v", "1", str(shot)],
                       capture_output=True, text=True)
        assert _bright_in_band(shot, 0.70, 0.88) > 50, "aucun glyphe dans la bande des sous-titres"
        assert _bright_in_band(shot, 0.0, 0.5) == 0, "du texte est apparu hors de la zone"
