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

1. **prepare** — fetch du pack (`pack_url`) ou repli `pack_filter`, G0, G0-S,
   injection de `source.vod_url` si absente, adaptation MARK1, puis
   `convert_pur_pack.mjs --packs-out BRIDGE/PUR` qui ecrit **un pack PUR
   mono-clip par angle** et la matrice.
2. **render** — 1 clip = 1 job (matrix `angle` + `pack` + `index`) :
   F00_SOURCE (segment VOD) -> F01_LOOK (Remotion, **terminal en V1**) ->
   verification `ffprobe` (video + audio) -> artifact `pur-result-<angle>`.
3. **aggregate** — `pur_aggregate.py` : P-AGG (aucun MP4 manquant) + P-AUD
   (aucun rendu muet), puis F05 (reencodage) et F06 (LUT) en batch.

`F04_HEISENBERG` n'est **pas** appele : pas de jump cut, pas de SFX.

## Inputs (etat actuel)

`pack_url`, `vod_url`, `pack_filter`, `canvas`, `perturabo_repo`,
`perturabo_branch`, `style` (`blur` | `reframing`), `max_parallel`.

> **A ajouter (PR6)** : `codex_render_url` et `codex_postprod_url`, symetriques
> de `pack_url`, pour que la CI consomme les deux codex commites.

> **A ajouter (PR6)** : `codex_render_url` et `codex_postprod_url`, symetriques
> de `pack_url`, pour que la CI consomme les deux codex commites.

Voir `TRACKING/PLAN_CODEX_V1.md` et `TRACKING/GUIDE_UTILISATION.md`.
