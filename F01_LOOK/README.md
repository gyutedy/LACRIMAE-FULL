# F01_LOOK — le moteur (Remotion)

> Ancien nom : `F03_PICTOR`. C'est **le seul moteur qui dessine du texte**.

Rendu LOOK : style (`blur` | `reframing`) + **titre du pack** + **logo PNG**,
sur canvas 9:16. Miroir exact de `F03_PREVIEW` : meme composition
(`F03_PREVIEW/CODEBASE/src/preview/_purPackComposition.jsx`), donc ce que
l'operateur valide est ce qui sort.

Il ne fait **pas** les sous-titres (c'est `F03_POSTPROD`) et **pas** les
jump cuts (Heisenberg, hors flux V1).

## Contrats

| | Chemin |
|--|--------|
| IN | `pur_manifest.json` (`dev10.pur.v1`) + clips de `F00_SOURCE/OUT` |
| OUT | `F01_LOOK/OUT/pur_<angle>_look.mp4` |
| Code | `CODEBASE/render_pictor.mjs` + `src/PurLook.jsx` |

Le manifeste est la **projection** de `REVIEW/codex_render.json` : le BRIDGE y
ecrit `style_params` (look), `narrative.overlay.style_params` (typographie du
titre) et `narrative.logo` (place du logo). Le **texte** du titre vient du
pack, jamais du codex.

## Lancer

```bash
cd F01_LOOK/CODEBASE
npm ci || npm install
node render_pictor.mjs \
  --manifest ../../BRIDGE/OUT/pur_manifest.json \
  --clips ../../F00_SOURCE/OUT \
  --out ../../F01_LOOK/OUT
```

`--entry N` pour un seul asset. `--dry-run` verifie G0-S / P-ZOOM ZERO sans
lancer Remotion.

`npm install` est un prerequis dur (AUDIT_V1 **L2**). Sur cette machine :
`env -u npm_config_allow_scripts npm install` (AUDIT_V1 **L7**).

## Ce qu'il dessine

| Element | Source |
|---|---|
| flou du fond (`degree`, `bg_scale`) | `manifest.style_params` |
| taille/place de la video claire (`fg_scale`, `fg_y_pct`) | `manifest.style_params` |
| texte du titre | **pack** (`copywriting.overlay_title`) |
| apparence du titre (taille, place, couleurs, contour, fond, auto_fit) | `manifest.narrative.overlay.style_params` |
| logo / watermark PNG | `manifest.narrative.logo` + fichier du pack (`watermark.file`) |

## Interdits

- Zoom, swell, scale anime, breathing_zoom.
- Sous-titres (post-prod), jump cuts / SFX / b-roll (hors V1).
- Ranking, reveal, hybrid.
- Un titre invente : le texte vient du pack.

`reframing` = recadrage **fixe** (echelle / offset), pas une animation.

Porte **G3** + P-ZOOM ZERO. Voir `TRACKING/PUR_GATES.md`.
