# F03_POSTPROD

Fregate post-production, appliquee a TOUS les clips, pilotee par
`REVIEW/codex_postprod.json` (schema `sanguinala.postprod.codex.v1`).

**Ordre grave : GLOW → CAPTION → LUT → FADE.**

Le glow passe **avant** le caption pour que les sous-titres ne soient jamais
floutes par le glow de l'image. Cet ordre est porte par le codex
(`order`) et verifie par la porte **PP2**.

| Sous-fregate | Source | Porte | Ou tourne |
|--------------|--------|-------|-----------|
| glow/ | Modal pattern F07 (`modal_glow.py` + `preview_glow.py`) | GL1 / GL2 | **Modal (GPU T4)** |
| caption/ | F07_CAPTION entier, 0 modification | G4 | Whisper/Blender = **Modal** |
| lut/lut_apply.py | CDC §7.6 | L1 / F1 | Actions (CPU) |
| lut/profiles/ | `atom_ic_profiles.json` depuis dev6 | L1 | — |

`postprod.py` s'arrete a la premiere porte en echec.

## Ce que la fregate ne fait PAS

- Les **titres** : c'est le moteur (`F01_LOOK`, Remotion). Le codex render les
  porte, pas le codex postprod.
- Le **watermark / logo PNG** : c'est le moteur aussi (`LogoOverlay`).
- Decider d'un style : elle lit le codex. Un codex absent ou
  `validated_by_magos: false` ⇒ **PP1 refuse** la post-prod.

## Review postprod

```bash
python run_all.py --pack <pack.json> --work WORK --out OUT --preview-stage
cd F03_POSTPROD/CODEBASE/caption/PREVIEW/CODEBASE && npm ci && npm run dev
```

Port 5173. L'operateur valide police / taille / place des sous-titres, le
sigma du glow, le profil LUT et la duree du fondu. Sortie :
`codex_postprod.json` (`validated_by_magos: true`).

GitHub Pages : `https://gyutedy.github.io/LACRIMAE-FULL/f07/` — chemins
relatifs. La sauvegarde disque (`/api/save-style`) n'existe qu'en Vite local ;
sur Pages le fichier est **telecharge**, puis commite par `codex_write.yml`.
