import React from 'react';
import { staticFile } from 'remotion';
import { PurPackComposition } from '../../../F03_PREVIEW/CODEBASE/src/preview/_purPackComposition.jsx';

function withStaticClips(manifest) {
  if (!manifest || typeof manifest !== 'object') return manifest;
  const entries = Array.isArray(manifest.entries) ? manifest.entries.map((entry) => {
    const clip = String(entry.clip_file || '');
    if (!clip || clip.startsWith('http') || clip.startsWith('data:')) return entry;
    const rel = clip.replace(/^\.?\//, '');
    return { ...entry, clip_file: staticFile(rel) };
  }) : [];
  // Le logo vit dans public/ (render_pictor.mjs le copie) : meme traitement.
  const logo = manifest.narrative?.logo;
  let narrative = manifest.narrative;
  if (logo && logo.src && !String(logo.src).startsWith('http') && !String(logo.src).startsWith('data:')) {
    narrative = {
      ...manifest.narrative,
      logo: { ...logo, src: staticFile(String(logo.src).replace(/^\.?\//, '')) },
    };
  }
  return { ...manifest, entries, narrative };
}

export function PurLook({ purManifest, session, entryIndex = 0, muted = false }) {
  return (
    <PurPackComposition
      purManifest={withStaticClips(purManifest)}
      session={session}
      entryIndex={entryIndex}
      muted={muted}
      fontUrl={staticFile('fonts/Montserrat-ExtraBold.ttf')}
    />
  );
}

export default PurLook;
