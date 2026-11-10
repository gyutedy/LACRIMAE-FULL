# F03_POSTPROD

Frégate post-production, appliquee a TOUS les clips (meme style_pack).

Ordre : CAPTION → GLOW → LUT → FADE.

| Sous-fregate | Source | Portes |
|--------------|--------|--------|
| caption/ | F07_CAPTION entier, 0 modification | G4 |
| glow/ | stubs Phase 2, Modal pattern F07 en Phase 4 | GL1 / GL2 |
| lut/lut_apply.py | CDC §7.6 | L1 / F1 |
| lut/profiles/ | `atom_ic_profiles.json` depuis dev6 | L1 |

`postprod.py` s'arrete a la premiere porte en echec.
