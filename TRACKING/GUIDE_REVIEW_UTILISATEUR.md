# PARCOURS UTILISATEUR — revue du clip avant rendu final

> Ce document decrit le chemin complet, du pack MARK1 au bouton W1.
> Etat au 2026-11-16 : le clip A01 est pret et l'app tourne.

---

## La chaine en une image

```
production_pack_mark1_<token>.json         (MARK1, 1 fichier, N assets)
        │
        │  lac_adapter_mark1.py --vod-url ...
        ▼
production_pack_pur_<token>_<ID>.json      (PUR, 1 fichier PAR clip)
        │
        │  lac_bridge_forge.py --pur
        ▼
pur_manifest.json                          (1080x1920, style, overlay)
        │
        │  f00_pur.py  (yt-dlp --download-sections)
        ▼
pur_<ID>.mp4                               (le segment seul, 30 s)
        │
        │  copie dans public/clips/pur_<angle_id>.mp4
        ▼
F03_PREVIEW (vite, port 5174)              <-- TOI, ICI
        │  tu regles titres / watermark / look
        │  tu cliques "Enregistrer review" (W1)
        ▼
REVIEW/sanguinala_review.json              (jamais commite)
        │
        │  run_all.py
        ▼
OUT/*.mp4                                  (rendu final)
```

## Ce qui est deja fait pour toi

| Piece | Emplacement | Taille |
|---|---|---|
| 3 packs PUR | `REVIEW/packs/production_pack_pur_e99bd523_A0{1,2,3}.json` | ~2 Ko |
| Manifeste | `F03_PREVIEW/CODEBASE/public/pur_manifest.json` | 2,8 Ko |
| Pack pour l'app | `F03_PREVIEW/CODEBASE/public/pack.json` | A01 |
| Clip A01 | `F03_PREVIEW/CODEBASE/public/clips/pur_A01.mp4` | 24,6 Mo |
| Dependances app | `F03_PREVIEW/CODEBASE/node_modules` | 253+ paquets |

## Lancer la revue

L'app tourne deja : **http://localhost:5174/**

Si tu dois la relancer :

```
cd LACRIMAE/F03_PREVIEW/CODEBASE
env -u npm_config_allow_scripts npx vite --port 5174
```

Le `env -u npm_config_allow_scripts` est obligatoire sur cette machine
(voir AUDIT_V1 constat L7).

## Ce que tu regles dans l'app

L'app charge automatiquement `public/pack.json` et affiche le clip A01 avec
l'overlay `She lost 50,000 dollars`.

| Element | Ou | Ce que ca change |
|---|---|---|
| Titres | panneau texte | le texte a l'ecran (T1) |
| Watermark | glisser sur l'image / clic logo | position et taille |
| `fg_scale` | slider | taille de la video claire (blur) |
| Look | selecteur | blur ou reframing |
| Canvas | selecteur | 9:16, 16:9, 1:1 |

## Enregistrer

Bouton **Enregistrer review** -> ecrit deux fois :
1. telechargement `sanguinala_review.json`
2. ecriture directe dans `REVIEW/sanguinala_review.json`
   (via `/api/save-review`, verifie : HTTP 200 le 2026-11-16)

Si l'ecriture directe echoue, un message s'affiche : `W1: save review
indisponible` — le fichier telecharge suffit alors, il faut le poser a la
main dans `REVIEW/`.

## Ensuite

```
python run_all.py --pack REVIEW/packs/production_pack_pur_e99bd523_A01.json \
    --work WORK --out OUT
```

La porte W1 lit `REVIEW/sanguinala_review.json` et applique tes titres.
Sans ce fichier, `W1 REVIEW: JSON absent — titres/watermark pack bruts`
(voir AUDIT_V1 constat L3).

---

## Prochaines etapes

1. **Noter les ajustements a faire** dans le clip A01 — titres, cadrage.
2. Les titres A02 et A03 sont haches (AUDIT_V1 constat M1) : A02 dit
   `She lost 86,000 seconds` pour un timeout Twitch, A03 dit
   `She paid 385 was much` qui n'est pas de l'anglais. A corriger avant de
   produire ces deux clips.
