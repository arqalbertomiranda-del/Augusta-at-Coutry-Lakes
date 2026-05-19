# -*- coding: utf-8 -*-
"""
Augusta at Country Lakes — Phase 2: Animate + Voiceover + Combine

Workflow:
  1. Toma el mejor still de Phase 1 (S1-alberca-augusta.jpg, preferido)
  2. Anima con Seedance 2.0 Pro via fal.ai (requiere FAL_KEY)
       Fallback: Arcads veo31 si FAL_KEY no está disponible
  3. Genera voiceover en español con ElevenLabs (Jessica, 12s)
  4. Combina video + audio con ffmpeg → final MP4 en 9:16

Prerequisito: haber corrido 01_generate_isabela_augusta_stills.py
              y tener FFmpeg instalado (https://ffmpeg.org/download.html)

Uso:
  # Con Seedance 2.0 Pro (fal.ai):
  set FAL_KEY=your_fal_api_key_here
  python 02_animate_voiceover_combine.py

  # Sin FAL_KEY usa Arcads veo31 automáticamente como fallback

Output: outputs/isabela-augusta-reel-{date}/isabela-augusta-reel.mp4
"""
import os, sys, json, time, subprocess, requests

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    import pathlib as _pl
    load_dotenv(_pl.Path(__file__).parent.parent / ".env")
except ImportError:
    pass
from datetime import datetime, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from PIL import Image
    import io as _io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ── Credenciales (desde .env — ver .env.example) ──────────────────────────────
ARCADS_AUTH        = os.environ["ARCADS_AUTH"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
FAL_KEY            = os.environ.get("FAL_KEY", "")   # Opcional — Seedance 2.0 Pro

ARCADS_BASE = "https://external-api.arcads.ai"
FAL_BASE    = "https://queue.fal.run"
EL_BASE     = "https://api.elevenlabs.io/v1"

PRODUCT_ID  = "3c7125f2-de97-4587-99b7-405e80d93f90"
PROJECT_ID  = "105d6a6b-c65e-40de-aefb-9b52da56d3e2"

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT  = SCRIPT_DIR.parent
TODAY      = datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = REPO_ROOT / "outputs" / f"isabela-augusta-reel-{TODAY}"
LOG_FILE   = REPO_ROOT / "logs" / "arcads-api.jsonl"

ARCADS_HEADERS = {"Authorization": ARCADS_AUTH, "Content-Type": "application/json"}
EL_HEADERS     = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
FAL_HEADERS    = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

# ── Voiceover ─────────────────────────────────────────────────────────────────
VOICE_ID = "cgSgspJ2msm6clMCkdW9"  # Jessica — ElevenLabs

VOICEOVER_SCRIPT = (
    "Este es Augusta at Country Lakes. "
    "La privada más exclusiva del sureste mexicano, "
    "frente al mejor campo de golf de Latinoamérica. "
    "Diseñado por Greg Letsche. "
    "Precios de preventa, por tiempo limitado."
)

VOICE_SETTINGS = {
    "stability": 0.38,
    "similarity_boost": 0.82,
    "style": 0.35,
    "use_speaker_boost": True,
}

# ── Prompt de animación ───────────────────────────────────────────────────────
ANIMATION_PROMPT = (
    "Animate this photograph into a cinematic video. "
    "A beautiful woman in an elegant ivory silk midi dress stands at the edge of a luxury "
    "infinity pool of an exclusive private residential community. "
    "Subtle natural human motion: gentle weight shift, slight head tilt, soft blink, "
    "hair moves gently with the breeze, fingers adjust grip on sun lounger slightly. "
    "The pool water shimmers softly in warm sunlight. Tall coconut palm fronds sway in the "
    "light tropical breeze. Warm golden afternoon light. Brilliant sunny day, few white clouds. "
    "Camera holds steady with a very slow gentle drift forward. "
    "Vertical 9:16. No text, no subtitles, no captions, no watermarks."
)


def log_entry(entry: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def find_best_still() -> Path | None:
    """Encuentra el still de Phase 1 más reciente."""
    preferred = "S1-alberca-augusta.jpg"
    fallback  = "S2-acceso-augusta.jpg"

    for pattern in [f"isabela-augusta-stills-{TODAY}", "isabela-augusta-stills-*"]:
        dirs = sorted((REPO_ROOT / "outputs").glob(pattern), reverse=True)
        for d in dirs:
            for name in [preferred, fallback]:
                candidate = d / name
                if candidate.exists():
                    return candidate
    return None


# ── Phase A: Animate con Seedance 2.0 Pro (fal.ai) ───────────────────────────
def animate_seedance2(image_url: str) -> dict:
    print("  Using Seedance 2.0 Pro (fal.ai)...")
    endpoint  = "bytedance/seedance-2.0/image-to-video"

    payload = {
        "prompt":       ANIMATION_PROMPT,
        "image_url":    image_url,
        "duration":     "10",
        "aspect_ratio": "9:16",
        "resolution":   "720p",
        "seed":         42,
    }
    r = requests.post(
        f"{FAL_BASE}/{endpoint}",
        headers=FAL_HEADERS, json=payload, timeout=60
    )
    r.raise_for_status()
    data       = r.json()
    request_id = data.get("request_id")
    print(f"  Submitted -> request_id={request_id}")

    status_url = f"{FAL_BASE}/{endpoint}/requests/{request_id}/status"
    result_url = f"{FAL_BASE}/{endpoint}/requests/{request_id}"

    for attempt in range(240):
        time.sleep(5)
        sr = requests.get(status_url, headers=FAL_HEADERS, timeout=30)
        if sr.status_code != 200:
            continue
        status_data = sr.json()
        status      = status_data.get("status", "")

        if status == "COMPLETED":
            rr      = requests.get(result_url, headers=FAL_HEADERS, timeout=30)
            result  = rr.json()
            video_d = (result.get("output") or result).get("video", {})
            url     = video_d.get("url") or result.get("video", {}).get("url", "")
            elapsed = attempt * 5
            print(f"  DONE  t={elapsed}s")
            return {"status": "completed", "url": url, "request_id": request_id}
        elif status in ("FAILED", "CANCELLED"):
            err = status_data.get("error", str(status_data)[:200])
            print(f"  FAILED: {err}")
            return {"status": "failed", "error": err, "request_id": request_id}
        else:
            if attempt % 12 == 0:
                elapsed = attempt * 5
                print(f"  ... {status} (t+{elapsed}s)")

    return {"status": "timeout", "request_id": request_id}


# ── Phase A fallback: Animate con Arcads veo31 ───────────────────────────────
def upload_to_arcads(img_path: Path, label: str) -> str:
    if HAS_PIL:
        img   = Image.open(img_path).convert("RGB")
        buf   = _io.BytesIO()
        img.save(buf, format="JPEG", quality=92)
        data  = buf.getvalue()
    else:
        data = img_path.read_bytes()

    r = requests.post(
        f"{ARCADS_BASE}/v1/file-upload/get-presigned-url",
        headers=ARCADS_HEADERS, json={"fileType": "image/jpeg"}, timeout=30
    )
    r.raise_for_status()
    d = r.json()
    requests.put(
        d["presignedUrl"], data=data,
        headers={"Content-Type": "image/jpeg"}, timeout=60
    ).raise_for_status()
    print(f"  [{label}] uploaded to Arcads ({len(data):,} B)")
    return d["filePath"]


def animate_arcads_veo31(still_path: Path) -> dict:
    print("  Using Arcads veo31 (fallback — FAL_KEY not set)...")
    start_frame = upload_to_arcads(still_path, "start-frame")

    payload = {
        "model":       "veo31",
        "productId":   PRODUCT_ID,
        "projectId":   PROJECT_ID,
        "prompt":      ANIMATION_PROMPT,
        "aspectRatio": "9:16",
        "resolution":  "720p",
        "startFrame":  start_frame,
    }
    r = requests.post(
        f"{ARCADS_BASE}/v2/videos/generate",
        headers=ARCADS_HEADERS, json=payload, timeout=30
    )
    ts = datetime.now(timezone.utc).isoformat()
    if r.status_code not in (200, 201):
        log_entry({"timestamp": ts, "endpoint": "POST /v2/videos/generate",
                   "model": "veo31", "status": "failed_create", "error": r.text[:300]})
        return {"status": "failed_create", "error": r.text[:300]}

    data     = r.json()
    asset_id = data.get("id") or data.get("assetId") or data.get("videoId")
    print(f"  Submitted -> asset_id={asset_id}")
    log_entry({"timestamp": ts, "endpoint": "POST /v2/videos/generate",
               "model": "veo31", "assetId": asset_id, "status": "pending",
               "session": {"folderName": f"Augusta - {TODAY}"}})

    start = time.time()
    for attempt in range(180):
        time.sleep(5)
        pr = requests.get(
            f"{ARCADS_BASE}/v1/assets/{asset_id}",
            headers={"Authorization": ARCADS_AUTH}, timeout=30
        )
        if pr.status_code != 200:
            continue
        asset  = pr.json()
        status = asset.get("status")
        if status == "generated":
            url     = asset.get("url") or asset.get("videoUrl")
            credits = asset.get("creditsCharged", "?")
            elapsed = int(time.time() - start)
            print(f"  DONE  credits={credits}  t={elapsed}s")
            return {"status": "completed", "url": url, "asset_id": asset_id}
        elif status == "failed":
            err = asset.get("error") or str(asset)[:300]
            print(f"  FAILED: {err}")
            return {"status": "failed", "error": err, "asset_id": asset_id}
        else:
            elapsed = int(time.time() - start)
            if attempt % 12 == 0:
                print(f"  ... {status} (t+{elapsed}s)")

    return {"status": "timeout", "asset_id": asset_id}


# ── Phase B: Voiceover con ElevenLabs ────────────────────────────────────────
def generate_voiceover() -> Path | None:
    print("\n[B] Generating ElevenLabs voiceover (Jessica, español)...")
    print(f"  Script: {VOICEOVER_SCRIPT[:80]}...")

    payload = {
        "text":           VOICEOVER_SCRIPT,
        "model_id":       "eleven_multilingual_v2",
        "voice_settings": VOICE_SETTINGS,
    }
    r = requests.post(
        f"{EL_BASE}/text-to-speech/{VOICE_ID}",
        headers=EL_HEADERS, json=payload, timeout=60
    )
    if r.status_code != 200:
        print(f"  FAILED: {r.status_code} {r.text[:200]}")
        return None

    out = OUTPUT_DIR / "voiceover.mp3"
    out.write_bytes(r.content)
    print(f"  Saved -> {out.name}  ({len(r.content):,} B)")
    return out


# ── Phase C: Combinar con ffmpeg ──────────────────────────────────────────────
def combine_video_audio(video_path: Path, audio_path: Path) -> Path | None:
    print("\n[C] Combining video + audio with ffmpeg...")
    out = OUTPUT_DIR / "isabela-augusta-reel.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(out),
    ]
    print(f"  {' '.join(cmd[:6])} ... {out.name}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size_mb = out.stat().st_size / 1_048_576
        print(f"  DONE -> {out.name}  ({size_mb:.1f} MB)")
        return out
    else:
        print(f"  FAILED:\n{result.stderr[-500:]}")
        print("  TIP: Install ffmpeg from https://ffmpeg.org/download.html")
        print("  Alternatively, combine manually:")
        print(f"    Video: {video_path}")
        print(f"    Audio: {audio_path}")
        return None


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  Augusta at Country Lakes — Isabela Reel (Phase 2)")
    if FAL_KEY:
        print("  Video engine : Seedance 2.0 Pro (fal.ai)")
    else:
        print("  Video engine : Arcads veo31 (fallback — set FAL_KEY for Seedance 2.0)")
    print(f"  Output dir   : {OUTPUT_DIR}")
    print("=" * 70)

    # ── Find input still ───────────────────────────────────────────────────────
    still_path = find_best_still()
    if still_path is None:
        print("\nERROR: No still found. Run 01_generate_isabela_augusta_stills.py first.")
        sys.exit(1)
    print(f"\nUsing still: {still_path.name}")

    # ── Phase A: Animate ──────────────────────────────────────────────────────
    print("\n[A] Animating still...")
    video_local = OUTPUT_DIR / "video_raw.mp4"

    if FAL_KEY:
        # Para Seedance 2.0 necesitamos una URL pública del still
        # Subimos el still a Arcads y usamos esa URL pública
        still_arcads_path = upload_to_arcads(still_path, "seedance-input")
        # Construir URL pública desde el filePath de Arcads
        # Nota: Arcads devuelve el filePath, no una URL directa.
        # Para Seedance, necesitamos una URL accesible. Subimos directamente a fal.ai.
        print("  Uploading still to fal.ai storage for Seedance...")
        with open(still_path, "rb") as f:
            img_data = f.read()

        # fal.ai storage upload
        init_r = requests.post(
            "https://rest.alpha.fal.ai/storage/upload/initiate",
            headers=FAL_HEADERS,
            json={"file_name": still_path.name, "content_type": "image/jpeg"},
            timeout=30
        )
        if init_r.status_code == 200:
            init_data = init_r.json()
            upload_url = init_data.get("upload_url")
            file_url   = init_data.get("file_url") or init_data.get("url")
            requests.put(
                upload_url, data=img_data,
                headers={"Content-Type": "image/jpeg"}, timeout=60
            ).raise_for_status()
            print(f"  Uploaded to fal.ai: {file_url[:60]}...")
            anim_result = animate_seedance2(file_url)
        else:
            print(f"  WARNING: fal.ai storage upload failed ({init_r.status_code})")
            print("  Trying with Arcads generated image URL...")
            # Generate a fresh Arcads URL for the still
            anim_result = {"status": "failed", "error": "fal.ai storage unavailable"}
    else:
        anim_result = animate_arcads_veo31(still_path)

    if anim_result["status"] not in ("completed",):
        print(f"\nERROR: Animation failed — {anim_result.get('error', anim_result.get('status'))}")
        sys.exit(1)

    # Download video
    video_url = anim_result["url"]
    print(f"  Downloading video from {video_url[:60]}...")
    vr = requests.get(video_url, timeout=120, allow_redirects=True)
    video_local.write_bytes(vr.content)
    print(f"  Video saved -> {video_local.name}  ({len(vr.content)/1_048_576:.1f} MB)")

    # ── Phase B: Voiceover ────────────────────────────────────────────────────
    audio_path = generate_voiceover()
    if audio_path is None:
        print("\nWARNING: Voiceover failed. Final video will have no audio.")
        # Copy raw video as final output
        import shutil
        final = OUTPUT_DIR / "isabela-augusta-reel.mp4"
        shutil.copy2(video_local, final)
        print(f"\n[OUTPUT] {final}")
        return

    # ── Phase C: Combine ──────────────────────────────────────────────────────
    final = combine_video_audio(video_local, audio_path)

    # Summary
    print("\n" + "=" * 70)
    if final and final.exists():
        size_mb = final.stat().st_size / 1_048_576
        print(f"  FINAL REEL -> {final}")
        print(f"  Size: {size_mb:.1f} MB")
        print(f"  Ready to post on Instagram Reels / TikTok / Facebook")
    else:
        print(f"  Video (no audio): {video_local}")
        print(f"  Audio (separate): {audio_path}")
        print("  NOTE: Install ffmpeg to auto-combine, or merge manually in any video editor")
    print("=" * 70)

    # Save manifest
    manifest = OUTPUT_DIR / "manifest.json"
    manifest.write_text(json.dumps({
        "project": "Augusta at Country Lakes",
        "date": TODAY,
        "still_input": str(still_path),
        "video_engine": "seedance-2.0-pro" if FAL_KEY else "arcads-veo31",
        "voiceover_script": VOICEOVER_SCRIPT,
        "voice": "Jessica (ElevenLabs)",
        "animation_result": anim_result,
        "output": str(final) if final else None,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
