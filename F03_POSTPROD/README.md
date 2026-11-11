# F03_POSTPROD

Frégate post-production, appliquee a TOUS les clips (meme style_pack).

Ordre : CAPTION → GLOW → LUT → FADE.

| Sous-fregate | Source | Portes |
|--------------|--------|--------|
| caption/ | F07_CAPTION entier, 0 modification | G4 |
| glow/ | Modal pattern F07 (`modal_glow.py` + `preview_glow.py`) | GL1 / GL2 |
| lut/lut_apply.py | CDC §7.6 | L1 / F1 |
| lut/profiles/ | `atom_ic_profiles.json` depuis dev6 | L1 |

`postprod.py` s'arrete a la premiere porte en echec.

F07 PREVIEW (TRAVAIL/modal_app.py 0 modification. PREVIEW : chemins relatifs pour GitHub Pages) :

```bash
python3 run_all.py --pack <pack.json> --work WORK --out OUT --preview-stage
cd F03_POSTPROD/CODEBASE/caption/PREVIEW/CODEBASE && npm ci && npm run dev
```

Port 5173. Operateur valide s1 (police, taille, place) → `caption/OUT/style.json`. `run_all` fusionne ce s1 dans `style_pack.caption`. Whisper/Blender overlay = runtime pack, pas recode.

GitHub Pages : `https://gyutedy.github.io/LACRIMAE-FULL/f07/` — chemins relatifs. Save disque = Vite sandbox seulement ; Pages telecharge s1.
