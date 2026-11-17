# F00_SOURCE

Ingest du segment VOD. Ancien nom : `F00_PUR`.

Le pack ne contient pas la video : il contient `vod_url` + `start_sec` +
`end_sec`. F00_SOURCE telecharge **uniquement le segment**
(`yt-dlp --download-sections`), jamais la VOD complete.

## Contrats

| | Chemin |
|--|--------|
| IN | pack PUR (via BRIDGE) |
| OUT | `OUT/pur_<angle>.mp4` + `OUT/pur_sources.json` |
| Code | `CODEBASE/f00_pur.py` |

## Portes

- **G1** VOD obtenue (segment seul)
- **G2** duree = `end − start` ± 0,5 s (re-decoupe locale si derive <= +3 s)
- **G3** codec lisible (h264 / vp9 / hevc / av1)

Sans F00_SOURCE, la preview et le rendu n'ont rien a monter.

## Pieges connus

- **L5** : une fixture `twitch.tv/videos/0` court-circuite yt-dlp sans creer
  de MP4 — il faut un vrai VOD ou fournir `--look-dir` avec des MP4 deja
  rendus.
- VOD expiree : basculer le clip en asset Release, jamais re-telecharger la
  VOD entiere.

Voir `TRACKING/PUR_GATES.md`.
