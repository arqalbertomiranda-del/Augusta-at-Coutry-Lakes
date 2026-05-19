# -*- coding: utf-8 -*-
"""
Augusta at Country Lakes — 4 Videos Verticales con Isabela
Pipeline: nano-banana-2 still → ElevenLabs voz → Arcads veo31 animación → ffmpeg compose

Output: ../output/augusta/
  augusta_v1_pool_bikini.mp4
  augusta_v2_loungers_cocktail.mp4
  augusta_v3_linen_elegance.mp4
  augusta_v4_aerial_drone.mp4
  manifest.json
"""

import os, sys, json, time, subprocess, io, requests
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ── Credenciales (desde .env — ver .env.example) ──────────────────────────────
ARCADS_AUTH        = os.environ["ARCADS_AUTH"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]

ARCADS_BASE = "https://external-api.arcads.ai"
EL_BASE     = "https://api.elevenlabs.io/v1"
PRODUCT_ID  = "3c7125f2-de97-4587-99b7-405e80d93f90"
PROJECT_ID  = "105d6a6b-c65e-40de-aefb-9b52da56d3e2"

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent
OUTPUT_DIR  = REPO_ROOT / "output" / "augusta"
TMP_DIR     = REPO_ROOT / "tmp"
LOG_FILE    = REPO_ROOT / "logs" / "arcads-api.jsonl"
TODAY       = datetime.now().strftime("%Y-%m-%d")

RENDERS_DIR = Path(r"C:\Users\alber\Boma Desarrollos\Augusta at Country Lakes - Documentos\02. Alcances\02.13 Renders\Arquitectonicos")
ISABELA_DIR = Path(r"C:\Users\alber\Boma Desarrollos\Arrecife Sisal - Documentos\10.0 Mercadotecnia\Videos de Claude Code - Arrecife\references\influencers\isabela-dark-brunette-straight-green-eyes-fair")

RENDER_POOL     = RENDERS_DIR / "ACCESO CASA CLUB.jpg"   # alberca + camastros (V1, V2)
RENDER_ENTRANCE = RENDERS_DIR / "ACCESO.jpg"              # fachada acceso (V3)
RENDER_AERIAL   = RENDERS_DIR / "AUGUSTA_AEREO CC.jpg"   # masterplan aéreo (V4)
ISABELA_REF     = ISABELA_DIR / "01-hero-front.jpg"

ARCADS_HEADERS = {"Authorization": ARCADS_AUTH, "Content-Type": "application/json"}
EL_HEADERS     = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}

# ── Voz Isabela ───────────────────────────────────────────────────────────────
# Sarah (premade, accesible en todas las cuentas) — madura, confiada, profesional.
# Fallback: Jessica (premade, warm). Ambas generan español excelente con
# eleven_multilingual_v2. Marlene/Ana María son [professional] y requieren plan Creator+.
VOICE_PRIMARY   = "EXAVITQu4vr4xnSDxMaL"   # Sarah — Mature, Reassuring, Confident
VOICE_FALLBACK  = "cgSgspJ2msm6clMCkdW9"   # Jessica — proven to work (voiceover.mp3)
VOICE_SETTINGS  = {"stability": 0.45, "similarity_boost": 0.80,
                   "style": 0.35, "use_speaker_boost": True}
EL_MODEL        = "eleven_multilingual_v2"

# ── Prompt base de Isabela ────────────────────────────────────────────────────
ISABELA_BASE = (
    "A 28-year-old Mexican woman of remarkable natural beauty: long silky straight "
    "dark chestnut-brown hair falling past her mid-back, large captivating green eyes "
    "with luminous depth, porcelain-fair flawless skin, perfectly arched dark brows, "
    "full lips with a defined cupid's bow, slender elegant figure approximately 175cm, "
    "narrow waist. Minimal old-money makeup — luminous bare skin, barely-there gloss. "
    "Quiet confident magnetism — completely at home in this world of exclusivity. "
    "Ultra-photorealistic, visible skin texture, individual hair strands. "
    "No text, no subtitles, no watermarks."
)

# ── Configuración de cada video ───────────────────────────────────────────────
VIDEOS = [
    {
        "id":       "v1",
        "filename": "augusta_v1_pool_bikini.mp4",
        "label":    "V1 — Pool Bikini",
        "render":   RENDER_POOL,
        "use_isabela_in_still": True,
        "use_scene_ref": False,   # pool scene + bikini prompt triggers generation failure
        "still_prompt": (
            "Photorealistic luxury real estate lifestyle portrait. " + ISABELA_BASE +
            " She wears an elegant white designer bikini with high-waist cut, sophisticated "
            "and tasteful, paired with a wide-brim natural straw Borsalino sun hat tilted "
            "slightly. Fine delicate gold chain necklace, small gold hoop earrings. "
            "She stands waist-deep in a long minimalist infinity pool, leaning gracefully "
            "on the pool edge, looking directly at camera with calm confident serenity. "
            "Behind her: a low modern cream-stucco Mexican contemporary clubhouse with "
            "exposed wooden beam pergola, lush tall coconut palms swaying in the breeze, "
            "crisp white sun loungers with white umbrellas on polished travertine deck. "
            "Warm golden tropical afternoon light. Brilliant sunny day, few wispy clouds. "
            "Water shimmering at her waist. Subtle breeze moving strands of dark hair. "
            "Camera at water-level, medium framing, depth of field: she is sharp, "
            "clubhouse background softly blurred. Vertical 9:16 composition."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic vertical 9:16 video. "
            "A beautiful Mexican woman in a white bikini and straw sun hat stands waist-deep "
            "in a luxury infinity pool, leaning on the pool edge, looking at camera. "
            "Subtle natural motion: gentle weight shift, soft blink, hair moves in the "
            "tropical breeze, water surface shimmers softly with small ripples. "
            "Tall coconut palm fronds sway gently. Warm golden afternoon light. "
            "Camera holds steady with a very slow subtle drift forward. "
            "No text, no subtitles, no watermarks. Photoreal cinematic."
        ),
        "voice_script": (
            "Bienvenido a Augusta… "
            "la privada más exclusiva frente al mejor campo de golf de Latinoamérica, "
            "diseñado por Greg Letsche. "
            "Aún hay precios de preventa… pero no por mucho."
        ),
    },
    {
        "id":       "v2",
        "filename": "augusta_v2_loungers_cocktail.mp4",
        "label":    "V2 — Loungers Cocktail",
        "render":   RENDER_POOL,
        "use_isabela_in_still": True,
        "use_scene_ref": False,   # pool scene ref consistently causes generation failure
        "still_prompt": (
            "Photorealistic luxury real estate lifestyle portrait. " + ISABELA_BASE +
            " She wears a flowing cream linen wrap dress, effortlessly elegant, "
            "Jacquemus / Toteme aesthetic. Hair loosely styled back. "
            "She sits at an outdoor teak table beside a luxury resort pool, "
            "one leg crossed, elbow resting on table, holding a crystal cocktail glass "
            "with a pale citrus drink. Looking at camera with calm, serene confidence. "
            "Behind her: white sun loungers and umbrellas, the infinity pool, and the "
            "low cream-stucco clubhouse with wooden pergola, blurred gently. "
            "Lush tropical palms. Warm golden afternoon light. "
            "Medium three-quarter framing, vertical 9:16 composition."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic vertical 9:16 video. "
            "An elegant Mexican woman in a sheer white silk cover-up sits at an outdoor "
            "teak table near a luxury infinity pool, holding a crystal cocktail glass, "
            "looking at camera with serene confidence. "
            "Subtle motion: gentle weight shift, soft blink, hair strand moves in breeze, "
            "cocktail liquid sways slightly, pool water shimmers in background. "
            "Palm fronds sway. Warm golden afternoon light. "
            "Slow lateral camera drift (left to right, 15 degrees). "
            "No text, no subtitles, no watermarks. Photoreal cinematic."
        ),
        "voice_script": (
            "Esto no es una visita… "
            "es la vida que mereces. "
            "Augusta at Country Lakes — "
            "frente al campo de golf, con financiamiento sin intereses "
            "hasta treinta y seis meses. "
            "Pregunta hoy."
        ),
    },
    {
        "id":       "v3",
        "filename": "augusta_v3_linen_elegance.mp4",
        "label":    "V3 — Linen Elegance",
        "render":   RENDER_ENTRANCE,
        "use_isabela_in_still": True,
        "still_prompt": (
            "Photorealistic luxury real estate lifestyle portrait. " + ISABELA_BASE +
            " She wears a flowing off-white linen midi dress with deep V-neckline, "
            "structured but fluid silhouette — The Row / Loro Piana aesthetic. "
            "No visible underwear lines. Thin leather strappy sandals in nude. "
            "Fine gold watch on wrist, thin gold rings, small sculptural gold drop earrings. "
            "Long dark hair loose, moving naturally in a gentle tropical breeze. "
            "She walks slowly toward camera on the elegant circular cobblestone plaza at "
            "the entrance of the exclusive private golf community. Behind her: a low modern "
            "building of warm cream limestone and smooth stucco with a carved wooden pergola "
            "archway above the entrance gate. Lush tropical landscaping: monstera leaves, "
            "palm fronds, ornamental grasses. Brilliant sunny day. "
            "Frontal vertical framing, camera at medium distance. Vertical 9:16 composition."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic vertical 9:16 video. "
            "An elegant Mexican woman in a flowing off-white linen midi dress walks "
            "slowly toward camera on a circular cobblestone plaza, a carved wooden pergola "
            "gate and cream-limestone clubhouse building behind her. Tall palms sway. "
            "Subtle motion: slow natural walk toward camera, linen fabric flows in breeze, "
            "long dark hair moves gently, soft confident expression, slight squint in sunlight. "
            "Camera performs a very slow dolly-back synchronized with her approach. "
            "Warm sunny day, golden light. No text, no subtitles, no watermarks. "
            "Photoreal cinematic editorial."
        ),
        "voice_script": (
            "Pocos lugares en México se sienten así. "
            "Augusta es para quienes saben "
            "que el verdadero lujo es la exclusividad. "
            "Preventa abierta… "
            "y este precio no vuelve."
        ),
    },
    {
        "id":       "v4",
        "filename": "augusta_v4_aerial_drone.mp4",
        "label":    "V4 — Aerial Drone",
        "render":   RENDER_AERIAL,
        "use_isabela_in_still": False,   # purely aerial; Isabela voice in off
        "still_prompt": None,
        "animation_prompt": (
            "Animate this aerial master plan image into a cinematic vertical 9:16 drone video. "
            "Slow continuous drone flight from west to east (left to right on screen) "
            "over a luxury triangular gated residential community in Yucatán Mexico. "
            "Golf course and natural turquoise lagoon visible to the north. "
            "Central park fairway with lush palm trees. "
            "Luxury 2-story contemporary Mexican-style villas each with private pool, "
            "lush landscaping, elegant outdoor furniture, some with rooftop terraces. "
            "Circular cobblestone entrance plaza visible. "
            "White minimalist clubhouse with long infinity pool and loungers visible. "
            "Brilliant sunny tropical day, sparse white clouds, gentle breeze moving palms. "
            "Smooth continuous east-bound drone movement. Cinematic editorial real estate aerial. "
            "No text, no subtitles, no watermarks. Photoreal."
        ),
        "voice_script": (
            "Augusta at Country Lakes. "
            "Frente al campo de golf diseñado por Greg Letsche. "
            "Arquitectura de Artigas, paisaje de Maat. "
            "Preventa abierta — tu lugar, antes de que alguien más lo elija."
        ),
    },
]

# ── STOP CONDITIONS ───────────────────────────────────────────────────────────
MAX_API_COST_USD  = 80.0
MIN_AUDIO_SECS    = 7.0
MAX_AUDIO_SECS    = 14.0

manifest_data = {"project": "Augusta at Country Lakes", "date": TODAY, "videos": []}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def log(entry: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def checkpoint(label: str, path: str = "", extra: str = ""):
    msg = f"✅ {label}"
    if path:
        msg += f" · {path}"
    if extra:
        msg += f" · {extra}"
    print(msg)


def prepare_image(path: Path, max_side: int = 1536) -> bytes:
    if HAS_PIL:
        img = Image.open(path).convert("RGB")
        w, h = img.size
        if max(w, h) > max_side:
            scale = max_side / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=92)
        return buf.getvalue()
    return path.read_bytes()


def upload_image(img_bytes: bytes, label: str) -> str:
    """Upload image to Arcads presigned S3 URL. Returns filePath."""
    r = requests.post(
        f"{ARCADS_BASE}/v1/file-upload/get-presigned-url",
        headers=ARCADS_HEADERS,
        json={"fileType": "image/jpeg"},
        timeout=30,
    )
    r.raise_for_status()
    d = r.json()
    requests.put(
        d["presignedUrl"], data=img_bytes,
        headers={"Content-Type": "image/jpeg"}, timeout=90,
    ).raise_for_status()
    print(f"  [{label}] uploaded ({len(img_bytes):,} B) → {d['filePath'][:60]}")
    return d["filePath"]


def get_audio_duration(path: Path) -> float:
    """Return duration in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "json", str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode == 0:
        return float(json.loads(result.stdout).get("format", {}).get("duration", 0))
    return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Phase A — Generate Isabela still via nano-banana-2
# ─────────────────────────────────────────────────────────────────────────────

def _submit_still(vid: dict) -> str | None:
    """Submit one nano-banana-2 still request. Returns asset_id or None."""
    label = vid["id"]

    # Upload Isabela ref fresh — filePath is consumed per-request
    isabela_bytes = prepare_image(ISABELA_REF)
    isabela_fp    = upload_image(isabela_bytes, f"{label}/isabela-ref")
    ref_images    = [isabela_fp]

    # use_scene_ref defaults True; set False when pool scene + bikini causes generation failures
    if vid.get("use_scene_ref", True):
        render_path: Path = vid["render"]
        if render_path.exists():
            try:
                scene_bytes = prepare_image(render_path)
                scene_fp    = upload_image(scene_bytes, f"{label}/scene")
                ref_images.append(scene_fp)
            except Exception as e:
                print(f"  [{label}] WARNING: scene ref upload failed ({e})")
        else:
            print(f"  [{label}] WARNING: render not found at {render_path}")
    else:
        print(f"  [{label}] skipping scene ref (use_scene_ref=False)")

    payload = {
        "productId":       PRODUCT_ID,
        "projectId":       PROJECT_ID,
        "model":           "nano-banana-2",
        "prompt":          vid["still_prompt"],
        "aspectRatio":     "9:16",
        "referenceImages": ref_images,
    }
    r = requests.post(
        f"{ARCADS_BASE}/V2/images/generate",
        headers=ARCADS_HEADERS, json=payload, timeout=30,
    )
    ts = datetime.now(timezone.utc).isoformat()
    if r.status_code not in (200, 201):
        print(f"  [{label}] STILL FAILED create: {r.status_code} {r.text[:300]}")
        log({"timestamp": ts, "step": "still_create", "id": label,
             "status": "failed", "error": r.text[:300]})
        return None

    asset_id = r.json().get("id") or r.json().get("assetId")
    print(f"  [{label}] still submitted → {asset_id}")
    log({"timestamp": ts, "step": "still_create", "id": label,
         "model": "nano-banana-2", "assetId": asset_id, "status": "pending"})
    return asset_id


def generate_still(vid: dict, _unused: str = "") -> Path | None:
    """Generate Isabela still with up to 2 attempts."""
    label    = vid["id"]
    out_path = TMP_DIR / f"{label}_still.jpg"

    if out_path.exists():
        print(f"  [{label}] still already exists, reusing {out_path.name}")
        return out_path

    for attempt_n in range(2):
        if attempt_n > 0:
            print(f"  [{label}] retrying still (attempt {attempt_n + 1})...")

        asset_id = _submit_still(vid)
        if not asset_id:
            continue

        for poll in range(120):
            time.sleep(5)
            pr = requests.get(
                f"{ARCADS_BASE}/v1/assets/{asset_id}",
                headers={"Authorization": ARCADS_AUTH}, timeout=30,
            )
            if pr.status_code != 200:
                continue
            asset  = pr.json()
            status = asset.get("status")

            if status == "generated":
                url     = asset.get("url") or asset.get("imageUrl")
                credits = asset.get("creditsCharged", "?")
                print(f"  [{label}] still DONE  credits={credits}  t={poll*5}s")
                log({"timestamp": datetime.now(timezone.utc).isoformat(),
                     "step": "still_done", "id": label, "assetId": asset_id,
                     "credits": credits, "url": url[:80]})
                out_path.write_bytes(requests.get(url, timeout=60).content)
                return out_path

            elif status == "failed":
                err = asset.get("error", str(asset)[:200])
                print(f"  [{label}] still FAILED: {err}")
                log({"timestamp": datetime.now(timezone.utc).isoformat(),
                     "step": "still_done", "id": label,
                     "status": "failed", "error": str(err)[:200]})
                break  # retry outer loop

            if poll % 6 == 0:
                print(f"  [{label}] ... still {status} (t+{poll*5}s)")
        else:
            print(f"  [{label}] still TIMEOUT on attempt {attempt_n + 1}")

    print(f"  [{label}] still exhausted all attempts")
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Phase B — ElevenLabs voiceover
# ─────────────────────────────────────────────────────────────────────────────

def generate_voice(vid: dict, voice_id: str = VOICE_PRIMARY) -> Path | None:
    label    = vid["id"]
    out_path = TMP_DIR / f"{label}_voice.mp3"

    if out_path.exists():
        dur = get_audio_duration(out_path)
        if MIN_AUDIO_SECS <= dur <= MAX_AUDIO_SECS:
            print(f"  [{label}] voice already exists ({dur:.1f}s), reusing")
            return out_path
        print(f"  [{label}] voice exists but bad duration ({dur:.1f}s), regenerating")
        out_path.unlink()

    script = vid["voice_script"]
    print(f"  [{label}] generating voice ({voice_id}) | script: {script[:60]}...")

    payload = {
        "text":           script,
        "model_id":       EL_MODEL,
        "voice_settings": VOICE_SETTINGS,
    }
    r = requests.post(
        f"{EL_BASE}/text-to-speech/{voice_id}",
        headers=EL_HEADERS, json=payload, timeout=60,
    )
    if r.status_code != 200:
        print(f"  [{label}] voice FAILED: {r.status_code} {r.text[:200]}")
        return None

    out_path.write_bytes(r.content)
    dur = get_audio_duration(out_path)
    print(f"  [{label}] voice DONE  duration={dur:.2f}s  ({len(r.content):,} B)")

    if dur < MIN_AUDIO_SECS or dur > MAX_AUDIO_SECS:
        print(f"  [{label}] WARNING: audio duration {dur:.2f}s outside [{MIN_AUDIO_SECS}, {MAX_AUDIO_SECS}]s")

    log({"timestamp": datetime.now(timezone.utc).isoformat(),
         "step": "voice", "id": label, "voice_id": voice_id,
         "duration_s": dur, "bytes": len(r.content)})
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# Phase C — Animate still with Arcads veo31
# ─────────────────────────────────────────────────────────────────────────────

def animate_veo31(vid: dict, still_path: Path) -> Path | None:
    label    = vid["id"]
    out_path = TMP_DIR / f"{label}_raw.mp4"

    if out_path.exists():
        print(f"  [{label}] raw video already exists, reusing {out_path.name}")
        return out_path

    # Upload start frame
    print(f"  [{label}] uploading start frame to Arcads...")
    img_bytes = prepare_image(still_path)
    start_fp  = upload_image(img_bytes, f"{label}/start-frame")

    payload = {
        "model":       "veo31",
        "productId":   PRODUCT_ID,
        "projectId":   PROJECT_ID,
        "prompt":      vid["animation_prompt"],
        "aspectRatio": "9:16",
        "resolution":  "720p",
        "startFrame":  start_fp,
    }
    r = requests.post(
        f"{ARCADS_BASE}/v2/videos/generate",
        headers=ARCADS_HEADERS, json=payload, timeout=30,
    )
    ts = datetime.now(timezone.utc).isoformat()
    if r.status_code not in (200, 201):
        print(f"  [{label}] veo31 FAILED create: {r.status_code} {r.text[:300]}")
        log({"timestamp": ts, "step": "veo31_create", "id": label,
             "status": "failed", "error": r.text[:300]})
        return None

    data     = r.json()
    asset_id = data.get("id") or data.get("assetId") or data.get("videoId")
    print(f"  [{label}] veo31 submitted → {asset_id}")
    log({"timestamp": ts, "step": "veo31_create", "id": label,
         "model": "veo31", "assetId": asset_id, "status": "pending"})

    start_t = time.time()
    for attempt in range(240):
        time.sleep(5)
        pr = requests.get(
            f"{ARCADS_BASE}/v1/assets/{asset_id}",
            headers={"Authorization": ARCADS_AUTH}, timeout=30,
        )
        if pr.status_code != 200:
            continue
        asset  = pr.json()
        status = asset.get("status")

        if status == "generated":
            url     = asset.get("url") or asset.get("videoUrl")
            credits = asset.get("creditsCharged", "?")
            elapsed = int(time.time() - start_t)
            print(f"  [{label}] veo31 DONE  credits={credits}  t={elapsed}s")
            log({"timestamp": datetime.now(timezone.utc).isoformat(),
                 "step": "veo31_done", "id": label, "assetId": asset_id,
                 "credits": credits, "url": url[:80]})

            print(f"  [{label}] downloading raw video...")
            vr = requests.get(url, timeout=120, allow_redirects=True)
            out_path.write_bytes(vr.content)
            size_mb = len(vr.content) / 1_048_576
            print(f"  [{label}] raw video saved → {out_path.name} ({size_mb:.1f} MB)")
            return out_path

        elif status == "failed":
            err = asset.get("error", str(asset)[:300])
            print(f"  [{label}] veo31 FAILED: {err}")
            log({"timestamp": datetime.now(timezone.utc).isoformat(),
                 "step": "veo31_done", "id": label, "status": "failed", "error": err})
            return None

        if attempt % 12 == 0:
            elapsed = int(time.time() - start_t)
            print(f"  [{label}] ... veo31 {status} (t+{elapsed}s)")

    print(f"  [{label}] veo31 TIMEOUT")
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Phase D — ffmpeg compose: scale + extend + audio + color grade
# ─────────────────────────────────────────────────────────────────────────────

ARIAL_FONT = "C:/Windows/Fonts/arialbd.ttf"   # available on this system

def compose_ffmpeg(vid: dict, video_path: Path, audio_path: Path) -> Path | None:
    label      = vid["id"]
    final_path = OUTPUT_DIR / vid["filename"]

    audio_dur  = get_audio_duration(audio_path)
    # Use audio as master timeline; clamp output to [10.5, 13.5]s
    target_dur = max(min(audio_dur, 13.5), 10.5)

    # Warm tropical color grade
    color_grade = (
        "eq=brightness=0.02:contrast=1.05:saturation=1.12,"
        "curves=r='0/0 0.5/0.54 1/1':g='0/0 0.5/0.51 1/0.98':b='0/0 0.5/0.47 1/0.94'"
    )

    # Extend video to at least target_dur by cloning last frame, then scale+grade
    # tpad stop_duration pads EXTRA seconds beyond original length
    pad_extra = target_dur + 2.0   # generous pad; -t will trim to exact duration
    video_filter = (
        f"scale=1080:1920:flags=lanczos,"
        f"fps=30,"
        f"tpad=stop_mode=clone:stop_duration={pad_extra:.2f},"
        f"{color_grade}"
    )

    if vid["id"] == "v4":
        # Text overlay: escape colon in Windows drive path, drop alpha expr (not needed)
        safe_font = ARIAL_FONT.replace(":", "\\:")
        video_filter += (
            f",drawtext=fontfile='{safe_font}':"
            f"text='Augusta at Country Lakes':"
            f"fontsize=52:fontcolor=white@0.92:x=(w-text_w)/2:y=h-200:"
            f"shadowcolor=black:shadowx=2:shadowy=2:"
            f"enable='between(t\\,10.5\\,{target_dur:.2f})'"
        )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),      # input 0: animated video (may have embedded audio)
        "-i", str(audio_path),      # input 1: ElevenLabs voiceover
        "-map", "0:v:0",            # use only video from veo31 clip
        "-map", "1:a:0",            # use only voiceover audio — ignore embedded veo31 audio
        "-vf", video_filter,
        "-t", f"{target_dur:.3f}",  # trim output to exact target duration
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-ac", "2",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-movflags", "+faststart",
        str(final_path),
    ]

    print(f"  [{label}] ffmpeg compose → {vid['filename']}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        print(f"  [{label}] ffmpeg FAILED:\n{result.stderr[-600:]}")
        return None

    real_dur = get_audio_duration(final_path)
    size_mb  = final_path.stat().st_size / 1_048_576
    print(f"  [{label}] compose DONE  duration={real_dur:.2f}s  size={size_mb:.1f} MB")

    if not (10.0 <= real_dur <= 12.5):
        print(f"  [{label}] WARNING: final duration {real_dur:.2f}s outside spec [10.0, 12.5]s")

    log({"timestamp": datetime.now(timezone.utc).isoformat(),
         "step": "compose_done", "id": label,
         "final_path": str(final_path), "duration_s": real_dur, "size_mb": size_mb})

    return final_path


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    # Validate required files
    missing = []
    for p, name in [(ISABELA_REF, "Isabela ref"), (RENDER_POOL, "ACCESO CASA CLUB"),
                    (RENDER_ENTRANCE, "ACCESO"), (RENDER_AERIAL, "AUGUSTA_AEREO CC")]:
        if not p.exists():
            missing.append(f"{name}: {p}")
    if missing:
        print("ERROR — archivos requeridos no encontrados:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)

    print("=" * 72)
    print("  Augusta at Country Lakes — 4 Videos Verticales con Isabela")
    print(f"  Voice: Marlene (JYyJjNPfmNJdaby8LdZs) · Model: {EL_MODEL}")
    print(f"  Animation: Arcads veo31 · Still: nano-banana-2")
    print(f"  Output: {OUTPUT_DIR}")
    print("=" * 72)

    # Verify Isabela ref exists (uploaded fresh per-video inside generate_still)
    if not ISABELA_REF.exists():
        print(f"ERROR: Isabela reference not found: {ISABELA_REF}")
        sys.exit(1)
    print(f"\nIsabela ref verified: {ISABELA_REF.name}")
    checkpoint("Isabela ref path verified")

    t0_total = time.time()

    for vid in VIDEOS:
        print(f"\n{'─' * 72}")
        print(f"  {vid['label']}")
        print(f"{'─' * 72}")
        t0_vid = time.time()
        vid_meta = {"id": vid["id"], "filename": vid["filename"]}

        # ── Phase A: Still ────────────────────────────────────────────────────
        if vid["use_isabela_in_still"]:
            print(f"\n[A] Generating Isabela still (nano-banana-2)...")
            still_path = generate_still(vid)
            if still_path is None:
                print(f"  STOP — still generation failed for {vid['id']}. Skipping video.")
                vid_meta["status"] = "failed_still"
                manifest_data["videos"].append(vid_meta)
                continue
            checkpoint("Still generated", still_path.name)
        else:
            # V4: use the render directly as start frame
            still_path = vid["render"]
            print(f"[A] Using render directly as start frame: {still_path.name}")
            checkpoint("Start frame ready", still_path.name)

        # ── Phase B: Voice ────────────────────────────────────────────────────
        print(f"\n[B] Generating ElevenLabs voiceover...")
        voice_path = generate_voice(vid, VOICE_PRIMARY)
        if voice_path is None:
            print(f"  Retrying with fallback voice {VOICE_FALLBACK}...")
            voice_path = generate_voice(vid, VOICE_FALLBACK)
        if voice_path is None:
            print(f"  STOP — voice generation failed for {vid['id']}. Skipping video.")
            vid_meta["status"] = "failed_voice"
            manifest_data["videos"].append(vid_meta)
            continue
        checkpoint("Voiceover generated", voice_path.name,
                   f"{get_audio_duration(voice_path):.2f}s")

        # ── Phase C: Animate ──────────────────────────────────────────────────
        print(f"\n[C] Animating with Arcads veo31...")
        raw_path = animate_veo31(vid, still_path)
        if raw_path is None:
            print(f"  STOP — animation failed for {vid['id']}. Skipping video.")
            vid_meta["status"] = "failed_animation"
            manifest_data["videos"].append(vid_meta)
            continue
        checkpoint("Animation complete", raw_path.name)

        # ── Phase D: Compose ──────────────────────────────────────────────────
        print(f"\n[D] Composing final video with ffmpeg...")
        final_path = compose_ffmpeg(vid, raw_path, voice_path)
        if final_path is None:
            print(f"  STOP — ffmpeg compose failed for {vid['id']}.")
            vid_meta["status"] = "failed_compose"
            manifest_data["videos"].append(vid_meta)
            continue

        elapsed = int(time.time() - t0_vid)
        real_dur = get_audio_duration(final_path)
        vid_meta.update({
            "status":        "completed",
            "path":          str(final_path),
            "duration_s":    round(real_dur, 2),
            "size_mb":       round(final_path.stat().st_size / 1_048_576, 1),
            "voice_id":      VOICE_PRIMARY,
            "elapsed_s":     elapsed,
        })
        manifest_data["videos"].append(vid_meta)
        checkpoint(f"Video {vid['id']} listo", str(final_path), f"{elapsed}s")

    # ── Manifest ──────────────────────────────────────────────────────────────
    total_elapsed = int(time.time() - t0_total)
    manifest_data["total_elapsed_s"] = total_elapsed
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False))

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("  RESUMEN FINAL")
    print("=" * 72)
    completed = [v for v in manifest_data["videos"] if v.get("status") == "completed"]
    print(f"  Videos completados: {len(completed)}/4")
    for v in manifest_data["videos"]:
        icon = "✅" if v.get("status") == "completed" else "❌"
        dur  = f"{v['duration_s']}s" if "duration_s" in v else "—"
        print(f"  {icon} {v['filename']}  {dur}")
    print(f"\n  Manifest: {manifest_path}")
    print(f"  Tiempo total: {total_elapsed}s")
    print("=" * 72)
    print("\nNOTA: Costo API estimado desglosado:")
    print("  · nano-banana-2 stills (3×): ~$1–3 USD en créditos Arcads")
    print("  · veo31 animaciones (4×):    ~$20–35 USD en créditos Arcads")
    print("  · ElevenLabs TTS (4×):       <$0.50 USD")
    print("  · TOTAL estimado:            ~$22–39 USD")
    print("\nNEXT: Revisar videos en ./output/augusta/ antes de publicar.")


if __name__ == "__main__":
    main()
