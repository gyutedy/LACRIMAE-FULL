# Workflows CI — LACRIMAE

Ce depot porte 6 workflows. **Un seul rend des videos** :
`dev10_pur_render.yml` (nom affiche : *DEV10-v2 — PUR render*).

| Workflow | Role |
|---|---|
| `dev10_pur_render.yml` | **le rendu** : pack -> N MP4 |
| `dev11_caption.yml` / `dev11_caption_test.yml` | F07 caption (Modal) + tests |
| `dev11_contracts.yml` | contrats F07 |
| `dev6f_lut_render.yml` | heritage LUT (dev6) |
| `pages-build-deployment` | publication Pages (`f03/`, `f07/`) |

## Flux de `dev10_pur_render.yml`

1. **prepare** — fetch du pack (`pack_url`) ou repli `pack_filter`, G0,
   G0-S, injection de `source.vod_url` si absente.
2. **render** — 1 clip = 1 job (matrix) : F00_SOURCE -> F01_LOOK ->
   F02_MONTAGE (passthrough) -> F04_HEISENBERG (present, hors flux V1).
3. **aggregate** — refus si un rendu manque (P-AGG / P-AUD).
4. **F05 / F06** en batch, artefacts de sortie.

## Inputs (etat actuel)

`pack_url`, `vod_url`, `pack_filter`, `canvas`, `perturabo_repo`,
`perturabo_branch`, `style`, `max_parallel`.

> **A corriger (PR2)** : le workflow appelle encore `F00_PUR/`, `F03_PICTOR/`
> et `F05_CAMOUFLAGE/`, trois dossiers qui n'existent pas sur cette branche
> (AUDIT_V1 **L9**). Les vrais sont `F00_SOURCE/`, `F01_LOOK/`, `F05/`.

> **A ajouter (PR6)** : `codex_render_url` et `codex_postprod_url`, symetriques
> de `pack_url`, pour que la CI consomme les deux codex commites.

Voir `TRACKING/PLAN_CODEX_V1.md` et `TRACKING/GUIDE_UTILISATION.md`.
