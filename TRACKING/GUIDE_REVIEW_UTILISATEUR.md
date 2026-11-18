# Les deux review — parcours operateur avant rendu

> Branche `sanguinala-v1`. Plan : `TRACKING/PLAN_CODEX_V1.md`.
> Remplace la version du 2026-11-16 (un seul `codex.json`, ecriture disque
> locale). Il y a maintenant **deux** review, **deux** codex, **deux** portes.

---

## 1. Vue d'ensemble

```text
pack MARK1 (1 fichier, N assets)            ▸ MATIERE
        │  texte du titre, bornes, vod_url, PNG watermark
        ▼
REVIEW 1 — RENDER   (F03_PREVIEW)
        │  look, typographie du titre, place du logo
        ▼
REVIEW/codex_render.json     + validated_by_magos
        │
        ▼
moteur F01_LOOK (Remotion)  →  N MP4 (titre + logo, ZERO sous-titre)
        │
REVIEW 2 — POSTPROD (F07 CAPTION PREVIEW + preview glow)
        │  police/taille/place des sous-titres, sigma du glow, LUT, fade
        ▼
REVIEW/codex_postprod.json   + validated_by_magos
        │
        ▼
F03_POSTPROD : GLOW → CAPTION → LUT → FADE
        │
        ▼
F05 → F06 → OUT/ (N livrables)
```

**Regle unique** : un codex = un style, applique a **N clips**. Il n'y a pas
de selecteur de clip, pas de reglage par clip. Le codex ne dit **jamais** quel
titre s'affiche : il dit sa taille, sa place, sa couleur, son contour, son fond.

## 2. Review 1 — render

Ce que tu regles :

| Element | Effet | Champ du codex |
|---|---|---|
| Look | `blur` ou `reframing` | `style`, `look.*` |
| Taille de la video claire | `fg_scale` | `look.fg_scale` |
| Flou du fond | `degree` | `look.degree` |
| Taille du texte | — | `title.size` |
| Position du texte | — | `title.x_pct`, `title.y_pct` |
| Couleurs (2 lignes) | — | `title.line1_color`, `title.line2_color` |
| Police | — | `title.font_family` |
| Contour | — | `title.outline_width`, `title.outline_color` |
| Fond du texte | — | `title.bg_enabled`, `bg_color`, `bg_opacity` |
| Logo / watermark | place, taille, opacite | `logo.width_pct`, `position`, `x_pct`, `y_pct`, `opacity` |

Ce que tu **ne** regles pas : le texte du titre. Il vient du pack
(`copywriting.overlay_title`). Si le texte est faux, c'est PERTURABO (MARK1),
pas la review.

Le PNG du logo vient **du pack** (`watermark.file`). Tu ne choisis que sa
place et sa taille.

Sortie : `codex_render.json`, `validated_by_magos: true`.

## 3. Review 2 — postprod

| Element | Effet | Champ du codex |
|---|---|---|
| Police des sous-titres | — | `caption.font` |
| Taille | — | `caption.size` |
| Place | — | `caption.position.x_pct / y_pct` |
| Couleur + contour | — | `caption.color`, `caption.outline` |
| Glow du texte | — | `caption.glow` |
| Animation | `pop-in` / `bounce` / `slide` | `caption.motion`, `motion_speed` |
| Glow de l'image | sigma, opacite | `glow.sigma`, `glow.opacity` |
| LUT | profil | `lut.profile` |
| Fondu de fin | duree | `fade_out.duration_sec` |

L'ordre est **grave dans le codex** : `["glow","caption","lut","fade"]`.
Le glow passe avant le caption, sinon les sous-titres sont floutes.

Sortie : `codex_postprod.json`, `validated_by_magos: true`.

## 4. Ou tourne la review

**Sur GitHub, jamais en local.** Deux surfaces permanentes :

| Review | URL |
|---|---|
| render | `https://gyutedy.github.io/LACRIMAE-FULL/f03/` |
| postprod | `https://gyutedy.github.io/LACRIMAE-FULL/f07/` |

Sur Pages, le bouton d'enregistrement **telecharge** le JSON (il n'y a pas de
disque a ecrire). Le fichier telecharge est ensuite commite dans `REVIEW/`
par l'action `codex_write.yml`. Aucune manipulation git pour l'operateur.

La sauvegarde disque directe (`/api/save-review`, `/api/save-style`) n'existe
que dans le serveur Vite local : c'est un confort de debogage, pas la voie
nominale.

## 5. Ensuite — le rendu

```text
Actions → DEV10-v2 — PUR render
  pack_url            = <pack MARK1>
  codex_render_url    = REVIEW/codex_render.json
  codex_postprod_url  = REVIEW/codex_postprod.json
```

En local (debogage seulement) :

```bash
python run_all.py --pack <pack.json> --work WORK --out OUT \
  --codex-render REVIEW/codex_render.json \
  --codex-postprod REVIEW/codex_postprod.json
```

Prerequis local : `ffmpeg` + `ffprobe` dans le `PATH` (`AUDIT_V1` L10), et
`python` (pas `python3`) sous Windows (L6).

## 6. Ce qui bloque un rendu

| Situation | Porte | Consequence |
|---|---|---|
| `codex_render.json` absent | W1-R | rendu refuse |
| `validated_by_magos: false` | W1-R / PP1 | rendu refuse |
| `codex_postprod.json` absent | PP1 | post-prod refusee |
| Pack sans `source.vod_url` et sans `vod_url` fourni | G0 | refus |
| Style absent / infere / `split_scene` | G0-S | exit 2 |

## 7. Rappels

- Le pack est **intouchable** cote LACRIMAE.
- Un titre faux se corrige dans PERTURABO, **jamais** dans la review.
- V1 : pas de b-roll, pas de SFX, pas de jump cut. `F02_MONTAGE` est un
  passthrough.
- Zero zoom, zero animation d'echelle.
