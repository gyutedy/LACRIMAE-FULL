# PLAN — « LE CODEX COMMANDE, LE PACK FOURNIT » (SANGUINALA V1)

> Plan valide par l'operateur le 2026-11-17. Ce document est la reference
> d'execution : 6 PR, dans cet ordre. Toute PR qui s'ecarte de ce plan doit
> etre rediscutee avant d'etre codee.
>
> Branche : `sanguinala-v1`. Depot : `gyutedy/LACRIMAE-FULL`.

---

## 1. Doctrine (verrouillee)

1. **Deux codex, deux review, deux portes.** Le codex `render` commande le
   moteur ; le codex `postprod` commande le glow et les sous-titres.
2. **Un seul codex par review pour N clips.** Aucun selecteur de clip, aucun
   reglage par clip. Le codex porte le **style**, jamais le texte de titre.
3. **Le pack est la matiere premiere.** Il porte le texte du titre, les bornes,
   la VOD, le PNG du watermark. Le bras arme ne le modifie jamais.
4. **Le moteur dessine les titres. Post-prod dessine les sous-titres.**
   Ordre de post-prod grave : **GLOW -> CAPTION -> LUT -> FADE**.
5. **Le watermark est un logo PNG, dessine par le moteur.** Il ne va jamais en
   post-prod. Le PNG vient du pack, la position/taille/opacite du codex.
6. **Le bras arme ne reflechit pas.** Il rend exactement ce que le pack donne.
   Un titre faux est un defaut PERTURABO, pas une correction LACRIMAE.
7. **V1 sans b-roll, sans SFX, sans jump cut.** `F02_MONTAGE` est un passthrough
   assume. Heisenberg reste hors flux.
8. **Les deux codex sont commites.** Rien ne vit en local : la review tourne sur
   GitHub, le rendu tourne sur Actions, le GPU sur Modal.

## 2. Flux

```
pack MARK1 (matiere)  ────────────────────────────────┐
                                                      │
codex_render.json (commite) ──► BRIDGE ──► pur_manifest.json (dev10.pur.v1)
                                             titre + look + logo
                                                      │
                                  F01_LOOK (Remotion, SEUL dessinateur de texte)
                                                      │
                                                  N MP4 propres
                                                      │
codex_postprod.json (commite) ──► F03_POSTPROD : GLOW (Modal) -> CAPTION (Modal)
                                                  -> LUT -> FADE
                                                      │
                                                F05 -> F06 -> OUT/
```

## 3. Contrat `REVIEW/codex_render.json`

Schema `sanguinala.render.codex.v1`. Rempli par la review render
(`F03_PREVIEW`). Consomme par le BRIDGE qui le projette dans le manifeste.

| Bloc | Champs | Projete dans |
|---|---|---|
| entete | `schema_version`, `pack_token`, `canvas`, `fps`, `style` | `manifest.style`, `canvas`, `fps` |
| `look` | `degree`, `bg_scale`, `fg_scale`, `fg_y_pct` | `manifest.style_params` |
| `title` | `size`, `x_pct`, `y_pct`, `line1_color`, `line2_color`, `font_family`, `uppercase`, `outline_width`, `outline_color`, `bg_enabled`, `bg_color`, `bg_opacity`, `box_radius`, `box_padding`, `auto_fit`, `min_size` | `manifest.narrative.overlay.style_params` |
| `logo` | `enabled`, `width_pct`, `position`, `x_pct`, `y_pct`, `opacity` | `manifest.narrative.logo` (nouveau) |
| porte | `validated_by_magos` | refuse le rendu si `false` |

Les listes de champs sont celles que le moteur lit deja :
`PUR_OVERLAY_DEFAULTS` + `normalizePurStyleParams` (`F03_PREVIEW/CODEBASE/src/preview/bridgeClipper.js`)
et `_purPackComposition.jsx`. **Le moteur n'est pas reecrit, il est branche.**

## 4. Contrat `REVIEW/codex_postprod.json`

Schema `sanguinala.postprod.codex.v1`.

| Bloc | Champs | Consomme par |
|---|---|---|
| `order` | `["glow","caption","lut","fade"]` (grave) | `F03_POSTPROD/CODEBASE/postprod.py` |
| `caption` | schema `dev11.caption.style.v1` deja present (`caption/PREVIEW/CODEBASE/src/styleSchema.js`) | `caption/TRAVAIL/CODEBASE/modal_app.py` (Modal) |
| `glow` | `enabled`, `sigma`, `opacity` | `glow/modal_glow.py` (Modal, GPU) |
| `lut` | `enabled`, `profile` | `lut/lut_apply.py` (Actions) |
| `fade_out` | `mode`, `duration_sec` | `lut/lut_apply.py` (Actions) |
| `validated_by_magos` | bool | porte PP1 |

## 5. Portes nouvelles

| Porte | Moment | Critere |
|---|---|---|
| **W1-R CODEX RENDER** | Avant tout rendu | `codex_render.json` present, schema valide, `validated_by_magos: true` |
| **PP1 CODEX POSTPROD** | Avant post-prod | `codex_postprod.json` present, schema valide, `validated_by_magos: true` |
| **PP2 ORDRE** | Post-prod | ordre applique = `glow -> caption -> lut -> fade`. Les sous-titres ne sont jamais floutes par le glow |

## 6. Pillage — ce qu'on reprend, ce qu'on refuse

| Source | On reprend | On refuse |
|---|---|---|
| `dev8` `OmniComposition.jsx:661-700` (copie locale : `TRACKING/SALVAGE/review_dev8/`) | `LogoOverlay` + `getLogoPosition` (7 positions + `custom`) | hybrid, reveal, ranking, music timeline |
| `dev8` `src/data/codex.json` (v4.0) | structure `session{composition, logo, texts_style, presets}` + `validated_by_magos` | `virtual_sequences`, motion-slow, `clips[].overlay` |
| `dev8` `TRACKING/CODEX_AUDIT_2026-08-24.md` | le pattern d'audit et son piege (« le moteur charge un manifeste separe ») | — (on l'evite : le manifeste **est** la projection du codex) |
| `dev11-F07` `styleSchema.js` + `styles/s1.json` | deja sur cette branche : `codex_postprod.caption` | — |
| `dev7` `App.jsx` panneau « FOND & LOGO » | panneau operateur du logo (PNG + position + taille) | fonds PNG / backgrounds (hors V1) |
| `gh-pages` `f03/` | le canal de review en ligne (Pages) | — |
| `dev6` `atom_ic_profiles.json` | deja porte dans `F03_POSTPROD/CODEBASE/lut/profiles/` | — |

## 7. Les 6 PR

| PR | Contenu | Sortie verifiable |
|---|---|---|
| **PR1** | Docs vraies (ce document + 9 docs alignes) | aucun code modifie |
| **PR2** | Route Actions reparee (chemins `F00_SOURCE` / `F01_LOOK` / `F05`, `BRIDGE/PUR` mono-clip, Heisenberg retire) + `ffmpeg` dans le PATH du job et `tools/ffmpeg_bin.py` | **FAIT** — le job va jusqu'a `CLIP PUR MANQUANT`, plus de 404 |
| **PR3** | Contrat des 2 codex : schemas, exemples, normaliseurs, tests, sortie du `.gitignore` | **FAIT** — `python tools/codex.py check ...` refuse un champ manquant (exit 1) et `validated_by_magos:false` (exit 2) ; 20 tests verts |
| **PR4** | Le moteur applique `codex_render` : `run_all.py` appelle Remotion, `apply_look_blur` supprime, `LogoOverlay` porte, watermark propage depuis le pack | **FAIT** — `convert_pur_pack.mjs --codex-render` projette style/look/titre/logo ; `run_all.py` rend par `render_pictor.mjs` (plus de blur) ; `LogoOverlay` dans `_purPackComposition.jsx` ; PNG du pack via `--watermarks` ; 3 clips locaux rendus puis livres (`logo 14,8 %` centre, titre du pack) |
| **PR5** | Post-prod applique `codex_postprod` + inversion `GLOW -> CAPTION` | **FAIT** — `postprod.py` lit le codex (PP1/PP2), glow reellement applique (import Modal rendu optionnel), LUT `--profile` traduit en filtres ffmpeg, fade en fin de la meme passe, rapport `postprod_report.json` qui nomme chaque passe (caption declaree non appliquee : pas de sequence Blender) |
| **PR6** | Review en ligne ecrit les 2 codex (action `codex_write.yml`) + inputs `codex_render_url` / `codex_postprod_url` | **FAIT** — l'Export de `F03_PREVIEW` produit `codex_render.json` + `codex_postprod.json` (ancien format supprime), le middleware `/api/save-codex` valide avec `tools/codex.py` avant d'ecrire, `codex_write.yml` valide puis commit depuis une URL/base64 |

## 8. Defaut de fin (une seule preuve)

> `pack_url` MARK1 -> Actions -> `OUT/` contient **N MP4**, chacun avec **son**
> titre (celui du pack) et **le logo PNG du pack**, **zero sous-titre**. Puis
> post-prod ajoute **glow puis sous-titres**, dans cet ordre. Les deux codex
> sont des fichiers du depot. `validated_by_magos: false` bloque le rendu.

## 9. Interdits (ne pas reintroduire)

- Selecteur de clip, reglage par clip, texte de titre dans un codex.
- b-roll, SFX, flash blanc, jump cut dans le flux V1.
- Zoom / swell / breathing_zoom. `split_scene`. Ranking / reveal / hybrid.
- Heisenberg dans le flux. F04_SIGNUM. Music timeline. `sequences.json`.
- Un codex qui vit hors du depot (fichier gitignore, sauvegarde navigateur seule).
- Corriger un pack ou un titre cote LACRIMAE.
