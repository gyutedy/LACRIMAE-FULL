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

## Verifie le 2026-11-16

- 253 paquets installes
- remotion 4.0.533 charge par node
- esbuild transformSync OK (binaire win32-x64 present)
- `node render_pictor.mjs` charge le module et echoue proprement sur
  `CLIP PUR MANQUANT` : c'est F00_PUR qui doit fournir le clip.
