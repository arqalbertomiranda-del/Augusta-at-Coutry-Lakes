# -*- coding: utf-8 -*-
"""
Augusta at Country Lakes — Camila Lip Sync via Sync.so
Pipeline:
  1. Regenera voiceover Ana María v4 (ElevenLabs) → mp3
  2. Sube imagen local S3-cinematic-terrace a tmpfiles.org → URL pública
  3. Sube audio a tmpfiles.org → URL pública
  4. Envía imagen + audio a Sync.so sync-2 → lip-synced video
  5. Descarga resultado

Output: outputs/camila-augusta-lipsync-{date}/camila-lipsync.mp4
"""
import sys, json, time, requests
from datetime import datetime, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Credenciales ──────────────────────────────────────────────────────────────
ELEVENLABS_API_KEY = "sk_64cc732491128013d3f56570a4ce42d35b4b997b8a03f260"
SYNCSO_API_KEY     = "sk-NgqYJ8wdRBq7U9xdnWrvfA.D1E9Iv4Z1Wb205Gs1J4UJDDglH4kh3_e"

SYNCSO_BASE  = "https://api.sync.so"
EL_BASE      = "https://api.elevenlabs.io/v1"

EL_HEADERS     = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
SYNCSO_HEADERS = {"x-api-key": SYNCSO_API_KEY, "Content-Type": "application/json"}

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent
TODAY       = datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR  = REPO_ROOT / "outputs" / f"camila-augusta-lipsync-{TODAY}"
LOG_FILE    = REPO_ROOT / "logs" / "arcads-api.jsonl"

# Imagen hero de Camila guardada localmente
CAMILA_STILL = REPO_ROOT / "outputs" / "camila-augusta-stills-2026-05-15" / "S3-cinematic-terrace.jpg"
CAMILA_ASSET_ID = "22a4e057-8a73-4457-a895-e74995b4c5fa"

# ── Voz Camila — Ana María v4 ─────────────────────────────────────────────────
VOICE_ID       = "m7yTemJqdIqrcNleANfX"
VOICE_SETTINGS = {"stability": 0.15, "similarity_boost": 0.80, "style": 0.90, "use_speaker_boost": True}

VOICEOVER_SCRIPT = (
    "Elegir dónde vivir no es una decisión... "
    "es una declaración. "
    "Augusta at Country Lakes. "
    "La privada más exclusiva frente al mejor campo de golf de Latinoamérica."
)


def log_entry(entry: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def upload_to_tmpfiles(file_path: Path, mime_type: str, label: str) -> str:
    """Upload any file to tmpfiles.org and return the direct download URL (valid ~60 min)."""
    size_kb = file_path.stat().st_size // 1024
    print(f"    Subiendo {label} ({size_kb} KB) a tmpfiles.org...")
    with open(file_path, "rb") as f:
        r = requests.post(
            "https://tmpfiles.org/api/v1/upload",
            files={"file": (file_path.name, f, mime_type)},
            timeout=120,
        )
    r.raise_for_status()
    data = r.json()
    # Response: {"status":"success","data":{"url":"https://tmpfiles.org/1234/file.jpg"}}
    # Direct download URL replaces tmpfiles.org/ with tmpfiles.org/dl/
    url = data["data"]["url"].replace("tmpfiles.org/", "tmpfiles.org/dl/")
    print(f"    OK -> {url}")
    return url


# ── Paso 1: Generar voiceover ─────────────────────────────────────────────────
def generate_voiceover(out_path: Path) -> Path:
    print("[1] Generando voiceover Ana María v4 (ElevenLabs)...")
    r = requests.post(
        f"{EL_BASE}/text-to-speech/{VOICE_ID}",
        headers=EL_HEADERS,
        json={"text": VOICEOVER_SCRIPT, "model_id": "eleven_multilingual_v2", "voice_settings": VOICE_SETTINGS},
        timeout=60,
    )
    r.raise_for_status()
    out_path.write_bytes(r.content)
    print(f"    Guardado -> {out_path.name}  ({len(r.content):,} B)")
    return out_path


# ── Paso 2: Convertir still a video MP4 corto + subir ────────────────────────
def still_to_video_and_upload(still_path: Path, out_dir: Path) -> str:
    """Convert still JPEG to short MP4 (Sync.so requires video input, not image)."""
    import subprocess
    print("[2] Convirtiendo still a video MP4 (ffmpeg)...")
    if not still_path.exists():
        raise FileNotFoundError(f"Imagen no encontrada: {still_path}")
    mp4_path = out_dir / "camila-still-input.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(still_path),
        "-c:v", "libx264",
        "-t", "8",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-movflags", "+faststart",
        str(mp4_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {result.stderr[-400:]}")
    size_mb = mp4_path.stat().st_size / 1_048_576
    print(f"    Video generado: {mp4_path.name} ({size_mb:.1f} MB, 8s)")
    return upload_to_tmpfiles(mp4_path, "video/mp4", "still-to-video Camila")


# ── Paso 3: Subir audio a hosting público ────────────────────────────────────
def upload_audio_public(audio_path: Path) -> str:
    print("[3] Subiendo audio a hosting público...")
    return upload_to_tmpfiles(audio_path, "audio/mpeg", "voiceover Ana María v4")


# ── Paso 4: Enviar a Sync.so ──────────────────────────────────────────────────
def submit_syncso(image_url: str, audio_url: str) -> str:
    print("[4] Enviando a Sync.so (sync-2)...")
    payload = {
        "model": "sync-2",
        "input": [
            {"type": "video", "url": image_url},
            {"type": "audio", "url": audio_url},
        ],
        "options": {
            "output_format": "mp4",
            "sync_mode":     "bounce",
            "fps":           25,
        },
    }
    r = requests.post(
        f"{SYNCSO_BASE}/v2/generate",
        headers=SYNCSO_HEADERS, json=payload, timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    job_id = data["id"]
    print(f"    Job enviado -> {job_id}  status={data.get('status')}")
    log_entry({"timestamp": datetime.now(timezone.utc).isoformat(),
               "step": "syncso_submit", "jobId": job_id, "model": "sync-2"})
    return job_id


# ── Paso 5: Polling Sync.so ───────────────────────────────────────────────────
def poll_syncso(job_id: str) -> str:
    print("[5] Esperando resultado de Sync.so...")
    for attempt in range(180):
        time.sleep(5)
        r = requests.get(
            f"{SYNCSO_BASE}/v2/generate/{job_id}",
            headers=SYNCSO_HEADERS, timeout=30,
        )
        if r.status_code != 200:
            continue
        data   = r.json()
        status = data.get("status", "")
        if status == "COMPLETED":
            url = data.get("outputUrl")
            elapsed = attempt * 5
            print(f"    DONE  t={elapsed}s")
            log_entry({"timestamp": datetime.now(timezone.utc).isoformat(),
                       "step": "syncso_completed", "jobId": job_id,
                       "elapsed_s": elapsed, "outputUrl": url})
            return url
        elif status in ("FAILED", "ERROR", "REJECTED"):
            err = data.get("error", str(data)[:300])
            raise RuntimeError(f"Sync.so {status}: {err}")
        else:
            if attempt % 6 == 0:
                print(f"    ... {status} (t+{attempt*5}s)")
    raise RuntimeError("Sync.so timeout después de 15 minutos")


# ── Paso 6: Descargar video ───────────────────────────────────────────────────
def download_video(url: str, out_path: Path) -> Path:
    print("[6] Descargando video lip-synced...")
    r = requests.get(url, timeout=120, stream=True)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    size_mb = len(r.content) / 1_048_576
    print(f"    Guardado -> {out_path.name}  ({size_mb:.1f} MB)")
    return out_path


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    audio_path = OUTPUT_DIR / "voiceover-ana-maria-v4.mp3"
    raw_path   = OUTPUT_DIR / "camila-lipsync-raw.mp4"

    print("=" * 70)
    print("  Augusta at Country Lakes — Camila Lip Sync (Sync.so)")
    print("  Imagen : S3-cinematic-terrace (hero, local)")
    print("  Voz    : Ana María v4 (mexicana, ElevenLabs)")
    print("  Motor  : Sync.so sync-2")
    print(f"  Output : {OUTPUT_DIR}")
    print("=" * 70 + "\n")

    # 1. Voiceover
    generate_voiceover(audio_path)

    # 2. Convertir still a video corto y subir a URL pública
    image_url = still_to_video_and_upload(CAMILA_STILL, OUTPUT_DIR)

    # 3. Audio a URL pública
    audio_url = upload_audio_public(audio_path)

    # 4-5. Sync.so
    job_id    = submit_syncso(image_url, audio_url)
    video_url = poll_syncso(job_id)

    # 6. Descargar
    download_video(video_url, raw_path)

    # 7. Renombrar como final
    final = OUTPUT_DIR / "camila-lipsync.mp4"
    if final.exists():
        final.unlink()
    raw_path.rename(final)

    size_mb = final.stat().st_size / 1_048_576
    print("\n" + "=" * 70)
    print(f"  FINAL -> {final}")
    print(f"  Size  : {size_mb:.1f} MB")
    print(f"  Listo para Instagram Reels / TikTok / Facebook")
    print("=" * 70)

    (OUTPUT_DIR / "manifest.json").write_text(json.dumps({
        "project":        "Augusta at Country Lakes",
        "influencer":     "Camila",
        "date":           TODAY,
        "still_asset_id": CAMILA_ASSET_ID,
        "voice_id":       VOICE_ID,
        "voice_name":     "Ana María v4 (mexicana)",
        "syncso_job_id":  job_id,
        "output":         str(final),
        "size_mb":        round(size_mb, 1),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
