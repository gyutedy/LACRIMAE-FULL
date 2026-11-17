# F02_MONTAGE

**Passthrough assume en V1.** `montage.py` copie l'entree vers la sortie.

Raison : le pack MARK1 n'emet aucune instruction de montage a executer —
aucun champ `broll`, `sfx` ni `flash` (verifie sur
`production_pack_mark1_e99bd523.json`). Le b-roll, le flash blanc et les SFX
sont **hors perimetre V1** (voir `TRACKING/PLAN_CODEX_V1.md` et l'erratum du
CDC V3). Heisenberg reste hors flux.

Code : `CODEBASE/montage.py` (34 lignes : `shutil.copy2`).

Porte **M1** : passthrough conforme — un MP4 entre, un MP4 sort, duree
identique, zero jump cut, zero b-roll, zero SFX.

Si un pack portait un jour un `broll` non vide alors que cette fregate ne
sait pas le monter, le comportement attendu est un **exit 2 explicite**, pas
un montage silencieusement ignore. Ce garde-fou n'existe pas encore : il sera
ajoute si le b-roll revient en V2+.
