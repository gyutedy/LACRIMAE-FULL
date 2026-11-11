# Guide d'utilisation — LACRIMAE SANGUINALA V1

Branche `sanguinala-v1`. Pack PUR in, N MP4 out. Heisenberg hors flux.
Operateur = toi. Tu valides les 3 previews sur le clip de reference AVANT le rendu N MP4.
Tu ne touches ni au code ni au pack.

## Ordre operateur (CDC §8)

1. Pack PUR (PERTURABO ou fixture).
2. **F03_PREVIEW** (AVANT le moteur) : look + titres T1 + watermark W1. Export `REVIEW/sanguinala_review.json` (l'ancien codex).
3. **F07 CAPTION PREVIEW** : police / taille / place s1. Save `F03_POSTPROD/CODEBASE/caption/OUT/style.json`.
4. **Preview GLOW** : 1 frame PNG (sigma / opacite). Deja dans run_all (GL2).
5. Relancer `run_all` : N MP4.

## Stage des 2 previews (clip de reference seulement)

```bash
python3 run_all.py --pack TRACKING/fixtures/sanguinala_p6_pack.json --work WORK/p6 --out OUT/p6 --preview-stage
```

Puis dans deux terminaux :

```bash
cd F03_PREVIEW/CODEBASE
npm ci
npm run dev
```

```bash
cd F03_POSTPROD/CODEBASE/caption/PREVIEW/CODEBASE
npm ci
npm run dev
```

F03_PREVIEW = port 5174. F07 caption = port 5173.
Valider : bouton Export JSON review (W1/T1) + Save s1 (G4).
Puis relancer **sans** `--preview-stage`.

## Rendu N MP4 (apres validation)

```bash
python3 run_all.py --pack TRACKING/fixtures/sanguinala_p6_pack.json --work WORK/p6 --out OUT/p6
```

Portes strictes (JSON absents = stop) :

```bash
python3 run_all.py --pack TRACKING/fixtures/sanguinala_p6_pack.json --work WORK/p6 --out OUT/p6 --require-previews
```

Portes : G0 PACK, G0-S (blur|reframing), W1/T1 review, G1 sample/VOD, G2 duree, G3 LOOK 9:16, M1 montage, G4 caption, GL1 glow, L1/F1 lut+fade, G-PACK, G6 F05/F06.

Fixture Phase 5 = 2 assets locaux 9:16, **sans VOD payante**.

```bash
python3 run_all.py --pack TRACKING/fixtures/sanguinala_p5_pack.json --work WORK --out OUT
```

```bash
python3 run_all.py --pack TRACKING/fixtures/sanguinala_p5_split_scene.json --dry-run
# G0-S FAIL exit 2
```

---

# Archive — LACRIMAE dev10-v2

## Vocabulaire

- **asset** : A01, A02, … = 1 video finale = 1 job
- **pack** : l'ensemble des assets
- **LOOK** : F03_PREVIEW + F03_PICTOR (blur / split / reframing, overlay)
- **TEMPS** : F04_HEISENBERG (cuts, SFX, B-roll, flash, punch-in-cut)

## Local

```bash
python3 BRIDGE_PERTURABO/CODEBASE/lac_bridge_forge.py --pur --pack-filter pur_A01 --style blur

python3 F00_PUR/CODEBASE/f00_pur.py \
  --pack BRIDGE_PERTURABO/IN/production_pack_pur_A01.json \
  --out F00_PUR/OUT

cd F03_PREVIEW/CODEBASE
npm ci
npm run dev

cd F03_PICTOR/CODEBASE
npm ci
node render_pictor.mjs \
  --manifest ../../BRIDGE_PERTURABO/OUT/pur_manifest.json \
  --clips ../../F00_PUR/OUT \
  --out ../../F03_PICTOR/OUT

python3 F04_HEISENBERG/CODEBASE/heisenberg.py \
  --input F03_PICTOR/OUT/pur_A01_look.mp4 \
  --manifest BRIDGE_PERTURABO/OUT/pur_manifest.json \
  --out F04_HEISENBERG/OUT

python3 F05_CAMOUFLAGE/CODEBASE/lac_f05_camouflage.py \
  --input F04_HEISENBERG/OUT/pur_A01.mp4 \
  --output F05_CAMOUFLAGE/OUT
python3 F06_LUTHER/CODEBASE/lac_f06_luther.py \
  --input F05_CAMOUFLAGE/OUT/short_camouflaged.mp4 \
  --output F06_LUTHER/OUT
```

## CI

Un seul workflow : `.github/workflows/dev10_pur_render.yml`

Actions → DEV10-v2 — PUR render → Run workflow.

Inputs : `pack_filter`, `canvas`, `perturabo_branch`, `style`,
`max_parallel`, `max_duration`.

Flux : prepare (fetch + G0-S) → matrix 1 asset / 1 job → F00_PUR →
PICTOR → Heisenberg → agregeur strict → F05/F06.

## Fichiers jamais commites

Clips, OUT/, `pur_manifest.json` genere, `codex.json` local.
Transit par artifacts CI ou GitHub Releases.

## En cas de probleme

| Symptome | Cause | Action |
|----------|-------|--------|
| G0 echoue | pack incomplet | retour PERTURABO |
| G0-S exit 2 | style absent / ranking | `--style blur\|split_scene\|reframing` |
| G1 echoue | VOD expiree | clip en Release, rejouer |
| G2 echoue | derive timestamps | verifier start/end_sec |
| CLIP PUR MANQUANT | F00_PUR pas lance | etape F00 |
| Zoom visible | P-ZOOM ZERO | revert, ne pas ship |
| Heisenberg JSON only | frégate incomplete | job rouge, pas de livraison |
| Agregation incomplete | un asset manque | P-AGG, zip refuse |
