# LACRIMAE — branche `sanguinala-v1`

> *For the Angel's Tears shall become gold.*

Bras arme SANGUINALA V1 (V3). Pack PUR in, N MP4 out.
Plan d'execution : `TRACKING/PLAN_CODEX_V1.md`. Cahier : `TRACKING/SANGUINALA_CDC_V3.html` (+ erratum).

## Doctrine

| Role | Qui | Decide | Ne fait PAS |
|------|-----|--------|-------------|
| Cerveau creatif | PERTURABO | Le OU et le QUOI (pack, titres) | La physique, le rendu, les gates |
| Bras arme | LACRIMAE | Le COMMENT | Editer le pack, corriger un titre, zoomer, jump-cutter (V1) |
| Operateur | Warsmith | Validation aux portes | — |

**Le codex commande, le pack fournit.** Deux codex commites, deux review,
deux portes : `codex_render.json` (moteur) et `codex_postprod.json`
(glow + sous-titres). Un seul codex par review pour **N clips** : il porte le
**style**, jamais le texte de titre (qui vient du pack).

## Pipeline V1

```text
pack PUR json (N assets)  ─────────────┐
codex_render.json ──► [BRIDGE] G0 + conversion ──► pur_manifest.json
        |
        v
[F00_SOURCE]     yt-dlp --download-sections
        v
[F01_LOOK]       blur | reframing + titre + logo PNG → MP4 9:16
        v
[F02_MONTAGE]    passthrough assume (V1 : 0 b-roll, 0 SFX, 0 jump cut)
        v
[F03_POSTPROD]   GLOW → CAPTION → LUT → FADE   (pilote par codex_postprod.json)
        v
[F05] → [F06_LUTHER] → N livrables OUT/
```

Le moteur dessine les **titres** ; la post-prod dessine les **sous-titres**.
Ordre grave : le glow passe **avant** le caption, sinon il floute les sous-titres.

`run_all.py` s'arrete a la premiere porte. `F04_HEISENBERG` existe hors flux
et n'est jamais appele en V1.

```bash
python3 run_all.py --pack TRACKING/fixtures/sanguinala_p5_pack.json --work WORK --out OUT
```

## Styles V1

`blur` | `reframing`. Autre (dont `split_scene`) = G0-S exit 2. V2+.

## Docs

| Document | Role |
|----------|------|
| `TRACKING/PLAN_CODEX_V1.md` | **Plan d'execution (2 codex, 6 PR)** |
| `TRACKING/SANGUINALA_CDC_V3.html` | Cahier V3 (+ erratum du 2026-11-17) |
| `TRACKING/SANGUINALA_IMPLEMENTATION_PLAN.md` | Phases 0–7 |
| `TRACKING/SANGUINALA_LOG.md` | 1 ligne par tentative |
| `TRACKING/TODO_CONTINUATION.md` | Reprise : etat reel + prochain pas |
| `TRACKING/PUR_GATES.md` | Portes (actives + archive) |
| `TRACKING/GUIDE_UTILISATION.md` | Mode d'emploi operateur |
| `TRACKING/GUIDE_REVIEW_UTILISATEUR.md` | Les deux review (render / postprod) |
| `TRACKING/GUIDE_BRAS_ARME_PUR.md` | Guide du bras arme |
| `AUDIT_V1.md` | Constats MARK1 ↔ LACRIMAE (M1-M4, L1-L12) |

## Ce qui vit dans le depot

`REVIEW/codex_render.json` et `REVIEW/codex_postprod.json` sont **commites** :
la review tourne sur GitHub, le rendu sur Actions, le GPU sur Modal. Aucun
reglage ne reste en local.
