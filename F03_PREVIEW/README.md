# F03_PREVIEW — SANGUINALA LOOK + W1/T1

Validation visuelle avant rendu. Vite + Remotion player.

Styles V1 : `blur` | `reframing`. `split_scene` = V2+. Zero zoom.

Moteur LOOK = `dev10-v2` (`_purPackComposition.jsx`, `bridgeClipper.js`).

Mecanismes portes depuis salvage `review_dev8` **par copie de handlers** (CDC §7.4), jamais collage OmniComposition / ranking / reveal / hybrid :

- T1 titres editables (texte, taille, place, in/out)
- blur `fg_scale` / `fg_y_pct` / `degree` / `bg_scale` (taille de la video claire)
- W1 double-clic pose logo + **curseur** (glisser le watermark)
- W1 images watermark du pack JSON
- Export JSON review unique (`REVIEW/sanguinala_review.json`) applique a N clips

Src complete non fusionnee : `TRACKING/SALVAGE/review_dev8/` — ne pas la coller par-dessus le LOOK.

IN : pack PUR json (`public/pack.json` stage par `run_all --preview-stage`). OUT : `REVIEW/sanguinala_review.json` (ancien codex). Pack jamais edite.

```bash
python3 run_all.py --pack <pack.json> --work WORK --out OUT --preview-stage
cd F03_PREVIEW/CODEBASE && npm ci && npm run dev
```

Port 5174. Operateur : titres T1, taille video claire blur, double-clic + glisser logo W1, Export JSON review. Puis relancer run_all sans `--preview-stage`.
