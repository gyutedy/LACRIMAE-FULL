# Dependances F01_LOOK (Remotion)

## Installation

    cd F01_LOOK/CODEBASE
    env -u npm_config_allow_scripts npm install --no-audit --no-fund

## Pourquoi `env -u npm_config_allow_scripts` (L2 / L7)

Le `~/.npmrc` de la machine porte `allow-scripts=all`, exporte dans
l'environnement comme `npm_config_allow_scripts`. npm 11.16 traite la
couche `env` comme un flag CLI et refuse alors tout install scope projet :

    npm error code EALLOWSCRIPTS
    npm error --allow-scripts is not allowed in project-scoped installs.

La policy est donc declaree dans `package.json` (`allowScripts[]`), pas dans
`.npmrc`. Retirer la variable d'environnement le temps de l'install suffit.

## Verifications

**2026-11-16** (machine de l'audit L2) : 253 paquets installes,
remotion 4.0.533, esbuild `transformSync` OK (binaire win32-x64 present).

**2026-11-17** (clone de travail) : `node_modules` present, remotion
**4.0.533** charge par node.

Dans les deux cas, `node render_pictor.mjs` charge le module et echoue
proprement sur `CLIP PUR MANQUANT` : c'est **F00_SOURCE** qui fournit le
clip. Ce message est le comportement attendu, pas une panne.

## Prerequis machine

`ffmpeg` et `ffprobe` doivent etre dans le `PATH` pour tout rendu
(AUDIT_V1 **L10**). Sous Windows : `C:\ffmpeg\bin`.
