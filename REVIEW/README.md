# REVIEW — les deux codex

Surface operateur avant rendu. Il y a **deux** review et **deux** codex, tous
deux **commites** dans ce dossier. Plan : `TRACKING/PLAN_CODEX_V1.md`.

| Codex | Review | Porte | Consomme par |
|---|---|---|---|
| `codex_render.json` | `F03_PREVIEW` (`f03/` sur Pages) | **W1-R** | BRIDGE → `pur_manifest.json` → `F01_LOOK` (Remotion) |
| `codex_postprod.json` | `F07 CAPTION PREVIEW` + preview glow (`f07/` sur Pages) | **PP1** | `F03_POSTPROD` : GLOW → CAPTION → LUT → FADE |

## Regle

Un codex = **un style**, applique a **N clips**. Pas de selecteur de clip, pas
de reglage par clip. Le codex ne nomme **jamais** un titre : il porte sa
taille, sa place, ses couleurs, son contour, son fond. Le **texte** vient du
pack (`copywriting.overlay_title`) — c'est la matiere PERTURABO.

## Ce que porte chaque codex

| `codex_render.json` (schema `sanguinala.render.codex.v1`) | `codex_postprod.json` (schema `sanguinala.postprod.codex.v1`) |
|---|---|
| `look` : `degree`, `bg_scale`, `fg_scale`, `fg_y_pct` | `order` : `glow → caption → lut → fade` (grave) |
| `title` : `size`, `x_pct`, `y_pct`, couleurs, police, contour, fond, `auto_fit` | `caption` : schema `dev11.caption.style.v1` (police, taille, place, contour, glow, motion) |
| `logo` : `width_pct`, `position`, `x_pct`, `y_pct`, `opacity` | `glow` : `enabled`, `sigma`, `opacity` |
| `validated_by_magos` | `lut` : `enabled`, `profile` |
| | `fade_out` : `mode`, `duration_sec` |
| | `validated_by_magos` |

## Le logo / watermark

- Le **PNG** vient du pack : `watermark.file`. Le pack declare
  `required: true` — un clip sans logo est un pack fautif, pas un choix.
- La **place, la taille, l'opacite** viennent de `codex_render.logo`.
- Il est dessine par `F01_LOOK` (calque logo Remotion). Il ne passe **jamais**
  en post-prod.

## Mecanismes portes depuis le salvage

Copie ciblee (CDC §7.4), jamais de collage du src complet :

| Mecanisme | Source | Ou |
|---|---|---|
| `LogoOverlay` + `getLogoPosition` (7 positions + `custom`) | `TRACKING/SALVAGE/review_dev8/.../OmniComposition.jsx` | `F01_LOOK` (via `_purPackComposition.jsx`) |
| Titres editables (style, pas le texte) | `review_dev8` panneau texte | `F03_PREVIEW/CODEBASE/src/App.jsx` |
| Curseur logo (glisser `x_pct`/`y_pct`) | `review_dev8` `LogoOverlay` | idem |
| Taille video claire (`fg_scale`) | LOOK `_purPackComposition` + slider | idem |
| Export du codex render | bouton `codex_render.json` | idem |
| Style des sous-titres (`s1`) | `dev11-F07` `styleSchema.js` | `F03_POSTPROD/CODEBASE/caption/PREVIEW` |

Le src complet du salvage (hybrid / reveal / ranking) reste dans
`TRACKING/SALVAGE/` — **ne pas le coller** par-dessus le LOOK.

## Portes

`run_all.py` lit `codex_render.json` **avant** le moteur (W1-R) et
`codex_postprod.json` **avant** la post-prod (PP1). Un codex absent, invalide,
ou avec `validated_by_magos: false` ⇒ **rendu refuse**. `--require-previews`
force le FAIL au lieu de tolerer.

## Le contrat est executable

Les schemas sont dans `REVIEW/SCHEMAS/` et **un seul endroit les applique** :
`tools/codex.py`. Pas de dependance externe (validateur minimal integre).

```bash
python tools/codex.py check REVIEW/codex_render.json          # schema + doctrine
python tools/codex.py check REVIEW/codex_postprod.json --gate  # + porte PP1
python -m unittest tools.test_codex -v                         # 20 tests
```

Codes de sortie : `0` valide, `1` invalide (le message nomme le chemin exact,
`$.title.line1_color: ...`), `2` valide mais **non valide par l'operateur**.

Refus automatiques :

- champ obligatoire absent, cle inconnue (`additionalProperties: false`),
  valeur hors bornes, couleur non hexa ;
- **toute cle de texte** (`text`, `overlay_title`, `titles`, `lines`,
  `content`, ...) — le codex porte le style, le pack porte le texte ;
- `order` post-prod autre que `glow → caption → lut → fade` (PP2) ;
- `validated_by_magos` different de `true` quand la porte est demandee.

## Etat transitoire (PR3 → PR6)

- Le bouton **Export** de `F03_PREVIEW` produit encore l'**ancien** format
  (`{style_pack: {titles, watermark, look}}`) sous le nom `codex.json` :
  `tools/codex.py check` le refuse, et c'est voulu — ce n'est pas un codex.
  La review ecrira les deux vrais codex en **PR6** (`codex_write.yml`).
- L'ancien `REVIEW/codex.json` unique reste ignore par git tant que
  `run_all.py` le lit (W1). Il disparait en **PR4**.
