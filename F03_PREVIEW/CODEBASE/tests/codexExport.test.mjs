/**
 * Tests de la projection review -> codex (aucun navigateur requis).
 *
 * Lancement : node --test F03_PREVIEW/CODEBASE/tests/
 */
import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
  buildCodexRender,
  buildCodexPostprod,
  projectTitle,
  projectLogo,
  projectCaption,
  stringifyCodex,
  PP2_ORDER,
  DEFAULT_POSTPROD,
} from '../src/preview/codexExport.js';

test('render : le titre ne porte jamais de texte', () => {
  const codex = buildCodexRender({
    overlay: { size: 68, x_pct: 50, y_pct: 22, static_text: true, text: 'TEXTE INTERDIT' },
    styleParams: { degree: 15, bg_scale: 118, fg_scale: 57, fg_y_pct: 50 },
  });
  const serialized = JSON.stringify(codex);
  assert.ok(!serialized.includes('TEXTE INTERDIT'), 'un texte de titre a fuie dans le codex');
  for (const key of ['text', 'static_text', 'titles']) {
    assert.ok(!(key in codex.title), `cle interdite dans title: ${key}`);
  }
  assert.equal(codex.title.size, 68);
  assert.equal(codex.title.y_pct, 22);
});

test('render : les cles sont exactement celles du schema', () => {
  const codex = buildCodexRender();
  assert.deepEqual(Object.keys(codex).sort(), [
    'canvas', 'fps', 'logo', 'look', 'schema_version', 'style', 'title', 'validated_by_magos',
  ]);
  assert.equal(codex.schema_version, 'sanguinala.render.codex.v1');
  assert.deepEqual(Object.keys(codex.look).sort(), ['bg_scale', 'degree', 'fg_scale', 'fg_y_pct']);
  assert.deepEqual(Object.keys(codex.logo).sort(), ['enabled', 'opacity', 'position', 'width_pct', 'x_pct', 'y_pct']);
});

test('render : bornes respectees (pas de valeur hors schema)', () => {
  const codex = buildCodexRender({
    canvas: '4:5',
    fps: 999,
    style: 'zoom',
    styleParams: { degree: -40, bg_scale: 5000, fg_scale: 0, fg_y_pct: 400 },
    overlay: { size: 900, y_pct: 250, outline_width: 99, line1_color: 'rouge' },
    logo: { width_pct: 300, opacity: 5, position: 'nulle_part' },
  });
  assert.equal(codex.canvas, '9:16');
  assert.equal(codex.fps, 120);
  assert.equal(codex.style, 'blur');
  assert.equal(codex.look.degree, 0);
  assert.equal(codex.look.fg_scale, 10);
  assert.equal(codex.title.size, 200);
  assert.equal(codex.title.y_pct, 100);
  assert.equal(codex.title.line1_color, '#FFFFFF');
  assert.equal(codex.logo.width_pct, 60);
  assert.equal(codex.logo.opacity, 1);
  assert.equal(codex.logo.position, 'centered');
});

test('postprod : ordre fige glow -> caption -> lut -> fade', () => {
  const codex = buildCodexPostprod({});
  assert.deepEqual(codex.order, PP2_ORDER);
  assert.deepEqual(PP2_ORDER, ['glow', 'caption', 'lut', 'fade']);
  assert.equal(codex.schema_version, 'sanguinala.postprod.codex.v1');
});

test('postprod : bornes glow / lut / fade', () => {
  const codex = buildCodexPostprod({
    glow: { enabled: true, mode: 'split_scene', sigma: 99, opacity: 3 },
    lut: { enabled: true, profile: 'profil_bidon' },
    fadeOut: { mode: 'flash', duration_sec: 40 },
  });
  assert.equal(codex.glow.mode, 'scene');
  assert.equal(codex.glow.sigma, 30);
  assert.equal(codex.glow.opacity, 0.6);
  assert.equal(codex.lut.profile, 'hdr_imperator');
  assert.equal(codex.fade_out.mode, 'darken');
  assert.equal(codex.fade_out.duration_sec, 10);
});

test('postprod : sous-titres (schema dev11.caption.style.v1)', () => {
  const caption = projectCaption({ size: 90, position: { y_pct: 84 }, color: '#FFD700' }, '16:9');
  assert.equal(caption.schema_version, 'dev11.caption.style.v1');
  assert.equal(caption.size, 90);
  assert.equal(caption.position.y_pct, 84);
  assert.equal(caption.position.x_pct, 50);
  assert.equal(caption.color, '#FFD700');
  assert.equal(caption.canvas, '16:9');
  assert.equal(caption.motion, DEFAULT_POSTPROD.caption.motion);
});

test('signature : validated_by_magos suit la case de la review', () => {
  assert.equal(buildCodexRender({ validated: false }).validated_by_magos, false);
  assert.equal(buildCodexPostprod({ validated: false }).validated_by_magos, false);
  assert.equal(buildCodexRender({ validated: true }).validated_by_magos, true);
});

test('pack_token : absent si inconnu, present sinon', () => {
  assert.ok(!('pack_token' in buildCodexRender({ packToken: null })));
  assert.equal(buildCodexRender({ packToken: 'e99bd523' }).pack_token, 'e99bd523');
  assert.equal(buildCodexPostprod({ packToken: 'e99bd523' }).pack_token, 'e99bd523');
});

test('serialisation : JSON lisible, termine par un saut de ligne', () => {
  const text = stringifyCodex(buildCodexPostprod({}));
  assert.ok(text.endsWith('\n'));
  assert.deepEqual(JSON.parse(text).order, PP2_ORDER);
  assert.ok(text.includes('\n  "glow"'));
});

test('logo : position connue seulement', () => {
  assert.equal(projectLogo({ position: 'top_right' }).position, 'top_right');
  assert.equal(projectLogo({ position: 'custom', x_pct: 12.5, y_pct: 88 }).x_pct, 12.5);
  assert.equal(projectLogo({}).enabled, false);
});

test('title : static_text (moteur) ne part pas dans le codex', () => {
  const title = projectTitle({ static_text: true, size: 70 });
  assert.ok(!('static_text' in title));
  assert.equal(Object.keys(title).length, 16);
});
