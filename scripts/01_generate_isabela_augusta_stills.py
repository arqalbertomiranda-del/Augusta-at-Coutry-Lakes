# -*- coding: utf-8 -*-
"""
Augusta at Country Lakes — Phase 1: Isabela stills via Arcads nano-banana-2
Genera 2 stills de Isabela en los amenidades de Augusta para usar como startFrame.

Output: outputs/isabela-augusta-stills-{date}/
"""
import os, sys, json, time, io, requests
from datetime import datetime, timezone
from pathlib import Path

# Load .env if python-dotenv is available
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
SCRIPT_DIR   = Path(__file__).parent
REPO_ROOT    = SCRIPT_DIR.parent
TODAY        = datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR   = REPO_ROOT / "outputs" / f"isabela-augusta-stills-{TODAY}"
LOG_FILE     = REPO_ROOT / "logs" / "arcads-api.jsonl"

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

HEADERS = {"Authorization": ARCADS_AUTH, "Content-Type": "application/json"}

# ── Identidad Isabela ─────────────────────────────────────────────────────────
ISABELA_BASE = (
    "A 27-year-old woman of astonishing beauty: long silky straight dark chestnut-brown hair "
    "falling past her mid-back with healthy shine, large captivating green eyes with luminous "
    "depth, porcelain-fair flawless skin with natural visible pores and warm subtle undertone, "
    "perfectly arched full dark brows, a charmingly upturned refined nose, a flawlessly "
    "sculpted angular jaw, full lips with a defined cupid's bow, athletic tall figure "
    "approximately 175cm, generous naturally lifted bust, narrow cinched waist. "
    "Minimal old-money makeup — luminous bare skin, barely-there gloss."
)

# ── Stills a generar ──────────────────────────────────────────────────────────
STILLS = [
    {
        "id": "S1-alberca-augusta",
        "scene_ref_key": "pool",
        "prompt": (
            "Photorealistic luxury real estate lifestyle portrait. " + ISABELA_BASE +
            " She wears an elegant ivory silk midi wrap dress with a gently plunging V-neckline "
            "— Jacquemus / Toteme aesthetic. Strappy tan leather sandals. Fine delicate gold chain "
            "necklace, small gold hoop earrings, thin polished gold cuff bracelet. Long straight "
            "dark hair loose and natural with a subtle breeze movement. "
            "She stands relaxed near the edge of a luxury infinity pool of an exclusive private "
            "golf residential community: wide polished travertine pool deck, crisp white sun "
            "loungers with thick white cushions and elegant white canvas umbrellas, lush tall "
            "coconut palms framing the scene. Beyond the pool: a low modern cream-stucco "
            "clubhouse building with exposed wooden beam pergola and covered outdoor terrace. "
            "Brilliant sunny tropical day with a few wispy white clouds. Golden afternoon warm "
            "light raking across the travertine deck. Two children play happily on a lush green "
            "lawn in the soft background distance near the clubhouse. "
            "Body angled three-quarter toward camera, one hand resting lightly on the back of a "
            "sun lounger, head turned toward camera with quiet confident magnetism — "
            "completely at home in this world. "
            "No text, no subtitles, no captions, no watermarks. Ultra-photorealistic, "
            "visible skin texture, individual dark hair strands catching the warm afternoon light."
        ),
    },
    {
        "id": "S2-acceso-augusta",
        "scene_ref_key": "entrance",
        "prompt": (
            "Photorealistic luxury real estate lifestyle portrait. " + ISABELA_BASE +
            " She wears a flowing sage-green wide-leg linen jumpsuit with a cinched waist "
            "and structured wide-lapel top — elegant tropical resort aesthetic. Tan leather "
            "strappy sandals with a slim ankle strap. Fine gold watch on her wrist, thin gold "
            "rings, small sculptural gold drop earrings. Long straight dark hair loose, "
            "a gentle tropical breeze moving it slightly. "
            "She stands on the elegant cobblestone circular roundabout at the entrance of an "
            "exclusive private luxury golf community: a low modern building of warm cream "
            "limestone and smooth stucco with a beautiful carved wooden pergola archway above "
            "the entrance gate. Lush tropical landscaping: monstera leaves, palm fronds, "
            "ornamental grasses framing the entrance walls. A cobblestone circular driveway "
            "in front. Brilliant sunny day, a few soft white clouds. "
            "Body angled three-quarter toward camera, looking directly toward camera with a "
            "serene, quietly confident, magnetic expression — she belongs here. "
            "No text, no subtitles, no captions, no watermarks. Ultra-photorealistic, "
            "visible skin texture, individual dark hair strands catching the warm daylight."
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


def generate_still(still: dict, isabela_path: str) -> dict:
    label = still["id"]
    ref_paths = [isabela_path]

    scene_key = still.get("scene_ref_key")
    if scene_key and scene_key in RENDERS and RENDERS[scene_key].exists():
        try:
            scene_bytes = prepare_image(RENDERS[scene_key])
            scene_path  = upload_image(scene_bytes, f"{label}/scene")
            ref_paths.append(scene_path)
        except Exception as e:
            print(f"  [{label}] WARNING: scene upload failed ({e}), continuing without it")

    payload = {
        "productId": PRODUCT_ID,
        "projectId": PROJECT_ID,
        "model": "nano-banana-2",
        "prompt": still["prompt"],
        "aspectRatio": "9:16",
        "referenceImages": ref_paths,
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
        "request": {"styleId": label, "referenceImagesCount": len(ref_paths)},
        "response": {"status": "pending"},
        "session": {"folderName": f"Augusta - {TODAY}"},
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
                "session": {"folderName": f"Augusta - {TODAY}"},
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

    # Verify reference files
    missing = []
    if not ISABELA_REF.exists():
        missing.append(str(ISABELA_REF))
    for key, path in RENDERS.items():
        if not path.exists():
            print(f"  WARNING: render '{key}' not found at {path} — will generate without it")
    if missing:
        print("ERROR: Missing required reference files:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)

    print("=" * 70)
    print("  Augusta at Country Lakes — Isabela Stills (Phase 1)")
    print(f"  {len(STILLS)} stills | nano-banana-2 | 9:16")
    print(f"  Output -> {OUTPUT_DIR}")
    print("=" * 70)

    print("\nUploading Isabela reference image...")
    isabela_bytes = prepare_image(ISABELA_REF)
    isabela_path  = upload_image(isabela_bytes, "isabela-ref")
    print(f"  Isabela ref uploaded\n")

    results = []
    for still in STILLS:
        print(f"Generating: {still['id']}...")
        result = generate_still(still, isabela_path)
        results.append(result)

        if result["status"] == "generated":
            img_r = requests.get(result["url"], timeout=60)
            out   = OUTPUT_DIR / f"{result['id']}.jpg"
            out.write_bytes(img_r.content)
            print(f"  Saved -> {out.name}\n")
        else:
            print(f"  FAILED: {result.get('error','')[:120]}\n")

    manifest = OUTPUT_DIR / "manifest.json"
    manifest.write_text(json.dumps(results, indent=2, ensure_ascii=False))

    ok = sum(1 for r in results if r["status"] == "generated")
    print("=" * 70)
    print(f"  Results: {ok}/{len(STILLS)} stills OK")
    print(f"  Manifest -> {manifest}")
    print("=" * 70)
    print("\nNext step: run 02_animate_voiceover_combine.py")


if __name__ == "__main__":
    main()
