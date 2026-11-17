# F03_PREVIEW — SANGUINALA LOOK + W1/T1

Validation visuelle avant rendu. Vite + Remotion player.

Styles V1 : `blur` | `reframing`. `split_scene` = V2+. Zero zoom.

Moteur LOOK = `dev10-v2` (`_purPackComposition.jsx`, `bridgeClipper.js`).

Mecanismes portes depuis salvage `review_dev8` **par copie de handlers** (CDC §7.4), jamais collage OmniComposition / ranking / reveal / hybrid :

- T1 titre : **style seulement** (taille, place, couleurs 2 lignes, police, contour, fond, auto_fit). Le **texte** vient du pack (`copywriting.overlay_title`) — la review ne le reecrit jamais.
- look : `fg_scale` / `fg_y_pct` / `degree` / `bg_scale` (taille de la video claire)
- logo / watermark : glisser `x_pct` / `y_pct`, `width_pct`, `position`, `opacity`. Le **PNG** vient du pack (`watermark.file`), la review ne choisit que sa place.
- Export `REVIEW/codex_render.json` — **un seul codex pour N clips**, commite, `validated_by_magos`

Src complete non fusionnee : `TRACKING/SALVAGE/review_dev8/` — ne pas la coller par-dessus le LOOK.

IN : pack PUR json (`public/pack.json` stage par `run_all --preview-stage`). OUT : `REVIEW/codex_render.json`. Pack jamais edite.

```bash
python run_all.py --pack <pack.json> --work WORK --out OUT --preview-stage
cd F03_PREVIEW/CODEBASE && npm ci && npm run dev
```

Port 5174. Operateur : style du titre T1, taille video claire blur, glisser le
logo W1, Export `codex_render.json`. Puis relancer run_all sans `--preview-stage`.
