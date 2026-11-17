# BRIDGE

Pont entre le monde forge (PERTURABO) et LACRIMAE. Recupere le pack, valide
G0, le convertit en manifeste `dev10.pur.v1`. **Ne telecharge pas la video.**

## Contrats

| | Chemin |
|--|--------|
| IN | `IN/production_pack_pur_*.json` (ou fetch distant PERTURABO EXPORT) |
| OUT | `OUT/pur_manifest.json` |
| Code | `CODEBASE/lac_bridge_forge.py` |
| Adaptation MARK1 -> PUR | `CODEBASE/lac_adapter_mark1.py` |

## Role

- Fetch du pack depuis `PERTURABO/MONDES_FORGES/CLIPPING/EXPORT/`
- Gate **G0 PACK** + **G0-S STYLE** (`blur` / `reframing` uniquement en V1)
- Conversion -> `pur_manifest.json`, consomme par `F03_PREVIEW` et `F01_LOOK`
- Le pack n'est **jamais** reecrit

Style infere = refus. `split_scene` = exit 2 (V2+).

## Ce que le BRIDGE doit projeter (PR4)

Le manifeste est la **projection** de `REVIEW/codex_render.json` :

| Codex render | Manifeste |
|---|---|
| `look.*` | `style_params` |
| `title.*` | `narrative.overlay.style_params` |
| `logo.*` | `narrative.logo` (nouveau) |
| `style` / `canvas` / `fps` | entete du manifeste |

Le **texte** du titre reste celui du pack (`copywriting.overlay_title`) : le
BRIDGE ne l'invente pas et ne le reecrit pas.

## Etat connu (AUDIT_V1)

- **L12** : le PNG du watermark (`watermark.file`, `required: true` dans le
  pack MARK1) est **jete** par `lac_adapter_mark1.py` — a propager en PR4.
- **M2** : `source.directive_path` peut contenir un chemin Windows local —
  defaut du pack, a traiter cote PERTURABO.

Voir `TRACKING/PLAN_CODEX_V1.md`, `TRACKING/PUR_GATES.md` et
`TRACKING/GUIDE_BRAS_ARME_PUR.md`.
