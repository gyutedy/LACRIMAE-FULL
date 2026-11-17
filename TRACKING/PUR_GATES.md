# LACRIMAE — PORTES (SANGUINALA V1 + archive PUR)

## SANGUINALA V1 — portes actives

> Mise a jour 2026-11-17 : les deux codex commites remplacent l'ancien
> `REVIEW/codex.json` mono-fichier. Voir `TRACKING/PLAN_CODEX_V1.md`.

```text
pack PUR + codex_render.json
  → BRIDGE G0
  → F03_PREVIEW W1-R / T1   (AVANT moteur : le codex render est valide)
  → F00_SOURCE G1/G2
  → F01_LOOK G3 (blur|reframing + titre + logo)
  → F02_MONTAGE M1 (passthrough : 0 b-roll, 0 SFX, 0 jump cut)
  → F03_POSTPROD PP1 / PP2 GLOW → CAPTION → LUT → FADE
  → F05 / F06 G6
```

| Porte | Moment | Critere |
|-------|--------|---------|
| **G0 PACK** | Avant tout | `mode=pur`, `vod_url`, `start_sec < end_sec` par asset, segment <= 150 s, `montage_instructions` |
| **G0-S STYLE** | Conversion | `blur` OU `reframing`. Autre / infere / `split_scene` = REFUS exit 2 |
| **W1-R CODEX RENDER** | Avant tout rendu | `REVIEW/codex_render.json` present, schema `sanguinala.render.codex.v1` valide, `validated_by_magos: true`. Absent ou `false` = rendu refuse. Verifie par `python tools/codex.py check REVIEW/codex_render.json --gate` |
| **PP1 CODEX POSTPROD** | Avant post-prod | `REVIEW/codex_postprod.json` present, schema `sanguinala.postprod.codex.v1` valide, `validated_by_magos: true`. Verifie par `python tools/codex.py check REVIEW/codex_postprod.json --gate` |
| **PP2 ORDRE** | Post-prod | ordre applique = `glow → caption → lut → fade`. Les sous-titres ne sont jamais floutes par le glow |
| **G1 SOURCE** | Download | yt-dlp OK, segment seulement |
| **G2 DUREE** | Download | end − start ± 0,5 s |
| **G3 LOOK** | F01 | MP4 9:16, 0 zoom anime, titre du pack + logo PNG pose |
| **M1 MONTAGE** | F02 | **passthrough assume** : F02 copie l'entree. V1 = 0 b-roll, 0 SFX, 0 flash, 0 jump cut |
| **G4 CAPTION** | POST-PROD | `codex_postprod.caption` (schema `dev11.caption.style.v1`) ; overlay Whisper/Blender = runtime Modal |
| **GL1 / GL2** | POST-PROD | `codex_postprod.glow` : sigma 4–30, opacite <= 0,6 ; preview frame avant batch |
| **L1 / F1** | POST-PROD | `codex_postprod.lut` (.cube existe si actif) ; `fade_out` vers la fin |
| **P3 WATERMARK** | F01_LOOK (avant rendu) | `codex_render.logo.enabled` et `narrative.logo.src` ; le PNG (`pack.watermark.file`) doit exister dans le dossier `--watermarks`. Absent = rendu refuse (`render_pictor.mjs`) |
| **T1 TITRES** | F01_LOOK | le titre vient du **pack** (`copywriting.overlay_title`), le style du **codex render**. Le codex ne nomme jamais un titre |
| **G-PACK** | POST-PROD | meme codex render applique a N clips, aucun reglage par clip |
| **G6 LIVRABLE** | F05/F06 | H.264 yuv420p faststart, N MP4 = N assets |

Heisenberg / P3 TEMPS (jump cuts) = **hors flux V1**, jamais appele.

---

# Archive — PUR GATES dev10-v2

## Doctrine

dev10-v2 est le bras arme du mode PUR. PERTURABO analyse et ecrit le pack.
LACRIMAE execute : recupere, telecharge le segment, compose le look,
execute le temps, camoufle, livre.

```text
PERTURABO EXPORT/production_pack_pur_*.json
        |
        v
[BRIDGE]  fetch + G0 + conversion → pur_manifest.json
        |
        v
[F00_PUR]  yt-dlp --download-sections → clips/pur_<angle>.mp4
        |
        v
[F03_PREVIEW]  validation visuelle (blur / split / reframing)
        |
        v
[F03_PICTOR]  LOOK → MP4 compose (0 zoom)
        |
        v
[F04_HEISENBERG]  TEMPS → MP4 reel (cuts / SFX / B-roll / flash)
        |
        v
[F05] → [F06] → livrable
        |
        v
[TRACKING/PUR_CAMPAIGN_LOG.md]
```

## Gates

| Gate | Moment | Verification | Critere |
|------|--------|--------------|---------|
| **G0 PACK** | Avant tout | Pack exploitable | `mode=pur`, `vod_url`, `start_sec < end_sec`, segment <= 150 s, `montage_instructions` presente |
| **G0-S STYLE** | Conversion | Style identifie ET autorise | `blur` / `split_scene` / `reframing` declare par le pack OU `--style` operateur. Infere = REFUS (exit 2). Ranking refuse. |
| **G1 VOD** | Download | Segment obtenu | yt-dlp OK, fichier produit |
| **G2 DUREE** | Apres download | Duree clip | `duration == end_sec − start_sec ± 0.5 s` (re-decoupe locale si derive <= +3 s) |
| **G3 CODEC** | Apres download | Lisibilite | codec in {h264, vp9, hevc, av1}, dimensions > 0 |
| **P0 MANIFESTE** | Apres conversion | `pur_manifest.json` | `schema_version=dev10.pur.v1`, >= 1 entree, overlay non vide, `style_source` in {pack, operator} |
| **P1 PREVIEW** | Avant rendu | Validation visuelle | Overlay lisible, style correct, **aucun zoom a l'ecran** |
| **P2 LOOK** | Apres PICTOR | MP4 compose | Resolution canvas, duree ≈ manifeste, framing fixe |
| **P3 TEMPS** | Apres Heisenberg | MP4 reel | Jump cuts / SFX / B-roll / flash / punch-in-cut conformes au pack. Punch-in = cut, pas scale. Sortie = fichier video, jamais JSON seul. |
| **P-AUD AUDIO** | Agregation | Piste audio | `audio_codec` present (ffprobe). Rendu muet = rendu manquant. |
| **P-AGG MULTI** | Apres N rendus | Agregeur | Chaque asset a son MP4. Un manque = publication refusee. |
| **P-ZOOM ZERO** | PICTOR + Heisenberg | Interdit | Aucun zoom, swell, scale anime, breathing_zoom. Echec = job stoppe. |

## Politique d'echec

- G0-S echoue → RENDU BLOQUE. Deux sorties : regenerer le pack cote
  PERTURABO, ou relancer avec `--style blur|split_scene|reframing`.
- G0 echoue → retour PERTURABO. Jamais de correction manuelle du pack.
- G1/G2/G3 echouent → VOD expiree : basculer le clip en asset Release.
- P1 echoue → corriger dans le preview, re-valider avant PICTOR.
- P3 echoue → Heisenberg n'a pas produit de MP4 conforme. Pas de livraison.
- P-ZOOM ZERO echoue → code a reintroduire un zoom. Revert, pas de workaround.

## Contrats

| Contrat | Chemin | Proprietaire |
|---------|--------|--------------|
| Pack PUR | `production_pack_pur_*.json` | PERTURABO |
| Manifeste `dev10.pur.v1` | `BRIDGE_PERTURABO/OUT/pur_manifest.json` | LACRIMAE bridge |
| Sources segment | `F00_PUR/OUT/pur_sources.json` | F00_PUR |
| Parite LOOK | F03_PREVIEW ↔ F03_PICTOR | LACRIMAE |
| Execution TEMPS | F04_HEISENBERG → MP4 | LACRIMAE |
