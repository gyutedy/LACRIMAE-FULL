import React, { useMemo, useRef, useState } from 'react';
import { Player } from '@remotion/player';
import { PurPackComposition } from './preview/_purPackComposition';
import {
  parsePurPack,
  parsePurPackMulti,
  normalizePurOverlayParams,
  normalizePurStyleParams,
  PUR_STYLE_VALUES,
} from './preview/bridgeClipper';

const CANVAS = {
  '9:16': { width: 1080, height: 1920 },
  '16:9': { width: 1920, height: 1080 },
  '1:1': { width: 1080, height: 1080 },
};

export default function App() {
  const [packs, setPacks] = useState([]);
  const [manifest, setManifest] = useState(null);
  const [entryIndex, setEntryIndex] = useState(0);
  const [canvas, setCanvas] = useState('9:16');
  const [style, setStyle] = useState('blur');
  const [error, setError] = useState(null);
  const playerRef = useRef(null);
  const lastClickRef = useRef({ t: 0, x: 0, y: 0 });
  const [logoPending, setLogoPending] = useState(null);
  const [review, setReview] = useState({
    titles: [],
    watermark: { enabled: false, images: [] },
    look: { style: 'blur' },
  });

  const size = CANVAS[canvas] || CANVAS['9:16'];
  const overlay = normalizePurOverlayParams(manifest?.narrative?.overlay?.style_params);
  const styleParams = normalizePurStyleParams(manifest?.style_params, manifest?.style || style);

  const rebuild = (nextPacks, nextStyle, nextCanvas, styleParamsOverride, overlayOverride) => {
    if (!nextPacks.length) {
      setManifest(null);
      return;
    }
    const parsed = nextPacks.length === 1
      ? parsePurPack(nextPacks[0], { fps: 30, canvas: nextCanvas, clipFiles: [`clips/pur_${nextPacks[0].identite?.angle_id || 'A01'}.mp4`], style: nextStyle, styleParams: styleParamsOverride, overlayParams: overlayOverride })
      : parsePurPackMulti(nextPacks, {
          fps: 30,
          canvas: nextCanvas,
          clipFiles: nextPacks.map((p, i) => `clips/pur_${p.identite?.angle_id || p.pack_id || `clip${i + 1}`}.mp4`),
          style: nextStyle,
          styleParams: styleParamsOverride,
          overlayParams: overlayOverride,
        });
    setManifest(parsed);
    setError(parsed.style_unknown ? `Style refuse : ${parsed.style_source}. Choisis blur / reframing.` : null);
  };

  const handleLogoClick = (e) => {
    const now = Date.now();
    const last = lastClickRef.current;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX, y = e.clientY;
    const isDouble = now - last.t < 350 && Math.abs(x - last.x) < 12 && Math.abs(y - last.y) < 12;
    lastClickRef.current = { t: now, x, y };
    if (!isDouble) return;
    const xPct = Math.round(((x - rect.left) / rect.width) * 1000) / 10;
    const yPct = Math.round(((y - rect.top) / rect.height) * 1000) / 10;
    setLogoPending({ x_pct: xPct, y_pct: yPct });
  };

  const confirmLogoPlacement = (ok) => {
    if (ok && logoPending) {
      setReview((s) => ({
        ...s,
        watermark: {
          ...(s.watermark || {}),
          enabled: true,
          images: [
            ...((s.watermark && s.watermark.images) || []),
            { src: 'wm.png', position: 'custom', x_pct: logoPending.x_pct, y_pct: logoPending.y_pct, opacity: 0.6 },
          ],
        },
      }));
    }
    setLogoPending(null);
  };

  const onFiles = async (fileList) => {
    const files = Array.from(fileList || []);
    const loaded = [];
    for (const file of files) {
      loaded.push(JSON.parse(await file.text()));
    }
    setPacks(loaded);
    setEntryIndex(0);
    const first = loaded[0] || {};
    const sp = first.style_pack || {};
    setReview((s) => ({
      ...s,
      titles: sp.titles || s.titles,
      watermark: sp.watermark || s.watermark,
      look: { style: sp.style || style },
    }));
    rebuild(loaded, sp.style || style, canvas);
  };

  const patchStyle = (partial) => {
    const next = { ...styleParams, ...partial };
    rebuild(packs, style, canvas, next, overlay);
  };

  const patchOverlay = (partial) => {
    const next = { ...overlay, ...partial };
    rebuild(packs, style, canvas, styleParams, next);
  };

  const durationInFrames = Math.max(1, Number(manifest?.entries?.[entryIndex]?.duration_seconds || manifest?.duration_seconds || 30) * 30);

  const composition = useMemo(() => (props) => (
    <PurPackComposition {...props} purManifest={manifest} entryIndex={entryIndex} />
  ), [manifest, entryIndex]);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#0b0b0f', color: '#eee', fontFamily: 'sans-serif' }}>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        {manifest ? (
          <div style={{ position: 'relative' }} title="Double-cliquez pour poser le logo ici" onClick={handleLogoClick}>
            <Player
              ref={playerRef}
              component={composition}
              durationInFrames={durationInFrames}
              fps={30}
              compositionWidth={size.width}
              compositionHeight={size.height}
              style={{ maxHeight: '90vh', width: 'auto' }}
              controls
            />
            {logoPending && (
              <div
                style={{
                  position: 'absolute',
                  left: `${logoPending.x_pct}%`,
                  top: `${logoPending.y_pct}%`,
                  transform: 'translate(-50%, -50%)',
                  zIndex: 30,
                }}
              >
                <div style={{
                  width: '44px', height: '44px', borderRadius: '50%',
                  border: '3px solid #00ff88', backgroundColor: 'rgba(0,0,0,0.4)',
                  pointerEvents: 'none',
                }} />
              </div>
            )}
            {logoPending && (
              <div style={{
                position: 'absolute', inset: 0, display: 'flex',
                alignItems: 'center', justifyContent: 'center', zIndex: 40,
              }}>
                <div style={{
                  background: '#141414', border: '1px solid #00ff88', borderRadius: '10px',
                  padding: '16px 20px', textAlign: 'center',
                }}>
                  <div style={{ fontSize: '15px', fontWeight: 700, marginBottom: '10px' }}>
                    Poser le logo ici ?
                  </div>
                  <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                    <button type="button" onClick={() => confirmLogoPlacement(true)}>Oui</button>
                    <button type="button" onClick={() => confirmLogoPlacement(false)}>Non</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ opacity: 0.7 }}>Depose un production_pack_pur_*.json</div>
        )}
      </div>
      <aside style={{ width: 360, padding: 16, borderLeft: '1px solid #222', overflow: 'auto' }}>
        <h1 style={{ fontSize: 18 }}>F03 PREVIEW — SANGUINALA LOOK + W1</h1>
        <p style={{ fontSize: 12, opacity: 0.7 }}>blur / reframing. Zero zoom. Clic/double-clic logo (dev8). Titres pack. Watermark JSON.</p>
        <input type="file" accept="application/json" multiple onChange={(e) => onFiles(e.target.files)} />
        {error && <p style={{ color: '#ff8866' }}>{error}</p>}

        <label>Canvas</label>
        <select value={canvas} onChange={(e) => { setCanvas(e.target.value); rebuild(packs, style, e.target.value, styleParams, overlay); }}>
          <option value="9:16">9:16</option>
          <option value="16:9">16:9</option>
          <option value="1:1">1:1</option>
        </select>

        <label>Style</label>
        <select value={style} onChange={(e) => { setStyle(e.target.value); rebuild(packs, e.target.value, canvas, undefined, overlay); }}>
          {PUR_STYLE_VALUES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>

        {packs.length > 1 && (
          <div>
            <button type="button" onClick={() => setEntryIndex((i) => Math.max(0, i - 1))}>prev</button>
            <span> video {entryIndex + 1}/{packs.length} </span>
            <button type="button" onClick={() => setEntryIndex((i) => Math.min(packs.length - 1, i + 1))}>next</button>
          </div>
        )}

        {style === 'blur' && (
          <fieldset>
            <legend>blur</legend>
            <label>degree <input type="number" value={styleParams.degree} onChange={(e) => patchStyle({ degree: Number(e.target.value) })} /></label>
            <label>fg_y_pct <input type="number" value={styleParams.fg_y_pct} onChange={(e) => patchStyle({ fg_y_pct: Number(e.target.value) })} /></label>
          </fieldset>
        )}
        {style === 'reframing' && (
          <fieldset>
            <legend>reframing (fixe)</legend>
            <label>scale <input type="number" value={styleParams.scale} onChange={(e) => patchStyle({ scale: Number(e.target.value) })} /></label>
            <label>offset_y <input type="number" value={styleParams.offset_y_pct} onChange={(e) => patchStyle({ offset_y_pct: Number(e.target.value) })} /></label>
          </fieldset>
        )}

        <fieldset>
          <legend>overlay</legend>
          <label>size <input type="number" value={overlay.size} onChange={(e) => patchOverlay({ size: Number(e.target.value) })} /></label>
          <label>y_pct <input type="number" value={overlay.y_pct} onChange={(e) => patchOverlay({ y_pct: Number(e.target.value) })} /></label>
        </fieldset>

        <fieldset>
          <legend>T1 titres (style_pack.titles)</legend>
          {(review.titles || []).length === 0 && <p style={{ fontSize: 12, opacity: 0.6 }}>Aucun titre pack.</p>}
          {(review.titles || []).map((t, i) => (
            <div key={i} style={{ fontSize: 12 }}>{t.text} [{t.in}-{t.out}] {t.position}</div>
          ))}
        </fieldset>

        <fieldset>
          <legend>W1 watermark</legend>
          <p style={{ fontSize: 12 }}>enabled={String(!!review.watermark?.enabled)} images={(review.watermark?.images || []).length}</p>
          {(review.watermark?.images || []).map((img, i) => (
            <div key={i} style={{ fontSize: 11 }}>{img.src} {img.position} {img.x_pct},{img.y_pct}</div>
          ))}
          <button
            type="button"
            onClick={() => {
              const blob = new Blob([JSON.stringify({ style_pack: { ...review, look: { style } } }, null, 2)], { type: 'application/json' });
              const a = document.createElement('a');
              a.href = URL.createObjectURL(blob);
              a.download = 'sanguinala_review.json';
              a.click();
            }}
          >
            Export JSON review unique
          </button>
        </fieldset>
      </aside>
    </div>
  );
}
