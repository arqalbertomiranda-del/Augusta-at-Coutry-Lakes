# -*- coding: utf-8 -*-
"""
Augusta at Country Lakes — 10 UGC Scenes (Isabela)
===================================================
Genera 10 escenas UGC completas en 3 fases:

  Phase 1 (Still)     : nano-banana-2  →  still 9:16 por escena
  Phase 2 (Animation) : Arcads veo31   →  video 9:16 por escena
  Phase 3 (Voiceover) : ElevenLabs Jessica  →  audio .mp3 por escena
  Phase 4 (Combine)   : ffmpeg          →  reel final .mp4 por escena

Output: outputs/ugc-10-scenes-{date}/scene-{N:02d}-{id}/
        └── still.jpg
        └── video_raw.mp4
        └── voiceover.mp3
        └── reel.mp4          ← entregable final

Resume: si reel.mp4 ya existe para una escena, la omite.

Uso:
  python 05_ugc_10_scenes.py                   # todas las escenas
  python 05_ugc_10_scenes.py --only 1 3 7      # solo escenas 1, 3 y 7
  python 05_ugc_10_scenes.py --from-scene 5    # desde escena 5 en adelante
"""

import os
import sys
import argparse
import json
import time
import io
import subprocess
import requests
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

# ── Credenciales (desde .env — ver .env.example) ───────────────────────────────
ARCADS_AUTH        = os.environ["ARCADS_AUTH"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]

ARCADS_BASE = "https://external-api.arcads.ai"
EL_BASE     = "https://api.elevenlabs.io/v1"
PRODUCT_ID  = "3c7125f2-de97-4587-99b7-405e80d93f90"
PROJECT_ID  = "105d6a6b-c65e-40de-aefb-9b52da56d3e2"

ARCADS_HEADERS = {"Authorization": ARCADS_AUTH, "Content-Type": "application/json"}
EL_HEADERS     = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT  = SCRIPT_DIR.parent
TODAY      = datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = REPO_ROOT / "outputs" / f"ugc-10-scenes-{TODAY}"
LOG_FILE   = REPO_ROOT / "logs" / "arcads-api.jsonl"

ISABELA_REF = Path(
    r"C:\Users\alber\Boma Desarrollos\Arrecife Sisal - Documentos"
    r"\10.0 Mercadotecnia\Videos de Claude Code - Arrecife"
    r"\references\influencers\isabela-dark-brunette-straight-green-eyes-fair"
    r"\01-hero-front.jpg"
)

RENDERS = {
    "pool": Path(
        r"C:\Users\alber\Boma Desarrollos\Augusta at Country Lakes - Documentos"
        r"\02. Alcances\02.13 Renders\Arquitectonicos\ACCESO CASA CLUB.jpg"
    ),
    "entrance": Path(
        r"C:\Users\alber\Boma Desarrollos\Augusta at Country Lakes - Documentos"
        r"\02. Alcances\02.13 Renders\Arquitectonicos\ACCESO.jpg"
    ),
}

# ── ElevenLabs Voice ───────────────────────────────────────────────────────────
VOICE_ID = "cgSgspJ2msm6clMCkdW9"  # Jessica
VOICE_SETTINGS = {
    "stability": 0.38,
    "similarity_boost": 0.82,
    "style": 0.35,
    "use_speaker_boost": True,
}

# ── Identidad Isabela ──────────────────────────────────────────────────────────
ISABELA_BASE = (
    "A 27-year-old woman of astonishing beauty: long silky straight dark chestnut-brown hair "
    "falling past her mid-back with healthy shine, large captivating green eyes with luminous "
    "depth, porcelain-fair flawless skin with natural visible pores and warm subtle undertone, "
    "perfectly arched full dark brows, a charmingly upturned refined nose, a flawlessly "
    "sculpted angular jaw, full lips with a defined cupid's bow, athletic tall figure "
    "approximately 175cm, generous naturally lifted bust, narrow cinched waist. "
    "Minimal old-money makeup — luminous bare skin, barely-there gloss."
)

# ── 10 UGC Scenes ─────────────────────────────────────────────────────────────
SCENES = [
    # ── 01 ───────────────────────────────────────────────────────────────────
    {
        "n": 1,
        "id": "llegada-acceso",
        "render": "entrance",
        "still_prompt": (
            "Photorealistic luxury real estate lifestyle portrait. " + ISABELA_BASE +
            " She wears a sleeveless white linen maxi dress with a deep V-neckline, "
            "flowing fabric, Jacquemus aesthetic. Strappy tan leather sandals. "
            "Fine delicate gold chain necklace, small gold hoop earrings. "
            "Long straight dark hair loose, caught by a light tropical breeze. "
            "She pauses under a carved wooden pergola archway at the entrance of an exclusive "
            "private luxury golf community. Cobblestone circular roundabout in front. "
            "Low warm cream-stucco building, lush tropical landscaping: monstera, palms, ornamental grasses. "
            "Brilliant sunny day. She touches her sunglasses lightly with one hand, "
            "half-smile, three-quarter angle toward camera. "
            "No text, no watermarks. Ultra-photorealistic, visible skin texture."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic video. "
            "An elegant woman in a flowing white linen dress pauses under a carved wooden pergola "
            "at the entrance of a luxury private estate. "
            "She slowly removes her sunglasses, looks up at the pergola, gentle confident smile. "
            "Light tropical breeze moves her dress hem and hair softly. "
            "Warm golden afternoon light. Camera holds steady. "
            "Vertical 9:16. No text, no subtitles, no watermarks."
        ),
        "voiceover": (
            "Cuando llegás aquí, sentís que el mundo se queda afuera. "
            "Augusta at Country Lakes. "
            "La privada más exclusiva frente al mejor campo de golf de Latinoamérica."
        ),
    },
    # ── 02 ───────────────────────────────────────────────────────────────────
    {
        "n": 2,
        "id": "camastro-alberca",
        "render": "pool",
        "still_prompt": (
            "Photorealistic luxury resort lifestyle portrait. " + ISABELA_BASE +
            " She reclines on a white linen-covered sun lounger beside a long infinity pool. "
            "She wears a white structured one-shoulder swimsuit, sheer white sarong tied loosely "
            "at her hip. One arm rests above her head, the other holds a cold glass of sparkling "
            "water with condensation droplets. Eyes closed, serene expression, lips softly parted. "
            "Polished travertine pool deck, crisp white canvas umbrellas, lush tall coconut palms. "
            "Beyond the pool: a low modern cream-stucco clubhouse. Golden hour warm light. "
            "No text, no watermarks. Ultra-photorealistic, individual hair strands in the light."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic video. "
            "A beautiful woman in a white one-shoulder swimsuit reclines on a sun lounger "
            "beside a luxury infinity pool. "
            "Gentle breeze moves her sheer white sarong. Her chest rises slowly with a deep breath. "
            "Palm fronds sway softly in the background. Pool water shimmers in warm golden light. "
            "Serene, slow. Camera holds with a gentle drift upward. "
            "Vertical 9:16. No text, no subtitles, no watermarks."
        ),
        "voiceover": (
            "El campo de golf de Greg Letsche al fondo. La alberca enfrente. "
            "Y 36 meses sin intereses para que esto sea tuyo. "
            "Augusta at Country Lakes."
        ),
    },
    # ── 03 ───────────────────────────────────────────────────────────────────
    {
        "n": 3,
        "id": "borde-alberca",
        "render": "pool",
        "still_prompt": (
            "Photorealistic luxury real estate lifestyle portrait. " + ISABELA_BASE +
            " She stands at the very edge of a long infinity pool overlooking a manicured golf course. "
            "She wears a white linen halter dress, deep open neckline, dress grazing her ankles. "
            "Thin gold bracelet on her wrist, no other jewelry. "
            "Long dark hair pinned loosely, a few strands loose in the breeze. "
            "Her back is mostly to camera; she turns her head over her shoulder "
            "to look directly into the lens — magnetic, self-assured. "
            "Bright afternoon sky, tall coconut palms, white travertine architecture. "
            "No text, no watermarks. Ultra-photorealistic."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic video. "
            "An elegant woman in a white linen halter dress stands at the edge of a luxury infinity pool. "
            "She slowly turns from looking at the golf course to face the camera directly, "
            "a quiet confident expression. Her dress and loose hair strands move with the breeze. "
            "Pool water shimmers. Warm afternoon light. Camera holds steady. "
            "Vertical 9:16. No text, no subtitles, no watermarks."
        ),
        "voiceover": (
            "Augusta at Country Lakes. "
            "Frente al mejor campo de golf de Latinoamérica, diseñado por Greg Letsche. "
            "Preventa activa, por tiempo limitado."
        ),
    },
    # ── 04 ───────────────────────────────────────────────────────────────────
    {
        "n": 4,
        "id": "cafe-manana",
        "render": "pool",
        "still_prompt": (
            "Photorealistic luxury lifestyle portrait, intimate morning scene. " + ISABELA_BASE +
            " She sits at an elegant outdoor table on a travertine terrace, morning light. "
            "She wears a white silk slip dress, thin straps, minimal and fluid. "
            "She holds a small espresso cup with both hands, looking out toward the lush golf course "
            "with a contemplative, content smile. "
            "Dark hair falls naturally over one shoulder. Single delicate gold ring on one hand. "
            "Tropical plants frame the scene, soft warm morning light filtering through palms. "
            "Candid feel, editorial quality. "
            "No text, no watermarks. Ultra-photorealistic."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic video. "
            "An elegant woman in a white silk slip dress sits at an outdoor terrace table with an espresso. "
            "She gently sets down the cup, leans back in her chair, exhales a slow contented breath "
            "while looking out at a golf course. Morning light through palm leaves. "
            "Tropical birds faintly audible. Camera holds steady. "
            "Vertical 9:16. No text, no subtitles, no watermarks."
        ),
        "voiceover": (
            "Despertar aquí no es un lujo. Es una decisión. "
            "Augusta at Country Lakes. Preventa con financiamiento a 180 meses."
        ),
    },
    # ── 05 ───────────────────────────────────────────────────────────────────
    {
        "n": 5,
        "id": "lobby-abierto",
        "render": "entrance",
        "still_prompt": (
            "Photorealistic luxury real estate lifestyle portrait. " + ISABELA_BASE +
            " She walks confidently through an open-air clubhouse pavilion: "
            "white travertine floors, exposed wooden beam ceiling, "
            "lush garden visible through the open sides. "
            "She wears a white structured linen blazer dress, deep V-neckline, belted loosely. "
            "Oversized cream designer sunglasses. She carries nothing. "
            "Full body shot, camera slightly low, stride relaxed and assured, chin slightly lifted. "
            "Bright tropical day light filtering through the structure. "
            "No text, no watermarks. Ultra-photorealistic."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic video. "
            "An elegant woman in a white blazer dress walks through an open-air luxury clubhouse. "
            "She walks slowly toward camera, heels click softly on travertine. "
            "She pauses mid-stride, tilts her chin slightly and looks directly at camera. "
            "Warm dappled light through wooden beams. Tropical greenery sways gently outside. "
            "Camera holds at low angle. "
            "Vertical 9:16. No text, no subtitles, no watermarks."
        ),
        "voiceover": (
            "Hay lugares que te hacen sentir quien eres. "
            "Augusta at Country Lakes es uno de ellos. "
            "Privada exclusiva, frente al campo de Country Lakes."
        ),
    },
    # ── 06 ───────────────────────────────────────────────────────────────────
    {
        "n": 6,
        "id": "coctel-atardecer",
        "render": "pool",
        "still_prompt": (
            "Photorealistic luxury lifestyle portrait, dusk scene. " + ISABELA_BASE +
            " She stands near an outdoor pool bar at golden hour, just past sunset. "
            "She wears a white asymmetric wrap dress — one shoulder exposed, fabric draping elegantly. "
            "She holds a crystal highball glass with a clear cocktail, mint and ice. "
            "Thin gold chain necklace, barely visible. "
            "Outdoor Edison string lights beginning to glow behind her. "
            "Expression: self-assured, slightly playful, looking directly at camera. "
            "Warm amber and blue dusk sky. Infinity pool reflects the last light. "
            "Rich cinematic depth of field. "
            "No text, no watermarks. Ultra-photorealistic."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic video. "
            "An elegant woman in a white asymmetric dress stands at an outdoor pool bar at dusk, "
            "holding a crystal cocktail glass. "
            "She raises the glass slightly, glances at it with a subtle smile, "
            "then looks back to camera. Pool lights begin glowing behind her. "
            "Warm amber light fading to blue dusk. Camera holds steady. "
            "Vertical 9:16. No text, no subtitles, no watermarks."
        ),
        "voiceover": (
            "Entrega julio 2028. Tiempo suficiente para planear exactamente cómo va a verse esto. "
            "Augusta at Country Lakes. Inversión de largo plazo."
        ),
    },
    # ── 07 ───────────────────────────────────────────────────────────────────
    {
        "n": 7,
        "id": "leyendo-camastro",
        "render": "pool",
        "still_prompt": (
            "Photorealistic luxury resort lifestyle portrait. " + ISABELA_BASE +
            " She lies on her stomach on a sun lounger, propped up on her elbows, "
            "reading a hardcover book. "
            "She wears a white bandeau bikini top and high-waisted white linen shorts. "
            "Dark hair cascades forward over one shoulder. Barefoot. "
            "A small structured designer bag on the travertine deck beside her. "
            "Infinity pool and tall coconut palms behind her. "
            "Afternoon light, vivid blue sky. Candid, editorial feel. "
            "No text, no watermarks. Ultra-photorealistic."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic video. "
            "An elegant woman in a white bandeau bikini top lies on a poolside sun lounger reading. "
            "She slowly flips a page, then looks up from the book directly to camera with a half-smile. "
            "Gentle breeze moves her hair. Palm fronds sway. Pool water glitters. "
            "Warm afternoon sun. Camera holds steady. "
            "Vertical 9:16. No text, no subtitles, no watermarks."
        ),
        "voiceover": (
            "No todo el mundo tiene esto. Pero podría. "
            "Augusta at Country Lakes. Preventa activa, 36 meses sin intereses."
        ),
    },
    # ── 08 ───────────────────────────────────────────────────────────────────
    {
        "n": 8,
        "id": "vista-golf",
        "render": "pool",
        "still_prompt": (
            "Photorealistic luxury real estate lifestyle portrait. " + ISABELA_BASE +
            " She stands at a low polished travertine terrace wall, forearms resting on top, "
            "looking out across an immaculate golf course at dusk. "
            "She wears a white sleeveless button-front linen dress, top two buttons open, "
            "soft fabric grazing her knees. Gold minimal ear cuffs. "
            "Behind her: the white modern clubhouse architecture. "
            "Before her: perfectly manicured fairways and distant palms. "
            "Warm orange and purple dusk sky. "
            "Her expression: serene, proud, belonging. "
            "No text, no watermarks. Ultra-photorealistic."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic video. "
            "An elegant woman in a white linen dress stands at a terrace wall overlooking a luxury golf course at dusk. "
            "She takes a slow deep breath, her posture relaxed and serene. "
            "She turns her face 30 degrees toward camera, a soft smile, then looks back to the fairway. "
            "Hair moves gently. Warm dusk light on skin. Camera holds with slow drift. "
            "Vertical 9:16. No text, no subtitles, no watermarks."
        ),
        "voiceover": (
            "Greg Letsche diseñó este campo. Artigas diseñó la privada. "
            "Yo elegí vivir aquí. Augusta at Country Lakes."
        ),
    },
    # ── 09 ───────────────────────────────────────────────────────────────────
    {
        "n": 9,
        "id": "carrito-golf",
        "render": "entrance",
        "still_prompt": (
            "Photorealistic luxury lifestyle portrait. " + ISABELA_BASE +
            " She steps gracefully out of a white golf cart that has just stopped "
            "on the cobblestone roundabout at the entrance of a luxury private estate. "
            "She wears a white pleated mini dress, structured, slight ruffle at the hem. "
            "Gold anklet on one foot, cream low-heeled mules. "
            "Oversized designer sunglasses. She steps onto the cobblestone, "
            "one hand resting lightly on the cart, looking toward the clubhouse entrance. "
            "Tall palms, carved wooden pergola in background. Bright tropical day. "
            "No text, no watermarks. Ultra-photorealistic."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic video. "
            "An elegant woman in a white pleated mini dress steps out of a white golf cart "
            "on a cobblestone roundabout at a luxury estate entrance. "
            "Her dress swings as she steps out. She pushes her sunglasses up "
            "and turns her gaze toward the clubhouse, confident and unhurried. "
            "Tropical palms in background. Bright sun. Camera holds steady. "
            "Vertical 9:16. No text, no subtitles, no watermarks."
        ),
        "voiceover": (
            "Así se ve vivir en la privada más exclusiva de Country Lakes. "
            "Augusta at Country Lakes. Tu nueva dirección."
        ),
    },
    # ── 10 ───────────────────────────────────────────────────────────────────
    {
        "n": 10,
        "id": "pies-alberca",
        "render": "pool",
        "still_prompt": (
            "Photorealistic luxury resort lifestyle portrait. " + ISABELA_BASE +
            " She sits on the very edge of an infinity pool, legs dangling over the side, "
            "feet submerged just below the surface. "
            "She leans back on her hands, head tilted back slightly, "
            "eyes half-closed, soaking up golden afternoon sun. "
            "She wears a white structured bandeau swimsuit with a thin gold clasp detail at center. "
            "Long dark hair draped over one shoulder. "
            "The infinity pool extends behind her toward tall coconut palms and a lush golf course. "
            "Pure white travertine. Brilliant golden afternoon light. Absolutely serene. "
            "No text, no watermarks. Ultra-photorealistic."
        ),
        "animation_prompt": (
            "Animate this photograph into a cinematic video. "
            "An elegant woman in a white bandeau swimsuit sits at the edge of a luxury infinity pool, "
            "feet submerged, head tilted back in the sun. "
            "She slowly brings her head forward, opens her eyes, "
            "and looks directly and calmly to camera. "
            "Water ripples gently around her feet. Palm fronds sway. Golden afternoon light. "
            "Camera holds steady. "
            "Vertical 9:16. No text, no subtitles, no watermarks."
        ),
        "voiceover": (
            "Preventa activa. Financiamiento a 36 meses sin intereses "
            "más crédito hipotecario a 180 meses. "
            "Augusta at Country Lakes. augustacountrylakes.mx"
        ),
    },
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def log_entry(entry: dict) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def prepare_image(path: Path) -> bytes:
    if not HAS_PIL:
        return path.read_bytes()
    img = Image.open(path).convert("RGB")
    w, h = img.size
    if max(w, h) < 1024:
        scale = 1080 / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def upload_image(img_bytes: bytes, label: str) -> str:
    r = requests.post(
        f"{ARCADS_BASE}/v1/file-upload/get-presigned-url",
        headers=ARCADS_HEADERS,
        json={"fileType": "image/jpeg"},
        timeout=30,
    )
    r.raise_for_status()
    d = r.json()
    requests.put(
        d["presignedUrl"],
        data=img_bytes,
        headers={"Content-Type": "image/jpeg"},
        timeout=60,
    ).raise_for_status()
    print(f"    [{label}] uploaded ({len(img_bytes):,} B)")
    return d["filePath"]


# ── Phase 1: Still ─────────────────────────────────────────────────────────────

def generate_still(scene: dict, scene_dir: Path) -> Path | None:
    label = f"S{scene['n']:02d}-{scene['id']}"
    out   = scene_dir / "still.jpg"

    if out.exists():
        print(f"  [{label}] still already exists, skipping Phase 1")
        return out

    # Re-upload Isabela reference fresh for each scene — Arcads filePaths expire quickly
    print(f"  [{label}] uploading Isabela reference...")
    isabela_path = upload_image(prepare_image(ISABELA_REF), f"{label}/isabela")
    ref_paths = [isabela_path]

    render_key = scene.get("render")
    if render_key and render_key in RENDERS and RENDERS[render_key].exists():
        try:
            scene_bytes = prepare_image(RENDERS[render_key])
            scene_path  = upload_image(scene_bytes, f"{label}/render")
            ref_paths.append(scene_path)
        except Exception as e:
            print(f"  [{label}] WARNING: render upload failed ({e})")

    payload = {
        "productId":       PRODUCT_ID,
        "projectId":       PROJECT_ID,
        "model":           "nano-banana-2",
        "prompt":          scene["still_prompt"],
        "aspectRatio":     "9:16",
        "referenceImages": ref_paths,
    }
    r  = requests.post(f"{ARCADS_BASE}/V2/images/generate", headers=ARCADS_HEADERS, json=payload, timeout=30)
    ts = datetime.now(timezone.utc).isoformat()

    if r.status_code not in (200, 201):
        log_entry({"timestamp": ts, "scene": label, "phase": "still", "status": "failed_create", "error": r.text[:300]})
        print(f"  [{label}] FAILED to submit still: {r.status_code}")
        return None

    data     = r.json()
    asset_id = data.get("id") or data.get("assetId")
    print(f"  [{label}] still submitted → {asset_id}")
    log_entry({"timestamp": ts, "scene": label, "phase": "still", "model": "nano-banana-2",
               "assetId": asset_id, "status": "pending"})

    for attempt in range(120):
        time.sleep(5)
        pr = requests.get(f"{ARCADS_BASE}/v1/assets/{asset_id}",
                          headers={"Authorization": ARCADS_AUTH}, timeout=30)
        if pr.status_code != 200:
            continue
        asset  = pr.json()
        status = asset.get("status")
        if status == "generated":
            url     = asset.get("url") or asset.get("imageUrl")
            credits = asset.get("creditsCharged", "?")
            elapsed = attempt * 5
            print(f"  [{label}] still DONE  credits={credits}  t={elapsed}s")
            log_entry({"timestamp": datetime.now(timezone.utc).isoformat(), "scene": label,
                       "phase": "still", "assetId": asset_id,
                       "status": "generated", "credits": credits, "url": url})
            img_r = requests.get(url, timeout=60)
            out.write_bytes(img_r.content)
            print(f"  [{label}] still saved → {out.name}")
            return out
        elif status == "failed":
            err = asset.get("error") or str(asset)[:300]
            print(f"  [{label}] still FAILED: {err}")
            return None
        else:
            if attempt % 6 == 0:
                print(f"  [{label}] still ... {status} (t+{attempt*5}s)")

    print(f"  [{label}] still TIMEOUT")
    return None


# ── Phase 2: Animation (veo31) ─────────────────────────────────────────────────

def animate_veo31(scene: dict, still_path: Path, scene_dir: Path) -> Path | None:
    label  = f"S{scene['n']:02d}-{scene['id']}"
    out    = scene_dir / "video_raw.mp4"

    if out.exists():
        print(f"  [{label}] video_raw already exists, skipping Phase 2")
        return out

    start_frame = upload_image(prepare_image(still_path), f"{label}/start-frame")

    payload = {
        "model":       "veo31",
        "productId":   PRODUCT_ID,
        "projectId":   PROJECT_ID,
        "prompt":      scene["animation_prompt"],
        "aspectRatio": "9:16",
        "resolution":  "720p",
        "startFrame":  start_frame,
    }
    r  = requests.post(f"{ARCADS_BASE}/v2/videos/generate", headers=ARCADS_HEADERS, json=payload, timeout=30)
    ts = datetime.now(timezone.utc).isoformat()

    if r.status_code not in (200, 201):
        log_entry({"timestamp": ts, "scene": label, "phase": "veo31", "status": "failed_create", "error": r.text[:300]})
        print(f"  [{label}] FAILED to submit veo31: {r.status_code} — {r.text[:200]}")
        return None

    data     = r.json()
    asset_id = data.get("id") or data.get("assetId") or data.get("videoId")
    print(f"  [{label}] veo31 submitted → {asset_id}")
    log_entry({"timestamp": ts, "scene": label, "phase": "veo31", "model": "veo31",
               "assetId": asset_id, "status": "pending"})

    start = time.time()
    for attempt in range(180):
        time.sleep(5)
        pr = requests.get(f"{ARCADS_BASE}/v1/assets/{asset_id}",
                          headers={"Authorization": ARCADS_AUTH}, timeout=30)
        if pr.status_code != 200:
            continue
        asset  = pr.json()
        status = asset.get("status")
        if status == "generated":
            url     = asset.get("url") or asset.get("videoUrl")
            credits = asset.get("creditsCharged", "?")
            elapsed = int(time.time() - start)
            print(f"  [{label}] veo31 DONE  credits={credits}  t={elapsed}s")
            log_entry({"timestamp": datetime.now(timezone.utc).isoformat(), "scene": label,
                       "phase": "veo31", "assetId": asset_id,
                       "status": "generated", "credits": credits, "url": url})
            vr = requests.get(url, timeout=120, allow_redirects=True)
            out.write_bytes(vr.content)
            print(f"  [{label}] video saved → {out.name}  ({len(vr.content)/1_048_576:.1f} MB)")
            return out
        elif status == "failed":
            err = asset.get("error") or str(asset)[:300]
            print(f"  [{label}] veo31 FAILED: {err}")
            return None
        else:
            elapsed = int(time.time() - start)
            if attempt % 12 == 0:
                print(f"  [{label}] veo31 ... {status} (t+{elapsed}s)")

    print(f"  [{label}] veo31 TIMEOUT")
    return None


# ── Phase 3: Voiceover ─────────────────────────────────────────────────────────

def generate_voiceover(scene: dict, scene_dir: Path) -> Path | None:
    label = f"S{scene['n']:02d}-{scene['id']}"
    out   = scene_dir / "voiceover.mp3"

    if out.exists():
        print(f"  [{label}] voiceover already exists, skipping Phase 3")
        return out

    payload = {
        "text":           scene["voiceover"],
        "model_id":       "eleven_multilingual_v2",
        "voice_settings": VOICE_SETTINGS,
    }
    r = requests.post(
        f"{EL_BASE}/text-to-speech/{VOICE_ID}",
        headers=EL_HEADERS, json=payload, timeout=60,
    )
    if r.status_code != 200:
        print(f"  [{label}] voiceover FAILED: {r.status_code} {r.text[:200]}")
        return None

    out.write_bytes(r.content)
    print(f"  [{label}] voiceover saved → {out.name}  ({len(r.content):,} B)")
    return out


# ── Phase 4: Combine ───────────────────────────────────────────────────────────

def combine(scene: dict, video_path: Path, audio_path: Path, scene_dir: Path) -> Path | None:
    label = f"S{scene['n']:02d}-{scene['id']}"
    out   = scene_dir / "reel.mp4"

    if out.exists():
        print(f"  [{label}] reel already exists, skipping Phase 4")
        return out

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size_mb = out.stat().st_size / 1_048_576
        print(f"  [{label}] reel DONE → {out.name}  ({size_mb:.1f} MB)")
        return out
    else:
        print(f"  [{label}] ffmpeg FAILED:\n{result.stderr[-400:]}")
        return None


# ── Main ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate 10 Augusta UGC scenes")
    p.add_argument("--only",        nargs="+", type=int, metavar="N",
                   help="Run only scene numbers (e.g. --only 1 3 7)")
    p.add_argument("--from-scene",  type=int,  metavar="N",
                   help="Start from scene N (inclusive)")
    return p.parse_args()


def filter_scenes(scenes: list[dict], args: argparse.Namespace) -> list[dict]:
    if args.only:
        return [s for s in scenes if s["n"] in args.only]
    if args.from_scene:
        return [s for s in scenes if s["n"] >= args.from_scene]
    return scenes


def main() -> None:
    args   = parse_args()
    active = filter_scenes(SCENES, args)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("  Augusta at Country Lakes — 10 UGC Scenes")
    print(f"  Scenes to process : {[s['n'] for s in active]}")
    print(f"  Output dir        : {OUTPUT_DIR}")
    print("=" * 72)

    # Verify Isabela reference exists (uploaded fresh per scene)
    if not ISABELA_REF.exists():
        print(f"\nERROR: Isabela reference not found:\n  {ISABELA_REF}")
        sys.exit(1)

    results = []

    for scene in active:
        n     = scene["n"]
        label = f"S{n:02d}-{scene['id']}"
        scene_dir = OUTPUT_DIR / f"scene-{n:02d}-{scene['id']}"
        scene_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'─'*60}")
        print(f"  Scene {n:02d}/10 — {scene['id']}")
        print(f"{'─'*60}")

        result: dict = {"scene": label, "n": n}

        # Phase 1 — Still
        print(f"\n[1/4] Generating still...")
        still = generate_still(scene, scene_dir)
        result["still"] = str(still) if still else None
        if not still:
            result["status"] = "failed_still"
            results.append(result)
            continue

        # Phase 2 — Animation
        print(f"\n[2/4] Animating with veo31...")
        video = animate_veo31(scene, still, scene_dir)
        result["video_raw"] = str(video) if video else None
        if not video:
            result["status"] = "failed_animation"
            results.append(result)
            continue

        # Phase 3 — Voiceover
        print(f"\n[3/4] Generating voiceover (ElevenLabs)...")
        audio = generate_voiceover(scene, scene_dir)
        result["voiceover"] = str(audio) if audio else None

        # Phase 4 — Combine
        if audio:
            print(f"\n[4/4] Combining with ffmpeg...")
            reel = combine(scene, video, audio, scene_dir)
            result["reel"] = str(reel) if reel else None
            result["status"] = "ok" if reel else "failed_combine"
        else:
            print(f"\n[4/4] Skipping combine (no voiceover), video_raw is final output")
            result["reel"]   = str(video)
            result["status"] = "ok_no_audio"

        results.append(result)

    # Summary
    print(f"\n{'='*72}")
    ok    = sum(1 for r in results if r["status"].startswith("ok"))
    total = len(results)
    print(f"  DONE: {ok}/{total} scenes completed")
    print()
    for r in results:
        icon = "✓" if r["status"].startswith("ok") else "✗"
        reel = Path(r["reel"]).name if r.get("reel") else "—"
        print(f"  {icon} Scene {r['n']:02d}  {r['scene']:30s}  {reel}")
    print(f"\n  Output: {OUTPUT_DIR}")
    print(f"{'='*72}")

    manifest = OUTPUT_DIR / "manifest.json"
    manifest.write_text(json.dumps({
        "project": "Augusta at Country Lakes",
        "date": TODAY,
        "engine_still":     "nano-banana-2",
        "engine_animation": "veo31",
        "engine_voice":     "ElevenLabs Jessica",
        "scenes": results,
    }, indent=2, ensure_ascii=False))
    print(f"\n  Manifest → {manifest.name}")


if __name__ == "__main__":
    main()
