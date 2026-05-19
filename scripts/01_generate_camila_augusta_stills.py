# -*- coding: utf-8 -*-
"""
Augusta at Country Lakes — Camila Stills via Arcads nano-banana-2
Genera 3 stills de Camila (influencer nueva, sin foto de referencia aún).
Los stills generados sirven como imágenes de referencia para producciones futuras.

Output: outputs/camila-augusta-stills-{date}/
"""
import os, sys, json, time, io, requests
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
ARCADS_AUTH = os.environ["ARCADS_AUTH"]
BASE_URL    = "https://external-api.arcads.ai"
PRODUCT_ID  = os.environ.get("ARCADS_PRODUCT_ID", "3c7125f2-de97-4587-99b7-405e80d93f90")
PROJECT_ID  = os.environ.get("ARCADS_PROJECT_ID", "105d6a6b-c65e-40de-aefb-9b52da56d3e2")

# ── Rutas ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT  = SCRIPT_DIR.parent
TODAY      = datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = REPO_ROOT / "outputs" / f"camila-augusta-stills-{TODAY}"
LOG_FILE   = REPO_ROOT / "logs" / "arcads-api.jsonl"

CAMILA_REF_DIR = Path(
    r"C:\Users\alber\Boma Desarrollos\Arrecife Sisal - Documentos"
    r"\10.0 Mercadotecnia\Videos de Claude Code - Arrecife"
    r"\references\influencers\camila-chestnut-straight-green-eyes-bronzed"
)

RENDERS = {
    "pool":     Path(r"C:\Users\alber\Boma Desarrollos\Augusta at Country Lakes - Documentos\02. Alcances\02.13 Renders\Arquitectonicos\ACCESO CASA CLUB.jpg"),
    "entrance": Path(r"C:\Users\alber\Boma Desarrollos\Augusta at Country Lakes - Documentos\02. Alcances\02.13 Renders\Arquitectonicos\ACCESO.jpg"),
    "aerial":   Path(r"C:\Users\alber\Boma Desarrollos\Augusta at Country Lakes - Documentos\02. Alcances\02.13 Renders\Arquitectonicos\AUGUSTA_AEREO CC.jpg"),
}

HEADERS = {"Authorization": ARCADS_AUTH, "Content-Type": "application/json"}

# ── Identidad Camila ──────────────────────────────────────────────────────────
CAMILA_BASE = (
    "A 35-year-old woman of timeless elegance: long silky straight hair in a warm light chestnut "
    "with subtle golden-blonde highlights catching the light — castaño claro dorado, "
    "falling past her shoulders with a natural healthy shine, large expressive olive-green eyes "
    "with depth and warmth, fair porcelain skin with only a faint barely-there natural warmth — "
    "luminous ivory-fair, not bronzed, subtle peachy undertone and visible natural "
    "pore texture, perfectly shaped full brows, a refined nose, a graceful jawline, "
    "full lips with a natural wide smile and flawless perfect white teeth, "
    "slim athletic build with generous natural bust, old money poise and quiet confidence. "
    "Minimal refined makeup — luminous skin, nude lip, subtle mascara. "
    "She radiates generational wealth without effort."
)

# ── Stills a generar ──────────────────────────────────────────────────────────
STILLS = [
    {
        "id": "S1-quiet-luxury-studio",
        "scene_ref_key": None,
        "prompt": (
            "Photorealistic luxury fashion portrait. " + CAMILA_BASE +
            " She wears a monochromatic ivory ensemble: a tailored oversized linen blazer, "
            "high-waisted pleated silk trousers, and a champagne satin camisole. "
            "Delicate gold jewelry — thin chain necklace, small stud earrings, minimal watch. "
            "No heavy accessories. Old money restraint. "
            "Studio setting: she leans lightly against a textured warm plaster wall, "
            "soft warm diffused directional light from the left creating subtle shadows "
            "on cheekbones and hair. Quiet Luxury aesthetic — elegant, serene, expensive. "
            "Body three-quarter toward camera, natural relaxed posture, direct warm gaze, "
            "genuine soft smile. "
            "Photorealistic, editorial fashion photography, 85mm lens, shallow depth of field, "
            "warm neutral color grade, 8k, ultra-detailed skin and hair texture. "
            "No text, no subtitles, no watermarks."
        ),
    },
    {
        "id": "S2-golf-resort-editorial",
        "scene_ref_key": "pool",
        "prompt": (
            "Photorealistic luxury real estate lifestyle portrait. " + CAMILA_BASE +
            " She wears a tailored white sleeveless polo dress, midi length, with subtle "
            "gold accents and nude strappy sandals. Thin gold bracelet, small gold hoop earrings. "
            "Long straight warm golden-chestnut hair loose, a gentle breeze moving it naturally. "
            "She stands at the edge of a manicured golf fairway near an exclusive private "
            "golf club: lush green grass extending into the distance, a modern clubhouse with "
            "infinity pool softly visible behind her, tall palm trees framing the scene. "
            "Golden hour light — warm backlight creating a halo on her warm golden-chestnut hair, "
            "soft fill on her face. She holds a single golf club casually at her side, "
            "looking toward camera with a warm natural smile — she lives here, this is her world. "
            "Photorealistic, luxury lifestyle editorial photography, 70mm lens, "
            "golden hour cinematography, shallow depth of field, 4:5 vertical, 8k. "
            "No text, no subtitles, no watermarks."
        ),
    },
    {
        "id": "S3-cinematic-terrace",
        "scene_ref_key": "pool",
        "prompt": (
            "Cinematic photorealistic luxury still. " + CAMILA_BASE +
            " She wears a fitted white sleeveless linen midi dress, simple and refined. "
            "Thin gold bracelet, small gold hoop earrings, nude heels. "
            "She stands on a private club terrace overlooking pristine golf fairways — "
            "Augusta at Country Lakes: sweeping view of immaculate emerald fairways, "
            "lush tropical landscaping, and a modern infinity pool below. "
            "One hand rests gracefully on the terrace railing, the other relaxed at her side. "
            "She looks directly toward camera with a warm genuine smile — "
            "confident, completely at home in this world. "
            "Golden hour: warm soft backlight wrapping her silhouette, slight atmospheric haze, "
            "individual warm golden-chestnut hair strands catching the golden light. "
            "Cinematic high-end editorial photography, 85mm f/1.4, warm color grade, "
            "4:5 vertical, 8k ultra photorealistic. "
            "No text, no subtitles, no watermarks."
        ),
    },
]


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
        f"{BASE_URL}/v1/file-upload/get-presigned-url",
        headers=HEADERS, json={"fileType": "image/jpeg"}, timeout=30
    )
    r.raise_for_status()
    d = r.json()
    requests.put(
        d["presignedUrl"], data=img_bytes,
        headers={"Content-Type": "image/jpeg"}, timeout=60
    ).raise_for_status()
    print(f"    [{label}] uploaded ({len(img_bytes):,} B)")
    return d["filePath"]


def log_entry(entry: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def generate_still(still: dict, ref_paths: list) -> dict:
    label = still["id"]
    all_refs = list(ref_paths)

    scene_key = still.get("scene_ref_key")
    if scene_key and scene_key in RENDERS and RENDERS[scene_key].exists():
        try:
            scene_bytes = prepare_image(RENDERS[scene_key])
            scene_path  = upload_image(scene_bytes, f"{label}/scene")
            all_refs.append(scene_path)
        except Exception as e:
            print(f"  [{label}] WARNING: scene upload failed ({e}), continuing without it")

    payload = {
        "productId": PRODUCT_ID,
        "projectId": PROJECT_ID,
        "model":     "nano-banana-2",
        "prompt":    still["prompt"],
        "aspectRatio": "9:16",
        "referenceImages": all_refs,
    }
    r = requests.post(
        f"{BASE_URL}/V2/images/generate",
        headers=HEADERS, json=payload, timeout=30
    )
    ts = datetime.now(timezone.utc).isoformat()

    if r.status_code not in (200, 201):
        log_entry({"timestamp": ts, "clip": label, "status": "failed_create", "error": r.text[:300]})
        return {"id": label, "status": "failed_create", "error": r.text[:300]}

    data     = r.json()
    asset_id = data.get("id") or data.get("assetId")
    print(f"  [{label}] submitted -> {asset_id}")
    log_entry({
        "timestamp": ts, "endpoint": "POST /V2/images/generate",
        "model": "nano-banana-2", "assetId": asset_id,
        "productId": PRODUCT_ID, "projectId": PROJECT_ID,
        "request": {"styleId": label, "referenceImagesCount": len(all_refs)},
        "response": {"status": "pending"},
        "session": {"folderName": f"Augusta - Camila - {TODAY}"},
    })

    for attempt in range(120):
        time.sleep(5)
        pr = requests.get(
            f"{BASE_URL}/v1/assets/{asset_id}",
            headers={"Authorization": ARCADS_AUTH}, timeout=30
        )
        if pr.status_code != 200:
            continue
        asset  = pr.json()
        status = asset.get("status")
        if status == "generated":
            url     = asset.get("url") or asset.get("imageUrl")
            credits = asset.get("creditsCharged", "?")
            elapsed = attempt * 5
            print(f"  [{label}] DONE  credits={credits}  t={elapsed}s")
            log_entry({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "endpoint": "POST /V2/images/generate",
                "model": "nano-banana-2", "assetId": asset_id,
                "response": {"status": "generated", "creditsCharged": credits, "imageUrl": url},
                "session": {"folderName": f"Augusta - Camila - {TODAY}"},
            })
            return {"id": label, "status": "generated", "url": url,
                    "credits": credits, "asset_id": asset_id}
        elif status == "failed":
            err = asset.get("error") or str(asset)[:300]
            print(f"  [{label}] FAILED: {err}")
            return {"id": label, "status": "failed", "error": err, "asset_id": asset_id}
        else:
            if attempt % 6 == 0:
                print(f"  [{label}] ... {status} (t+{attempt*5}s)")

    return {"id": label, "status": "timeout", "asset_id": asset_id}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CAMILA_REF_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  Augusta at Country Lakes — Camila Stills (Phase 1)")
    print(f"  {len(STILLS)} stills | nano-banana-2 | 9:16 | sin foto de referencia")
    print(f"  Output -> {OUTPUT_DIR}")
    print("=" * 70)

    # Sin foto de referencia de cara — Camila se genera desde el prompt puro.
    # Los stills resultantes serán sus imágenes de referencia para el futuro.
    ref_paths = []

    results = []
    for still in STILLS:
        print(f"\nGenerando: {still['id']}...")
        result = generate_still(still, ref_paths)
        results.append(result)

        if result["status"] == "generated":
            img_r   = requests.get(result["url"], timeout=60)
            out     = OUTPUT_DIR / f"{result['id']}.jpg"
            out.write_bytes(img_r.content)

            # Copiar también a carpeta de referencias de Camila
            ref_copy = CAMILA_REF_DIR / f"{result['id']}.jpg"
            ref_copy.write_bytes(img_r.content)

            print(f"  Saved -> {out.name}")
            print(f"  Ref   -> {ref_copy}")
        else:
            print(f"  FAILED: {result.get('error','')[:120]}")

    manifest = OUTPUT_DIR / "manifest.json"
    manifest.write_text(json.dumps(results, indent=2, ensure_ascii=False))

    ok = sum(1 for r in results if r["status"] == "generated")
    print("\n" + "=" * 70)
    print(f"  Resultados: {ok}/{len(STILLS)} stills OK")
    print(f"  Manifest  -> {manifest}")
    print(f"  Referencias guardadas en: {CAMILA_REF_DIR}")
    print("=" * 70)
    if ok > 0:
        print("\nSiguiente paso: seleccionar la mejor imagen como referencia principal")
        print("  -> Renombrar a '01-hero-front.jpg' en la carpeta de referencias")
        print("  -> Luego ejecutar 02_animate_voiceover_combine.py")


if __name__ == "__main__":
    main()
