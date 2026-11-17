#!/usr/bin/env python3
"""lac_adapter_mark1.py -- adaptateur MARK1 -> livrable PUR (LACRIMAE).

LE CONTRAT (valide avec l'operateur)
    Un pack MARK1 = UN livrable = N clips.
    Le pack porte les bornes et les titres de chaque clip dans assets[].
    LACRIMAE sait deja lire ce format : expandSanguinalaPack() dans
    F03_PREVIEW/CODEBASE/src/preview/bridgeClipper.js lit assets[] et
    source.vod_url.

    Il ne manque qu'UN champ : source.vod_url.
    Ce script le pose. Une seule fois. Jamais ecrase s'il existe deja.

CE QU IL NE FAIT PAS
    - Il ne renomme PAS le pack : le nom est l'identite du livrable.
    - Il ne decoupe PAS le pack en N fichiers : le pack reste multi-clips.
    - Il ne liste PAS de dossier : l'operateur fournit l'URL exacte.
    - Il n invente aucun contenu : il relit et reinjecte tel quel.

USAGE
    python lac_adapter_mark1.py \\
        --pack-url https://raw.githubusercontent.com/.../production_pack_mark1_e99bd523.json \\
        --vod-url https://twitch.tv/videos/2927914500 \\
        --out BRIDGE/OUT

    --vod-url n'est necessaire QUE si le pack n a pas deja source.vod_url.
    En local, --pack remplace --pack-url.
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def log(msg):
    print(msg, flush=True)


def load_pack(src):
    """Charge un pack depuis un chemin local ou une URL http(s)."""
    if str(src).startswith(("http://", "https://")):
        with urllib.request.urlopen(src, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    return json.loads(Path(src).read_text(encoding="utf-8"))


def bound(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_assets(pack):
    """Verifie que chaque asset porte des bornes exploitables.

    Rend une liste d erreurs. Ne corrige rien : si le pack est casse, il faut
    le savoir avant le rendu, pas pendant.
    """
    errors = []
    assets = pack.get("assets") or []
    if not assets:
        return ["assets[] absent ou vide"]
    seen = set()
    for i, asset in enumerate(assets):
        aid = asset.get("id") or ("#%d" % i)
        if aid in seen:
            errors.append("asset '%s' en double" % aid)
        seen.add(aid)
        mi = asset.get("montage_instructions") or {}
        seg = (mi.get("segment") or {}) if isinstance(mi, dict) else {}
        start = asset.get("start_sec", seg.get("start_sec"))
        end = asset.get("end_sec", seg.get("end_sec"))
        if not bound(start) or not bound(end):
            errors.append("asset '%s' : bornes absentes ou non numeriques" % aid)
            continue
        if float(end) <= float(start):
            errors.append("asset '%s' : end_sec <= start_sec (%.1f <= %.1f)"
                          % (aid, float(end), float(start)))
    return errors


def with_vod(pack, vod_url):
    """Pose source.vod_url. Ne l ecrase jamais.

    Rend (pack_enrichi, action) ou action est 'present', 'injecte' ou
    'unchanged'. Un seul endroit porte la VOD : source.vod_url.
    """
    source = dict(pack.get("source") or {})
    existing = str(source.get("vod_url") or "").strip()
    if existing:
        if vod_url and vod_url.strip() != existing:
            log("NOTE: source.vod_url deja present (%s) — l argument --vod-url "
                "(%s) est ignore. Une seule source de verite." % (existing, vod_url.strip()))
        action = "present"
    elif vod_url:
        source["vod_url"] = vod_url.strip()
        action = "injecte"
    else:
        action = "unchanged"
    out = dict(pack)
    out["source"] = source
    return out, action


def main():
    ap = argparse.ArgumentParser(description="Adaptateur MARK1 -> livrable PUR (LACRIMAE)")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--pack", help="pack MARK1 local")
    grp.add_argument("--pack-url", help="URL raw du pack MARK1")
    ap.add_argument("--vod-url", default="", help="VOD source, si absente du pack")
    ap.add_argument("--out", default=str(ROOT / "BRIDGE" / "OUT"),
                    help="dossier de sortie")
    ap.add_argument("--dry-run", action="store_true", help="analyse seule, n ecrit rien")
    args = ap.parse_args()

    src = args.pack or args.pack_url
    pack = load_pack(src)
    log("PACK: %s" % pack.get("pack_id") or "(sans pack_id)")

    mode = pack.get("mode")
    if mode != "mark1":
        log("ADAPTER FAIL: mode=%r, attendu 'mark1'" % (mode,))
        return 2

    errors = check_assets(pack)
    if errors:
        for e in errors:
            log("ADAPTER FAIL: %s" % e)
        return 2

    # P3 : un pack qui exige un watermark doit nommer son PNG, sinon le moteur
    # ne peut rien dessiner et le MP4 sort nu sans que rien ne le signale.
    wm = pack.get("watermark") or {}
    if wm.get("required") is True and not str(wm.get("file") or "").strip():
        log("ADAPTER FAIL: watermark.required=true mais watermark.file vide (P3)")
        return 2

    assets = pack.get("assets") or []
    enriched, action = with_vod(pack, args.vod_url)

    if action == "unchanged":
        log("ADAPTER FAIL: source.vod_url absent et --vod-url non fourni.")
        log("  Le pack ne dit pas quelle VOD telecharger. Fournir --vod-url.")
        return 2

    label = {"present": "deja present", "injecte": "injecte"}[action]
    log("VOD: %s (%s)" % (enriched["source"].get("vod_url"), label))

    for asset in assets:
        aid = asset.get("id")
        start = float(asset.get("start_sec"))
        end = float(asset.get("end_sec"))
        log("CLIP %-4s %8.1fs -> %8.1fs  (%5.1fs)  %r"
            % (aid, start, end, end - start, asset.get("overlay_title")))

    if args.dry_run:
        log("DRY-RUN: %d clip(s) valides, rien ecrit." % len(assets))
        return 0

    # Le nom du pack est son identite : on ne le change pas.
    name = Path(src.split("?")[0]).name or "production_pack_mark1.json"
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / name
    dest.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")

    log("ADAPTER OK: %s (%d clip(s), 1 livrable)" % (dest, len(assets)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
