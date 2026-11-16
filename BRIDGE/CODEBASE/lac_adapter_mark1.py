#!/usr/bin/env python3
"""lac_adapter_mark1.py -- adaptateur MARK1 -> pack PUR (LACRIMAE).

LE PROBLEME QU IL RESOUT (AUDIT_V1, constat M4)
    MARK1 produit UN pack contenant N assets :
        {"mode": "mark1", "assets": [{id, start_sec, end_sec, ...}, ...]}
    LACRIMAE attend UN pack par clip, au format PUR :
        {"mode": "pur", "source": {vod_url, start_sec, end_sec}, ...}
    Il n y a pas de chemin direct : ce script fait la conversion.

CE QU IL FAIT
    1. lit un pack MARK1 (fichier local ou URL)
    2. injecte la vod_url (M3 : le pack MARK1 n en porte pas)
    3. eclate chaque asset en un pack PUR autonome
    4. ecrit N fichiers production_pack_pur_<token>_<ID>.json

CE QU IL NE FAIT PAS
    Il n invente aucun contenu. Le copywriting vient du pack MARK1 ; si un
    champ manque, il est absent du pack PUR (les portes le diront).
    Il n appelle aucune fregate. Il ne rend aucune video.

USAGE
    python lac_adapter_mark1.py \\
        --pack production_pack_mark1_e99bd523.json \\
        --vod-url https://twitch.tv/videos/2927914500 \\
        --out BRIDGE/OUT
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


def vod_id(url):
    """Extrait l identifiant de la VOD pour nommer les fichiers."""
    tail = str(url or "").rstrip("/").rsplit("/", 1)[-1]
    return "".join(ch for ch in tail if ch.isalnum()) or "vod"


def asset_bounds(asset):
    """Rend (start, end) quel que soit le format d entree."""
    mi = asset.get("montage_instructions") or {}
    seg = mi.get("segment") or {}
    start = asset.get("start_sec", seg.get("start_sec"))
    end = asset.get("end_sec", seg.get("end_sec"))
    if start is None or end is None:
        return None, None
    return float(start), float(end)


def to_pur(asset, mark_pack, vod_url, style):
    """Convertit UN asset MARK1 en UN pack PUR."""
    aid = asset.get("id") or "clip"
    start, end = asset_bounds(asset)
    if start is None:
        raise ValueError("asset %s : bornes introuvables" % aid)

    duration = round(end - start, 3)
    generated = mark_pack.get("generated_at") or ""

    # copywriting : on recopie ce que MARK1 a produit, rien de plus
    copywriting = {
        "overlay_title": asset.get("overlay_title") or "",
        "overlay_lines": 2,
        "metadata_title": asset.get("metadata_title") or "",
        "description": asset.get("description") or "",
        "tags": list(asset.get("tags") or []),
        "hashtags": list(asset.get("hashtags") or []),
    }

    mi = {
        "metadata": {
            "generated_at": generated,
            "generator": "MARK1",
            "version": "3.0.0-mark1-adapted",
            "mode": "mark1_adapted",
            "campaign_id": (mark_pack.get("campaign") or {}).get("campaign_id") or "",
            "angle_id": aid,
            "segment_id": aid,
            "style": style,
        },
        "segment": {
            "source_url": vod_url,
            "start_sec": start,
            "end_sec": end,
            "duration_sec": duration,
            "signal_type": "mixed",
        },
        "style": {"style": style},
    }

    return {
        "mode": "pur",
        "pack_id": "%s-%s" % (mark_pack.get("pack_token") or "mark1", aid),
        "campaign_id": (mark_pack.get("campaign") or {}).get("campaign_id") or "",
        "asset_mode": mark_pack.get("asset_mode") or style,
        "generated_at": generated,
        "source": {
            "vod_url": vod_url,
            "start_sec": start,
            "end_sec": end,
            "duration_sec": duration,
            "source_permission": "campaign_provided",
        },
        "montage_instructions": mi,
        "copywriting": copywriting,
        "review": {
            "overlay_title": asset.get("overlay_title") or "",
            "metadata_title": asset.get("metadata_title") or "",
            "caption": asset.get("caption") or "",
            "clip_token": asset.get("clip_token") or "",
        },
        "compliance": {
            "language": mark_pack.get("language") or "en",
            "watermark": mark_pack.get("watermark") or {},
        },
    }


def main():
    ap = argparse.ArgumentParser(description="Adaptateur MARK1 -> PUR (LACRIMAE)")
    ap.add_argument("--pack", required=True, help="pack MARK1 (chemin ou URL raw)")
    ap.add_argument("--vod-url", required=True, help="URL de la VOD source")
    ap.add_argument("--out", default=str(ROOT / "BRIDGE" / "OUT"))
    ap.add_argument("--style", default=None, choices=["blur", "reframing"],
                    help="force le style ; sinon asset_mode du pack MARK1")
    args = ap.parse_args()

    mark = load_pack(args.pack)
    if mark.get("mode") != "mark1":
        log("ADAPTER FAIL: mode=%r, attendu 'mark1'" % (mark.get("mode"),))
        return 2

    assets = mark.get("assets") or []
    if not assets:
        log("ADAPTER FAIL: assets[] vide")
        return 2

    style = args.style or mark.get("asset_mode") or "blur"
    if style not in ("blur", "reframing"):
        log("ADAPTER FAIL: style=%r (blur|reframing seulement)" % (style,))
        return 2

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    token = mark.get("pack_token") or "mark1"
    vid = vod_id(args.vod_url)

    written = []
    for asset in assets:
        try:
            pur = to_pur(asset, mark, args.vod_url, style)
        except ValueError as e:
            log("ADAPTER FAIL: %s" % e)
            return 2
        name = "production_pack_pur_%s_%s.json" % (token, asset.get("id"))
        (out / name).write_text(json.dumps(pur, ensure_ascii=False, indent=2),
                                encoding="utf-8")
        written.append(name)
        log("PUR: %s (%.1fs -> %.1fs, %s)" %
            (name, pur["source"]["start_sec"], pur["source"]["end_sec"], style))

    log("ADAPTER OK: %d pack(s) PUR depuis %d asset(s), vod=%s"
        % (len(written), len(assets), vid))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
