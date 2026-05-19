# -*- coding: utf-8 -*-
"""
Augusta at Country Lakes — Post-Process & Finalize 11 Videos
=============================================================
Toma los outputs de 05_ugc_10_scenes.py (720p/24fps/8s) y los convierte a:
  - 1080×1920 (lanczos upscale)
  - 30 fps
  - Duración = min(voiceover_duration, 12.3s)  [video looped para cubrir]
  - H.264 CRF 18, preset slow, yuv420p
  - AAC 320kbps 48kHz stereo

V11 (aerial drone, ya 1080p/30fps/13.5s): solo trim a 12.0s.

Output: output/augusta/
  augusta_v01_llegada_acceso.mp4
  ...
  augusta_v10_pies_alberca.mp4
  augusta_v11_aerial_drone.mp4
  manifest.json
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT  = Path(__file__).parent.parent
UGC_DIR    = REPO_ROOT / "outputs" / "ugc-10-scenes-2026-05-14"
OUT_DIR    = REPO_ROOT / "output" / "augusta"
AERIAL_SRC = OUT_DIR / "augusta_v4_aerial_drone.mp4"

TARGET_W   = 1080
TARGET_H   = 1920
TARGET_FPS = 30
MAX_DUR    = 12.3   # seconds — spec allows ±0.3 from 12s
MIN_DUR    = 7.0    # minimum acceptable (short VO scenes)

SCENES = [
    {"n":  1, "id": "llegada-acceso",    "dir": "scene-01-llegada-acceso"},
    {"n":  2, "id": "camastro-alberca",  "dir": "scene-02-camastro-alberca"},
    {"n":  3, "id": "borde-alberca",     "dir": "scene-03-borde-alberca"},
    {"n":  4, "id": "cafe-manana",       "dir": "scene-04-cafe-manana"},
    {"n":  5, "id": "lobby-abierto",     "dir": "scene-05-lobby-abierto"},
    {"n":  6, "id": "coctel-atardecer",  "dir": "scene-06-coctel-atardecer"},
    {"n":  7, "id": "leyendo-camastro",  "dir": "scene-07-leyendo-camastro"},
    {"n":  8, "id": "vista-golf",        "dir": "scene-08-vista-golf"},
    {"n":  9, "id": "carrito-golf",      "dir": "scene-09-carrito-golf"},
    {"n": 10, "id": "pies-alberca",      "dir": "scene-10-pies-alberca"},
]


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def probe_video_info(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet",
         "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate,codec_name",
         "-show_entries", "format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    stream = data.get("streams", [{}])[0]
    fmt    = data.get("format", {})
    fps_str = stream.get("r_frame_rate", "0/1")
    num, den = fps_str.split("/")
    fps = int(num) / int(den) if int(den) else 0
    return {
        "width":    stream.get("width"),
        "height":   stream.get("height"),
        "fps":      fps,
        "codec":    stream.get("codec_name"),
        "duration": float(fmt.get("duration", 0)),
    }


def run(cmd: list, label: str):
    print(f"  → ffmpeg {label}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print(f"  ERROR:\n{result.stderr[-2000:]}")
        raise RuntimeError(f"ffmpeg failed for {label}")


def upscale_scene(scene: dict, out_dir: Path) -> dict:
    n       = scene["n"]
    slug    = scene["id"].replace("-", "_")
    src_dir = UGC_DIR / scene["dir"]
    vid_src = src_dir / "video_raw.mp4"
    vo_src  = src_dir / "voiceover.mp3"
    out_mp4 = out_dir / f"augusta_v{n:02d}_{slug}.mp4"

    if not vid_src.exists():
        raise FileNotFoundError(f"video_raw not found: {vid_src}")
    if not vo_src.exists():
        raise FileNotFoundError(f"voiceover not found: {vo_src}")

    if out_mp4.exists():
        print(f"  ⏭  V{n:02d} already exists, skipping.")
        dur = probe_duration(out_mp4)
        return {"file": str(out_mp4), "duration": round(dur, 2), "status": "skipped"}

    vo_dur  = probe_duration(vo_src)
    tgt_dur = min(vo_dur, MAX_DUR)
    tgt_dur = max(tgt_dur, MIN_DUR)

    # Build ffmpeg: loop video_raw (-stream_loop -1) + voiceover, scale & re-encode
    # -t tgt_dur on output caps total duration
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",           # loop video indefinitely
        "-i", str(vid_src),
        "-i", str(vo_src),
        "-t", str(tgt_dur),             # cap output duration
        "-vf", (
            f"scale={TARGET_W}:{TARGET_H}:flags=lanczos,"
            f"fps={TARGET_FPS}"
        ),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-ac", "2",
        "-shortest",                    # end when shortest stream (VO) ends
        str(out_mp4),
    ]
    run(cmd, f"V{n:02d} upscale+loop+combine")

    actual_dur = probe_duration(out_mp4)
    size_mb    = out_mp4.stat().st_size / 1_048_576
    print(f"  ✅ V{n:02d} → {out_mp4.name} | {actual_dur:.2f}s | {size_mb:.1f}MB")
    return {
        "file":     str(out_mp4),
        "duration": round(actual_dur, 2),
        "size_mb":  round(size_mb, 1),
        "status":   "ok",
    }


def process_aerial(out_dir: Path) -> dict:
    out_mp4 = out_dir / "augusta_v11_aerial_drone.mp4"

    if not AERIAL_SRC.exists():
        print(f"  ⚠  Aerial source not found: {AERIAL_SRC}")
        return {"status": "missing"}

    if out_mp4.exists():
        print(f"  ⏭  V11 already exists, skipping.")
        dur = probe_duration(out_mp4)
        return {"file": str(out_mp4), "duration": round(dur, 2), "status": "skipped"}

    info = probe_video_info(AERIAL_SRC)
    src_dur = info["duration"]
    tgt_dur = min(src_dur, MAX_DUR)

    if info["width"] == TARGET_W and info["height"] == TARGET_H and abs(info["fps"] - TARGET_FPS) < 0.1:
        # Already correct spec — just trim
        cmd = [
            "ffmpeg", "-y",
            "-i", str(AERIAL_SRC),
            "-t", str(tgt_dur),
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "slow",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "320k",
            "-ar", "48000",
            "-ac", "2",
            str(out_mp4),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(AERIAL_SRC),
            "-t", str(tgt_dur),
            "-vf", f"scale={TARGET_W}:{TARGET_H}:flags=lanczos,fps={TARGET_FPS}",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "slow",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "320k",
            "-ar", "48000",
            "-ac", "2",
            str(out_mp4),
        ]

    run(cmd, "V11 aerial trim/convert")
    actual_dur = probe_duration(out_mp4)
    size_mb    = out_mp4.stat().st_size / 1_048_576
    print(f"  ✅ V11 → {out_mp4.name} | {actual_dur:.2f}s | {size_mb:.1f}MB")
    return {
        "file":     str(out_mp4),
        "duration": round(actual_dur, 2),
        "size_mb":  round(size_mb, 1),
        "status":   "ok",
    }


def write_manifest(results: list, out_dir: Path):
    manifest = {
        "project":    "Augusta at Country Lakes",
        "generated":  datetime.now().isoformat(timespec="seconds"),
        "spec": {
            "resolution": f"{TARGET_W}x{TARGET_H}",
            "fps":        TARGET_FPS,
            "codec":      "H.264 (libx264)",
            "audio":      "AAC 320kbps 48kHz stereo",
            "target_dur": "12.0s ±0.3s",
        },
        "videos": results,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ manifest.json → {manifest_path}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for scene in SCENES:
        n = scene["n"]
        print(f"\n🎬 V{n:02d} — {scene['id']}")
        try:
            r = upscale_scene(scene, OUT_DIR)
            results.append({"n": n, "id": scene["id"], **r})
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append({"n": n, "id": scene["id"], "status": "error", "error": str(e)})

    print(f"\n🚁 V11 — aerial-drone")
    r11 = process_aerial(OUT_DIR)
    results.append({"n": 11, "id": "aerial-drone", **r11})

    write_manifest(results, OUT_DIR)

    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    ok  = [r for r in results if r.get("status") in ("ok", "skipped")]
    err = [r for r in results if r.get("status") not in ("ok", "skipped")]
    for r in results:
        sym = "✅" if r.get("status") in ("ok", "skipped") else "❌"
        dur = f"{r.get('duration', '?'):.2f}s" if isinstance(r.get('duration'), float) else "?"
        mb  = f"{r.get('size_mb', '?')}MB" if r.get('size_mb') else ""
        print(f"  {sym} V{r['n']:02d} {r['id']:<25} {dur}  {mb}")
    print(f"\n  {len(ok)}/11 listos  |  {len(err)} errores")
    print(f"  Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
