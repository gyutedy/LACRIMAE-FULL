#!/usr/bin/env python3
"""POSTPROD/LUT + FADE.

L1 : le profil LUT existe et est applicable. F1 : fade obligatoire vers la fin.

Deux voies, dans cet ordre de priorite :
  --cube <fichier.cube>  : vraie LUT 3D (lut3d)
  --profile <nom>        : profil ATOM-IC (lut/profiles/atom_ic_profiles.json),
                           qui n'est PAS un .cube mais un jeu de parametres :
                           on le traduit en filtres ffmpeg reels (denoise -> eq ->
                           unsharp). Avant PR5 le champ `profile` du codex
                           n'etait lu par personne : le LUT ne s'appliquait
                           jamais et rien ne le signalait (AUDIT_V1 L16).
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from ffmpeg_bin import FFMPEG, FFPROBE  # noqa: E402  (AUDIT_V1 L10)

PROFILES_JSON = Path(__file__).resolve().parent / "profiles" / "atom_ic_profiles.json"


def load_profiles() -> dict:
    return json.loads(PROFILES_JSON.read_text(encoding="utf-8"))


def profile_filters(profile: dict) -> list[str]:
    """Profil ATOM-IC -> filtres ffmpeg. Denoise, puis etalonnage, puis nettete."""
    restaura = profile.get("restaura") or {}
    chroma = profile.get("chroma") or {}
    texture = profile.get("textura") or {}
    filters: list[str] = []

    luma = restaura.get("denoise_luma")
    if luma:
        chroma_dn = restaura.get("denoise_chroma", luma)
        filters.append(
            f"hqdn3d=luma_spatial={float(luma):.2f}:chroma_spatial={float(chroma_dn):.2f}"
        )

    eq = []
    for name in ("contrast", "saturation", "brightness", "gamma"):
        value = chroma.get(name)
        if value is None:
            continue
        eq.append(f"{name}={float(value):.3f}")
    if eq:
        filters.append("eq=" + ":".join(eq))

    amount = texture.get("unsharp_amount")
    if amount:
        radius = max(3, min(13, int(round(float(texture.get("unsharp_radius", 5))))))
        filters.append(
            f"unsharp=luma_msize_x={radius}:luma_msize_y={radius}"
            f":luma_amount={float(amount):.2f}"
        )
    return filters


def _filter_path(path: Path) -> str:
    """ffmpeg veut un chemin echappe : `:` et antislash cassent le filtre."""
    return str(path).replace("\\", "/").replace(":", "\\\\:")


def resolve_profile(name: str) -> dict:
    data = load_profiles()
    profiles = data.get("profiles") or {}
    if name not in profiles:
        raise KeyError(
            f"profil LUT inconnu : {name!r} (disponibles : {', '.join(sorted(profiles))})"
        )
    return profiles[name]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--cube", type=Path, default=None)          # optionnel
    ap.add_argument("--profile", default=None, help="profil ATOM-IC (ex. hdr_imperator)")
    ap.add_argument("--fade", default="darken", choices=["darken", "black"])
    ap.add_argument("--fade-duration", type=float, default=1.5) # vers la fin
    ap.add_argument("--ass", type=Path, default=None,
                    help="sous-titres .ass a graver (CAPTION -> LUT -> FADE, une passe)")
    ap.add_argument("--fontsdir", type=Path, default=None,
                    help="repertoire de polices pour libass")
    args = ap.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    probe = subprocess.run([FFPROBE, "-v", "quiet", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(args.input)], capture_output=True, text=True)
    dur = float(probe.stdout.strip() or 0)
    audio = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "a:0",
                            "-show_entries", "stream=index", "-of", "csv=p=0", str(args.input)],
                           capture_output=True, text=True)
    filters = []
    cwd = None
    if args.ass:
        if not args.ass.is_file():
            print("G4 FAIL: .ass introuvable:", args.ass); return 2
        # Un chemin absolu Windows (`D:` + espaces) casse le parseur de filtres.
        # On grave depuis le dossier du .ass, avec la police copiee a cote :
        # le filtre ne contient plus que des noms de fichiers.
        ass_dir = args.ass.resolve().parent
        chain = f"ass={args.ass.name}"
        if args.fontsdir and args.fontsdir.is_dir():
            fonts_local = ass_dir / "_fonts"
            fonts_local.mkdir(exist_ok=True)
            for font in sorted(args.fontsdir.glob("*.ttf")) + sorted(args.fontsdir.glob("*.otf")):
                shutil.copy2(font, fonts_local / font.name)
            chain += ":fontsdir=_fonts"
        filters.append(chain)
        cwd = str(ass_dir)
    if args.cube:
        if not args.cube.exists():
            print("L1 FAIL: cube introuvable:", args.cube); return 2
        filters.append(f"lut3d=file={args.cube}")
    elif args.profile:
        try:
            profile = resolve_profile(args.profile)
        except KeyError as exc:
            print("L1 FAIL:", exc.args[0]); return 2
        filters.extend(profile_filters(profile))
        if not filters:
            print(f"L1 FAIL: profil {args.profile!r} vide (aucun parametre exploitable)"); return 2
        print("L1:", args.profile, "->", ",".join(filters))
    fade_d = min(float(args.fade_duration), max(0.01, dur))
    fade_st = max(0.0, dur - fade_d)
    if args.fade == "black":
        filters.append(f"fade=t=out:st={fade_st:.3f}:d={fade_d:.3f}:color=black")
    else:
        filters.append(f"eq=brightness=-0.15:enable='gte(t,{fade_st:.3f})'")
    vf = ",".join(filters)
    cmd = [FFMPEG, "-y", "-i", str(args.input.resolve()), "-vf", vf]
    if (audio.stdout or "").strip():
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-an"]
    cmd += [str(args.output.resolve())]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if r.returncode != 0:
        print("F1/L1 FAIL:", (r.stderr or "")[-2000:])
        return 2
    print("F1/L1 OK:", args.output); return 0

if __name__ == "__main__":
    sys.exit(main())
