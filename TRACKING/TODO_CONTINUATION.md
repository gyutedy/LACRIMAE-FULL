# LACRIMAE — TODO DE CONTINUATION

> Point d'entree obligatoire apres toute reprise.
> Derniere mise a jour : 2026-11-17.
> Branche active : `sanguinala-v1`. Depot : `https://github.com/gyutedy/LACRIMAE-FULL`
> Plan d'execution : **`TRACKING/PLAN_CODEX_V1.md`** (2 codex, 6 PR).

---

## 1. Etat reel au 2026-11-17

| Element | Etat | Preuve |
|---|---|---|
| Pack MARK1 -> PUR | fait | `REVIEW/packs/production_pack_pur_e99bd523_A0{1,2,3}.json` |
| Bridge PUR -> manifeste | fait | `BRIDGE/OUT/pur_manifest.json` (`dev10.pur.v1`, 1080x1920, blur) |
| Dependances Remotion (`F01_LOOK`) | installees | `npm install` OK (AUDIT L2) |
| preview render (F03_PREVIEW) | live | `f03/` sur Pages |
| preview postprod (F07) | live | `f07/` sur Pages |
| **Le codex commande le moteur** | **PAS FAIT** | `run_all.py:34` definit `F01_MJS`, jamais appele ; `apply_look_blur` code `sigma=20` en dur (AUDIT **L8**) |
| **Le watermark atteint le MP4** | **PAS FAIT** | le PNG est jete par l'adaptateur et le converter (AUDIT **L12**) |
| **La CI sait rendre** | **route reparee (PR2)**, jamais lancee sur un vrai VOD | le workflow pointait `F00_PUR/`, `F03_PICTOR/`, `F05_CAMOUFLAGE/` : inexistants (AUDIT **L9**, corrige) |
| Un MP4 livre | **aucun** | `OUT/` vide, `F00_SOURCE/OUT/` vide |

Conclusion : la chaine est validee **jusqu'a la porte**, pas jusqu'au MP4.
Il ne manque pas « le telechargement du segment et le rendu » : il manque le
branchement du moteur sur le codex, la survie du watermark, et la route CI.

## 2. Ce qui a ete fige le 2026-11-17 (decisions operateur)

1. Deux codex commites : `REVIEW/codex_render.json` et `REVIEW/codex_postprod.json`.
2. Un codex = un style, applique a N clips. Aucun selecteur de clip.
3. Le codex ne nomme jamais un titre : le texte vient du pack.
4. Le moteur dessine les titres, la post-prod les sous-titres.
5. Ordre post-prod grave : **GLOW -> CAPTION -> LUT -> FADE**.
6. Watermark = logo PNG dessine par le moteur ; PNG du pack, place/taille du codex.
7. V1 sans b-roll, SFX ni jump cut : `F02_MONTAGE` = passthrough assume.
8. La review tourne sur GitHub, le rendu sur Actions, le GPU sur Modal.

## 3. Prochaine etape exacte

**PR1 (docs) est faite.** L'ordre des PR est dans `TRACKING/PLAN_CODEX_V1.md` §7 :

| PR | Contenu | Etat |
|---|---|---|
| PR1 | docs vraies (ce fichier + 9 docs + `PLAN_CODEX_V1.md`) | FAIT |
| PR2 | route Actions reparee + `ffmpeg` dans le PATH du job | **fait** |
| PR3 | contrat des 2 codex (schemas, normaliseurs, tests, `.gitignore`) | **fait** |
| PR4 | le moteur applique `codex_render` (Remotion branche, logo, watermark propage) | **fait** |
| PR5 | post-prod applique `codex_postprod` + inversion `GLOW -> CAPTION` | a faire |
| PR6 | review en ligne ecrit les 2 codex (`codex_write.yml`) | a faire |

Prochain pas concret : **PR5** — post-prod applique `codex_postprod.json` + inversion `GLOW -> CAPTION`. Le
contrat existe et il est executable (`tools/codex.py`), mais rien ne le lit
encore au moment de rendre : aujourd'hui le style vient de `--style blur` en
dur et le logo du pack n'atteint pas le MP4 (L12).

## 4. Ce qui n'appartient PAS a cette branche

| Sujet | Ou ca se corrige |
|---|---|
| Titres haches (M1 : `She lost 86,000 seconds`, `She paid 385 was much`) | **PERTURABO** (`ORACLE/answers.json`) |
| `source.directive_path` en chemin Windows (M2) | **PERTURABO** |
| `vod_url` absente du pack (M3) | **PERTURABO** (ou `--vod-url` a l'adaptation) |
| Pack qui ne declare pas `montage_style` | **PERTURABO** |

Le bras arme ne corrige rien : il rend ce que le pack donne.

## 5. Reprise (sandbox)

```bash
git clone https://github.com/gyutedy/LACRIMAE-FULL.git
cd LACRIMAE-FULL
git checkout sanguinala-v1
```

Lire dans cet ordre :

1. `TRACKING/PLAN_CODEX_V1.md` — le plan, les 2 codex, les 6 PR.
2. `TRACKING/PUR_GATES.md` — les portes actives.
3. `AUDIT_V1.md` — les constats et leur etat (M1-M4, L1-L12).
4. `TRACKING/GUIDE_UTILISATION.md` — mode d'emploi operateur.
5. `TRACKING/SANGUINALA_LOG.md` — 1 ligne par tentative, l'historique vrai.

---

# Archive — dev10-v2 (avant SANGUINALA)

> Derniere mise a jour historique : 2026-10-05. Branche `dev10-v2`.
> Statut : A-G poses (F05/F06, F00_PUR, Bridge, Preview, PICTOR, Heisenberg, CI).
> Conserve pour memoire seulement : l'arbre a change de noms et Heisenberg,
> b-roll et SFX sont sortis du flux V1.

Doctrine figee a l'epoque, toujours valable :

1. PERTURABO = cerveau (OU / QUOI). LACRIMAE = bras (COMMENT).
2. Pack in, MP4 out. 1 asset = 1 job.
3. Trois styles : blur, split_scene, reframing. (V1 : blur et reframing seulement.)
4. Zoom banni partout.
5. SIGNUM n'existe pas.

Interdits toujours en vigueur : ranking, reveal, hybrid, music timeline,
zoom / swell / breathing_zoom, F04_SIGNUM, `sequences.json`.
