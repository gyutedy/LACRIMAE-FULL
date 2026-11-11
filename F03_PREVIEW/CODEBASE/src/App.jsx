import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Player } from '@remotion/player';
import { PurPackComposition } from './preview/_purPackComposition';
import {
  parsePurPack,
  parsePurPackMulti,
  expandSanguinalaPack,
  clipFileCandidates,
  normalizePurOverlayParams,
  normalizePurStyleParams,
  PUR_STYLE_VALUES,
} from './preview/bridgeClipper';

const CANVAS = {
  '9:16': { width: 1080, height: 1920 },
  '16:9': { width: 1920, height: 1080 },
  '1:1': { width: 1080, height: 1080 },
};

const field = { display: 'block', margin: '8px 0 4px', fontSize: 12, opacity: 0.8 };
const input = { width: '100%', background: '#16161c', color: '#eee', border: '1px solid #333', padding: 6 };
const btn = { background: '#222', color: '#eee', border: '1px solid #444', padding: '6px 10px', cursor: 'pointer' };
const slider = { width: '100%', accentColor: '#00ff88', cursor: 'pointer' };

function normalizeTitle(t) {
  const position = t.position || 'top';
  return {
    text: t.text || '',
    in: Number(t.in || 0),
    out: Number(t.out || 3),
    position,
    y_pct: t.y_pct ?? (position === 'bottom' ? 82 : position === 'center' ? 50 : 8),
    size: t.size ?? 64,
    color: t.color || '#FFFFFF',
  };
}

function defaultLook(style) {
  return {
    style: style || 'blur',
    style_params: { degree: 24, bg_scale: 118, fg_scale: 72, fg_y_pct: 62, scale: 130, offset_x_pct: 0, offset_y_pct: -6 },
  };
}

async function resolveClipFile(angleId) {
  const candidates = clipFileCandidates(angleId);
  for (const path of candidates) {
    try {
      const head = await fetch(`./${path}`, { method: 'HEAD' });
      if (head.ok) return path;
    } catch {
      /* HEAD absent */
    }
    try {
      const ranged = await fetch(`./${path}`, { headers: { Range: 'bytes=0-0' } });
      if (ranged.ok || ranged.status === 206) return path;
    } catch {
      /* Range absent */
    }
  }
  return candidates[0];
}

export default function App() {
  const [packs, setPacks] = useState([]);
  const [clipFiles, setClipFiles] = useState([]);
  const [manifest, setManifest] = useState(null);
  const [entryIndex, setEntryIndex] = useState(0);
  const [canvas, setCanvas] = useState('9:16');
  const [style, setStyle] = useState('blur');
  const [error, setError] = useState(null);
  const [saveMsg, setSaveMsg] = useState('');
  const playerRef = useRef(null);
  const stageRef = useRef(null);
  const lastClickRef = useRef({ t: 0, x: 0, y: 0 });
  const dragRef = useRef(null);
  const [logoPending, setLogoPending] = useState(null);
  const [wmCursor, setWmCursor] = useState(false);
  const [review, setReview] = useState({
    titles: [],
    watermark: { enabled: false, images: [] },
    look: defaultLook('blur'),
  });

  const size = CANVAS[canvas] || CANVAS['9:16'];
  const overlay = normalizePurOverlayParams(manifest?.narrative?.overlay?.style_params);
  const styleParams = normalizePurStyleParams(manifest?.style_params, manifest?.style || style);
  const wmImages = review.watermark?.images || [];

  const rebuild = (nextPacks, nextStyle, nextCanvas, styleParamsOverride, overlayOverride, nextClipFiles) => {
    if (!nextPacks.length) {
      setManifest(null);
      return;
    }
    const files = (nextClipFiles && nextClipFiles.length)
      ? nextClipFiles
      : nextPacks.map((p, i) => clipFileCandidates(p.identite?.angle_id || p.pack_id || `clip${i + 1}`)[0]);
    const parsed = nextPacks.length === 1
      ? parsePurPack(nextPacks[0], { fps: 30, canvas: nextCanvas, clipFiles: [files[0]], style: nextStyle, styleParams: styleParamsOverride, overlayParams: overlayOverride })
      : parsePurPackMulti(nextPacks, {
          fps: 30,
          canvas: nextCanvas,
          clipFiles: files,
          style: nextStyle,
          styleParams: styleParamsOverride,
          overlayParams: overlayOverride,
        });
    setManifest(parsed);
    setError(parsed.style_unknown ? `Style refuse : ${parsed.style_source}. Choisis blur / reframing.` : null);
  };

  const handleLogoClick = (e) => {
    if (dragRef.current) return;
    const now = Date.now();
    const last = lastClickRef.current;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX;
    const y = e.clientY;
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
            {
              src: 'wm.png',
              position: 'custom',
              x_pct: logoPending.x_pct,
              y_pct: logoPending.y_pct,
              opacity: 0.7,
              width_pct: 18,
            },
          ],
        },
      }));
    }
    setLogoPending(null);
  };

  const pctFromEvent = (e) => {
    const rect = stageRef.current ? stageRef.current.getBoundingClientRect() : e.currentTarget.getBoundingClientRect();
    return {
      x_pct: Math.min(100, Math.max(0, Math.round(((e.clientX - rect.left) / rect.width) * 1000) / 10)),
      y_pct: Math.min(100, Math.max(0, Math.round(((e.clientY - rect.top) / rect.height) * 1000) / 10)),
    };
  };

  const onWmPointerDown = (e, i) => {
    e.stopPropagation();
    e.preventDefault();
    e.currentTarget.setPointerCapture(e.pointerId);
    dragRef.current = { i };
    setWmCursor(true);
  };

  const onWmPointerMove = (e) => {
    if (!dragRef.current) return;
    const { i } = dragRef.current;
    const next = pctFromEvent(e);
    setReview((s) => {
      const images = [...((s.watermark && s.watermark.images) || [])];
      if (!images[i]) return s;
      images[i] = { ...images[i], position: 'custom', ...next };
      return { ...s, watermark: { ...(s.watermark || {}), enabled: true, images } };
    });
  };

  const onWmPointerUp = (e) => {
    if (!dragRef.current) return;
    e.stopPropagation();
    dragRef.current = null;
    setWmCursor(false);
  };

  const loadPacks = async (loaded, nextStyle) => {
    const expanded = loaded.flatMap((p) => expandSanguinalaPack(p));
    const files = await Promise.all(expanded.map((p) => resolveClipFile(p.identite?.angle_id || 'A01')));
    setPacks(expanded);
    setClipFiles(files);
    setEntryIndex(0);
    const first = expanded[0] || {};
    const sp = first.style_pack || {};
    const st = sp.style || nextStyle || style;
    setStyle(st);
    setReview((s) => ({
      ...s,
      titles: (sp.titles || s.titles || []).map(normalizeTitle),
      watermark: sp.watermark || s.watermark,
      look: {
        style: st,
        style_params: { ...(defaultLook(st).style_params), ...(sp.look?.style_params || {}), ...(sp.style_params || {}) },
      },
    }));
    rebuild(expanded, st, canvas, sp.look?.style_params || sp.style_params, undefined, files);
  };

  const onFiles = async (fileList) => {
    const files = Array.from(fileList || []);
    const loaded = [];
    for (const file of files) {
      loaded.push(JSON.parse(await file.text()));
    }
    await loadPacks(loaded, style);
  };

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch('./pack.json');
        if (!res.ok || cancelled) return;
        const data = await res.json();
        if (cancelled || !data) return;
        loadPacks([data], (data.style_pack || {}).style);
      } catch {
        /* pack.json optionnel — drop manuel */
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const patchStyle = (partial) => {
    const next = { ...styleParams, ...partial };
    setReview((s) => ({
      ...s,
      look: { style, style_params: next },
    }));
    rebuild(packs, style, canvas, next, overlay, clipFiles);
  };

  const patchOverlay = (partial) => {
    const next = { ...overlay, ...partial };
    rebuild(packs, style, canvas, styleParams, next, clipFiles);
  };

  const patchTitle = (i, partial) => {
    setReview((s) => {
      const titles = [...(s.titles || [])];
      titles[i] = normalizeTitle({ ...(titles[i] || {}), ...partial });
      return { ...s, titles };
    });
  };

  const addTitle = () => {
    setReview((s) => ({
      ...s,
      titles: [...(s.titles || []), normalizeTitle({ text: 'TITRE', in: 0, out: 3, position: 'top' })],
    }));
  };

  const removeTitle = (i) => {
    setReview((s) => ({ ...s, titles: (s.titles || []).filter((_, idx) => idx !== i) }));
  };

  const patchWm = (i, partial) => {
    setReview((s) => {
      const images = [...((s.watermark && s.watermark.images) || [])];
      if (!images[i]) return s;
      images[i] = { ...images[i], ...partial };
      return { ...s, watermark: { ...(s.watermark || {}), enabled: true, images } };
    });
  };

  const removeWm = (i) => {
    setReview((s) => {
      const images = ((s.watermark && s.watermark.images) || []).filter((_, idx) => idx !== i);
      return { ...s, watermark: { ...(s.watermark || {}), enabled: images.length > 0, images } };
    });
  };

  const exportReview = async () => {
    setSaveMsg('');
    const payload = {
      style_pack: {
        titles: review.titles,
        watermark: review.watermark,
        look: { style, style_params: styleParams },
      },
    };
    const text = JSON.stringify(payload, null, 2);
    const blob = new Blob([text], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'sanguinala_review.json';
    a.click();
    try {
      const res = await fetch('/api/save-review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: text,
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok || !body.ok) setError('W1: save review echoue — JSON non ecrit');
      else {
        setError(null);
        setSaveMsg(`W1 : ${body.path}`);
      }
    } catch {
      setError('W1: save review indisponible — JSON telecharge seulement');
    }
  };

  const durationInFrames = Math.max(1, Number(manifest?.entries?.[entryIndex]?.duration_seconds || manifest?.duration_seconds || 30) * 30);

  const composition = useMemo(() => (props) => (
    <PurPackComposition {...props} purManifest={manifest} entryIndex={entryIndex} />
  ), [manifest, entryIndex]);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#0b0b0f', color: '#eee', fontFamily: 'sans-serif' }}>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        {manifest ? (
          <div
            ref={stageRef}
            style={{ position: 'relative', width: '100%', maxWidth: 300, cursor: wmCursor ? 'grabbing' : 'crosshair' }}
            title="Double-cliquez pour poser le logo. Glissez le watermark."
            onClick={handleLogoClick}
          >
            <Player
              ref={playerRef}
              component={composition}
              durationInFrames={durationInFrames}
              fps={30}
              compositionWidth={size.width}
              compositionHeight={size.height}
              style={{
                width: '100%',
                maxWidth: 300,
                aspectRatio: `${size.width} / ${size.height}`,
                borderRadius: 12,
                overflow: 'hidden',
                boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
              }}
              controls
              autoPlay
              loop
            />
            {(review.titles || []).map((t, i) => (
              <div
                key={`title_${i}`}
                style={{
                  position: 'absolute',
                  left: '50%',
                  top: `${t.y_pct}%`,
                  transform: 'translate(-50%, -50%)',
                  zIndex: 20,
                  pointerEvents: 'none',
                  color: t.color,
                  fontSize: Math.max(12, Math.round((t.size || 64) * 0.22)),
                  fontWeight: 900,
                  textAlign: 'center',
                  textShadow: '0 2px 8px #000',
                  whiteSpace: 'nowrap',
                  maxWidth: '92%',
                }}
              >
                {t.text}
              </div>
            ))}
            {wmImages.map((img, i) => (
              <div
                key={`wm_${i}`}
                onPointerDown={(e) => onWmPointerDown(e, i)}
                onPointerMove={onWmPointerMove}
                onPointerUp={onWmPointerUp}
                onClick={(e) => e.stopPropagation()}
                style={{
                  position: 'absolute',
                  left: `${img.x_pct ?? 50}%`,
                  top: `${img.y_pct ?? 50}%`,
                  transform: 'translate(-50%, -50%)',
                  zIndex: 25,
                  width: `${img.width_pct || 18}%`,
                  opacity: img.opacity ?? 0.7,
                  cursor: 'grab',
                  pointerEvents: 'auto',
                }}
              >
                <div style={{
                  width: '100%',
                  aspectRatio: '1',
                  borderRadius: '50%',
                  border: '3px solid #00ff88',
                  background: 'rgba(0,0,0,0.45)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#00ff88',
                  fontSize: 11,
                  fontWeight: 800,
                }}>
                  WM
                </div>
              </div>
            ))}
            {logoPending && (
              <div
                style={{
                  position: 'absolute',
                  left: `${logoPending.x_pct}%`,
                  top: `${logoPending.y_pct}%`,
                  transform: 'translate(-50%, -50%)',
                  zIndex: 30,
                  pointerEvents: 'none',
                }}
              >
                <div style={{
                  width: 44, height: 44, borderRadius: '50%',
                  border: '3px solid #00ff88', backgroundColor: 'rgba(0,0,0,0.4)',
                }} />
              </div>
            )}
            {logoPending && (
              <div style={{
                position: 'absolute', inset: 0, display: 'flex',
                alignItems: 'center', justifyContent: 'center', zIndex: 40,
              }}>
                <div style={{
                  background: '#141414', border: '1px solid #00ff88', borderRadius: 10,
                  padding: '16px 20px', textAlign: 'center',
                }}>
                  <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 10 }}>
                    Poser le logo ici ?
                  </div>
                  <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
                    <button type="button" style={btn} onClick={() => confirmLogoPlacement(true)}>Oui</button>
                    <button type="button" style={btn} onClick={() => confirmLogoPlacement(false)}>Non</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ opacity: 0.7 }}>Depose un production_pack_pur_*.json</div>
        )}
      </div>
      <aside style={{ width: 380, padding: 16, borderLeft: '1px solid #222', overflow: 'auto' }}>
        <h1 style={{ fontSize: 18 }}>F03 PREVIEW — LOOK + review W1/T1</h1>
        <p style={{ fontSize: 12, opacity: 0.7 }}>
          Titres editables. Blur fg_scale. Curseur watermark (double-clic puis glisser). Zero zoom. Pas de ranking/reveal/hybrid.
        </p>
        <input type="file" accept="application/json" multiple onChange={(e) => onFiles(e.target.files)} />
        {error && <p style={{ color: '#ff8866' }}>{error}</p>}
        {saveMsg && <p style={{ color: '#00ff88', fontSize: 12 }}>{saveMsg}</p>}

        <label style={field}>Canvas</label>
        <select style={input} value={canvas} onChange={(e) => { setCanvas(e.target.value); rebuild(packs, style, e.target.value, styleParams, overlay, clipFiles); }}>
          <option value="9:16">9:16</option>
          <option value="16:9">16:9</option>
          <option value="1:1">1:1</option>
        </select>

        <label style={field}>Style</label>
        <select style={input} value={style} onChange={(e) => { setStyle(e.target.value); setReview((s) => ({ ...s, look: { ...s.look, style: e.target.value } })); rebuild(packs, e.target.value, canvas, undefined, overlay, clipFiles); }}>
          {PUR_STYLE_VALUES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>

        {packs.length > 1 && (
          <div>
            <button type="button" style={btn} onClick={() => setEntryIndex((i) => Math.max(0, i - 1))}>prev</button>
            <span> video {entryIndex + 1}/{packs.length} </span>
            <button type="button" style={btn} onClick={() => setEntryIndex((i) => Math.min(packs.length - 1, i + 1))}>next</button>
          </div>
        )}

        {style === 'blur' && (
          <fieldset>
            <legend>blur — video claire</legend>
            <label style={field}>degree {styleParams.degree}</label>
            <input style={slider} type="range" min="4" max="48" value={styleParams.degree} onChange={(e) => patchStyle({ degree: Number(e.target.value) })} />
            <label style={field}>fg_scale (taille video claire) {styleParams.fg_scale}</label>
            <input style={slider} type="range" min="30" max="100" value={styleParams.fg_scale} onChange={(e) => patchStyle({ fg_scale: Number(e.target.value) })} />
            <label style={field}>fg_y_pct {styleParams.fg_y_pct}</label>
            <input style={slider} type="range" min="20" max="80" value={styleParams.fg_y_pct} onChange={(e) => patchStyle({ fg_y_pct: Number(e.target.value) })} />
            <label style={field}>bg_scale {styleParams.bg_scale}</label>
            <input style={slider} type="range" min="100" max="160" value={styleParams.bg_scale} onChange={(e) => patchStyle({ bg_scale: Number(e.target.value) })} />
          </fieldset>
        )}
        {style === 'reframing' && (
          <fieldset>
            <legend>reframing (fixe)</legend>
            <label style={field}>scale {styleParams.scale}</label>
            <input style={slider} type="range" min="100" max="180" value={styleParams.scale} onChange={(e) => patchStyle({ scale: Number(e.target.value) })} />
            <label style={field}>offset_y {styleParams.offset_y_pct}</label>
            <input style={slider} type="range" min="-30" max="30" value={styleParams.offset_y_pct} onChange={(e) => patchStyle({ offset_y_pct: Number(e.target.value) })} />
          </fieldset>
        )}

        <fieldset>
          <legend>overlay pack</legend>
          <label style={field}>size</label>
          <input style={input} type="number" value={overlay.size} onChange={(e) => patchOverlay({ size: Number(e.target.value) })} />
          <label style={field}>y_pct</label>
          <input style={input} type="number" value={overlay.y_pct} onChange={(e) => patchOverlay({ y_pct: Number(e.target.value) })} />
        </fieldset>

        <fieldset>
          <legend>T1 titres (editables)</legend>
          {(review.titles || []).length === 0 && <p style={{ fontSize: 12, opacity: 0.6 }}>Aucun titre. Ajoute-en un.</p>}
          {(review.titles || []).map((t, i) => (
            <div key={i} style={{ borderBottom: '1px solid #222', paddingBottom: 8, marginBottom: 8 }}>
              <input style={input} type="text" value={t.text} onChange={(e) => patchTitle(i, { text: e.target.value })} />
              <label style={field}>place {t.position} / y {t.y_pct}%</label>
              <select style={input} value={t.position} onChange={(e) => patchTitle(i, { position: e.target.value, y_pct: e.target.value === 'bottom' ? 82 : e.target.value === 'center' ? 50 : 8 })}>
                <option value="top">top</option>
                <option value="center">center</option>
                <option value="bottom">bottom</option>
              </select>
              <input style={slider} type="range" min="4" max="90" value={t.y_pct} onChange={(e) => patchTitle(i, { y_pct: Number(e.target.value) })} />
              <label style={field}>taille {t.size}px</label>
              <input style={slider} type="range" min="24" max="160" value={t.size} onChange={(e) => patchTitle(i, { size: Number(e.target.value) })} />
              <label style={field}>in / out</label>
              <input style={input} type="number" value={t.in} onChange={(e) => patchTitle(i, { in: Number(e.target.value) })} />
              <input style={input} type="number" value={t.out} onChange={(e) => patchTitle(i, { out: Number(e.target.value) })} />
              <button type="button" style={{ ...btn, marginTop: 6 }} onClick={() => removeTitle(i)}>retirer</button>
            </div>
          ))}
          <button type="button" style={btn} onClick={addTitle}>ajouter titre</button>
        </fieldset>

        <fieldset>
          <legend>W1 watermark curseur</legend>
          <p style={{ fontSize: 12 }}>Double-clic sur la video, Oui, puis glisse le cercle WM.</p>
          <p style={{ fontSize: 12 }}>enabled={String(!!review.watermark?.enabled)} images={wmImages.length}</p>
          {wmImages.map((img, i) => (
            <div key={i} style={{ fontSize: 12, marginBottom: 8 }}>
              <div>{img.src} {img.x_pct},{img.y_pct}</div>
              <label style={field}>taille {img.width_pct || 18}%</label>
              <input style={slider} type="range" min="6" max="40" value={img.width_pct || 18} onChange={(e) => patchWm(i, { width_pct: Number(e.target.value) })} />
              <label style={field}>opacite {img.opacity ?? 0.7}</label>
              <input style={slider} type="range" min="0.1" max="1" step="0.05" value={img.opacity ?? 0.7} onChange={(e) => patchWm(i, { opacity: Number(e.target.value) })} />
              <button type="button" style={btn} onClick={() => removeWm(i)}>retirer</button>
            </div>
          ))}
          <button type="button" style={{ ...btn, marginTop: 8 }} onClick={exportReview}>
            Export JSON review unique
          </button>
        </fieldset>
      </aside>
    </div>
  );
}
