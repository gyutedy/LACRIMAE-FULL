# LACRIMAE — branche `sanguinala-v1`

> *For the Angel's Tears shall become gold.*

Bras arme SANGUINALA V1 (V3). Pack PUR in, N MP4 out.
Cahier : `TRACKING/SANGUINALA_CDC_V3.html`. Plan : `TRACKING/SANGUINALA_IMPLEMENTATION_PLAN.md`.

## Doctrine

| Role | Qui | Decide | Ne fait PAS |
|------|-----|--------|-------------|
| Cerveau creatif | PERTURABO | Le OU et le QUOI | La physique, le rendu, les gates |
| Bras arme | LACRIMAE | Le COMMENT | Editer le pack, zoomer, jump-cutter (V1) |
| Operateur | Warsmith | Validation aux portes | — |

## Pipeline V1

```text
pack PUR json (N assets)
        |
        v
[BRIDGE]         G0 + conversion
        v
[F00_SOURCE]     yt-dlp --download-sections
        v
[F01_LOOK]       blur | reframing → MP4 9:16
        v
[F02_MONTAGE]    b-roll + flash blanc ajustable + SFX (0 jump cut)
        v
[F03_POSTPROD]   CAPTION → GLOW → LUT → FADE
        v
[F05] → [F06_LUTHER] → N livrables OUT/
```

`run_all.py` s'arrete a la premiere porte. `F04_HEISENBERG` existe hors flux.

```bash
python3 run_all.py --pack TRACKING/fixtures/sanguinala_p5_pack.json --work WORK --out OUT
```

## Styles V1

`blur` | `reframing`. Autre (dont `split_scene`) = G0-S exit 2. V2+.

## Docs

| Document | Role |
|----------|------|
| `TRACKING/SANGUINALA_CDC_V3.html` | Cahier V3 |
| `TRACKING/SANGUINALA_IMPLEMENTATION_PLAN.md` | Phases 0–7 |
| `TRACKING/SANGUINALA_LOG.md` | 1 ligne par tentative |
| `TRACKING/TODO_CONTINUATION.md` | Reprise sandbox |
| `TRACKING/PUR_GATES.md` | Portes |
