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
| 2026-11-10 | 2 | mkdir F02/F03_POSTPROD/REVIEW/OUT + git mv F07 → caption + LUT profiles | — | OK. |
| 2026-11-10 | 2 | collage montage.py §7.5 + lut_apply.py §7.6 | — | OK tel quel. ffmpeg montage non installe (CDC ligne commentaire). |
| 2026-11-10 | 2 | postprod.py + run_all.py squelette §7.7 | — | OK. Heisenberg jamais appele. G0-S blur\|reframing. |
| 2026-11-10 | 2 | glow stubs signature §7.2 | — | OK. Modal = Phase 4. |
| 2026-11-10 | 2 | E2E argparse + portes | M1 L1 G0-S GL1 | OK. broll absent exit 2. cube absent exit 2. split_scene exit 2. blur dry-run 0. sigma 99 exit 2. |
| 2026-11-10 | 3 | Copie handlers W1 depuis salvage review_dev8 vers F03_PREVIEW App.jsx (LOOK conserve) | W1 T1 | OK. handleLogoClick + confirmLogoPlacement + watermark pack JSON + titles + export review. split_scene retire PUR_STYLE_VALUES. Src complete reste dans SALVAGE (pas collee par-dessus LOOK). |
| 2026-11-10 | 4 | modal_glow.py pattern F07 (debian_slim + ffmpeg + GPU T4 + volume + local_entrypoint) | GL1 GL2 | OK. scene = gblur mix. subject = rembg d'abord, rembg absent = log + mat rigide. |
| 2026-11-10 | 4 | preview_glow.py 1 frame PNG | GL2 | OK. scene.png + subject.png + clip mp4. |
| 2026-11-10 | 4 | E2E tests/test_glow.py | GL1 GL2 | OK. sigma 99 exit 2. opacity 0.9 exit 2. bande caption blanche conservee (mean R>200). rembg import FAIL logue, repli mat. |
| 2026-11-10 | 5 | run_all.py portes G0-G6 + fixture 2 assets | G0 G0-S G1 G2 G3 M1 G4 GL1 L1/F1 G-PACK G6 | OK. split_scene dry-run exit 2. blur 2 clips → OUT/A01.mp4 + OUT/A02.mp4. Heisenberg jamais appele. VOD = sample local 9:16 (pas de VOD payante). |
| 2026-11-10 | 5 | montage.py passthrough si broll vide | M1 | OK. copy input → out. broll absent reste exit 2. |
| 2026-11-10 | 5 | lut_apply.py fade black + video-only | L1 F1 | OK. -an si pas d'audio. cube absent reste exit 2. |
| 2026-11-10 | 6 | VOD twitch.tv/videos/2923715533 probe | G1 | OK. 8805s 1920x1080. Segments 120-128 et 480-488. |
| 2026-11-10 | 6 | yt-dlp --download-sections 8s A01+A02 | G1 G2 | OK. duree 8.00s. Jamais la VOD complete. |
| 2026-11-10 | 6 | LOOK blur 1080x1920 0 zoom | G3 | OK. ffmpeg scale/crop/gblur overlay, pas Remotion. |
| 2026-11-10 | 6 | preview glow 1 frame A01 | GL2 | OK. A01_glow_preview.png. |
| 2026-11-10 | 6 | run_all P6 A01 | G6 | OK. OUT/p6/A01.mp4 1080x1920 h264 yuv420p. |
| 2026-11-10 | 6 | glow A02 timeout 300s mid-file | GL | FAIL partiel (1.9s). Relance glow_clip OK 8s. Consigné, pas de rewrite pipeline. |
| 2026-11-10 | 6 | premier E2E multi-videos | G-PACK G6 | OK. OUT/p6/A01.mp4 + A02.mp4. LUT off (pas de .cube). Caption housing only. Heisenberg jamais appele. 0 jump cut 0 zoom. |
| 2026-11-10 | 7 | publication operateur MID | — | OK. YouTube Shorts https://youtube.com/shorts/M9P1qCwsgR0 — clip MID seulement (01:13:20–01:13:28). A01/A02 non publies. Whop non soumis. |
| 2026-11-10 | 7b | branchement F03_PREVIEW + F07 PREVIEW | W1 T1 G4 | OK. run_all --preview-stage stage pack+clip. F03_PREVIEW save REVIEW/sanguinala_review.json. F07 PREVIEW save caption/OUT/style.json. F07 fichiers 0 modification. --require-previews = FAIL si JSON absents. |
| 2026-11-11 | 7c | F03 live : titres editables + fg_scale + curseur WM | W1 T1 | OK. LOOK conserve. Handlers copies depuis salvage review_dev8. Pas de collage Omni/ranking/reveal/hybrid. F07 PREVIEW 0 modification. |
| 2026-11-11 | 7d | rebranchement GitHub Pages | W1 G4 | OK. Erreur CDC : gh-pages hors perimetre. Hub f03/ + f07/. Archive OMNIS conservee. F07 chemins relatifs pour Pages. |
