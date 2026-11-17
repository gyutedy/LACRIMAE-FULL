#!/usr/bin/env python3
"""ffmpeg_bin.py — resolution unique de ffmpeg / ffprobe (AUDIT_V1 L10).

Sur la machine de dev, `ffmpeg` et `ffprobe` existent (C:\\ffmpeg\\bin) mais ne
sont pas dans le PATH. Un nom nu fait mourir G1/G3/P-AUD sur un
FileNotFoundError, transforme en faux refus metier. Ici, un seul ordre de
recherche pour tout le depot :

  1. <NOM>_BIN (et FFMPEG_BIN pour ffmpeg) — override operateur / CI
  2. PATH
  3. binaire livre par imageio-ffmpeg (ffmpeg seulement)
  4. dossiers connus (FFMPEG_DIR, C:\\ffmpeg\\bin, /usr/local/bin, /opt/homebrew/bin)
  5. nom nu : l'echec reste visible, mais il est desormais explicite

Usage :
    from ffmpeg_bin import FFMPEG, FFPROBE
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

KNOWN_DIRS = [
    os.environ.get("FFMPEG_DIR"),
    r"C:\ffmpeg\bin",
    "/usr/local/bin",
    "/opt/homebrew/bin",
]


def resolve_tool(name: str) -> str:
    env = os.environ.get(f"{name.upper()}_BIN")
    if not env and name == "ffmpeg":
        env = os.environ.get("FFMPEG_BIN")
    if env and Path(env).is_file():
        return env
    found = shutil.which(name)
    if found:
        return found
    exe = name + (".exe" if os.name == "nt" else "")
    candidates = [Path(d) / exe for d in KNOWN_DIRS if d]
    try:
        import imageio_ffmpeg  # installe sur cette machine, sinon on continue

        bundled = Path(imageio_ffmpeg.get_ffmpeg_exe())
        candidates.insert(0, bundled.with_name(exe))
        if name == "ffmpeg":
            candidates.insert(0, bundled)
    except Exception:
        pass
    for c in candidates:
        if Path(c).is_file():
            return str(c)
    return name


FFMPEG = resolve_tool("ffmpeg")
FFPROBE = resolve_tool("ffprobe")


def tools_dir() -> str:
    """Dossier contenant ffmpeg ET ffprobe.

    yt-dlp exige les DEUX dans le meme dossier pour `--download-sections` ; sur
    cette machine ffmpeg vient d'imageio-ffmpeg (sans ffprobe) et ffprobe de
    C:\ffmpeg\bin. Donner le seul dossier de ffmpeg a yt-dlp echoue avec
    « ffmpeg is not installed » — message trompeur, le binaire etant present.
    """
    wanted = ("ffmpeg", "ffprobe")
    for exe in (FFPROBE, FFMPEG):
        folder = Path(exe).parent
        try:
            names = [p.name.lower() for p in folder.iterdir() if p.is_file()]
        except OSError:
            continue
        if all(any(n.startswith(w) for n in names) for w in wanted):
            return str(folder)
    return str(Path(FFMPEG).parent)


FFMPEG_TOOLS_DIR = tools_dir()
