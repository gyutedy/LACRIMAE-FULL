# SANGUINALA V1 (V3) — Plan d'implementation

> Point d'entree obligatoire pour cette sandbox et toutes les suivantes.
> Source unique : `TRACKING/SANGUINALA_CDC_V3.html` (cahier V3 definitif, 2026-11-10).
> Branche cible : `sanguinala-v1` depuis `dev10-v2`.
> Depot public : `https://github.com/gyutedy/LACRIMAE-FULL`
> Derniere mise a jour : 2026-11-10.

## Doctrine (ne pas devier)

1. Rien a inventer, rien a « ameliorer ». Copier les blocs du CDC et les commandes git.
2. Marque **RECUPERER** = `git checkout <branche> -- <chemin>` tel quel.
3. Marque **NOUVEAU** = coller le code fourni dans le CDC (§7.5, §7.6, §7.7).
4. Marque **V2+** = interdit en V1. Heisenberg (jump cuts), zoom, sharpen, split_scene, ranking, reveal, hybrid, upload auto : ne pas coder.
5. Si un bloc ne s'execute pas : consigner l'erreur exacte dans `TRACKING/SANGUINALA_LOG.md` et s'arreter a la porte fautive. Ne pas reecrire le pipeline.
6. Pack PERTURABO jamais edite cote bras.
7. Fin de chaque phase : docs a jour + tests E2E de la phase + commit + push. Sinon le travail se perd.

## 22 branches vues — ou piller

| Branche | Role SANGUINALA | Action |
|---------|-----------------|--------|
| `dev10-v2` | BASE. Bridge, F00_PUR, F03_PICTOR, F03_PREVIEW LOOK, F05, F06 | checkout -b sanguinala-v1 |
| `dev11-F07` | F07_CAPTION entier (TRAVAIL + PREVIEW + modal_app.py) | git checkout -- F07_CAPTION |
| `dev6` | CONFIG/atom_ic_profiles.json (LUT) + review clic/dblclic/titres | git checkout -- CONFIG/atom_ic_profiles.json |
| `dev7` | Review candidate CDC §10.3 (clic, double-clic, titres) | git checkout -- F03_PREVIEW puis consolider |
| `dev8` | Review la plus complete pour watermark **dans le src** (3 hits src + 8 json) | porter watermark src par copie de composants |
| `dev9` | Review clic / double-clic / titres (mecanismes presents) | source secondaire §7.4 |
| `dev10` | Review clic / double-clic / titres + overlay_title | source secondaire §7.4 |
| `dev10-v1` | Idem dev10 (palimpseste) | source secondaire §7.4 |
| `dev11-F07` / `dev10-v2` PREVIEW | LOOK PUR 9:16 blur/reframing, 0 zoom — garder le moteur LOOK | ne pas ecraser le LOOK par la review legacy |
| `dev`, `dev2`..`dev5`, `dev6-B`..`F`, `dev-11`, `archive/*`, `gh-pages`, `main` | Hors perimetre V1 | ne pas piller |

### Consolidation review W1 (CDC §7.4) — resultat du grep

| Mecanisme | Present sur | Absent sur |
|-----------|-------------|------------|
| Clic (`handleLogoClick` / `confirmLogoPlacement`) | dev6, dev7, dev8, dev9, dev10, dev10-v1 | **dev10-v2**, dev11-F07 |
| Double-clic (`onDoubleClick` + « Double-cliquez ») | dev6, dev7, dev8, dev9, dev10, dev10-v1 | **dev10-v2**, dev11-F07 |
| Watermark JSON pack | dev6..dev10-v1 (public/) ; **src watermark : dev8 uniquement** | **dev10-v2**, dev11-F07 |
| Titres (texts.title / overlay) | dev6..dev10-v1 (controle texte) ; overlay_title sur dev10 / v1 / v2 | — |

Branche qui en contient le PLUS : **dev8** (clic + double-clic + watermark src + titres).
Base LOOK a conserver : **dev10-v2** F03_PREVIEW (blur / reframing, 0 zoom).
Procedure : partir de dev10-v2 LOOK, porter depuis **dev8** (puis dev7 si manque) les 3 mecanismes **par copie de composants, jamais par reecriture**. Si les 3 ne se reunissent pas par recuperation pure : STOP + rapport dans `SANGUINALA_LOG.md`.

## Pipeline cible (CDC §7) — ordre ferme

```
pack PUR json (N assets)
  -> [BRIDGE]      recup + G0 + conversion -> sanguinala_manifest.json     RECUPERER dev10-v2
  -> [F00_SOURCE]  yt-dlp --download-sections                              RECUPERER F00_PUR tel quel
  -> [F01_LOOK]    blur | reframing -> MP4 9:16                            RECUPERER F03_PICTOR, restreint
  -> [F02_MONTAGE] b-roll + flash blanc ajustable + SFX debut              NOUVEAU code CDC §7.5
  -> [F03_POSTPROD] CAPTION -> GLOW -> LUT -> FADE                         mixte
  -> [F05]         H.264 yuv420p + faststart                               RECUPERER tel quel
  -> [F06_LUTHER]  nettoyage metadonnees -> N livrables                    RECUPERER tel quel
  -> [REVIEW]      validation AVANT rendu final -> N MP4 dans OUT/
```

Heisenberg (F04) n'est PAS recupere.

## Arbre cible (CDC §7.1)

```
SANGUINALA layout (a la racine du repo, pas un sous-dossier magique) :
  BRIDGE/   F00_SOURCE/   F01_LOOK/   F02_MONTAGE/
  F03_POSTPROD/
    CODEBASE/
      postprod.py
      caption/             <- F07_CAPTION entier, 0 modification
      glow/                <- modal_glow.py + preview_glow.py (pattern F07)
      lut/                 <- lut_apply.py + profils dev6
    PREVIEW/glow/
  F05/   F06_LUTHER/
  REVIEW/
  TRACKING/SANGUINALA_LOG.md
  TRACKING/SANGUINALA_CDC_V3.html
  TRACKING/SANGUINALA_IMPLEMENTATION_PLAN.md
  run_all.py
```

## Portes (CDC §9) — aucune n'est optionnelle

G0 PACK, G0-S STYLE (blur|reframing seulement), G1 SOURCE, G2 DUREE, G3 LOOK,
M1 MONTAGE, G4 CAPTION, GL1/GL2 GLOW, L1/F1 LUT+FADE, W1 REVIEW, T1 TITRES,
G-PACK, G6 LIVRABLE.

Echec d'une porte = stop. Loguer. Ne pas contourner.

## Interdit V1 (CDC §5 stop)

jump cuts / smash / punch-in, sharpening, zoom (swell, breathing_zoom, scale anime),
split_scene, ranking, reveal, hybrid, upload automatique, musique additionnelle.

---

# Phases

Chaque phase se termine par : (1) docs TRACKING a jour (2) tests E2E de la phase (3) commit (4) push `origin sanguinala-v1` vers `gyutedy/LACRIMAE-FULL`.

Remote a utiliser :

```bash
git remote add full https://github.com/gyutedy/LACRIMAE-FULL.git
# push : git push -u full sanguinala-v1
```

Ne jamais committer de token. Ne jamais editer le pack PUR.

---

## Phase 0 — Ancrage docs + branche (CETTE PHASE)

Objectif : le plan et le CDC sont sur GitHub, branche creee, journal ouvert. Aucun code pipeline.

Livrables :

- Branche `sanguinala-v1` depuis `dev10-v2`
- `TRACKING/SANGUINALA_CDC_V3.html`
- `TRACKING/SANGUINALA_IMPLEMENTATION_PLAN.md` (ce fichier)
- `TRACKING/SANGUINALA_LOG.md` (journal, 1 ligne par tentative)
- `TRACKING/TODO_CONTINUATION.md` pointe ici
- Commit + push

E2E Phase 0 :

```bash
git checkout sanguinala-v1
test -f TRACKING/SANGUINALA_CDC_V3.html
test -f TRACKING/SANGUINALA_IMPLEMENTATION_PLAN.md
test -f TRACKING/SANGUINALA_LOG.md
git log -1 --oneline
git ls-remote --heads full sanguinala-v1
```

---

## Phase 1 — Recup git des scraps (CDC §10.1 a §10.4)

Objectif : tous les morceaux **RECUPERER** sont dans l'arbre, encore sans coller le code NOUVEAU.

Commandes (copier-coller CDC §10, adaptees a LACRIMAE-FULL) :

```bash
git checkout sanguinala-v1

# 1. Absorber F07 EN ENTIER -> sous-fregate CAPTION (0 modification)
git checkout origin/dev11-F07 -- F07_CAPTION

# 2. Profils LUT depuis dev6
git checkout origin/dev6 -- CONFIG/atom_ic_profiles.json

# 3. Review candidate (CDC dit dev7 ; grep dit dev8 plus complete pour watermark src)
git checkout origin/dev7 -- F03_PREVIEW
# NE PAS ecraser tout de suite : extraire les handlers, les poser a cote.
# Procedure §7.4 : comparer avec origin/dev8 F03_PREVIEW/CODEBASE/src (watermark src).

# 4. Renommages fretés recuperees telles quelles
git mv BRIDGE_PERTURABO BRIDGE
git mv F00_PUR F00_SOURCE
git mv F03_PICTOR F01_LOOK
git mv F05_CAMOUFLAGE F05
# F06_LUTHER reste F06_LUTHER
# F04_HEISENBERG : NE PAS le deplacer dans le pipeline. Laisser hors flux (ne pas l'appeler).
```

F07 housing : CDC demande `git mv F07_CAPTION F03_POSTPROD/CODEBASE/caption`. Creer d'abord l'arbre F03_POSTPROD (Phase 2) puis mv. En Phase 1, F07 reste a la racine jusqu'a ce que le dossier cible existe.

Docs Phase 1 :

- `TRACKING/SANGUINALA_LOG.md` : une ligne par checkout / mv (OK ou FAIL + message git exact)
- Mettre a jour ce plan : Phase 1 = FAIT + chemins reels
- `TRACKING/GUIDE_BRAS_ARME_PUR.md` : noter le nouvel arbre (BRIDGE, F00_SOURCE, F01_LOOK, F05)

E2E Phase 1 :

```bash
test -d F07_CAPTION/TRAVAIL/CODEBASE
test -f F07_CAPTION/TRAVAIL/CODEBASE/modal_app.py
test -f CONFIG/atom_ic_profiles.json
test -d BRIDGE
test -d F00_SOURCE
test -d F01_LOOK
test -d F05
test -d F06_LUTHER
test ! -d BRIDGE_PERTURABO
# Heisenberg existe encore mais n'est pas dans le flux
```

Commit : `sanguinala-v1 P1: recover F07, LUT profiles, rename frigates from CDC §10`

### Phase 1 — FAIT (2026-11-10)

Chemins reels :

- `F07_CAPTION/` (racine, housing Phase 2)
- `CONFIG/atom_ic_profiles.json`
- `BRIDGE/` `F00_SOURCE/` `F01_LOOK/` `F05/` `F06_LUTHER/`
- `F04_HEISENBERG/` present, hors flux
- `F03_PREVIEW/` LOOK dev10-v2 intact (150 lignes)
- `TRACKING/SALVAGE/review_dev7/` + `review_dev8/` (src extraite, pas de checkout ecrasant)

Ecart CDC §10.3 : `git checkout origin/dev7 -- F03_PREVIEW` non execute (detruirait le LOOK). Voir LOG.

---

## Phase 2 — Arbre POSTPROD + coller le code NOUVEAU (CDC §7.5 §7.6 §7.7)

Objectif : coller **tel quel** le code fourni. Pas d'invention ffmpeg au-dela de ce que le CDC ecrit.

```bash
mkdir -p F02_MONTAGE/CODEBASE F02_MONTAGE/IN F02_MONTAGE/OUT
mkdir -p F03_POSTPROD/CODEBASE/caption
mkdir -p F03_POSTPROD/CODEBASE/glow
mkdir -p F03_POSTPROD/CODEBASE/lut/profiles
mkdir -p F03_POSTPROD/PREVIEW/glow
mkdir -p REVIEW
mkdir -p OUT

# Housing F07 (0 modification des fichiers)
git mv F07_CAPTION F03_POSTPROD/CODEBASE/caption

# Housing LUT profiles
git mv CONFIG/atom_ic_profiles.json F03_POSTPROD/CODEBASE/lut/profiles/atom_ic_profiles.json
# si CONFIG vide ensuite, ne pas le garder pour le pipeline
```

Coller :

| Fichier | Source |
|---------|--------|
| `F02_MONTAGE/CODEBASE/montage.py` | CDC §7.5 (script fourni) |
| `F03_POSTPROD/CODEBASE/lut/lut_apply.py` | CDC §7.6 (script fourni) |
| `F03_POSTPROD/CODEBASE/postprod.py` | orchestrateur CAPTION -> GLOW -> LUT -> FADE (squelette §7.7, appelle les scripts colles) |
| `run_all.py` | CDC §7.7 : BRIDGE -> F00 -> F01 -> F02 -> F03 -> F05 -> F06, stop premiere porte |

GLOW Phase 2 = stubs de fichiers `modal_glow.py` / `preview_glow.py` avec la signature CDC §7.2 uniquement. Implementation Modal = Phase 4. Ne pas inventer SAM/rembg ici.

F01_LOOK : restreindre les styles a `blur` | `reframing`. Autre = exit 2 (G0-S). Copier le garde existant F00/bridge, ne pas reecrire PICTOR.

Docs Phase 2 :

- README racine : pipeline SANGUINALA (remplacer Heisenberg par F02_MONTAGE)
- `TRACKING/PUR_GATES.md` : portes SANGUINALA §9 (G0-S sans split_scene)
- `F02_MONTAGE/README.md`, `F03_POSTPROD/README.md` : mission + portes M1 / G4 / GL / L1 / F1
- Log : fichiers colles, chemins, premiere execution a sec (help / argparse)

E2E Phase 2 (unitaire, pas encore vraie VOD) :

```bash
python3 F02_MONTAGE/CODEBASE/montage.py --help
python3 F03_POSTPROD/CODEBASE/lut/lut_apply.py --help
python3 F03_POSTPROD/CODEBASE/caption/TRAVAIL/CODEBASE/caption_schema.py || true
test -f F03_POSTPROD/CODEBASE/caption/TRAVAIL/CODEBASE/modal_app.py
test -f F03_POSTPROD/CODEBASE/lut/profiles/atom_ic_profiles.json
# montage : broll absent -> exit 2 (porte M1)
# lut : cube absent -> exit 2 (porte L1)
```

Commit : `sanguinala-v1 P2: paste F02_MONTAGE + LUT/FADE + postprod tree from CDC`

---

## Phase 3 — Review W1 + titres T1 (CDC §7.3 §7.4)

Objectif : reunir clic, double-clic, images pack, titres. Copie de composants depuis dev8/dev7 vers REVIEW / F03_PREVIEW SANGUINALA. Zero reecriture.

Procedure exacte CDC §7.4 :

```bash
git grep -n "onClick\|onDoubleClick\|dblclick" origin/dev6 origin/dev7 origin/dev8 origin/dev10 origin/dev10-v1 -- F03_PREVIEW/CODEBASE/src/App.jsx
git grep -n "watermark" origin/dev6 origin/dev7 origin/dev8 origin/dev10 origin/dev10-v1 -- F03_PREVIEW/
```

Deja execute en Phase 0 (voir tableau plus haut). Execution :

1. Conserver le LOOK pur de `dev10-v2` (blur / reframing, 0 zoom, overlay_title).
2. Copier depuis `origin/dev8` les handlers `handleLogoClick`, `confirmLogoPlacement`, `onDoubleClick`, lecture `watermark` JSON.
3. Copier le controle titre (police, position, apparition) et le brancher sur `style_pack.titles`.
4. JSON de review unique, applique a N clips.

Si les 3 mecanismes ne se reunissent pas par copie : STOP, log, pas de nouveau moteur.

Docs Phase 3 : `F03_PREVIEW/README.md` + `REVIEW/README.md` + portes W1 / T1 dans PUR_GATES.

E2E Phase 3 :

- Preview demarre (Vite).
- Clic pose / selectionne.
- Double-clic pose image bas de frame.
- Image watermark lue depuis le pack JSON.
- Titres `style_pack.titles` visibles.
- Export JSON review unique.

Commit : `sanguinala-v1 P3: consolidate review W1 (click/dblclick/pack images) + titles T1`

---

## Phase 4 — GLOW Modal pattern F07 (CDC §7.2)

Objectif : sous-fregate GLOW = copie du pattern `F03_POSTPROD/CODEBASE/caption/TRAVAIL/CODEBASE/modal_app.py`.

Fichiers :

- `F03_POSTPROD/CODEBASE/glow/modal_glow.py`
- `F03_POSTPROD/CODEBASE/glow/preview_glow.py`
- Params : `{ "mode": "scene"|"subject", "sigma": 12, "opacity": 0.35 }`
- Bornes GL1 : sigma 4–30, opacite 0–0.6
- GL2 : preview 1 frame avant batch ; ne blanchit pas les sous-titres
- subject : person segmentation type rembg/SAM sur Modal. Repli documente = mat rigide. Essayer le modele d'abord. Si echec qualite : log + repli, pas de nouveau modele.

Docs Phase 4 : README glow, portes GL1/GL2, reference Q2/Q3.

E2E Phase 4 :

- Preview 1 frame PNG temps reel.
- Validation bornes (sigma hors plage = refus).
- Un clip court scene + un clip subject.

Commit : `sanguinala-v1 P4: glow Modal pattern F07 + preview frame`

---

## Phase 5 — Orchestrateur + portes G0 a G6 sur pack fixture

Objectif : `run_all.py` boucle `assets[]`, meme `style_pack`, `montage_instructions` par clip, stop premiere porte.

Fixture : pack JSON conforme CDC §6, 2 assets minimum, **sans vraie VOD payante** si un sample local existe ; sinon Phase 6.

Restreindre G0-S : style autre que blur|reframing = exit 2 (split_scene refuse en V1).

Docs Phase 5 : GUIDE_UTILISATION + PUR_GATES completes + log des portes.

E2E Phase 5 :

```bash
python3 run_all.py --pack <fixture> --work WORK --out OUT
# chaque porte loguee OK ou FAIL
# N MP4 = N assets si toutes portes OK
# Heisenberg jamais appele
```

Commit : `sanguinala-v1 P5: run_all orchestrator + gates G0-G6 on fixture pack`

---

## Phase 6 — Premier E2E multi-videos vraie VOD (CDC J2 / DoD partiel)

Objectif : vraie VOD Twitch ou YouTube, plusieurs assets, clip de reference -> 3 previews (review, glow, caption) -> validation -> N MP4 dans `OUT/`.

Operateur valide les 3 surfaces avant rendu final.

Docs Phase 6 : `PUR_CAMPAIGN_LOG.md` + `SANGUINALA_LOG.md` ligne « premier E2E multi-videos ».

E2E Phase 6 = le DoD video :

- N MP4 partagent titres, captions, watermark, glow, LUT, fade
- flash blanc duree dans [0.04, 0.5] + SFX au debut de chaque b-roll aux temps du pack
- 0 jump cut, 0 zoom
- H.264 yuv420p faststart, metadonnees nettoyees

Commit : `sanguinala-v1 P6: first multi-asset E2E N MP4 in OUT/`

Si une porte bloque plus d'un jour : publier avec le maillon degrade (sans LUT, sans glow) plutot que bloquer. Loguer le degrade.

---

## Phase 7 — Publication + Whop (CDC J3) — hors code

Pas de code d'upload automatique (V2+). L'operateur publie a la main TikTok/Reels, soumet Whop Content Rewards (>= ~2 $/1000 vues).

Livrable : une ligne dans `TRACKING/SANGUINALA_LOG.md` et `PUR_CAMPAIGN_LOG.md` : premiere campagne publiee.

Commit docs only : `sanguinala-v1 P7: first published campaign log`

---

## Checklist agent (a cocher dans le LOG)

- [x] Phase 0 docs + branche poussee
- [x] Phase 1 scraps git
- [ ] Phase 2 collage code CDC
- [ ] Phase 3 review W1 + titres
- [ ] Phase 4 glow Modal
- [ ] Phase 5 run_all + portes fixture
- [ ] Phase 6 E2E vraie VOD N MP4
- [ ] Phase 7 log publication (operateur)

## Ce que VANUS n'est pas

Le depot `gyutedy/VANUS` est un autre projet (pronos foot). Le cahier fourni est **SANGUINALA / LACRIMAE**. On n'y touche pas.

## Reprise sandbox

```bash
git clone https://github.com/gyutedy/LACRIMAE-FULL.git
cd LACRIMAE-FULL
git fetch origin --prune
git checkout sanguinala-v1
```

Lire dans l'ordre :

1. `TRACKING/SANGUINALA_CDC_V3.html`
2. `TRACKING/SANGUINALA_IMPLEMENTATION_PLAN.md`
3. `TRACKING/SANGUINALA_LOG.md`
4. `TRACKING/TODO_CONTINUATION.md`
