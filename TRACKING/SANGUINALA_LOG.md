# SANGUINALA_LOG

> 1 ligne par tentative. Echec = message exact, porte, stop. Pas de reecriture silencieuse.
> Branche : `sanguinala-v1` | Depot : `gyutedy/LACRIMAE-FULL`

| Date | Phase | Tentative | Porte | Resultat |
|------|-------|-----------|-------|----------|
| 2026-11-10 | 0 | Lecture CDC V3 + inventaire 22 branches + grep W1 | — | OK. Plan ecrit. Review la plus complete = origin/dev8. Base = origin/dev10-v2. F07 = origin/dev11-F07. LUT = origin/dev6 CONFIG/atom_ic_profiles.json. Heisenberg hors flux. |
| 2026-11-10 | 0 | Branche sanguinala-v1 + docs CDC/plan/log + push LACRIMAE-FULL | — | OK. Commit fc84f15. Branche https://github.com/gyutedy/LACRIMAE-FULL/tree/sanguinala-v1 |
| 2026-11-10 | 1 | git checkout origin/dev11-F07 -- F07_CAPTION | — | OK. modal_app.py present. 0 modification. |
| 2026-11-10 | 1 | git checkout origin/dev6 -- CONFIG/atom_ic_profiles.json | — | OK. |
| 2026-11-10 | 1 | git checkout origin/dev7 -- F03_PREVIEW | W1 | NON EXECUTE tel quel. Ecraserait le LOOK dev10-v2 (150 lignes, 0 mecanisme W1). Ecart CDC §10.3 / plan Phase 1 : src extraite a cote dans TRACKING/SALVAGE/review_dev7 et review_dev8. LOOK intact. Consolidation = Phase 3. |
| 2026-11-10 | 1 | git mv BRIDGE_PERTURABO BRIDGE | — | OK. |
| 2026-11-10 | 1 | git mv F00_PUR F00_SOURCE | — | OK. |
| 2026-11-10 | 1 | git mv F03_PICTOR F01_LOOK | — | OK. |
| 2026-11-10 | 1 | git mv F05_CAMOUFLAGE F05 | — | OK. F06_LUTHER inchange. F04_HEISENBERG present hors flux. |
