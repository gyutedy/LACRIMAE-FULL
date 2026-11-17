# Guide d'utilisation — LACRIMAE SANGUINALA V1

Branche `sanguinala-v1`. Pack PUR in, N MP4 out.
Plan : `TRACKING/PLAN_CODEX_V1.md`. Portes : `TRACKING/PUR_GATES.md`.

Operateur = toi. Tu valides **deux review** sur un clip de reference, puis le
rendu produit **N MP4**. Tu ne touches ni au code ni au pack, et tu ne
corriges jamais un titre ici.

---

## 1. Ordre operateur

1. **Pack PUR** (PERTURABO, ou fixture). Il porte le texte des titres, les
   bornes, la `vod_url` et le PNG du watermark.
2. **Review RENDER** (`F03_PREVIEW`) : look, typographie du titre, place du
   logo. Sortie : `REVIEW/codex_render.json` + `validated_by_magos: true`.
3. **Review POSTPROD** (`F07 CAPTION PREVIEW` + preview glow) : police, taille
   et place des sous-titres, sigma du glow, LUT, fade. Sortie :
   `REVIEW/codex_postprod.json` + `validated_by_magos: true`.
4. **Rendu** : `run_all` (ou Actions) applique les deux codex et produit
   N MP4. Ordre post-prod grave : **GLOW → CAPTION → LUT → FADE**.

Un codex = un style, applique a **N clips**. Aucun reglage par clip.

## 2. Les deux review, en ligne (voie nominale)

| Review | URL | Produit |
|---|---|---|
| render | `https://gyutedy.github.io/LACRIMAE-FULL/f03/` | `codex_render.json` |
| postprod | `https://gyutedy.github.io/LACRIMAE-FULL/f07/` | `codex_postprod.json` |

Sur Pages, l'enregistrement **telecharge** le JSON ; l'action `codex_write.yml`
le commite dans `REVIEW/`. L'ecriture disque directe (`/api/save-review`,
`/api/save-style`) n'existe que dans Vite en local — c'est du debogage.

Hub : `https://gyutedy.github.io/LACRIMAE-FULL/`
Archive review OMNIS (sept 2026, historique) : `.../archive/omnis-watch/`

## 3. Stage des deux review en local (debogage seulement)

```bash
python run_all.py --pack TRACKING/fixtures/sanguinala_p6_pack.json --work WORK/p6 --out OUT/p6 --preview-stage
```

Puis :

```bash
cd F03_PREVIEW/CODEBASE
npm ci
npm run dev          # port 5174
```

```bash
cd F03_POSTPROD/CODEBASE/caption/PREVIEW/CODEBASE
npm ci
npm run dev          # port 5173
```

Puis relancer **sans** `--preview-stage`.

Sur cette machine : `env -u npm_config_allow_scripts npm install`
(`AUDIT_V1` L7), et `python` — pas `python3` (L6).

## 4. Rendu N MP4

```bash
python run_all.py --pack TRACKING/fixtures/sanguinala_p6_pack.json --work WORK/p6 --out OUT/p6 \
  --codex-render REVIEW/codex_render.json \
  --codex-postprod REVIEW/codex_postprod.json
```

Portes strictes (codex absents ou non valides = stop) :

```bash
python run_all.py --pack <pack.json> --work WORK --out OUT --require-previews
```

Portes actives : **G0** pack, **G0-S** style, **W1-R** codex render,
**G1/G2** source + duree, **G3** look 9:16 (0 zoom), **M1** montage
(passthrough V1), **PP1** codex postprod, **PP2** ordre post-prod,
**GL1/GL2** glow, **L1/F1** lut + fade, **G-PACK**, **G6** livrable.

## 5. Fixtures

Fixture Phase 5 = 2 assets locaux 9:16, **sans VOD payante**.

```bash
python run_all.py --pack TRACKING/fixtures/sanguinala_p5_pack.json --work WORK --out OUT
```

```bash
python run_all.py --pack TRACKING/fixtures/sanguinala_p5_split_scene.json --dry-run
# G0-S FAIL exit 2 (split_scene = V2+)
```

## 6. Prerequis machine

| Outil | Attendu |
|---|---|
| `ffmpeg`, `ffprobe` | dans le `PATH` (Windows : `C:\ffmpeg\bin`). Sans eux, aucun rendu — `AUDIT_V1` **L10** |
| `node` + `npm` | `npm install` dans `F01_LOOK/CODEBASE` (Remotion) et `F03_PREVIEW/CODEBASE` |
| `yt-dlp` | segment seulement, jamais la VOD entiere |
| GPU | uniquement sur Modal (glow, whisper) |

## 7. CI

Un seul workflow de rendu : `.github/workflows/dev10_pur_render.yml`.

Actions → **DEV10-v2 — PUR render** → Run workflow.
Inputs : `pack_url`, `codex_render_url`, `codex_postprod_url`, `vod_url`,
`canvas`, `style`.

Flux : prepare (fetch + G0 + G0-S + codex) → matrix 1 clip / 1 job →
F00_SOURCE → F01_LOOK → F02 (passthrough) → agregation → F03 POSTPROD
(GLW Modal → CAPTION Modal → LUT → FADE) → F05 → F06.

## 8. Fichiers jamais commites

Clips, `OUT/`, `pur_manifest.json` genere, artefacts de siege.
Transit par artifacts CI ou Releases.

En revanche `REVIEW/codex_render.json` et `REVIEW/codex_postprod.json` **sont
commites** : ce sont des decisions operateur, versionnees et diffables.

---

# HERITAGE — dev10-v2 (archive, ne pas executer)

Cette section est conservee pour memoire. Elle decrit l'arbre **avant**
SANGUINALA : noms `BRIDGE_PERTURABO` / `F00_PUR` / `F03_PICTOR` /
`F05_CAMOUFLAGE`, et un flux avec **Heisenberg (jump cuts), b-roll, SFX,
punch-in**. **Rien de tout cela n'existe en V1** : Heisenberg est hors flux,
le b-roll et les SFX sont bannis, et `F02_MONTAGE` est un passthrough.

Vocabulaire historique : *asset* = 1 video finale = 1 job ; *pack* = l'ensemble
des assets ; *LOOK* = F03_PREVIEW + F03_PICTOR ; *TEMPS* = F04_HEISENBERG.

Les commandes de l'archive pointent des dossiers qui n'existent plus sur cette
branche (voir `AUDIT_V1` constat **L9**). Ne pas les rejouer.
