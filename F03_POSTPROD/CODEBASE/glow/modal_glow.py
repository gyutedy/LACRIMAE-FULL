#!/usr/bin/env python3
"""F03_POSTPROD/glow/modal_glow.py — fonction Modal : frame/clip + params → frame/clip glowed.

Pattern F07 : F03_POSTPROD/CODEBASE/caption/TRAVAIL/CODEBASE/modal_app.py
CDC §7.2 / Q2 / Q3. GL1 sigma 4–30 opacite 0–0.6. GL2 caption zone preservee.

Parametres : { "mode": "scene"|"subject", "sigma": 12, "opacity": 0.35 }
subject : rembg d'abord, repli mat rigide (log + pas de nouveau modele).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import modal

APP_NAME = "lacrimae-sanguinala-glow"
VOLUME_NAME = "lacrimae-sanguinala-glow"
VOLUME_MOUNT = "/data"
HERE = Path(__file__).resolve().parent

GL1_SIGMA = (4.0, 30.0)
GL1_OPACITY = (0.0, 0.6)
CAPTION_Y = 0.78
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("rembg", "onnxruntime", "pillow")
)

volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
app = modal.App(APP_NAME, image=image)


def check_gl1(params: dict) -> int:
    mode = params.get("mode", "scene")
    if mode not in ("scene", "subject"):
        print("GL1 FAIL: mode", mode)
        return 2
    sigma = float(params.get("sigma", 12))
    opacity = float(params.get("opacity", 0.35))
    if not (GL1_SIGMA[0] <= sigma <= GL1_SIGMA[1]):
        print("GL1 FAIL: sigma", sigma)
        return 2
    if not (GL1_OPACITY[0] <= opacity <= GL1_OPACITY[1]):
        print("GL1 FAIL: opacity", opacity)
        return 2
    return 0


def _ffmpeg(cmd: list[str]) -> subprocess.CompletedProcess:
    print("GLOW ffmpeg:", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, capture_output=True, text=True)


def _has_audio(path: Path) -> bool:
    r = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=index", "-of", "csv=p=0", str(path),
        ],
        capture_output=True,
        text=True,
    )
    return r.returncode == 0 and bool((r.stdout or "").strip())


def _try_rembg_mask(frame: Path, mask_png: Path) -> bool:
    try:
        from rembg import remove
        from PIL import Image
    except Exception as e:
        print("GLOW subject: rembg import FAIL, rigid mat fallback:", e)
        return False
    try:
        im = Image.open(frame).convert("RGBA")
        cut = remove(im)
        alpha = cut.split()[-1]
        mask = alpha.point(lambda p: 255 if p > 32 else 0)
        if mask.getextrema()[1] < 32:
            print("GLOW subject: rembg mask empty, rigid mat fallback")
            return False
        mask.save(mask_png)
        print("GLOW subject: rembg OK", mask_png)
        return True
    except Exception as e:
        print("GLOW subject: rembg FAIL, rigid mat fallback:", e)
        return False


def _scene_filter(sigma: float, opacity: float) -> str:
    w0 = 1.0 - opacity
    return (
        f"[0:v]split=4[o_mix][o_out][b][mask_src];"
        f"[b]gblur=sigma={sigma:.3f}[g];"
        f"[o_mix][g]mix=weights='{w0:.4f} {opacity:.4f}'[mixed];"
        f"[mask_src]format=gray,geq=lum='if(lt(Y,H*{CAPTION_Y}),255,0)'[capmask];"
        f"[o_out][mixed][capmask]maskedmerge[v]"
    )


def _subject_rigid_filter(sigma: float, opacity: float) -> str:
    w0 = 1.0 - opacity
    return (
        f"[0:v]split=4[o_mix][o_out][b][mask_src];"
        f"[b]gblur=sigma={sigma:.3f}[g];"
        f"[o_mix][g]mix=weights='{w0:.4f} {opacity:.4f}'[mixed];"
        f"[mask_src]format=gray,geq=lum='if(between(Y,0,H*{CAPTION_Y})*lt(sqrt((X-W/2)*(X-W/2)+(Y-H*0.42)*(Y-H*0.42)),if(lt(W,H),W,H)*0.28),255,0)',gblur=sigma=8[mask];"
        f"[o_out][mixed][mask]maskedmerge[v]"
    )


def _subject_rembg_filter(sigma: float, opacity: float) -> str:
    w0 = 1.0 - opacity
    return (
        f"[0:v]split=3[o_mix][o_out][b];"
        f"[b]gblur=sigma={sigma:.3f}[g];"
        f"[o_mix][g]mix=weights='{w0:.4f} {opacity:.4f}'[mixed];"
        f"[1:v]format=gray,geq=lum='if(lt(Y,H*{CAPTION_Y}),lum(X,Y),0)'[mask];"
        f"[o_out][mixed][mask]maskedmerge[v]"
    )


def _extract_frame(src: Path, dst: Path) -> int:
    dst.parent.mkdir(parents=True, exist_ok=True)
    r = _ffmpeg(["ffmpeg", "-y", "-i", str(src), "-frames:v", "1", str(dst)])
    if r.returncode != 0 or not dst.is_file():
        print("GL2 FAIL: extract frame:", (r.stderr or "")[-2000:])
        return 2
    return 0


def glow_clip(frame_or_clip: Path, params: dict, out: Path) -> int:
    code = check_gl1(params)
    if code != 0:
        return code
    if not frame_or_clip.exists():
        print("GLOW FAIL: input absent:", frame_or_clip)
        return 2
    mode = params.get("mode", "scene")
    sigma = float(params.get("sigma", 12))
    opacity = float(params.get("opacity", 0.35))
    out.parent.mkdir(parents=True, exist_ok=True)
    inp = Path(frame_or_clip)
    work = out.parent / (out.stem + "_glow_work")
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)

    extra_inputs: list[str] = []
    if mode == "subject":
        frame = work / "frame.png"
        if inp.suffix.lower() in IMAGE_EXT:
            shutil.copy2(inp, frame)
        else:
            if _extract_frame(inp, frame) != 0:
                return 2
        mask_png = work / "subject_mask.png"
        if _try_rembg_mask(frame, mask_png) and mask_png.is_file():
            extra_inputs = ["-i", str(mask_png)]
            vf = _subject_rembg_filter(sigma, opacity)
        else:
            print("GLOW subject: using rigid mat fallback")
            vf = _subject_rigid_filter(sigma, opacity)
    else:
        vf = _scene_filter(sigma, opacity)

    cmd = ["ffmpeg", "-y", "-i", str(inp), *extra_inputs, "-filter_complex", vf, "-map", "[v]"]
    if out.suffix.lower() in IMAGE_EXT:
        cmd += ["-frames:v", "1", str(out)]
    else:
        if inp.suffix.lower() in VIDEO_EXT and _has_audio(inp):
            cmd += ["-map", "0:a", "-c:a", "copy"]
        cmd += ["-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    r = _ffmpeg(cmd)
    if r.returncode != 0 or not out.is_file():
        print("GLOW FAIL:", (r.stderr or "")[-2000:])
        return 2
    print("GLOW OK:", out, "mode", mode, "sigma", sigma, "opacity", opacity)
    return 0


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@app.function(
    gpu="T4",
    timeout=600,
    memory=8192,
    volumes={VOLUME_MOUNT: volume},
)
def preview(params: dict) -> dict:
    work = Path(f"{VOLUME_MOUNT}/preview")
    inbox = Path(f"{VOLUME_MOUNT}/inbox")
    work.mkdir(parents=True, exist_ok=True)
    inbox.mkdir(parents=True, exist_ok=True)

    media = sorted(
        p for p in inbox.iterdir()
        if p.is_file() and p.suffix.lower() in VIDEO_EXT | IMAGE_EXT
    )
    if not media:
        return {"qa_pass": False, "reason": "GL2: inbox Modal vide"}
    src = media[0]
    out = work / "preview.png"
    code = glow_clip(src, params, out)
    summary = {
        "qa_pass": code == 0 and out.is_file(),
        "returncode": code,
        "src": src.name,
        "out": out.name if out.is_file() else None,
        "params": params,
    }
    _write_json(work / "preview_remote.json", summary)
    volume.commit()
    return summary


@app.function(
    gpu="T4",
    timeout=3600,
    memory=16384,
    volumes={VOLUME_MOUNT: volume},
)
def render_glow(params: dict) -> dict:
    work = Path(f"{VOLUME_MOUNT}/render")
    inbox = Path(f"{VOLUME_MOUNT}/inbox")
    work.mkdir(parents=True, exist_ok=True)
    inbox.mkdir(parents=True, exist_ok=True)

    videos = sorted(p for p in inbox.glob("*.mp4"))
    if not videos:
        return {"qa_pass": False, "reason": "GLOW: inbox Modal vide"}
    results = []
    qa = True
    for video in videos:
        out = work / (video.stem + "_glow.mp4")
        code = glow_clip(video, params, out)
        results.append({"src": video.name, "out": out.name if out.is_file() else None, "returncode": code})
        qa = qa and code == 0 and out.is_file()
    summary = {"qa_pass": qa, "clips": results, "params": params}
    _write_json(work / "glow_remote.json", summary)
    volume.commit()
    return summary


@app.local_entrypoint()
def main(task: str = "preview", glow_mode: str = "scene", sigma: float = 12.0, opacity: float = 0.35) -> None:
    params = {"mode": glow_mode, "sigma": sigma, "opacity": opacity}
    if check_gl1(params) != 0:
        raise SystemExit(2)
    if task == "preview":
        summary = preview.remote(params=params)
        print(json.dumps(summary, indent=2, default=str))
        return
    summary = render_glow.remote(params=params)
    print(json.dumps(summary, indent=2, default=str))
