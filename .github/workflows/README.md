# Workflows CI — LACRIMAE

Ce depot porte 3 workflows maison. **Un seul rend des videos** :
`dev10_pur_render.yml` (nom affiche : *DEV10-v2 — PUR render*).

| Workflow | Role |
|---|---|
| `dev10_pur_render.yml` | **le rendu** : pack + 2 codex -> N MP4 |
| `codex_write.yml` | **l'ecriture des codex** : review -> `REVIEW/` (validation puis commit) |
| `preview_pages.yml` | **la review en ligne** : build `f03/` + `f07/` -> `gh-pages` |

## Flux de `dev10_pur_render.yml`

1. **prepare** — fetch du pack (`pack_url`) ou repli `pack_filter`, G0, G0-S,
   injection de `source.vod_url` si absente, adaptation MARK1, puis
   `convert_pur_pack.mjs --packs-out BRIDGE/PUR` qui ecrit **un pack PUR
   mono-clip par angle** et la matrice. Les deux codex sont lus, verifies
   (`tools/codex.py check --gate`, portes W1-R et PP1) et projetes dans les
   manifs ; le PNG du watermark est telecharge depuis PERTURABO (P3 : rendu
   refuse si le pack l'exige et qu'il manque).
2. **render** — 1 clip = 1 job (matrix `angle` + `pack` + `index`) :
   F00_SOURCE (segment VOD) -> F01_LOOK (Remotion, **terminal en V1**) ->
   verification `ffprobe` (video + audio) -> artifact `pur-result-<angle>`.
3. **aggregate** — `pur_aggregate.py` : P-AGG (aucun MP4 manquant) + P-AUD
   (aucun rendu muet), puis **F03_POSTPROD** (`codex_postprod` : GLOW ->
   CAPTION -> LUT -> FADE, rapport par clip), puis F05 et F06 en batch.

`F04_HEISENBERG` n'est **pas** appele : pas de jump cut, pas de SFX.

## Inputs

`pack_url`, `codex_render_url`, `codex_postprod_url`, `vod_url`,
`pack_filter`, `canvas`, `perturabo_repo`, `perturabo_branch`, `style`
(`blur` | `reframing`), `max_parallel`.

Une URL de codex vide = le codex **commite** dans `REVIEW/` est utilise.

## Ecriture des codex

`codex_write.yml` (dispatch) prend `codex_render_url` / `codex_postprod_url` ou
`codex_render_b64` / `codex_postprod_b64`, valide avec le meme
`tools/codex.py` que la CI, puis commit **seulement** si le contenu change. Un
codex qui viole le schema ou l'ordre PP2 fait echouer le job sans rien ecrire.

## Review en ligne

`preview_pages.yml` reconstruit `F03_PREVIEW` (`f03/`) et le preview caption
(`f07/`), lance les tests de projection (`node --test`) et publie sur
`gh-pages` avec `keep_files: true` : les medias deja presents (clips,
`pack.json`, `target.mp4`, `archive/`) sont conserves.

Voir `TRACKING/PLAN_CODEX_V1.md` et `TRACKING/GUIDE_UTILISATION.md`.
