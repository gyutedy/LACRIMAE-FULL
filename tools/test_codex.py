#!/usr/bin/env python3
"""Tests du contrat des deux codex (tools/codex.py) — PR3.

    python -m unittest tools.test_codex -v

Cas : les 2 codex commites valident ; un champ manquant est refuse ; la
porte W1-R/PP1 refuse `validated_by_magos: false` ; le codex ne nomme jamais
un titre ; l'ordre post-prod est grave (PP2) ; les bornes de valeurs sont
appliquees ; les cles inconnues sont refusees.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from codex import (  # noqa: E402
    CodexError,
    FROZEN_ORDER,
    POSTPROD,
    RENDER,
    check,
    ensure_validated,
    load_postprod_codex,
    load_render_codex,
    normalize_postprod_codex,
    normalize_render_codex,
)

ROOT = Path(__file__).resolve().parent.parent
RENDER_CODEX = ROOT / "REVIEW" / "codex_render.json"
POSTPROD_CODEX = ROOT / "REVIEW" / "codex_postprod.json"


def render_sample() -> dict:
    return json.loads(RENDER_CODEX.read_text(encoding="utf-8"))


def postprod_sample() -> dict:
    return json.loads(POSTPROD_CODEX.read_text(encoding="utf-8"))


class TestCommittedCodex(unittest.TestCase):
    def test_render_commite_valide(self):
        raw = render_sample()
        self.assertEqual(check(RENDER, raw), [], "codex_render.json doit valider")

    def test_postprod_commite_valide(self):
        raw = postprod_sample()
        self.assertEqual(check(POSTPROD, raw), [], "codex_postprod.json doit valider")

    def test_les_deux_sont_chargeables(self):
        load_render_codex(RENDER_CODEX, require_validated=False)
        load_postprod_codex(POSTPROD_CODEX, require_validated=False)

    def test_ordre_fige(self):
        self.assertEqual(FROZEN_ORDER, ["glow", "caption", "lut", "fade"])


class TestRefusSchema(unittest.TestCase):
    def test_champ_obligatoire_absent(self):
        raw = render_sample()
        del raw["logo"]
        errors = check(RENDER, raw)
        self.assertTrue(any("$.logo: champ obligatoire absent" in e for e in errors))

    def test_schema_version_fausse(self):
        raw = render_sample()
        raw["schema_version"] = "autre.v1"
        self.assertTrue(check(RENDER, raw))

    def test_cle_inconnue_refusee(self):
        raw = render_sample()
        raw["zoom"] = {"amount": 1.1}  # interdit en V1
        self.assertTrue(any("$.zoom: champ inconnu" in e for e in check(RENDER, raw)))

    def test_valeur_hors_bornes(self):
        raw = render_sample()
        raw["look"]["degree"] = 500  # schema : 0..120
        self.assertTrue(any("$.look.degree" in e for e in check(RENDER, raw)))

    def test_couleur_non_hexa(self):
        raw = render_sample()
        raw["title"]["line1_color"] = "bleu"
        self.assertTrue(any("$.title.line1_color" in e for e in check(RENDER, raw)))

    def test_style_split_scene_refuse(self):
        raw = render_sample()
        raw["style"] = "split_scene"  # V2+
        self.assertTrue(check(RENDER, raw))


class TestDoctrineTexte(unittest.TestCase):
    def test_render_ne_porte_jamais_un_titre(self):
        for key in ("text", "overlay_title", "titles", "lines", "content"):
            raw = render_sample()
            raw[key] = "un titre invente"
            self.assertTrue(
                check(RENDER, raw),
                f"cle texte {key!r} : le codex ne porte jamais un titre",
            )

    def test_nested_interdit(self):
        raw = render_sample()
        raw["title"]["overlay_title"] = "interdit"
        self.assertTrue(any("$.title.overlay_title" in e for e in check(RENDER, raw)))


class TestPortes(unittest.TestCase):
    def test_w1r_refuse_non_valide(self):
        raw = render_sample()
        with self.assertRaises(CodexError) as ctx:
            ensure_validated(raw, RENDER)
        self.assertEqual(ctx.exception.code, 2)

    def test_w1r_ouvre_si_valide(self):
        raw = render_sample()
        raw["validated_by_magos"] = True
        ensure_validated(raw, RENDER)  # ne doit pas lever

    def test_pp1_refuse_non_valide(self):
        raw = postprod_sample()
        with self.assertRaises(CodexError) as ctx:
            ensure_validated(raw, POSTPROD)
        self.assertEqual(ctx.exception.code, 2)

    def test_pp2_ordre_grave(self):
        raw = postprod_sample()
        raw["order"] = ["caption", "glow", "lut", "fade"]  # sous-titres floutes
        errors = check(POSTPROD, raw)
        self.assertTrue(any("$.order" in e for e in errors), errors)


class TestNormalisation(unittest.TestCase):
    def test_render_custom_logo_defauts(self):
        raw = render_sample()
        raw["logo"]["position"] = "custom"
        norm = normalize_render_codex(raw)
        self.assertEqual(norm["logo"]["x_pct"], 50)
        self.assertEqual(norm["logo"]["y_pct"], 50)

    def test_render_aucune_invention(self):
        raw = render_sample()
        norm = normalize_render_codex(raw)
        self.assertEqual(norm, raw)  # ni champ ajoute ni champ efface

    def test_postprod_ordre_force(self):
        raw = postprod_sample()
        raw["order"] = ["caption", "glow", "lut", "fade"]
        self.assertEqual(normalize_postprod_codex(raw)["order"], FROZEN_ORDER)

    def test_postprod_mode_glow_defaut(self):
        raw = postprod_sample()
        del raw["glow"]["mode"]
        self.assertEqual(normalize_postprod_codex(raw)["glow"]["mode"], "scene")


if __name__ == "__main__":
    unittest.main()