# REVIEW — SANGUINALA W1 / T1

Surface operateur avant rendu final (clip de reference).

LOOK (blur/reframing, 0 zoom) reste `F03_PREVIEW/` — moteur dev10-v2.

Mecanismes portes depuis salvage **par copie** (CDC §7.4), pas de reecriture :

| Mecanisme | Source | Ou |
|-----------|--------|----|
| Clic / double-clic logo (`handleLogoClick`, `confirmLogoPlacement`) | `TRACKING/SALVAGE/review_dev8` | `F03_PREVIEW/CODEBASE/src/App.jsx` |
| Watermark images pack (`style_pack.watermark`) | lecture JSON au drop pack | idem |
| Titres (`style_pack.titles`) | lecture JSON + panneau T1 | idem |
| Export JSON review unique | bouton `sanguinala_review.json` | idem |

Src complete non fusionnee (hybrid/reveal/ranking) : `TRACKING/SALVAGE/review_dev8/` — ne pas la coller par-dessus le LOOK.

`run_all.py` lit `REVIEW/sanguinala_review.json` AVANT le moteur (W1/T1). Fichier jamais commite (gitignore). `--require-previews` = FAIL si absent.
