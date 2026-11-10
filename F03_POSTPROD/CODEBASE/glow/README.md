# F03_POSTPROD / GLOW

Sous-fregate glow, pattern Modal F07 (CDC §7.2, Q2). Preview 1 frame avant batch (GL2).

## Fichiers

| Fichier | Role |
|---------|------|
| `modal_glow.py` | Fonction Modal + `glow_clip` local (ffmpeg). Pattern `caption/TRAVAIL/CODEBASE/modal_app.py`. |
| `preview_glow.py` | Endpoint local : 1 frame + params → PNG temps reel. |

Parametres : `{ "mode": "scene"|"subject", "sigma": 12, "opacity": 0.35 }`

## Portes

| Porte | Regle |
|-------|--------|
| **GL1** | `mode` = `scene` \| `subject`. sigma 4–30. opacite 0–0.6. Hors plage = exit 2. |
| **GL2** | Preview 1 frame PNG avant application a N clips. Zone caption (y ≥ 78 %, contrat F07) exclue du glow — les sous-titres ne sont pas blanchis. Mix lineaire `gblur` (pas `screen`). |

## Q2 / Q3

- **Q2** : architecture Modal = copie du pattern F07 (`debian_slim` + `apt ffmpeg` + GPU T4 + volume + `local_entrypoint`).
- **Q3** : mode `subject` = segmentation personne **rembg** sur Modal. Si import / masque vide / qualite insuffisante : **mat rigide** (ellipse centre, talking-head) — log + repli, pas de nouveau modele.

## Local (sans credentials Modal)

```bash
python3 preview_glow.py --frame <frame|clip> --out preview.png --mode scene --sigma 12 --opacity 0.35
python3 -c "from modal_glow import glow_clip, check_gl1"
```

Batch Modal (inbox volume) :

```bash
modal run modal_glow.py --task preview --glow-mode scene --sigma 12 --opacity 0.35
modal run modal_glow.py --task glow --glow-mode subject --sigma 12 --opacity 0.35
```
