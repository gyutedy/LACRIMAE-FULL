#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "run_all.py"
PACK_OK = Path(__file__).resolve().parent / "sanguinala_p5_pack.json"
PACK_SPLIT = Path(__file__).resolve().parent / "sanguinala_p5_split_scene.json"


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(RUN), *args], capture_output=True, text=True)


def test_g0s_split_scene():
    r = run(["--pack", str(PACK_SPLIT), "--dry-run"])
    assert r.returncode == 2, r.stdout + r.stderr
    assert "G0-S STYLE FAIL" in r.stdout
    assert "split_scene" in r.stdout


def test_g0_ok_dry_run():
    r = run(["--pack", str(PACK_OK), "--dry-run"])
    assert r.returncode == 0, r.stdout + r.stderr
    assert "G0 PACK OK: 2 assets" in r.stdout
    assert "G0-S STYLE OK: blur" in r.stdout
    assert "F04_HEISENBERG" in r.stdout
    assert "jamais appele" in r.stdout


def test_g0_missing_assets(tmp_path: Path):
    bad = tmp_path / "bad.json"
    data = json.loads(PACK_OK.read_text())
    data["assets"] = []
    bad.write_text(json.dumps(data))
    r = run(["--pack", str(bad), "--dry-run"])
    assert r.returncode == 2
    assert "G0 PACK FAIL" in r.stdout


if __name__ == "__main__":
    tmp = ROOT / "WORK" / "p5_gate_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    failed = 0
    for t in (test_g0s_split_scene, test_g0_ok_dry_run, lambda: test_g0_missing_assets(tmp)):
        name = getattr(t, "__name__", "lambda")
        try:
            t()
            print("OK", name)
        except Exception as e:
            failed += 1
            print("FAIL", name, e)
    sys.exit(2 if failed else 0)
