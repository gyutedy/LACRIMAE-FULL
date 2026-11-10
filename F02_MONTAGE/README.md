# F02_MONTAGE

Insertion b-roll + flash blanc (duree ajustable 0.04–0.5 s) + SFX au debut du b-roll.
Pas de jump cuts en V1. Remplace Heisenberg (hors flux).

Code : `CODEBASE/montage.py` — collage CDC §7.5.

Porte **M1** : chaque `broll.src` existe, `in < out`, `flash_duration` clamp 0.04..0.5.
Si `broll` est vide : passthrough (copie input → out). Broll declare mais fichier absent = exit 2.
