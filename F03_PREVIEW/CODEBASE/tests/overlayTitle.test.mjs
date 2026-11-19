/**
 * PR9 : le titre d'un clip vient de SON entree, jamais du global.
 *
 * Le pack MARK1 porte `narrative.overlay` (global) + `overlay` par clip. Avant
 * ce correctif le global gagnait : les 3 clips sortaient avec le titre du
 * premier (« She lost 50,000 dollars » partout).
 */
import assert from 'node:assert/strict';
import { test } from 'node:test';

import { pickOverlayLines, mergeOverlay, parsePurPackMulti } from '../src/preview/bridgeClipper.js';

const pack = (angle, title) => ({
  mode: 'pur',
  pack_id: `mark1-${angle}`,
  identite: { angle_id: angle },
  copywriting: { overlay_title: title },
  montage_instructions: { source: { start_sec: 0, end_sec: 30, source_url: 'u' } },
  duration_seconds: 30,
});

test('pickOverlayLines : l entree gagne, le global comble', () => {
  const global = { lines: ['titre du premier'] };
  assert.deepEqual(pickOverlayLines(global, { lines: ['titre du clip'] }), ['titre du clip']);
  assert.deepEqual(pickOverlayLines(global, {}), ['titre du premier']);
  assert.deepEqual(pickOverlayLines({}, {}), []);
  assert.deepEqual(pickOverlayLines({ lines: ['a'] }, { lines: [] }), ['a']);
});

test('mergeOverlay : le style de l entree gagne champ par champ', () => {
  const merged = mergeOverlay(
    { lines: ['global'], color: '#FF0000', style_params: { size: 68, y_pct: 22 } },
    { lines: ['clip'], style_params: { y_pct: 30 } },
  );
  assert.deepEqual(merged.lines, ['clip']);
  assert.equal(merged.color, '#FF0000');          // comble par le global
  assert.equal(merged.style_params.size, 68);     // comble par le global
  assert.equal(merged.style_params.y_pct, 30);    // gagne par l entree
  assert.equal(merged.style_params.y_pct === 22, false);
});

test('multi : aucun texte global, chaque entree porte le sien', () => {
  const manifest = parsePurPackMulti([pack('A01', 'un'), pack('A02', 'deux')], {
    fps: 30,
    canvas: '9:16',
    clipFiles: ['a.mp4', 'b.mp4'],
    style: 'blur',
  });
  assert.equal(manifest.entries.length, 2);
  assert.deepEqual(manifest.narrative.overlay.lines, [], 'un titre global mentirait pour un clip');
  assert.deepEqual(manifest.entries.map((e) => e.overlay.lines[0]), ['un', 'deux']);
});

test('multi : ce que le moteur affiche par clip', () => {
  const manifest = parsePurPackMulti([pack('A01', 'un'), pack('A02', 'deux'), pack('A03', 'trois')], {
    fps: 30,
    canvas: '9:16',
    clipFiles: ['a.mp4', 'b.mp4', 'c.mp4'],
    style: 'blur',
  });
  const shown = manifest.entries.map((e) => mergeOverlay(manifest.narrative.overlay, e.overlay).lines[0]);
  assert.deepEqual(shown, ['un', 'deux', 'trois']);
});
