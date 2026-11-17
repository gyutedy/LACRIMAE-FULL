"""Tests F03_POSTPROD : le codex commande, l'ordre est grave, le LUT s'applique.

Aucun ffmpeg n'est requis : on teste la projection du codex, la porte PP2 et la
construction des filtres. Les chemins mediа sont couverts par run_all/CI.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
F03 = HERE.parent
ROOT = F03.parent.parent
sys.path.insert(0, str(F03))
sys.path.insert(0, str(F03 / "lut"))

import postprod  # noqa: E402
import lut_apply  # noqa: E402


def codex_sample() -> dict:
    return json.loads((ROOT / "REVIEW" / "codex_postprod.json").read_text(encoding="utf-8"))


class TestOrder:
    """PP2 : glow -> caption -> lut -> fade. Inverser floute les sous-titres."""

    def test_ordre_nominal(self):
        assert postprod.check_pp2(codex_sample()) == 0

    def test_ordre_inverse_refuse(self, capsys):
        codex = codex_sample()
        codex["order"] = ["caption", "glow", "lut", "fade"]
        assert postprod.check_pp2(codex) == 2
        assert "PP2 FAIL" in capsys.readouterr().out

    def test_ordre_sans_fade_refuse(self):
        codex = codex_sample()
        codex["order"] = ["glow", "caption", "lut"]
        assert postprod.check_pp2(codex) == 2


class TestProfile:
    """L1 : un profil inconnu est une erreur, pas un silence."""

    def test_profil_connu_donne_des_filtres(self):
        profile = lut_apply.resolve_profile("hdr_imperator")
        filters = lut_apply.profile_filters(profile)
        joined = ",".join(filters)
        assert any(f.startswith("eq=") for f in filters), joined
        assert any(f.startswith("unsharp=") for f in filters), joined
        assert any(f.startswith("hqdn3d=") for f in filters), joined

    def test_profil_inconnu_leve(self):
        with pytest.raises(KeyError) as exc:
            lut_apply.resolve_profile("profil_qui_n_existe_pas")
        assert "hdr_imperator" in str(exc.value)

    def test_tous_les_profils_sont_applicables(self):
        data = lut_apply.load_profiles()
        assert data["profiles"], "atom_ic_profiles.json vide"
        assert data["default_profile"] in data["profiles"]
        for name in data["profiles"]:
            assert lut_apply.profile_filters(data["profiles"][name]), name


class TestProjection:
    def test_codex_porte_glow_lut_fade(self):
        codex = codex_sample()
        assert codex["glow"]["enabled"] is True
        assert codex["lut"]["enabled"] is True
        assert codex["lut"]["profile"]
        assert codex["fade_out"]["mode"] in ("darken", "black")

    def test_legacy_style_pack_est_converti(self):
        legacy = {"glow": {"enabled": True, "mode": "subject", "sigma": 20, "opacity": 0.5},
                  "lut": {"enabled": False}, "caption": {}}
        codex = postprod.legacy_style_pack_to_codex(legacy)
        assert codex["order"] == postprod.PP2_ORDER
        assert codex["glow"]["sigma"] == 20
        assert codex["fade_out"]["mode"] == "darken"


class TestPortes:
    """PP1 : un codex non signe ferme la post-prod."""

    def _run(self, tmp_path: Path, codex: dict) -> subprocess.CompletedProcess:
        tmp = tmp_path
        path = tmp / "codex_postprod.json"
        path.write_text(json.dumps(codex), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(F03 / "postprod.py"),
             "--input", str(tmp / "absent.mp4"),
             "--output", str(tmp / "out.mp4"),
             "--codex-postprod", str(path),
             "--work", str(tmp / "work")],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_codex_non_signe_refuse(self, tmp_path):
        codex = codex_sample()
        codex["validated_by_magos"] = False
        proc = self._run(tmp_path, codex)
        assert proc.returncode == 2, proc.stdout
        assert "PP1 FAIL" in proc.stdout

    def test_codex_ordre_inverse_refuse(self, tmp_path):
        codex = codex_sample()
        codex["order"] = ["caption", "glow", "lut", "fade"]
        proc = self._run(tmp_path, codex)
        assert proc.returncode in (1, 2), proc.stdout
        assert "PP2 FAIL" in proc.stdout or "order" in proc.stdout
