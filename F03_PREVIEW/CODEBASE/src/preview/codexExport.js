/**
 * Projection review -> codex.
 *
 * La review ne produit QUE les deux fichiers que les fregates consomment :
 *   - codex_render.json    (F01_LOOK / Remotion : style, look, titre, logo)
 *   - codex_postprod.json  (F03_POSTPROD : glow, caption, lut, fade)
 *
 * Regles gravees :
 *   - le codex porte un STYLE, jamais un texte de titre (les textes viennent
 *     du pack) ;
 *   - l'ordre post-prod est fige : glow -> caption -> lut -> fade (PP2) ;
 *   - aucun champ hors schema : `tools/codex.py check` refuse l'inconnu.
 */

export const RENDER_SCHEMA = 'sanguinala.render.codex.v1';
export const POSTPROD_SCHEMA = 'sanguinala.postprod.codex.v1';
export const PP2_ORDER = ['glow', 'caption', 'lut', 'fade'];

export const LUT_PROFILES = [
  'hdr_imperator',
  'cinematic_hyper_detail',
  'realistic_aurea',
  'old_main_noctis',
  'balanced',
];

export const DEFAULT_POSTPROD = {
  caption: {
    schema_version: 'dev11.caption.style.v1',
    id: 's1',
    font: 'Montserrat-ExtraBold.ttf',
    position: { x_pct: 50, y_pct: 78 },
    size: 72,
    color: '#FFFFFF',
    outline: { width: 4, color: '#000000' },
    glow: { intensity: 1.2, color: '#FFFFFF' },
    motion: 'pop-in',
    motion_speed: 1,
    canvas: '9:16',
  },
  glow: { enabled: true, mode: 'scene', sigma: 12, opacity: 0.35 },
  lut: { enabled: true, profile: 'hdr_imperator' },
  fade_out: { mode: 'darken', duration_sec: 1.5 },
};

const clamp = (v, lo, hi, fallback) => {
  const n = Number(v);
  if (!Number.isFinite(n)) return fallback;
  return Math.min(hi, Math.max(lo, Math.round(n * 1000) / 1000));
};

const hexa = (v, fallback) => (typeof v === 'string' && /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(v) ? v : fallback);

/** Le titre ne garde QUE le style : le texte reste dans le pack. */
export function projectTitle(overlay = {}) {
  return {
    size: clamp(overlay.size, 8, 200, 68),
    x_pct: clamp(overlay.x_pct, 0, 100, 50),
    y_pct: clamp(overlay.y_pct, 0, 100, 22),
    line1_color: hexa(overlay.line1_color, '#FFFFFF'),
    line2_color: hexa(overlay.line2_color, '#FFD700'),
    font_family: typeof overlay.font_family === 'string' && overlay.font_family.trim()
      ? overlay.font_family
      : 'Arial Black, Impact',
    uppercase: Boolean(overlay.uppercase),
    outline_width: clamp(overlay.outline_width, 0, 40, 3),
    outline_color: hexa(overlay.outline_color, '#000000'),
    bg_enabled: Boolean(overlay.bg_enabled),
    bg_color: hexa(overlay.bg_color, '#000000'),
    bg_opacity: clamp(overlay.bg_opacity, 0, 1, 0.65),
    box_radius: clamp(overlay.box_radius, 0, 100, 10),
    box_padding: clamp(overlay.box_padding, 0, 100, 14),
    auto_fit: overlay.auto_fit !== false,
    min_size: clamp(overlay.min_size, 8, 200, 28),
  };
}

/** Le logo est dessine par le MOTEUR (jamais par la post-prod). */
export function projectLogo(logo = {}) {
  const positions = [
    'top_left', 'top_center', 'top_right',
    'centered', 'bottom_left', 'bottom_center', 'bottom_right', 'custom',
  ];
  return {
    enabled: Boolean(logo.enabled),
    width_pct: clamp(logo.width_pct, 1, 60, 15),
    position: positions.includes(logo.position) ? logo.position : 'centered',
    x_pct: clamp(logo.x_pct, 0, 100, 50),
    y_pct: clamp(logo.y_pct, 0, 100, 50),
    opacity: clamp(logo.opacity, 0, 1, 0.8),
  };
}

export function projectLook(styleParams = {}) {
  return {
    degree: clamp(styleParams.degree, 0, 120, 15),
    bg_scale: clamp(styleParams.bg_scale, 100, 300, 118),
    fg_scale: clamp(styleParams.fg_scale, 10, 100, 57),
    fg_y_pct: clamp(styleParams.fg_y_pct, 0, 100, 50),
  };
}

export function buildCodexRender({
  canvas = '9:16',
  fps = 30,
  style = 'blur',
  styleParams = {},
  overlay = {},
  logo = {},
  packToken = null,
  validated = true,
} = {}) {
  const codex = {
    schema_version: RENDER_SCHEMA,
    canvas: ['9:16', '16:9', '1:1'].includes(canvas) ? canvas : '9:16',
    fps: clamp(fps, 1, 120, 30),
    style: style === 'reframing' ? 'reframing' : 'blur',
    look: projectLook(styleParams),
    title: projectTitle(overlay),
    logo: projectLogo(logo),
    validated_by_magos: Boolean(validated),
  };
  if (packToken) codex.pack_token = String(packToken);
  return codex;
}

export function projectCaption(caption = {}, canvas = '9:16') {
  const base = { ...DEFAULT_POSTPROD.caption, ...(caption || {}) };
  const position = { ...DEFAULT_POSTPROD.caption.position, ...(base.position || {}) };
  const outline = { ...DEFAULT_POSTPROD.caption.outline, ...(base.outline || {}) };
  const glow = { ...DEFAULT_POSTPROD.caption.glow, ...(base.glow || {}) };
  return {
    schema_version: 'dev11.caption.style.v1',
    id: typeof base.id === 'string' && base.id ? base.id : 's1',
    font: typeof base.font === 'string' && base.font ? base.font : DEFAULT_POSTPROD.caption.font,
    position: {
      x_pct: clamp(position.x_pct, 0, 100, 50),
      y_pct: clamp(position.y_pct, 0, 100, 78),
    },
    size: clamp(base.size, 12, 240, 72),
    color: hexa(base.color, '#FFFFFF'),
    outline: {
      width: clamp(outline.width, 0, 24, 4),
      color: hexa(outline.color, '#000000'),
    },
    glow: {
      intensity: clamp(glow.intensity, 0, 5, 1.2),
      color: hexa(glow.color, '#FFFFFF'),
    },
    motion: ['pop-in', 'bounce', 'slide'].includes(base.motion) ? base.motion : 'pop-in',
    motion_speed: clamp(base.motion_speed, 0.25, 3, 1),
    canvas: ['9:16', '16:9', '1:1'].includes(canvas) ? canvas : '9:16',
  };
}

export function buildCodexPostprod({
  caption = {},
  glow = {},
  lut = {},
  fadeOut = {},
  canvas = '9:16',
  packToken = null,
  validated = true,
} = {}) {
  const g = { ...DEFAULT_POSTPROD.glow, ...(glow || {}) };
  const l = { ...DEFAULT_POSTPROD.lut, ...(lut || {}) };
  const f = { ...DEFAULT_POSTPROD.fade_out, ...(fadeOut || {}) };
  const codex = {
    schema_version: POSTPROD_SCHEMA,
    order: [...PP2_ORDER],
    caption: projectCaption(caption, canvas),
    glow: {
      enabled: Boolean(g.enabled),
      mode: g.mode === 'subject' ? 'subject' : 'scene',
      sigma: clamp(g.sigma, 4, 30, 12),
      opacity: clamp(g.opacity, 0, 0.6, 0.35),
    },
    lut: {
      enabled: Boolean(l.enabled),
      profile: LUT_PROFILES.includes(l.profile) ? l.profile : 'hdr_imperator',
    },
    fade_out: {
      mode: f.mode === 'black' ? 'black' : 'darken',
      duration_sec: clamp(f.duration_sec, 0.1, 10, 1.5),
    },
    validated_by_magos: Boolean(validated),
  };
  if (packToken) codex.pack_token = String(packToken);
  return codex;
}

/** Le fichier postprod est lisible par l'humain : ordre en clair, puis passes. */
export function stringifyCodex(codex) {
  return `${JSON.stringify(codex, null, 2)}\n`;
}
