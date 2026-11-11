# F03_PREVIEW — SANGUINALA LOOK + W1

Validation visuelle avant rendu. Vite + Remotion player.

Styles V1 : `blur` | `reframing`. `split_scene` = V2+. Zero zoom.

Moteur LOOK = `dev10-v2` (`_purPackComposition.jsx`, `bridgeClipper.js`).

Portees depuis salvage dev8 **par copie de handlers** (CDC §7.4) :

- W1 clic / double-clic pose logo (`handleLogoClick` / `confirmLogoPlacement`)
- W1 images watermark du pack JSON
- T1 titres `style_pack.titles`
- Export JSON review unique (`sanguinala_review.json`) applique a N clips

IN : pack PUR json (`public/pack.json` stage par `run_all --preview-stage`). OUT : `REVIEW/sanguinala_review.json` (ancien codex). Pack jamais edite.

```bash
python3 run_all.py --pack <pack.json> --work WORK --out OUT --preview-stage
cd F03_PREVIEW/CODEBASE && npm ci && npm run dev
```

Port 5174. Operateur : titres T1, double-clic logo W1, Export JSON review. Puis relancer run_all sans `--preview-stage`.
