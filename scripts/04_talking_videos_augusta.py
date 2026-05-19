# -*- coding: utf-8 -*-
"""
Augusta at Country Lakes — V1 / V2 / V3 Talking-Head Videos (Arcads Only)
Pipeline: Arcads arcads_1.0 talking-actor (actor + voice + script → video) → ffmpeg post-process

No ElevenLabs. Voice and lip-sync generated entirely inside Arcads.
Output: ../output/augusta/
  augusta_v1_pool_talking.mp4
  augusta_v2_loungers_talking.mp4
  augusta_v3_linen_talking.mp4
  manifest_talking.json

API reference (discovered via /docs):
  POST /v2/talking-actors/generate   → submit job
  GET  /v2/talking-actors/{id}       → poll status
  GET  /v2/talking-actors/{id}/watch → download video binary
"""

import os, sys, json, time, subprocess, requests
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Credentials (from .env — see .env.example) ────────────────────────────────
ARCADS_AUTH = os.environ["ARCADS_AUTH"]

ARCADS_BASE = "https://external-api.arcads.ai"
PRODUCT_ID  = "3c7125f2-de97-4587-99b7-405e80d93f90"
PROJECT_ID  = "105d6a6b-c65e-40de-aefb-9b52da56d3e2"

ARCADS_HEADERS = {"Authorization": ARCADS_AUTH, "Content-Type": "application/json"}

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent
OUTPUT_DIR  = REPO_ROOT / "output" / "augusta"
TMP_DIR     = REPO_ROOT / "tmp"
LOG_FILE    = REPO_ROOT / "logs" / "arcads-talking.jsonl"

# ── Actor & Voice Selection ───────────────────────────────────────────────────
# Actor: Danielle (skin100, elegant, AI Avatar with balcony situations)
# Situations discovered via /v1/actors/{actorId}/situations scan
#   927d7c7a → balcony / sitting / Enthusiastic
#   c08004ce → balcony / sitting / nature / Smiling
DANIELLE_SIT_ENTHUSIASTIC = "927d7c7a-74a4-4bc3-b312-bf7d088d5dab"
DANIELLE_SIT_SMILING      = "c08004ce-d522-40a9-959c-98275e85942a"

# Voices: Mexican Spanish females
#   DJnPsh1Jk4NQJTqaI55i → Shirley home  | Mexican | Young   | casual
#   hHjbwzYZW17oh0p05AKv → Sofia         | Mexican | Old     | casual
#   2Lb1en5ujrODDIqmp7F3 → Ana           | Latin American | Middle Aged
VOICE_PRIMARY  = "DJnPsh1Jk4NQJTqaI55i"  # Shirley home — Mexican, Young Female
VOICE_FALLBACK = "hHjbwzYZW17oh0p05AKv"  # Sofia — Mexican, Female

# ── Approved scripts (psychologically crafted, user-approved) ─────────────────
VIDEOS = [
    {
        "id":       "v1",
        "filename": "augusta_v1_pool_talking.mp4",
        "label":    "V1 — Pool Bikini (Talking Head)",
        "situation": DANIELLE_SIT_SMILING,   # balcony/nature, Smiling → introspective
        "script": (
            "¿Sabes cuántos años trabajé para poder estar aquí — "
            "sin prisa, sin culpa, sin nada que demostrarle a nadie? "
            "Augusta no es una casa. Es una llegada. "
            "Y todavía hay lugar para ti."
        ),
    },
    {
        "id":       "v2",
        "filename": "augusta_v2_loungers_talking.mp4",
        "label":    "V2 — Loungers Cocktail (Talking Head)",
        "situation": DANIELLE_SIT_ENTHUSIASTIC,  # balcony, Enthusiastic → assertive
        "script": (
            "Hay éxito... y hay esto. "
            "Augusta no es para quien quiere demostrar algo — "
            "es para quien ya no necesita hacerlo. "
            "Los mejores lotes se están yendo. ¿Tú ya elegiste?"
        ),
    },
    {
        "id":       "v3",
        "filename": "augusta_v3_linen_talking.mp4",
        "label":    "V3 — Linen Elegance (Talking Head)",
        "situation": DANIELLE_SIT_ENTHUSIASTIC,  # balcony, Enthusiastic → inviting
        "script": (
            "No te lo puedo explicar. Entras por aquí... "
            "y algo en ti dice: esto es. "
            "La privada más exclusiva dentro de Country Lakes, "
            "frente al campo de Greg Letsche. "
            "Pocos lugares quedan — y los que importan, ya no."
        ),
    },
]

# ── Limits ────────────────────────────────────────────────────────────────────
POLL_MAX_SECONDS = 600   # 10 min per video
POLL_INTERVAL    = 5


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def log(entry: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def checkpoint(label: str, path: str = "", extra: str = ""):
    msg = f"[OK] {label}"
    if path:
        msg += f" - {path}"
    if extra:
        msg += f" - {extra}"
    print(msg)


def get_duration(path: Path) -> float:
    cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
           "-of", "json", str(path)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode == 0:
        return float(json.loads(r.stdout).get("format", {}).get("duration", 0))
    return 0.0


def probe_video(path: Path) -> dict:
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json",
           "-show_streams", "-show_format", str(path)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode == 0:
        return json.loads(r.stdout)
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# Phase A — Submit talking-actor job to Arcads
# ─────────────────────────────────────────────────────────────────────────────

def submit_talking_actor(vid: dict, voice_id: str) -> str | None:
    label  = vid["id"]
    script = vid["script"]
    sit_id = vid["situation"]

    payload = {
        "model":     "arcads_1.0",
        "productId": PRODUCT_ID,
        "projectId": PROJECT_ID,
        "script":    script,
        "actors":    [{"situationId": sit_id, "voiceId": voice_id}],
        "autoAddScriptEmotion": True,
    }

    print(f"  [{label}] submitting talking-actor job...")
    print(f"  [{label}] situationId={sit_id[:8]}...  voiceId={voice_id[:8]}...")
    print(f"  [{label}] script: {script[:70]}...")

    r = requests.post(
        f"{ARCADS_BASE}/v2/talking-actors/generate",
        headers=ARCADS_HEADERS, json=payload, timeout=30,
    )
    ts = datetime.now(timezone.utc).isoformat()

    if r.status_code not in (200, 201):
        print(f"  [{label}] submit FAILED: {r.status_code} {r.text[:300]}")
        log({"timestamp": ts, "step": "submit", "id": label, "status": "failed",
             "error": r.text[:300]})
        return None

    items = r.json()
    if not isinstance(items, list) or not items:
        print(f"  [{label}] submit returned unexpected: {r.text[:200]}")
        return None

    job_id = items[0].get("id")
    status = items[0].get("status")
    print(f"  [{label}] job submitted -> {job_id}  status={status}")
    log({"timestamp": ts, "step": "submit", "id": label, "jobId": job_id,
         "model": "arcads_1.0", "situationId": sit_id, "voiceId": voice_id})
    return job_id


# ─────────────────────────────────────────────────────────────────────────────
# Phase B — Poll until completed
# ─────────────────────────────────────────────────────────────────────────────

def poll_talking_actor(vid: dict, job_id: str) -> bool:
    label   = vid["id"]
    elapsed = 0

    while elapsed < POLL_MAX_SECONDS:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        try:
            r = requests.get(
                f"{ARCADS_BASE}/v2/talking-actors/{job_id}",
                headers={"Authorization": ARCADS_AUTH}, timeout=15,
            )
            if not r.text:
                if elapsed % 30 == 0:
                    print(f"  [{label}] ... pending (t+{elapsed}s)")
                continue

            data   = r.json()
            status = data.get("status", "?")

            if status == "completed":
                print(f"  [{label}] DONE  t={elapsed}s")
                log({"timestamp": datetime.now(timezone.utc).isoformat(),
                     "step": "completed", "id": label, "jobId": job_id,
                     "elapsed_s": elapsed})
                return True

            elif status == "failed":
                err = data.get("error", str(data)[:200])
                print(f"  [{label}] FAILED: {err}")
                log({"timestamp": datetime.now(timezone.utc).isoformat(),
                     "step": "failed", "id": label, "jobId": job_id, "error": err})
                return False

            if elapsed % 30 == 0:
                print(f"  [{label}] ... {status} (t+{elapsed}s)")

        except Exception as e:
            if elapsed % 30 == 0:
                print(f"  [{label}] poll error: {e}")

    print(f"  [{label}] TIMEOUT after {POLL_MAX_SECONDS}s")
    return False


# ─────────────────────────────────────────────────────────────────────────────
# Phase C — Download video from /watch
# ─────────────────────────────────────────────────────────────────────────────

def download_talking_actor(vid: dict, job_id: str) -> Path | None:
    label    = vid["id"]
    raw_path = TMP_DIR / f"{label}_talking_raw.mp4"

    print(f"  [{label}] downloading video...")
    r = requests.get(
        f"{ARCADS_BASE}/v2/talking-actors/{job_id}/watch",
        headers={"Authorization": ARCADS_AUTH}, timeout=120, stream=True,
    )
    if r.status_code != 200:
        print(f"  [{label}] download FAILED: {r.status_code}")
        return None

    raw_path.write_bytes(r.content)
    size_mb = len(r.content) / 1_048_576
    print(f"  [{label}] downloaded {size_mb:.1f} MB -> {raw_path.name}")
    return raw_path


# ─────────────────────────────────────────────────────────────────────────────
# Phase D — ffmpeg post-process (normalize + color grade)
# ─────────────────────────────────────────────────────────────────────────────

def compose_ffmpeg(vid: dict, raw_path: Path) -> Path | None:
    label      = vid["id"]
    final_path = OUTPUT_DIR / vid["filename"]

    # Probe the raw video to get actual dimensions and duration
    info = probe_video(raw_path)
    raw_dur = float(info.get("format", {}).get("duration", 0))
    vstream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    raw_w   = vstream.get("width", 1080)
    raw_h   = vstream.get("height", 1920)

    print(f"  [{label}] raw: {raw_w}x{raw_h}  {raw_dur:.2f}s")

    # Scale to 1080x1920 if not already correct
    if raw_w == 1080 and raw_h == 1920:
        scale_filter = "scale=1080:1920:flags=lanczos"
    elif raw_w * 19 == raw_h * 10 or raw_w * 9 == raw_h * 16:
        # Already 9:16 ratio, just scale
        scale_filter = "scale=1080:1920:flags=lanczos"
    else:
        # Crop to 9:16 then scale
        scale_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"

    # Warm color grade (same as V1-V4 pipeline for visual consistency)
    color_grade = (
        "eq=brightness=0.02:contrast=1.05:saturation=1.12,"
        "curves=r='0/0 0.5/0.54 1/1':g='0/0 0.5/0.51 1/0.98':b='0/0 0.5/0.47 1/0.94'"
    )

    video_filter = f"{scale_filter},fps=30,{color_grade}"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_path),
        "-vf", video_filter,
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
        # Audio: normalize + convert from 96kHz mono → 48kHz stereo
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-movflags", "+faststart",
        str(final_path),
    ]

    print(f"  [{label}] ffmpeg compose -> {vid['filename']}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        print(f"  [{label}] ffmpeg FAILED:\n{result.stderr[-400:]}")
        return None

    real_dur = get_duration(final_path)
    size_mb  = final_path.stat().st_size / 1_048_576
    print(f"  [{label}] compose DONE  duration={real_dur:.2f}s  size={size_mb:.1f} MB")

    log({"timestamp": datetime.now(timezone.utc).isoformat(),
         "step": "compose_done", "id": label,
         "final_path": str(final_path), "duration_s": real_dur, "size_mb": size_mb})

    return final_path


# ─────────────────────────────────────────────────────────────────────────────
# Per-video pipeline
# ─────────────────────────────────────────────────────────────────────────────

def process_video(vid: dict) -> dict:
    label  = vid["id"]
    t0_vid = time.time()

    # Reuse cached raw if it exists
    raw_path = TMP_DIR / f"{label}_talking_raw.mp4"

    if not raw_path.exists():
        # Submit job with primary voice
        job_id = submit_talking_actor(vid, VOICE_PRIMARY)
        if job_id is None:
            print(f"  [{label}] retrying with fallback voice...")
            job_id = submit_talking_actor(vid, VOICE_FALLBACK)
        if job_id is None:
            return {"id": label, "filename": vid["filename"], "status": "failed_submit"}

        # Poll
        ok = poll_talking_actor(vid, job_id)
        if not ok:
            return {"id": label, "filename": vid["filename"], "status": "failed_generation",
                    "jobId": job_id}

        # Download
        raw_path = download_talking_actor(vid, job_id)
        if raw_path is None:
            return {"id": label, "filename": vid["filename"], "status": "failed_download",
                    "jobId": job_id}
        checkpoint("Raw video downloaded", raw_path.name)
    else:
        print(f"  [{label}] raw already cached, reusing {raw_path.name}")
        job_id = "cached"
        checkpoint("Raw video (cached)", raw_path.name)

    # ffmpeg post-process
    print(f"\n[D] Post-processing with ffmpeg...")
    final_path = compose_ffmpeg(vid, raw_path)
    if final_path is None:
        return {"id": label, "filename": vid["filename"], "status": "failed_compose"}

    elapsed = int(time.time() - t0_vid)
    real_dur = get_duration(final_path)
    checkpoint(f"Video {label} done", str(final_path), f"{elapsed}s")

    return {
        "id":          label,
        "filename":    vid["filename"],
        "status":      "completed",
        "path":        str(final_path),
        "duration_s":  round(real_dur, 2),
        "size_mb":     round(final_path.stat().st_size / 1_048_576, 1),
        "voice_id":    VOICE_PRIMARY,
        "model":       "arcads_1.0",
        "situationId": vid["situation"],
        "script":      vid["script"],
        "elapsed_s":   elapsed,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    TODAY = datetime.now().strftime("%Y-%m-%d")

    print("=" * 72)
    print("  Augusta at Country Lakes — V1/V2/V3 Talking-Head Videos")
    print("  Actor: Danielle (skin100, balcony situations)")
    print(f"  Voice: Shirley home (Mexican, Young) / fallback: Sofia (Mexican)")
    print("  Model: arcads_1.0  |  autoAddScriptEmotion: true")
    print(f"  Output: {OUTPUT_DIR}")
    print("=" * 72)

    t0_total = time.time()
    manifest = {
        "project":   "Augusta at Country Lakes — Talking Head Videos",
        "generated": TODAY,
        "pipeline": {
            "talking_model": "Arcads arcads_1.0",
            "voice_primary": "Shirley home — Mexican Young Female (DJnPsh1Jk4NQJTqaI55i)",
            "voice_fallback": "Sofia — Mexican Female (hHjbwzYZW17oh0p05AKv)",
            "actor": "Danielle — skin100, AI Avatar, balcony situations",
            "compose": "ffmpeg H.264 CRF18 slow, 1080x1920, 30fps, AAC 192k 48kHz, loudnorm I=-16",
            "auto_emotion": True,
        },
        "videos": [],
    }

    for vid in VIDEOS:
        print(f"\n{'─' * 72}")
        print(f"  {vid['label']}")
        print(f"{'─' * 72}")

        print(f"\n[A] Generating talking-head video (Arcads arcads_1.0)...")
        result = process_video(vid)
        manifest["videos"].append(result)

    # Write manifest
    total_elapsed = int(time.time() - t0_total)
    manifest["total_elapsed_s"] = total_elapsed
    manifest_path = OUTPUT_DIR / "manifest_talking.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    # Summary
    print("\n" + "=" * 72)
    print("  RESUMEN FINAL")
    print("=" * 72)
    completed = [v for v in manifest["videos"] if v.get("status") == "completed"]
    print(f"  Videos completados: {len(completed)}/3")
    for v in manifest["videos"]:
        icon = "[OK]" if v.get("status") == "completed" else "[XX]"
        dur  = f"{v['duration_s']}s" if "duration_s" in v else v.get("status", "—")
        print(f"  {icon} {v['filename']}  {dur}")
    print(f"\n  Manifest: {manifest_path}")
    print(f"  Tiempo total: {total_elapsed}s")
    print("=" * 72)
    print("\nNOTA: Costo API estimado:")
    print("  · arcads_1.0 talking-actor (3x): ~$5-15 USD en creditos Arcads")
    print("\nNEXT: Revisar videos en ./output/augusta/ antes de publicar.")


if __name__ == "__main__":
    main()
