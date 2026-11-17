# SANGUINALA_LOG

> 1 ligne par tentative. Echec = message exact, porte, stop. Pas de reecriture silencieuse.
> Branche : `sanguinala-v1` | Depot : `gyutedy/LACRIMAE-FULL`

| Date | Phase | Tentative | Porte | Resultat |
|------|-------|-----------|-------|----------|
| 2026-11-10 | 0 | Lecture CDC V3 + inventaire 22 branches + grep W1 | — | OK. Plan ecrit. Review la plus complete = origin/dev8. Base = origin/dev10-v2. F07 = origin/dev11-F07. LUT = origin/dev6 CONFIG/atom_ic_profiles.json. Heisenberg hors flux. |
| 2026-11-10 | 0 | Branche sanguinala-v1 + docs CDC/plan/log + push LACRIMAE-FULL | — | OK. Commit fc84f15. Branche https://github.com/gyutedy/LACRIMAE-FULL/tree/sanguinala-v1 |
| 2026-11-10 | 1 | git checkout origin/dev11-F07 -- F07_CAPTION | — | OK. modal_app.py present. 0 modification. |
| 2026-11-10 | 1 | git checkout origin/dev6 -- CONFIG/atom_ic_profiles.json | — | OK. |
| 2026-11-10 | 1 | git checkout origin/dev7 -- F03_PREVIEW | W1 | NON EXECUTE tel quel. Ecraserait le LOOK dev10-v2 (150 lignes, 0 mecanisme W1). Ecart CDC §10.3 / plan Phase 1 : src extraite a cote dans TRACKING/SALVAGE/review_dev7 et review_dev8. LOOK intact. Consolidation = Phase 3. |
| 2026-11-10 | 1 | git mv BRIDGE_PERTURABO BRIDGE | — | OK. |
| 2026-11-10 | 1 | git mv F00_PUR F00_SOURCE | — | OK. |
| 2026-11-10 | 1 | git mv F03_PICTOR F01_LOOK | — | OK. |
| 2026-11-10 | 1 | git mv F05_CAMOUFLAGE F05 | — | OK. F06_LUTHER inchange. F04_HEISENBERG present hors flux. |
| 2026-11-10 | 2 | mkdir F02/F03_POSTPROD/REVIEW/OUT + git mv F07 → caption + LUT profiles | — | OK. |
| 2026-11-10 | 2 | collage montage.py §7.5 + lut_apply.py §7.6 | — | OK tel quel. ffmpeg montage non installe (CDC ligne commentaire). |
| 2026-11-10 | 2 | postprod.py + run_all.py squelette §7.7 | — | OK. Heisenberg jamais appele. G0-S blur\|reframing. |
| 2026-11-10 | 2 | glow stubs signature §7.2 | — | OK. Modal = Phase 4. |
| 2026-11-10 | 2 | E2E argparse + portes | M1 L1 G0-S GL1 | OK. broll absent exit 2. cube absent exit 2. split_scene exit 2. blur dry-run 0. sigma 99 exit 2. |
| 2026-11-10 | 3 | Copie handlers W1 depuis salvage review_dev8 vers F03_PREVIEW App.jsx (LOOK conserve) | W1 T1 | OK. handleLogoClick + confirmLogoPlacement + watermark pack JSON + titles + export review. split_scene retire PUR_STYLE_VALUES. Src complete reste dans SALVAGE (pas collee par-dessus LOOK). |
| 2026-11-10 | 4 | modal_glow.py pattern F07 (debian_slim + ffmpeg + GPU T4 + volume + local_entrypoint) | GL1 GL2 | OK. scene = gblur mix. subject = rembg d'abord, rembg absent = log + mat rigide. |
| 2026-11-10 | 4 | preview_glow.py 1 frame PNG | GL2 | OK. scene.png + subject.png + clip mp4. |
| 2026-11-10 | 4 | E2E tests/test_glow.py | GL1 GL2 | OK. sigma 99 exit 2. opacity 0.9 exit 2. bande caption blanche conservee (mean R>200). rembg import FAIL logue, repli mat. |
| 2026-11-10 | 5 | run_all.py portes G0-G6 + fixture 2 assets | G0 G0-S G1 G2 G3 M1 G4 GL1 L1/F1 G-PACK G6 | OK. split_scene dry-run exit 2. blur 2 clips → OUT/A01.mp4 + OUT/A02.mp4. Heisenberg jamais appele. VOD = sample local 9:16 (pas de VOD payante). |
| 2026-11-10 | 5 | montage.py passthrough si broll vide | M1 | OK. copy input → out. broll absent reste exit 2. |
| 2026-11-10 | 5 | lut_apply.py fade black + video-only | L1 F1 | OK. -an si pas d'audio. cube absent reste exit 2. |
| 2026-11-10 | 6 | VOD twitch.tv/videos/2923715533 probe | G1 | OK. 8805s 1920x1080. Segments 120-128 et 480-488. |
| 2026-11-10 | 6 | yt-dlp --download-sections 8s A01+A02 | G1 G2 | OK. duree 8.00s. Jamais la VOD complete. |
| 2026-11-10 | 6 | LOOK blur 1080x1920 0 zoom | G3 | OK. ffmpeg scale/crop/gblur overlay, pas Remotion. |
| 2026-11-10 | 6 | preview glow 1 frame A01 | GL2 | OK. A01_glow_preview.png. |
| 2026-11-10 | 6 | run_all P6 A01 | G6 | OK. OUT/p6/A01.mp4 1080x1920 h264 yuv420p. |
| 2026-11-10 | 6 | glow A02 timeout 300s mid-file | GL | FAIL partiel (1.9s). Relance glow_clip OK 8s. Consigné, pas de rewrite pipeline. |
| 2026-11-10 | 6 | premier E2E multi-videos | G-PACK G6 | OK. OUT/p6/A01.mp4 + A02.mp4. LUT off (pas de .cube). Caption housing only. Heisenberg jamais appele. 0 jump cut 0 zoom. |
| 2026-11-10 | 7 | publication operateur MID | — | OK. YouTube Shorts https://youtube.com/shorts/M9P1qCwsgR0 — clip MID seulement (01:13:20–01:13:28). A01/A02 non publies. Whop non soumis. |
| 2026-11-10 | 7b | branchement F03_PREVIEW + F07 PREVIEW | W1 T1 G4 | OK. run_all --preview-stage stage pack+clip. F03_PREVIEW save REVIEW/codex.json. F07 PREVIEW save caption/OUT/style.json. F07 fichiers 0 modification. --require-previews = FAIL si JSON absents. |
| 2026-11-11 | 7c | F03 live : titres editables + fg_scale + curseur WM | W1 T1 | OK. LOOK conserve. Handlers copies depuis salvage review_dev8. Pas de collage Omni/ranking/reveal/hybrid. F07 PREVIEW 0 modification. |
| 2026-11-11 | 7d | rebranchement GitHub Pages | W1 G4 | OK. Erreur CDC : gh-pages hors perimetre. Hub f03/ + f07/. Archive OMNIS conservee. F07 chemins relatifs pour Pages. |
| 2026-11-11 | 7e | F03 Player taille + parse pack SANGUINALA | W1 G4 | OK. Player 300px aspectRatio controls autoPlay. expandSanguinalaPack assets[] → clip_file. LOOK conserve. Pages f03 rebuild. |

## 2026-11-16 — Correctifs AUDIT_V1 (L1, L4, M3/M4)

- **L1 CORRIGE** : `run_all.py` reconfigure stdout/stderr en UTF-8 avec
  errors="replace". Le crash `UnicodeEncodeError` sur la fleche U+2192 en
  cp1252 ne se produit plus. Verifie par dry-run sans PYTHONIOENCODING.
- **L4 CORRIGE** : `dev10_pur_render.yml` pointe `gyutedy/PERTURABO` +
  `pari-forge-perturabo-xs4c` (defaut et repli inline).
- **M3/M4 CORRIGE** : nouveau `BRIDGE/CODEBASE/lac_adapter_mark1.py`.
  Convertit un pack MARK1 (N assets, mode:mark1) en N packs PUR
  (mode:pur, 1 clip chacun) et injecte `--vod-url`. Verifie : 3 packs PUR
  produits depuis `production_pack_mark1_e99bd523.json`, et le premier
  passe `lac_bridge_forge.py --pur` avec `[ok] Pack PUR valide`.

Restent ouverts : M1 (titres haches), M2 (chemin local), L2 (npm install),
L3 (review), L5 (fixture), L6 (python3).

## 2026-11-16 — Pack multi-clips natif + URL operateur

Contrat retabli : UN pack MARK1 = UN livrable = N clips. On ne renomme
jamais le pack, on ne le decoupe pas en N fichiers.

- `lac_adapter_mark1.py` reecrit : prend `--pack-url` (ou `--pack` en local),
  valide les bornes de chaque asset, pose `source.vod_url` UNE SEULE FOIS
  (jamais ecrase si deja present), et reecrit le pack sous SON nom d'origine.
  Refuse si la VOD manque et n'est pas fournie.
- `bridgeClipper.js` : `expandSanguinalaPack()` lisait les bornes dans
  `montage_instructions.start_sec` (format PUR) alors que MARK1 les ecrit a
  plat sur l'asset -> tous les clips faisaient 8s. Lit maintenant les deux.
  Il propage aussi le copywriting de l'asset (overlay_title, metadata_title,
  description, tags, hashtags) : l'overlay n'est plus vide.
- `convert_pur_pack.mjs` : branche `expand()` sur les deux chemins (`--pack`
  et `--packs`). Un pack a N assets produit N entrees de manifeste.
- `dev10_pur_render.yml` : nouvel input `pack_url` (voie nominale) +
  `vod_url`. Le listing de dossier ne reste qu'en repli sur `pack_filter`
  explicite. Plus de run aveugle sur les autres VOD du dossier EXPORT.

Verifie de bout en bout, en local, comme la CI :
  adapter --pack-url <raw>/production_pack_mark1_e99bd523.json
         --vod-url https://twitch.tv/videos/2927914500
  -> 3 clips 30s (A01 10328-10358, A02 8616.6-8646.6, A03 2375.8-2405.8)
  convert --packs ... --style blur
  -> 3 entrees, 90s, 2700 frames, overlay ["She lost 50,000 dollars"]

## 2026-11-17 — Nom canonique codex.json retabli

Le JSON que produit la preview reprend son nom canonique `codex.json`
(ancien `sanguinala_review.json`). Renomme partout : run_all.py,
F03_PREVIEW (App.jsx + vite.config.js), .gitignore, docs.
Fichier existant renomme REVIEW/sanguinala_review.json -> REVIEW/codex.json.

## 2026-11-17 — PR1 : docs alignees sur « le codex commande, le pack fournit »

Aucun code touche. Le but est que la doc ne mente plus avant de brancher le
moteur (sinon on code contre un cahier faux, cf. AUDIT_V1 constat L11).

- **Nouveau** `TRACKING/PLAN_CODEX_V1.md` : le plan valide (doctrine en 8
  points, contrat des 2 codex, portes W1-R / PP1 / PP2, inventaire du pillage
  branche par branche, les 6 PR, defaut de fin, interdits).
- **Deux codex, deux review, deux portes** : `codex_render.json` (moteur) et
  `codex_postprod.json` (glow + sous-titres), tous deux commites. Le fragment
  unique `codex.json` disparait des docs.
- **Bannissement acte** : b-roll, flash blanc et SFX sont hors V1. Le pack
  MARK1 n'emet aucun de ces champs et `F02_MONTAGE` est un passthrough
  (AUDIT_V1 L11).
- `README.md` : pipeline corrige (2 codex en entree, F02 passthrough,
  GLOW -> CAPTION), tableau Docs, section « ce qui vit dans le depot ».
- `TRACKING/PUR_GATES.md` : portes actives reecrites — **W1-R** (codex render),
  **PP1** (codex postprod), **PP2** (ordre post-prod), M1 = passthrough. Les
  portes dev10-v2 restent en archive, clairement separees.
- `TRACKING/GUIDE_BRAS_ARME_PUR.md` : reecrit pour V1 (l'archive Heisenberg /
  b-roll / punch-in est retiree, seul un tableau d'interdits et de depannage
  reel subsiste).
- `TRACKING/GUIDE_REVIEW_UTILISATEUR.md` : les deux review, ce que chacune
  grave, et la regle « le texte du titre vient du pack, jamais de la review ».
- `TRACKING/GUIDE_UTILISATION.md` : `python3` -> `python` (L6), codex renommes,
  prerequis ffmpeg/PATH (L10), heritage dev10-v2 isole et marque non executable.
- `TRACKING/TODO_CONTINUATION.md` : etat reel (aucun MP4 livre), les 8
  decisions du 2026-11-17, la table des 6 PR, et ce qui n'appartient PAS a
  cette branche (M1, M2, M3 = PERTURABO).
- `TRACKING/SANGUINALA_CDC_V3.html` : erratum date en tete (5 points) — le
  cahier reste la reference de perimetre, il n'est pas reecrit en silence.
- `AUDIT_V1.md` : constats **L10** (ffmpeg hors PATH), **L11** (docs b-roll
  fausses, corrige ici), **L12** (watermark jete par l'adaptateur et le
  converter). M1 et M2 reattribues a PERTURABO. Table d'etat mise a jour.
- `REVIEW/README.md` : les 2 codex, leur schema, le logo (PNG du pack + place
  du codex), les portes.

Docs de fregate alignees sur l'arbre reel et sur les 2 codex (elles decrivaient
encore `F03_PICTOR` / `F00_PUR` / `F05_CAMOUFLAGE` et un codex unique) :
`F01_LOOK/README.md` (reecrit : le moteur est le seul dessinateur de texte),
`F01_LOOK/CODEBASE/README_DEPS.md`, `F02_MONTAGE/README.md` (passthrough),
`F03_POSTPROD/README.md` (ordre GLOW -> CAPTION), `F03_PREVIEW/README.md`
(T1 = style seul, le texte vient du pack), `F00_SOURCE/README.md`,
`BRIDGE/README.md` (projection du codex), `F05/README.md`, `SHARED/README.md`,
`F04_HEISENBERG/README.md` (marque hors flux), `.github/workflows/README.md`.

Prochaine etape : **PR2** — reparer la route Actions (`F00_SOURCE`,
`F01_LOOK`, `F05`) et mettre ffmpeg dans le PATH du job.

## 2026-11-17 — PR2 : la route Actions est reparee (L9, L10)

Aucun rendu n'a encore ete lance sur GitHub. Ce qui est verifie ici l'est en
local, avec les memes commandes que la CI.

### 1. Le workflow ne pointait aucun dossier reel (L9)

`dev10_pur_render.yml` a ete reecrit sur l'arbre de la branche :

| Avant | Apres |
|---|---|
| `BRIDGE_PERTURABO/` | `BRIDGE/` |
| `F00_PUR/` | `F00_SOURCE/` |
| `F03_PICTOR/` | `F01_LOOK/` |
| `F05_CAMOUFLAGE/` | `F05/` |
| `F04_HEISENBERG` dans le flux | **retire** (V1 : pas de jump cut) |
| `style` proposait `split_scene` | `blur` / `reframing` (G0-S) |

### 2. Trois trous de route bouches au passage

1. **Aucun pack par angle.** `f00_pur.py` exige UN pack = UN segment ; un pack
   MARK1 en porte N. `tools/convert_pur_pack.mjs` prend maintenant
   `--packs-out <dir>` et ecrit un pack PUR mono-clip par angle, obtenu via
   `expandSanguinalaPack()`. Le pack MARK1 reste la seule source de verite :
   on le decoupe, on n'invente aucun champ et on ne touche pas au titre.
   Noms produits : `production_pack_pur_e99bd523_A01.json` (identiques aux
   packs PUR historiques).
2. **La matrice ne pouvait rien passer a F00.** Elle est construite sur les
   packs mono-clip (`angle`, `pack`, `index`) et **refuse** si le nombre de
   packs differe du nombre d'entrees du manifeste.
3. **`sfxDir` pointait `F03_PICTOR/CODEBASE/public/sfx`** (mort) :
   `F01_LOOK/CODEBASE/public/sfx`.

### 3. ffmpeg/ffprobe hors PATH (L10)

Nouveau module unique `tools/ffmpeg_bin.py` (`FFMPEG`, `FFPROBE`) : override
`<NOM>_BIN` / `FFMPEG_BIN`, puis PATH, puis binaire `imageio-ffmpeg`, puis
`FFMPEG_DIR` / `C:\ffmpeg\bin` / `/usr/local/bin` / `/opt/homebrew/bin`.
Plus un seul nom nu dans la route : `run_all.py`, `tools/pur_aggregate.py`,
`F05/CODEBASE/lac_f05_camouflage.py`, `F06_LUTHER/CODEBASE/lac_f06_luther.py`.
Le job CI installe ffmpeg et le prouve (`command -v ffmpeg && ffmpeg -version`).

Defaut secondaire revele : `pur_aggregate.py` annoncait « piste audio
ABSENTE » quand `ffprobe` echouait, donc un probleme d'outillage devenait un
defaut du pack. Statuts separes (`PROBE_FAILED` vs `NO_AUDIO`), liste
`unreadable` dans le rapport, et sortie UTF-8 (famille L1 : le script
crashait en cp1252 avant d'agreger quoi que ce soit).

### 4. Ce qui a ete verifie, et comment

Fixture MARK1 a 3 clips construite a partir des packs PUR de `REVIEW/packs` :

- `convert_pur_pack.mjs --packs-out` -> 3 packs mono-clip + manifeste 3 entrees,
  90 s, 1080x1920, style `blur`.
- Chaque pack mono-clip passe **G0 PACK** en `f00_pur.py --dry-run` (segment
  lu : A01 02:52:08 -> 02:52:38, etc.).
- Matrice a 3 entrees coherente (`index`/`angle`/`pack`) ; le glob par angle ne
  ramene qu'un pack.
- `pur_aggregate.py` retrouve des `pur_<A01, A02, A03>_look.mp4`, refuse un
  bundle incomplet (rc=1), refuse un rendu muet (P-AUD), puis publie
  `pur_<angle>_finale.mp4` + `pur_aggregate_report.json` quand les 3 sont la
  (rc=0).
- `F05` puis `F06` en batch sur le bundle : `all_qa_pass` vrai.
- `run_all.py` resout `FFMPEG` (imageio-ffmpeg 7.1) et `FFPROBE`
  (`C:\ffmpeg\bin`), les deux repondent `-version`.

Non verifie : un run GitHub reel sur le VOD Twitch. Il appartient a PR4, quand
le moteur sera branche sur `codex_render`.

Connu et assume : `lac_f05_camouflage.py` echoue sous 3 s de clip (`loudnorm`
ne peut pas mesurer). Les clips V1 font 30 s.

Prochaine etape : **PR3** — contrat des deux codex (schemas, normaliseurs,
validation, sortie du `.gitignore`, tests).

## 2026-11-17 — PR3 : le contrat des deux codex devient executable

### Ce qui existe desormais dans le depot

| Fichier | Role |
|---|---|
| `REVIEW/codex_render.json` | codex render **commite** (schema `sanguinala.render.codex.v1`), exemple complet avec les valeurs qui reproduisent le look actuel (degree 15, bg 118 %, fg 57 %, defaults `PUR_OVERLAY_DEFAULTS` pour le titre, logo 15 % centre opacite 0.8) |
| `REVIEW/codex_postprod.json` | codex postprod **commite** (schema `sanguinala.postprod.codex.v1`), `order` fige, caption s1 (`dev11.caption.style.v1` = `DEFAULT_STYLE` de `styleSchema.js`), glow GL1, lut profil `hdr_imperator`, fade `darken` 1.5 s |
| `REVIEW/SCHEMAS/codex_render.schema.json` | verite unique, `additionalProperties: false` partout |
| `REVIEW/SCHEMAS/codex_postprod.schema.json` | idem |
| `tools/codex.py` | validateur minimal (aucune dependance) + doctrine + portes W1-R / PP1 / PP2 + CLI `check` |
| `tools/test_codex.py` | 20 tests `unittest` |

Les deux commites dans git : `git check-ignore` ne les voit pas. L'ancien
`REVIEW/codex.json` unique reste ignore et disparait en PR4.

### Ce que le validateur refuse

- champ obligatoire absent, cle inconnue (strict partout), valeur hors bornes
  (glow `sigma` 4-30, opacite <= 0.6, LUT au schema), couleur non hexa ;
- **toute cle de texte** (`text`, `overlay_title`, `titles`, `lines`,
  `content`, et leurs formes imbriquees) : doctrine « le codex porte le
  style, le pack porte le texte » ;
- `order` post-prod != `[glow, caption, lut, fade]` (PP2) ;
- `validated_by_magos` != `true` quand la porte est demandee (exit 2).

### Verification

`python -m unittest tools.test_codex` : 20/20 verts. CLI :
`check codex_render.json` -> 0 + avertissement W1-R ; `--gate` -> 2.
Cas demontres par les tests : champ manquant refuse avec le chemin exact,
`split_scene` refuse (V2+), cle inconnue `zoom` refuse, texte imbrique
`$.title.overlay_title` refuse, ordre inverti refuse, normalisation qui
n'invente rien sauf les defauts declares (logo custom -> x_pct/y_pct 50,
glow qui n'a pas de mode -> scene).

### Transitoire (assume, documente dans REVIEW/README.md)

- Le bouton Export de `F03_PREVIEW` produit encore l'ancien format
  (`style_pack.titles/watermark/look`) : le validateur le refuse, et c'est
  voulu. La review ecrira les deux vrais codex en **PR6** (`codex_write.yml`).
- Rien ne consomme encore les codex : c'est **PR4** (BRIDGE projette le codex
  render dans le manifeste ; `run_all` remplace son W1 sur `codex.json`).

Prochaine etape : **PR5** — post-prod applique `codex_postprod.json` et
inverse l'ordre `GLOW -> CAPTION`.

## PR4 — le codex commande le moteur (2026-11-17)

Le codex n'est plus un fichier decoratif : il traverse jusqu'au MP4.

- `convert_pur_pack.mjs --codex-render` projette le codex dans le manifeste :
  `style`, `style_params` (`look`), `narrative.overlay.style_params` (`title`),
  `narrative.logo` (`logo` + PNG du pack). Le codex refuse si
  `validated_by_magos != true` (exit 2) et si le schema n'est pas
  `sanguinala.render.codex.v1`.
- `bridgeClipper.js` : `buildPurLogo()` (PNG du pack par defaut, codex
  par-dessus), `pur.watermark` conserve. L12 ferme cote parse.
- `render_pictor.mjs` : `--watermarks <dir>` copie le PNG dans
  `public/watermark/` et **refuse de rendre** s'il manque alors que le pack dit
  `required: true` ; Remotion est appele par node (plus `npx`, cf. L14).
- `_purPackComposition.jsx` : `LogoOverlay` + `getLogoPosition` portes du
  salvage dev8 (7 positions + custom), z-index au-dessus du titre.
- `run_all.py` : `apply_look_blur` **supprime** ; le pipeline passe par
  `build_manifest()` puis `render_look()` ; W1 devient `gate_w1r`
  (`codex_render.json`) ; `segment_of()` lit les bornes MARK1 a plat comme
  `montage_instructions.segment` (sinon 0-2 s pour un pack MARK1) ; le clip
  source s'appelle `pur_<angle>.mp4` et le look `pur_<angle>_look.mp4`.
- Workflow : etape codex (`--gate`) + etape watermark (PNG recupere depuis
  l'EXPORT PERTURABO, refus si introuvable), `--codex-render` et `--watermarks`
  transmis ; les PNG sont restaures dans les jobs `render`.
- `lut_apply.py` et `f00_pur.py` passent par `ffmpeg_bin` (L10 avait laisse
  deux trous) ; `download_segment` donne a yt-dlp le dossier qui contient
  ffmpeg **et** ffprobe (L15).
- Verifie localement : pack MARK1 3 clips -> 3 livrables `OUT/A0*.mp4`,
  `G-PACK OK`. Mesure du logo dans le livrable : 14,8 % de la largeur (codex
  15 %), centre (540, 960) sur 1080x1920.
