# AUDIT — constats croisés MARK1 ↔ LACRIMAE

> Document racine. Chaque problème est daté et décrit avec sa cause et sa
> conséquence. Aucun correctif n'est appliqué ici : ce document EST la liste
> de travail. VOD de référence du cycle : `https://twitch.tv/videos/2927914500`.

---

## Partie 1 — Problèmes constatés sur MARK1 (le bras qui produit le pack)

Tous constatés en date du 2026-11-16 sur le pack
`production_pack_mark1_e99bd523.json`.

### M1. Titres d'overlay hachés / grammaticalement cassés

| Asset | bornes | overlay_title produit | texte source réel |
|---|---|---|---|
| A01 | 10328 → 10358 | She lost 50,000 dollars | « I looks like it's like 50,000 dollars » |
| A02 | 8616 → 8646 | **She lost 86,000 seconds** | « Yo, being timed out for 86,000 seconds is » |
| A03 | 2375 → 2405 | **She paid 385 was much** | « I feel like 385 was a bit much, » |

**Cause** : en mode ORACLE (mode 2, sans clé LLM), le titre vient d'une
réponse humaine collée dans `ORACLE/answers.json`. La porte `accept()` vérifie :
`title_forge.validate()` (mots max, CTA, ponctuation) et `s1_context.analyse()`
(entités inexpliquées). **Aucune de ces deux règles ne vérifie que le titre est
une phrase grammaticalement correcte.**

**Conséquence** : les titres hachés passent toutes les portes. A02 déforme le
sens (86 000 s = 24 h de timeout Twitch, pas une « perte »). A03 n'est pas de
l'anglais. En production, ces titres partent à l'écran sur TikTok.

**Piste** : ajouter un contrôle de grammaticalité (détection de fragments :
titre commençant par un verbe conjugué haché, absence de sujet, fragments
prépositionnels orphelins), ou contraindre davantage le prompt ORACLE avec le
texte source complet au lieu d'un fragment.

### M2. `source.directive_path` = chemin local Windows

```json
"source": {
  "directive_path": "D:\\mes couilles\\_perturabo_tmp\\MONDES_FORGES\\CLIPPING\\ARCHIVUM\\..."
}
```

**Cause** : `directiva.run()` écrit le chemin absolu de la machine qui a lancé
le siège.

**Conséquence** : inutile et hostile. Ne veut rien dire pour GitHub Actions,
ni pour le consommateur du pack. Les références doivent être `campaign_id`
+ `source_file` relatifs au repo.

### M3. Le pack MARK1 ne porte pas de `vod_url`

Le pack MARK1 a `source.campaign_id` mais **aucune `vod_url`**. Or LACRIMAE et
`F00_SOURCE` ne peuvent rien télécharger sans elle.

**Cause** : le siège MARK1 travaille sur une transcription F00B_VOX déjà
produite ; la VOD n'est pas une entrée de MARK1.

**Conséquence** : le pack seul est inutilisable pour un rendu. L'adaptateur
(`lac_adapter_mark1`) doit injecter la `vod_url` — actuellement fournie à la
main : `https://twitch.tv/videos/2927914500`.

### M4. Contrat de format absent : `mode: mark1` ≠ `mode: pur`

| | MARK1 produit | LACRIMAE attend |
|---|---|---|
| `mode` | `mark1` | `pur` |
| bornes | `assets[].start_sec` | `source.start_sec` / `montage_instructions` |
| granularité | 1 pack = N assets | 1 pack = 1 clip |

**Cause** : MARK1 a été conçu autonome, sans connaître le contrat PUR.

**Conséquence** : le bridge actuel (`BRIDGE/CODEBASE/lac_bridge_forge.py`)
refuse le pack à `G0 : mode != pur`. L'adaptateur est indispensable, il n'y a
pas de chemin direct.

---

## Partie 2 — Problèmes constatés sur LACRIMAE (le bras qui rend le MP4)

Tous constatés en date du 2026-11-16, branch `sanguinala-v1`.

### L1. Crash Windows sur le caractère « → » (U+2192)

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'
  File "run_all.py", line 381, in main  →  print(msg) → cp1252
```

**Cause** : `log()` fait `print(msg)` sans forcer l'UTF-8. La console Windows
est en cp1252, qui ne connaît pas `→`.

**Conséquence** : le crash survient **après** les portes G0/G0-S pourtant
vertes — le pack est accepté puis le script meurt. Trompeur : on croit que le
problème est le pack, alors que c'est l'encodage.

**Contournement existant** : `export PYTHONIOENCODING=utf-8`.
**Correction attendue** : `sys.stdout.reconfigure(encoding="utf-8")` en tête
de `run_all.py`, ou `hide` des caractères non-ASCII des logs.

### L2. `node_modules` absent dans F01_LOOK

`F01_LOOK/CODEBASE/package.json` déclare Remotion 4 + React 18, mais
`node_modules/` n'existe pas. **Prérequis** : `npm install` dans
`F01_LOOK/CODEBASE` avant tout rendu (`render_pictor.mjs`).

### L3. `REVIEW/codex.json` absent

`REVIEW/` ne contient que `README.md` + `.gitkeep`. Le code **tolère**
l'absence (`W1 REVIEW: JSON absent — titres/watermark pack bruts`), donc le
run continue — mais la validation opérateur est contournée silencieusement.
Avec `--require-previews`, la porte `W1` passe en FAIL. **Décider** : est-ce
qu'un siège doit exiger le review ?

### L4. Workflow `dev10_pur_render.yml` pointe vers un repo inexistant

```yaml
perturabo_repo:   "jfbjfojfonf/PERTURABO"
perturabo_branch: "v2-live-vox-c"
```

Le pack réel est sur **`gyutedy/PERTURABO`**, branche
**`pari-forge-perturabo-xs4c`**. Tel quel, le workflow cherche le pack au
mauvais endroit et échouerait (fetch 404).

### L5. Fixture `twitch.tv/videos/0` court-circuite yt-dlp

`is_fixture_vod()` détecte un VOD terminant par `/videos/0` et saute le
téléchargement **sans** créer les MP4 sources. La chaîne F01→F06 ne peut donc
pas être validée avec la fixture seule : il faut un vrai VOD ou fournir
`--look-dir` avec des MP4 pré-rendus.

### L6. `python3` absent sous Windows

Le README dit `python3 run_all.py` ; Windows ne connaît que `python`. Sans
conséquence fonctionnelle, mais cohérence du guide à prévoir.

---

## Section 3 — Chaîne cible (ce que le document prépare)

```
production_pack_mark1_*.json   (MARK1, mode: mark1, N assets)
        │
        ▼
lac_adapter_mark1.py           (BRIDGE — éclate N → N packs PUR, injecte
        │                       vod_url + montage_instructions minimum)
        ▼
dev10_pur_render.yml           (corrigé : gyutedy/PERTURABO,
        │                       pari-forge-perturabo-xs4c)
        ▼
F00_SOURCE yt-dlp → F01_LOOK Remotion 9:16 → F02 → F03 → F05 → F06
        ▼
OUT/*.mp4
```

## État de chaque constat

| # | Constat | Sévérité | Corrigé ? |
|---|---|---|---|
| M1 | titres hachés | haute | **PROPRIETE PERTURABO** (le bras armé rend ce que le pack donne) |
| M2 | directive_path local | moyenne | non |
| M3 | vod_url absente | haute | **RESOLU** par l adaptateur (--vod-url) |
| M4 | format mark1 vs pur | haute | **CORRIGE** (BRIDGE/lac_adapter_mark1.py) |
| L1 | crash « → » cp1252 | haute | **CORRIGE** (run_all.py reconfigure UTF-8) |
| L2 | node_modules absent | blocante | **CORRIGE** (253 paquets, remotion 4.0.533) |
| L3 | review absent | moyenne | **SUPERSEDE** par les 2 codex commites (PLAN_CODEX_V1) |
| L4 | workflow mauvais repo | blocante | **CORRIGE** (gyutedy/PERTURABO, pari-forge) |
| L5 | fixture sans MP4 | moyenne | non |
| L6 | python3 vs python | basse | **CORRIGE** (docs alignees : python) |
| L7 | `allow-scripts` global casse npm | blocante | **CONTOURNE** (allowScripts[] + env -u) |
| L8 | codex.json lu mais jamais applique | **haute** | non — planifie : PR4 rend le codex autoritaire |
| L9 | CI pointe des dossiers inexistants | **blocante** | **corrige (PR2)** |
| L10 | ffmpeg/ffprobe hors PATH | **blocante (local)** | **corrige (PR2)** : `tools/ffmpeg_bin.py` |
| L11 | docs b-roll/SFX/flash fausses | moyenne | **CORRIGE** (PR1, erratum CDC) |
| L12 | watermark jete par l adaptateur + le converter | **haute** | non — planifie : PR4 |

---

## Section 4 — Correctifs appliques le 2026-11-16

### L1 — CORRIGE
`run_all.py` reconfigure `sys.stdout` et `sys.stderr` en UTF-8 avec
`errors="replace"` a l'import. Plus besoin de `PYTHONIOENCODING`.
Verifie : le dry-run affiche la fleche dans les logs sans variable
d'environnement.

### L4 — CORRIGE
`.github/workflows/dev10_pur_render.yml` pointe desormais
`gyutedy/PERTURABO` + `pari-forge-perturabo-xs4c` (defaut ET repli dans le
script inline).

### M4 / M3 — CORRIGE
Nouveau `BRIDGE/CODEBASE/lac_adapter_mark1.py` : lit un pack MARK1, injecte
`--vod-url`, eclate chaque asset en un pack PUR autonome.

Verifie de bout en bout :

    python BRIDGE/CODEBASE/lac_adapter_mark1.py         --pack ../pack_e99.json         --vod-url https://twitch.tv/videos/2927914500 --out /tmp/pur_test

    -> 3 packs PUR (A01, A02, A03), style blur

    python BRIDGE/CODEBASE/lac_bridge_forge.py --pur         --pack /tmp/pur_test/production_pack_pur_e99bd523_A01.json --dry-run

    -> [ok] Pack PUR valide : e99bd523-A01 | segment 10328.0s -> 10358.0s

La chaine MARK1 -> PUR -> bridge est bouclee.


### L2 — CORRIGE
`npm install` dans `F01_LOOK/CODEBASE` : 253 paquets, remotion 4.0.533.
Verifie reellement : `require('remotion/package.json')` rend 4.0.533,
`esbuild.transformSync` passe, `node render_pictor.mjs` charge le module et
echoue proprement sur `CLIP PUR MANQUANT` (comportement attendu : c'est
F00_PUR qui fournit le clip). Procedure dans `F01_LOOK/CODEBASE/README_DEPS.md`.

### L7 — NOUVEAU, CONTOURNE
Le `~/.npmrc` global porte `allow-scripts=all`, exporte en
`npm_config_allow_scripts`. npm 11.16 traite la couche `env` comme un flag
CLI et refuse alors TOUT install scope projet :

    npm error code EALLOWSCRIPTS
    npm error --allow-scripts is not allowed in project-scoped installs.

Ni `.npmrc` local, ni `--allow-scripts=all`, ni `npm_config_userconfig=/dev/null`
ne le corrigent (5 variantes testees). La source npm
(`lib/utils/resolve-allow-scripts.js`, ligne 104) traite `['cli','env']` comme
policy CLI et `throw`. Solution : declarer `allowScripts[]` dans
`package.json` et retirer la variable le temps de l'install :

    env -u npm_config_allow_scripts npm install

### Chaine validee de bout en bout
    adapter MARK1 -> PUR          : 3 packs
    lac_bridge_forge --pur        : [ok] manifeste 1080x1920, style blur
    render_pictor.mjs             : charge, reclame le clip PUR (normal)
    f00_pur.py --dry-run          : [ok] G0, yt-dlp --download-sections
                                    *02:52:08.000-02:52:38.000 sur la VOD

Il ne reste QUE le telechargement du segment et le rendu.


### L8 — Le codex.json est lu mais JAMAIS applique au rendu (2026-11-17)

Question posee : « le moteur de rendu recoit-il bien le codex.json ? »
Reponse verifiee dans le code : **non, dans aucun des deux chemins.**

**Chemin local (`run_all.py`)** : `merge_review()` lit bien `REVIEW/codex.json`
et fusionne `titles`/`watermark`/`look` dans `style_pack`, puis ecrit
`WORK/style_pack.json`. MAIS rien en aval ne consomme ces cles :

| Etape | Ce qu'elle lit de style_pack | Applique titres ? | Applique watermark ? |
|---|---|---|---|
| F02_MONTAGE `montage.py` | rien (stub : copie le fichier) | non | non |
| F03_POSTPROD `postprod.py` | `caption`, `glow`, `lut`, `fade_out` | non | non |
| `apply_look_blur` (run_all) | rien : `gblur=sigma=20` code en dur | non | non |

Le seul moteur qui DESSINE du texte est Remotion
(`render_pictor.mjs` -> `PurLook.jsx` -> `_purPackComposition.jsx`), et il
lit les overlays depuis le **manifeste** (`narrative.overlay`), pas depuis le
codex. Or `F01_MJS` est declare dans `run_all.py` **ligne 34 et jamais
appele** : le chemin local utilise `apply_look_blur` (ffmpeg nu, zero texte).

**Chemin CI (`dev10_pur_render.yml`)** : ne mentionne `codex`/`review` nulle
part (`grep` = 0). Il repart du pack via `convert_pur_pack.mjs`. Tes
ajustements de preview n'y arrivent pas.

### L9 — Le workflow CI pointe des dossiers INEXISTANTS (2026-11-17)

Le workflow appelle des chemins qui n'existent pas sur cette branche :

| Chemin dans le workflow | Existe sur la branche ? | Reel |
|---|---|---|
| `F00_PUR/CODEBASE/f00_pur.py` | **ABSENT** | `F00_SOURCE/CODEBASE/f00_pur.py` |
| `F03_PICTOR/CODEBASE/render_pictor.mjs` | **ABSENT** | `F01_LOOK/CODEBASE/render_pictor.mjs` |
| `F05_CAMOUFLAGE/CODEBASE/lac_f05_camouflage.py` | **ABSENT** | `F05/CODEBASE/lac_f05_camouflage.py` |
| `F04_HEISENBERG/...` | OK | — |
| `F06_LUTHER/...` | OK | — |

Ainsi, meme avec `pack_url` correct, le job CI echouerait au premier appel de
fichier absent. Le workflow n'a jamais ete aligne sur la disposition reelle
des fregates de la branche `sanguinala-v1`.

**CORRIGE (PR2).** Le workflow a ete reecrit sur la route reelle :

| Avant | Apres |
|---|---|
| `BRIDGE_PERTURABO/` | `BRIDGE/` |
| `F00_PUR/` | `F00_SOURCE/` |
| `F03_PICTOR/` | `F01_LOOK/` |
| `F05_CAMOUFLAGE/` | `F05/` |
| `F04_HEISENBERG` dans le flux | **retire** (V1 = pas de jump cut) |
| `style` proposait `split_scene` | `blur` / `reframing` seulement (G0-S) |

Trois autres trous de la meme route ont ete bouches au passage :

1. **Aucun pack par angle.** `f00_pur.py` exige UN pack = UN segment, alors
   qu'un pack MARK1 porte N clips. `convert_pur_pack.mjs` ecrit desormais des
   packs PUR mono-clip (`--packs-out BRIDGE/PUR`), produits par
   `expandSanguinalaPack()` : le pack MARK1 reste la seule source de verite,
   on ne fait que le decouper (aucun champ invente, aucun titre touche).
2. **La matrice n'avait pas de pack a passer.** Elle vient maintenant des
   packs mono-clip (`angle`, `pack`, `index`) et refuse si le nombre de packs
   differe du nombre d'entrees du manifeste.
3. **`sfxDir` pointait `F03_PICTOR/CODEBASE/public/sfx`** (mort) — corrige en
   `F01_LOOK/...`.

Verifie localement sur une fixture MARK1 a 3 clips : 3 packs mono-clip ecrits
(`production_pack_pur_e99bd523_A0{1,2,3}.json`), chacun passe **G0 PACK** en
`--dry-run`, matrice a 3 entrees coherente, et `pur_aggregate` retrouve bien
les `pur_<angle>_look.mp4`.

### L10 — `ffmpeg` et `ffprobe` hors du PATH (2026-11-17)

Sur la machine de l'operateur, `command -v ffmpeg` repond
`command not found`, alors que le binaire existe (`C:\ffmpeg\bin\ffmpeg.exe`,
plus une copie fournie par `imageio-ffmpeg`).

`run_all.py` appelle `"ffmpeg"` en **nom nu** (lignes 161, 182, 200), donc
tout rendu local echoue avant meme d'atteindre une porte de contenu. Le
paquet `imageio-ffmpeg` installe n'est pas utilise par le code.

**Consequence** : un operateur qui clone et lance `run_all.py` sans avoir
bricole son PATH croit que le pack est refuse, alors que c'est l'outil qui
manque. Même famille de piege que L1 (l'erreur n'est pas celle qu'on croit).

**CORRIGE (PR2).** Nouveau module unique `tools/ffmpeg_bin.py` :
`FFMPEG` / `FFPROBE` sont resolus dans cet ordre — `<NOM>_BIN` (et
`FFMPEG_BIN`), PATH, binaire livre par `imageio-ffmpeg`, puis
`FFMPEG_DIR` / `C:\ffmpeg\bin` / `/usr/local/bin` / `/opt/homebrew/bin`.
Tous les appels en nom nu ont disparu de la route CI : `run_all.py`,
`tools/pur_aggregate.py`, `F05/CODEBASE/lac_f05_camouflage.py`,
`F06_LUTHER/CODEBASE/lac_f06_luther.py`.

Verifie sur la machine : `FFMPEG` = binaire `imageio-ffmpeg` 7.1,
`FFPROBE` = `C:\ffmpeg\bin\ffprobe.exe`, les deux repondent `-version`.

**Defaut secondaire revele par ce constat.** `pur_aggregate.py` transformait
un `ffprobe` en echec en « piste audio ABSENTE » : un probleme d'outillage
etait annonce comme un rendu muet, donc comme un defaut du pack. Les deux
causes sont maintenant separees (`PROBE_FAILED` vs `NO_AUDIO`) et le rapport
porte une liste `unreadable`. Le meme fichier crashait aussi en cp1252 sur la
console Windows avant d'agreger quoi que ce soit (famille **L1**) :
stdout/stderr sont reconfigures en UTF-8 comme dans `run_all.py`.

Non corrige (assume) : `lac_f05_camouflage.py` echoue si le clip fait moins
de 3 s, `loudnorm` ne pouvant pas mesurer une loudness sur un extrait plus
court. Les clips V1 font 30 s ; le message reste « Conversion failed! ».

### L11 — Les docs declarent du b-roll et des SFX qui n'existent pas (2026-11-17)

Trois documents decrivent une V1 qui n'existe ni dans le code ni dans le pack :

| Document | Ce qu'il annonce | Realite |
|---|---|---|
| `TRACKING/SANGUINALA_CDC_V3.html` | livrables V1 : « b-roll avec flash blanc + SFX au debut de chaque b-roll » | aucun champ `broll`/`sfx`/`flash` dans le pack MARK1 ; `F02_MONTAGE` = `shutil.copy2` |
| `README.md` | `[F02_MONTAGE] b-roll + flash + SFX` | idem |
| `TRACKING/PUR_GATES.md` porte M1 | « b-roll aux temps du pack, flash [0,04;0,5] s, SFX debut » | porte inapplicable : rien a monter |

**Consequence** : un operateur qui lit la porte M1 cherche une fonctionnalite
qui n'existe pas, et conclut que le rendu est casse.

**Corrige le 2026-11-17 (PR1)** : `F02_MONTAGE` documente comme
**passthrough assume**, porte M1 reecrite, erratum date en tete du CDC V3.

### L12 — Le watermark du pack est jete trois fois (2026-11-17)

Le pack MARK1 **porte** le watermark :

```json
"watermark": { "file": "production_pack_mark1_e99bd523.png",
               "opacity": 0.8, "position": "centered",
               "size_pct": 15, "required": true, "bundled": true }
```

Il est perdu a chaque etape du transport :

| Etape | Verifie | Resultat |
|---|---|---|
| `BRIDGE/CODEBASE/lac_adapter_mark1.py` | `grep watermark` = 0 | le pack PUR mono-clip ne porte **pas** `watermark` |
| `tools/convert_pur_pack.mjs` | `grep watermark` = 0 | le manifeste ne porte **pas** de watermark |
| `F03_PREVIEW/src/preview/bridgeClipper.js` | `grep watermark` = 0 | l'entree non plus |
| `_purPackComposition.jsx` | `grep watermark` = 0 | **aucun moteur ne dessine le PNG** |

La preview ne dessine que des reperes DOM par-dessus le player
(`App.jsx:371-412`) : ca ne part jamais dans le MP4. Or le pack declare
`required: true`.

**Correction (PR4 : FAITE)** : le PNG reste la **matiere** (il vient du pack,
via `watermark.file`), la place/taille/opacite viennent du
`codex_render.logo`, et le rendu est fait par un calque logo Remotion
(`LogoOverlay`, recupere de la branche `dev8` via
`TRACKING/SALVAGE/review_dev8/CODEBASE/src/preview/OmniComposition.jsx`).

Verifie a la mesure sur un rendu local : le logo couvre 14,8 % de la largeur
(codex : 15 %) et son centre tombe a (540, 960) sur un canvas 1080x1920
(`position: centered`) ; il survit jusqu'au livrable final (energie de bord
63,4 au centre contre 0,07 dans une zone temoin).

### L8 — Le codex n'est jamais applique : le moteur n'est pas appele (2026-11-17, corrige PR4)

La LOOK etait un blur ffmpeg code en dur (`apply_look_blur`, `gblur=sigma=20`) :
le JSON de la review ne commandait rien, et Remotion n'etait jamais appele sur
la route `run_all.py`.

**Corrige (PR4)** :

| Maillon | Avant | Apres |
|---|---|---|
| `run_all.py` | `apply_look_blur` | `render_look()` -> `F01_LOOK/CODEBASE/render_pictor.mjs` |
| BRIDGE | aucun codex | `convert_pur_pack.mjs --codex-render` projette style/look/titre/logo |
| W1 | `REVIEW/codex.json` (legacy, gitignore) | `REVIEW/codex_render.json` (`tools/codex.py check --gate`) |
| Logo | inexistant | `LogoOverlay` (salvage dev8) + PNG du pack via `--watermarks` |

### L14 — Sous Windows, `spawnSync('npx')` echoue en silence (2026-11-17)

`render_pictor.mjs` lancait Remotion par `spawnSync('npx', ...)`. Sous Windows
`npx` est un shim `.cmd` : `spawnSync('npx')` renvoie `ENOENT` (`status: null`),
et `spawnSync('npx.cmd')` renvoie `EINVAL` — sans `shell: true`. La CI (Linux)
ne voit jamais le probleme. **Corrige** : le CLI est appele avec node quand il
existe (`node node_modules/@remotion/cli/remotion-cli.js`), sinon `npx`.

### L15 — `yt-dlp` exige ffmpeg ET ffprobe dans le MEME dossier (2026-11-17)

`--download-sections` a besoin des deux binaires. Sur cette machine `ffmpeg`
resolu est celui d'`imageio-ffmpeg` (sans `ffprobe`) : passer ce seul dossier a
`--ffmpeg-location` produit « ffmpeg is not installed », message faux. **Corrige** :
`ffmpeg_bin.tools_dir()` ne rend qu'un dossier qui contient les deux, et
`run_all.download_segment` le passe a yt-dlp.

### L16 — Le LUT du codex n'est jamais applique (2026-11-17, corrige PR5)

`postprod.py` ne posait `--cube` que si `style_pack.lut.cube` existait. Or
aucun `.cube` n'existe dans le depot (`find . -name '*.cube'` = vide) et
`atom_ic_profiles.json` n'est **pas** un fichier LUT : ce sont des jeux de
parametres (`chroma`, `textura`, `restaura`). Resultat : le codex disait
`lut.enabled: true, profile: hdr_imperator` et **rien n'etait applique**, sans
un mot dans les logs.

**Corrige** : `lut_apply.py --profile <nom>` charge le profil et le traduit en
filtres ffmpeg reels (`hqdn3d` -> `eq` -> `unsharp`). Un profil inconnu est une
erreur (exit 2) qui liste les profils disponibles. Mesure : 98 % des pixels
changent, contraste 19,8 -> 21,6.

### L17 — Le glow ne pouvait pas tourner hors Modal (2026-11-17, corrige PR5)

`glow/modal_glow.py` faisait `import modal` au niveau module : sans Modal
installe (CI, machine locale), l'import plantait et `glow_clip` n'etait jamais
appele. **Corrige** : import optionnel + `_NullApp` (les decorateurs restent en
place), et le coeur ffmpeg utilise `ffmpeg_bin`. Le glow s'applique maintenant
sur un runner Actions (CPU), sans GPU.

### L18 — Les sous-titres ne sont pas graves (2026-11-17, corrige PR8)

Le codex postprod portait le style `dev11.caption.style.v1` (police, taille,
place, contour, motion) mais la gravure demandait une sequence PNG rendue par
**Blender** (runtime Modal) : rien n'etait produit, la passe CAPTION etait
declaree `applied: false` dans chaque rapport.

**Corrige** : `caption/ass_render.py` grave pour de vrai, sans Blender ni GPU —
mots (whisper CPU ou transcript) -> cues de 1-2 mots -> fichier `.ass` (police
`Montserrat-ExtraBold.ttf` du depot, taille/place/couleur/contour/motion du
codex) -> `ass=` (libass) dans **la meme passe** que LUT et FADE. Verifie en
local : 2991 pixels de glyphes dans la bande 70-85 %, 0 en dehors ; un style
dont la police manque au depot, une taille hors 12..240 ou une transcription
impossible sont refuses/declares (`degraded`), jamais silencieux.

### L19 — La review ecrivait un codex fantome (2026-11-17, corrige PR6)

Le bouton Export de `F03_PREVIEW` construisait
`{style_pack: {titles, watermark, look}}` et l'ecrivait sous
`REVIEW/codex.json` via `/api/save-review`. Ce fichier n'est lu par aucune
fregate depuis PR4, et sa forme n'est pas un codex : la review produisait donc
un objet que rien ne consomme, avec un nom que le validateur refuse.

**Corrige** : l'Export produit `codex_render.json` **et** `codex_postprod.json`
au format exact des schemas, `/api/save-codex` les valide avec
`tools/codex.py` avant de les ecrire (un codex refuse n'ecrit rien), et
`codex_write.yml` est la porte d'ecriture en ligne (Pages est en lecture
seule). Preuve : l'export par defaut reproduit **a l'identique** les deux codex
committes (`diff` = vide), et un ordre PP2 inverse ou un champ `title.text` sont
refuses en 400.

### L20 — Rien ne publiait la review en ligne (2026-11-17, corrige PR7)

`gh-pages` etait reste au **2026-11-11** (`fa0b0b4`) : aucun workflow ne
reconstruisait `f03/` ni `f07/`. Les guides disaient « l'operateur valide sur
GitHub Pages », mais la page servie etait un build d'avant les codex — donc
l'export de la review n'aurait jamais eu la bonne forme.

**Corrige** : `preview_pages.yml` reconstruit les deux previews, lance
`node --test tests/codexExport.test.mjs`, publie sur `gh-pages` avec
`keep_files: true` (les medias deja en place — clips, `pack.json`,
`target.mp4`, `archive/` — sont conserves). Verifie : `f03/index.html` de
`gh-pages` pointe maintenant `assets/index-BmhfKw7z.js`, qui contient
`sanguinala.render.codex.v1`, `sanguinala.postprod.codex.v1` et
`/api/save-codex` ; `f07/` et les medias repondent 200.

### L21 — Tous les clips sortaient avec le titre du premier (2026-11-18, corrige PR9)

Le pack MARK1 porte un `narrative.overlay` **global** (celui du premier asset) et
un `overlay` par clip. `_purPackComposition.jsx` preferait le global :

```js
lines: (globalOverlay.lines?.length ? globalOverlay.lines : entryOverlay.lines) || []
```

Les trois clips rendus affichaient donc **« She lost 50,000 dollars »**, alors que
le pack disait A02 « She lost 86,000 seconds » et A03 « She paid 385 was much ».
Le pack etait juste : c'etait le moteur qui ecrasait le titre de chaque entree.

**Corrige** : `pickOverlayLines` / `mergeOverlay` (l'entree gagne, le global
comble), `parsePurPackMulti` ne publie **aucun** titre global quand il y a
plusieurs clips, et 4 tests verrouillent le comportement.

### Restent ouverts
| # | Constat | Note |
|---|---|---|
| L5 | fixture sans MP4 | utiliser un vrai VOD ou `--look-dir` |

Corriges : **L9** et **L10** en PR2, **L11** en PR1, **L3** et **L6** en PR1,
**L8** et **L12** en PR4, **L14** et **L15** en PR4, **L16** et **L17** en PR5,
**L19** en PR6, **L20** en PR7, **L18** en PR8, **L21** en PR9.


Reattribues hors de cette branche : **M1** (titres haches) et **M2**
(`directive_path` local) sont des defauts du **pack**, donc PERTURABO.

Plan d'execution de ces constats : `TRACKING/PLAN_CODEX_V1.md`.
