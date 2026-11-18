# F03_POSTPROD

Fregate post-production, appliquee a TOUS les clips, pilotee par
`REVIEW/codex_postprod.json` (schema `sanguinala.postprod.codex.v1`).

**Ordre grave : GLOW → CAPTION → LUT → FADE.**

Le glow passe **avant** le caption pour que les sous-titres ne soient jamais
floutes par le glow de l'image. Cet ordre est porte par le codex
(`order`) et verifie par la porte **PP2**.

| Sous-fregate | Source | Porte | Ou tourne | Applique ? |
|--------------|--------|-------|-----------|------------|
| glow/ | `modal_glow.py::glow_clip` (ffmpeg pur) | GL1 / GL2 | Actions (CPU) ou Modal (GPU) | **oui** |
| caption/ | `ass_render.py` (style du codex -> ASS -> libass) ; Whisper CPU | G4 | Actions (CPU) | **oui** : sous-titres graves, 1-2 mots par cue, police du depot |
| lut/lut_apply.py | CDC §7.6 + `--profile` | L1 / F1 | Actions (CPU) | **oui** |
| lut/profiles/ | `atom_ic_profiles.json` depuis dev6 | L1 | — | oui (traduit en filtres ffmpeg) |

`postprod.py` s'arrete a la premiere porte en echec et ecrit
`<work>/postprod_report.json` (schema `sanguinala.postprod.report.v1`) : une
passe non appliquee y est **nommee**, jamais silencieuse.

## Cequi est reellement applique (mesure)

Sur un clip 1080x1920 (codex par defaut) : les sous-titres apparaissent dans la
bande 70-85 % (2991 pixels de glyphes, 0 hors zone), le glow `scene` sigma 12 /
opacite 0.35 laisse cette bande intacte, le profil
`hdr_imperator` change 98 % des pixels et monte le contraste (ecart-type
19,8 -> 21,6), le fade assombrit la fin (luminance 47,7 -> 1,0), et le logo du
moteur garde 97 % de son energie de bord (74,0 -> 71,8) : il reste lisible.

CAPTION, LUT et FADE partent dans **une seule** passe ffmpeg (filtres ordonnes
caption -> lut -> fade) : une seule re-encode par clip,
`single_pass_caption_lut_fade: true` dans le rapport.

Si la transcription est impossible (ni `--transcript`, ni `faster-whisper`), la
passe est **declaree degradee** (`applied: false`, `degraded: ["caption"]`) avec sa raison, jamais silencieuse.

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
