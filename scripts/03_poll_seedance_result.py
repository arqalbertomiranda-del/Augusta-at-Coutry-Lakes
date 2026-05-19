# -*- coding: utf-8 -*-
"""
Poll existing Seedance 2.0 request y descarga el video resultante.
Combina con voiceover existente usando ffmpeg.
"""
import os, sys, time, json, subprocess, requests
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FAL_KEY    = os.environ.get("FAL_KEY", "c3e735a2-6335-4786-a189-493b64ff4eb8:7212281c7ac39dd46407c21be2613ce2")
REQUEST_ID = "019e23f7-ad4a-7b01-a8e9-e8926eebeaf3"
ENDPOINT   = "bytedance/seedance-2.0/image-to-video"
FAL_BASE   = "https://queue.fal.run"

TODAY      = "2026-05-13"
OUTPUT_DIR = Path(r"C:\Users\alber\Boma Desarrollos\Automatizaciones Boma - Documentos\05. Augusta\outputs") / f"isabela-augusta-reel-{TODAY}"
AUDIO_PATH = OUTPUT_DIR / "voiceover.mp3"

FAL_HEADERS = {"Authorization": f"Key {FAL_KEY}"}

status_url = f"{FAL_BASE}/{ENDPOINT}/requests/{REQUEST_ID}/status"
result_url = f"{FAL_BASE}/{ENDPOINT}/requests/{REQUEST_ID}"

print(f"Polling request_id={REQUEST_ID}")
print(f"Endpoint: {ENDPOINT}\n")

video_url = None
for attempt in range(120):
    sr = requests.get(status_url, headers=FAL_HEADERS, timeout=30)
    status_data = sr.json() if sr.status_code == 200 else {}
    status      = status_data.get("status", f"HTTP {sr.status_code}")
    elapsed     = attempt * 5

    print(f"  [{elapsed:>4}s] status={status}")

    if status == "COMPLETED":
        rr     = requests.get(result_url, headers=FAL_HEADERS, timeout=30)
        result = rr.json()
        # fal.ai result shape: {"video": {"url": "..."}} or nested under "output"
        video_d   = result.get("video") or (result.get("output") or {}).get("video") or {}
        video_url = video_d.get("url") or ""
        if not video_url:
            # Fallback: scan all string values for an mp4 URL
            def find_url(d):
                if isinstance(d, dict):
                    for v in d.values():
                        u = find_url(v)
                        if u:
                            return u
                elif isinstance(d, str) and d.startswith("http") and "mp4" in d:
                    return d
                return None
            video_url = find_url(result) or ""
        print(f"\n  COMPLETED! video_url={video_url[:80]}...")
        break
    elif status in ("FAILED", "CANCELLED"):
        print(f"\n  FAILED: {status_data.get('error', str(status_data)[:300])}")
        sys.exit(1)

    if attempt < 119:
        time.sleep(5)
else:
    print("\n  Still processing after 10 min — run again later.")
    sys.exit(1)

if not video_url:
    print("ERROR: No video URL in response.")
    sys.exit(1)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
video_raw = OUTPUT_DIR / "video_raw_seedance2.mp4"
print(f"\nDownloading video...")
vr = requests.get(video_url, timeout=120, allow_redirects=True)
video_raw.write_bytes(vr.content)
print(f"  Saved -> {video_raw.name}  ({len(vr.content)/1_048_576:.1f} MB)")

# Combine with ffmpeg if voiceover exists
if AUDIO_PATH.exists():
    final = OUTPUT_DIR / "isabela-augusta-reel-seedance2.mp4"
    print(f"\nCombining with ffmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_raw),
        "-i", str(AUDIO_PATH),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(final),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  DONE -> {final.name}  ({final.stat().st_size/1_048_576:.1f} MB)")
    else:
        print(f"  ffmpeg failed: {result.stderr[-300:]}")
        print(f"  Raw video: {video_raw}")
else:
    print(f"\nNo voiceover found at {AUDIO_PATH}")
    print(f"Raw video: {video_raw}")

print(f"\n{'='*60}")
print(f"  Augusta Reel — Seedance 2.0 Pro")
print(f"  Output: {OUTPUT_DIR}")
print(f"{'='*60}")
