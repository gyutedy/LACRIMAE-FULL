# Guide du Bras Arme — SANGUINALA V1

> Branche `sanguinala-v1`. Pack PUR in, N MP4 out.
> Plan d'execution : `TRACKING/PLAN_CODEX_V1.md`. Portes : `TRACKING/PUR_GATES.md`.
> Remplace l'ancien guide (archive dev10-v2, qui decrivait Heisenberg, b-roll,
> SFX et punch-in : rien de tout cela n'existe en V1).

---

## 1. Ce que fait le bras arme

**Le codex commande, le pack fournit.**

| Piece | Proprietaire | Contenu |
|---|---|---|
| `production_pack_mark1_<token>.json` | PERTURABO | matiere : bornes, `vod_url`, texte du titre, PNG du watermark |
| `REVIEW/codex_render.json` | LACRIMAE (review render) | style : look, typographie du titre, position du logo |
| `REVIEW/codex_postprod.json` | LACRIMAE (review postprod) | style : caption, glow, lut, fade, ordre |

Le bras arme **ne reflechit pas** : il execute exactement ce que le pack
donne. Un titre faux est un defaut PERTURABO, jamais une correction locale.
Le pack n'est **jamais** modifie cote LACRIMAE.

## 2. Pipeline

```text
pack PUR + codex_render.json
  → BRIDGE            G0, conversion, projection du codex dans le manifeste
  → F00_SOURCE        yt-dlp --download-sections (jamais la VOD entiere)
  → F01_LOOK          Remotion : blur|reframing + titre + logo → MP4 9:16
  → F02_MONTAGE       passthrough (0 b-roll, 0 SFX, 0 jump cut)
  → F03_POSTPROD      GLOW (Modal) → CAPTION (Modal) → LUT → FADE
  → F05               camouflage
  → F06_LUTHER        livrable
```

**Le moteur dessine les titres. La post-prod dessine les sous-titres.**
Le glow passe **avant** le caption : sinon il floute les sous-titres.

## 3. Les trois portes de l'operateur

| Porte | Ce que tu fais | Ce que ca grave |
|---|---|---|
| **W1-R** | review render : look, taille/place/couleurs du titre, place du logo | `REVIEW/codex_render.json` + `validated_by_magos: true` |
| **PP1** | review postprod : police/taille/place des sous-titres, sigma du glow, LUT, fade | `REVIEW/codex_postprod.json` + `validated_by_magos: true` |
| **G6** | tu regardes le MP4 final | livraison |

Rien ne se regle « par clip ». Un codex = un style, applique a **N clips**.
Tu ne choisis jamais quel titre : le texte vient du pack, le codex n'en porte
que l'apparence.

## 4. Lancer un rendu (voie nominale : GitHub Actions)

Actions → **DEV10-v2 — PUR render** → Run workflow.

| Input | Valeur |
|---|---|
| `pack_url` | URL brute du pack MARK1 (`production_pack_mark1_<token>.json`) |
| `codex_render_url` | URL brute de `REVIEW/codex_render.json` |
| `codex_postprod_url` | URL brute de `REVIEW/codex_postprod.json` |
| `vod_url` | seulement si le pack ne porte pas `source.vod_url` |
| `canvas` / `style` | defaut `9:16` / style declare par le pack |

Sorties : artefacts `OUT/` (N MP4), rapports F05/F06. Aucun fichier lourd
n'est commite.

## 5. Lancer un rendu (local, pour deboguer)

```bash
python run_all.py --pack <pack.json> --work WORK --out OUT \
  --codex-render REVIEW/codex_render.json \
  --codex-postprod REVIEW/codex_postprod.json
```

Prerequis machine :

- `ffmpeg` et `ffprobe` dans le `PATH` (sous Windows : `C:\ffmpeg\bin`).
  Sans eux, tout rendu echoue — voir `AUDIT_V1` constat **L10**.
- `npm install` dans `F01_LOOK/CODEBASE` (Remotion) et `F03_PREVIEW/CODEBASE`.
- Sur cette machine, `env -u npm_config_allow_scripts` pour les installs
  (voir `AUDIT_V1` constat **L7**).
- Sous Windows, la commande est `python`, pas `python3` (constat **L6**).

## 6. Les deux review, en ligne

| Review | URL | Produit |
|---|---|---|
| render | `https://gyutedy.github.io/LACRIMAE-FULL/f03/` | `codex_render.json` |
| postprod | `https://gyutedy.github.io/LACRIMAE-FULL/f07/` | `codex_postprod.json` |

Les deux sortent un fichier **telecharge**, puis l'action `codex_write.yml`
le commite dans `REVIEW/`. Aucune ecriture disque locale n'est requise : la
review doit tourner sur GitHub, pas sur un sandbox.

## 7. Le watermark

- Le **PNG** vient du pack : `watermark.file` (bundle par MARK1, `required: true`).
- La **place, la taille et l'opacite** viennent de `codex_render.logo`.
- Il est dessine par `F01_LOOK` (calque logo Remotion). Il ne va **jamais**
  en post-prod.

## 8. Interdits V1

b-roll · SFX · flash blanc · jump cut · zoom / swell / breathing_zoom ·
`split_scene` · Heisenberg dans le flux · ranking / reveal / hybrid ·
music timeline · selecteur de clip · texte de titre dans un codex ·
corriger le pack ou un titre cote LACRIMAE.

## 9. En cas de probleme

| Symptome | Cause reelle | Action |
|---|---|---|
| `G0` echoue | pack incomplet | retour PERTURABO |
| `G0-S` exit 2 | style absent / infere / `split_scene` | le pack doit declarer `blur` ou `reframing` |
| `W1-R` refuse | `codex_render.json` absent ou `validated_by_magos: false` | refaire la review render |
| `PP1` refuse | `codex_postprod.json` absent ou non valide | refaire la review postprod |
| `ffmpeg: command not found` | PATH (L10) | ajouter `C:\ffmpeg\bin` |
| `UnicodeEncodeError` | console cp1252 (L1) | corrige, ne doit plus arriver |
| `CLIP PUR MANQUANT` | F00_SOURCE pas lance | etape F00 |
| Titre faux a l'ecran | defaut du pack (M1) | **PERTURABO**, pas ici |
| Pas de logo a l'ecran | PNG absent du pack ou `logo.enabled: false` | verifier `watermark.file` |
| Zoom visible | P-ZOOM ZERO | revert, ne pas livrer |
| Sous-titres flous | ordre post-prod inverse | PP2 : glow avant caption |
