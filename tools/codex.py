#!/usr/bin/env python3
"""codex.py — contrat des deux codex SANGUINALA V1.

Doctrine (TRACKING/PLAN_CODEX_V1.md) : **le codex commande, le pack fournit.**

- `REVIEW/codex_render.json`  -> le moteur `F01_LOOK` (style, look, titre, logo)
- `REVIEW/codex_postprod.json` -> `F03_POSTPROD` (glow, sous-titres, lut, fade)

Un codex ne nomme JAMAIS un titre : le texte vient du pack. Il porte le style.

Les schemas JSON (`REVIEW/SCHEMAS/*.schema.json`) sont la verite unique ; ce
module les execute avec un validateur minimal (pas de dependance externe) et
ajoute les portes du plan :

| Porte | Sens |
|---|---|
| W1-R | `codex_render.json` valide + `validated_by_magos: true` |
| PP1 | `codex_postprod.json` valide + `validated_by_magos: true` |
| PP2 | `order` grave : `glow -> caption -> lut -> fade` |

Codes de sortie : 0 = valide, 1 = invalide/illisible, 2 = valide mais non
valide par l'operateur (`validated_by_magos: false`).

Usage :
    python tools/codex.py check REVIEW/codex_render.json
    python tools/codex.py check REVIEW/codex_postprod.json --gate
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# L1 (AUDIT_V1) : console Windows en cp1252 -> logs illisibles / crash.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "REVIEW" / "SCHEMAS"

RENDER = "render"
POSTPROD = "postprod"

SCHEMAS = {
    RENDER: SCHEMA_DIR / "codex_render.schema.json",
    POSTPROD: SCHEMA_DIR / "codex_postprod.schema.json",
}
FROZEN_ORDER = ["glow", "caption", "lut", "fade"]

# Le codex porte le style, jamais le texte : ces cles sont refusees partout.
TEXT_KEYS = {
    "text", "titles", "title_text", "overlay_title", "overlay_lines",
    "lines", "content", "static_text", "caption_text", "words", "transcript",
}


class CodexError(Exception):
    """Refus d'un codex. `code` : 1 invalide, 2 non valide par l'operateur."""

    def __init__(self, message: str, code: int = 1, errors: list[str] | None = None):
        super().__init__(message)
        self.code = code
        self.errors = errors or []


# ── validateur minimal JSON Schema (le sous-ensemble utilise par nos schemas) ──

def _is_type(value, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    raise CodexError(f"type de schema inconnu : {expected!r}")


def validate(instance, schema: dict, path: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected and not _is_type(instance, expected):
        return [f"{path}: {expected} attendu, {type(instance).__name__} trouve"]

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: doit valoir {json.dumps(schema['const'], ensure_ascii=False)}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} hors {json.dumps(schema['enum'], ensure_ascii=False)}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: trop court (min {schema['minLength']})")
        pattern = schema.get("pattern")
        if pattern:
            import re

            if not re.match(pattern, instance):
                errors.append(f"{path}: {instance!r} ne respecte pas {pattern}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: moins de {schema['minItems']} element(s)")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: plus de {schema['maxItems']} element(s)")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for i, item in enumerate(instance):
                errors.extend(validate(item, item_schema, f"{path}[{i}]"))

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}.{key}: champ obligatoire absent")
        props = schema.get("properties") or {}
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}.{key}: champ inconnu (schema strict)")
        for key, sub in props.items():
            if key in instance:
                errors.extend(validate(instance[key], sub, f"{path}.{key}"))
    return errors


# ── doctrine : le codex ne nomme jamais un titre ──

def doctrine_errors(node, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if str(key).lower() in TEXT_KEYS:
                found.append(
                    f"{path}.{key}: un codex ne porte jamais de texte de titre"
                    " (le texte vient du pack)"
                )
            found.extend(doctrine_errors(value, f"{path}.{key}"))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            found.extend(doctrine_errors(value, f"{path}[{i}]"))
    return found


# ── chargement ──

def load_schema(kind: str) -> dict:
    path = SCHEMAS[kind]
    if not path.is_file():
        raise CodexError(f"schema absent : {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CodexError(f"schema illisible ({path}) : {exc}") from exc


def check(kind: str, raw) -> list[str]:
    """Liste d'erreurs ; liste vide = codex conforme au schema et a la doctrine."""
    if kind not in SCHEMAS:
        raise CodexError(f"type de codex inconnu : {kind!r}")
    try:
        schema = load_schema(kind)
    except CodexError as exc:
        return [str(exc)]
    errors = validate(raw, schema)
    if kind == RENDER:
        errors.extend(doctrine_errors(raw))
    else:
        order = (raw or {}).get("order")
        if order != FROZEN_ORDER:
            errors.append(
                f"$.order: ordre grave {FROZEN_ORDER} attendu (PP2), recu {order!r}"
            )
        errors.extend(doctrine_errors(raw))
    return errors


def _read_json(path: Path):
    if not path.is_file():
        raise CodexError(f"codex absent : {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CodexError(f"codex illisible ({path}) : {exc}") from exc


def ensure_validated(raw: dict, kind: str) -> None:
    """Porte W1-R / PP1 : refus si l'operateur n'a pas valide."""
    if raw.get("validated_by_magos") is not True:
        gate = "W1-R" if kind == RENDER else "PP1"
        raise CodexError(
            f"{gate} FAIL: validated_by_magos={raw.get('validated_by_magos')!r}"
            " — la review doit etre validee avant tout rendu",
            code=2,
        )


def validate_codex(kind: str, raw, require_validated: bool = True) -> dict:
    """Valide et rend le codex tel quel (aucun remplissage silencieux)."""
    errors = check(kind, raw)
    if errors:
        label = "codex_render" if kind == RENDER else "codex_postprod"
        raise CodexError(
            f"{label} REFUSE ({len(errors)} erreur(s))", code=1, errors=errors
        )
    if require_validated:
        ensure_validated(raw, kind)
    return raw


def load_codex(kind: str, path: Path | None = None, require_validated: bool = True) -> dict:
    if path is None:
        name = "codex_render.json" if kind == RENDER else "codex_postprod.json"
        path = ROOT / "REVIEW" / name
    return validate_codex(kind, _read_json(Path(path)), require_validated=require_validated)


def load_render_codex(path: Path | None = None, require_validated: bool = True) -> dict:
    return load_codex(RENDER, path, require_validated)


def load_postprod_codex(path: Path | None = None, require_validated: bool = True) -> dict:
    return load_codex(POSTPROD, path, require_validated)


# ── normalisation (remplit les seuls champs optionnels, sans rien inventer) ──

def normalize_render_codex(raw: dict) -> dict:
    """Codex render complet : defauts d'affichage du logo quand position=custom."""
    codex = json.loads(json.dumps(raw))  # copie profonde
    logo = codex.setdefault("logo", {})
    if logo.get("position") == "custom":
        logo.setdefault("x_pct", 50)
        logo.setdefault("y_pct", 50)
    return codex


def normalize_postprod_codex(raw: dict) -> dict:
    """Codex postprod complet : `mode` du glow (defaut scene) et ordre grave."""
    codex = json.loads(json.dumps(raw))
    codex["glow"].setdefault("mode", "scene")
    codex["order"] = list(FROZEN_ORDER)
    return codex


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Contrat des codex SANGUINALA V1")
    sub = ap.add_subparsers(dest="cmd", required=True)
    chk = sub.add_parser("check", help="valide un codex contre son schema")
    chk.add_argument("path", help="chemin du codex JSON")
    chk.add_argument("--gate", action="store_true",
                     help="applique aussi la porte W1-R / PP1 (validated_by_magos)")
    args = ap.parse_args(argv)

    path = Path(args.path)
    kind = POSTPROD if "postprod" in path.name else RENDER
    try:
        raw = _read_json(path)
    except CodexError as exc:
        print(f"[x] {exc}", file=sys.stderr)
        return 1

    errors = check(kind, raw)
    if errors:
        print(f"[x] {path.name} REFUSE — {len(errors)} erreur(s) :", file=sys.stderr)
        for e in errors:
            print(f"    - {e}", file=sys.stderr)
        return 1

    label = raw.get("schema_version")
    print(f"[ok] {path.name} conforme a {label}", flush=True)
    if args.gate:
        try:
            ensure_validated(raw, kind)
        except CodexError as exc:
            print(f"[x] {exc}", file=sys.stderr)
            return exc.code
        print("[ok] validated_by_magos: true — porte ouverte")
    elif raw.get("validated_by_magos") is not True:
        print("[!] validated_by_magos: false — le rendu sera refuse (W1-R / PP1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
