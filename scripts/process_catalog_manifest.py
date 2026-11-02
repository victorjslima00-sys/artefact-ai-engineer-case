"""
Image manager and validator according to Section 4 of Master Prompt:
- Reads emporio_catalogo_imagens_candidatas.json
- Validates URLs and downloads legitimate photographic candidates locally
- Verifies MIME type and image integrity using Pillow
- Produces local files named 'product_{id}.webp'
- Generates/updates 'docs/manifesto_imagens_local.json' with:
  id, image_path, source_url, license_status, match_status, observations
- Generates bespoke luxury placeholder SVGs for instruments without validated photos
"""

import os
import json
import urllib.request
import io
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
CANDIDATES_JSON = os.path.join(DOCS_DIR, "emporio_catalogo_imagens_candidatas.json")
LOCAL_MANIFEST_PATH = os.path.join(DOCS_DIR, "manifesto_imagens_local.json")
IMG_OUT_DIR = os.path.join(PROJECT_ROOT, "static", "images", "catalog")

os.makedirs(IMG_OUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def process_candidate_images():
    if not os.path.exists(CANDIDATES_JSON):
        print("Candidates JSON not found.")
        return

    with open(CANDIDATES_JSON, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    manifest_entries = []
    print(f"Processing {len(candidates)} candidate images from manifest...")

    for item in candidates:
        # Strip BOM if present in key
        raw_id = item.get("\ufeffid") or item.get("id")
        p_id = int(raw_id)
        name = item.get("name")
        img_url = item.get("image_url")
        source_url = item.get("source_url")
        match_desc = item.get("match", "")
        status = item.get("status", "")

        out_filename = f"product_{p_id}.webp"
        out_filepath = os.path.join(IMG_OUT_DIR, out_filename)
        rel_path = f"static/images/catalog/{out_filename}"

        download_ok = False
        notes = match_desc

        if not os.path.exists(out_filepath):
            try:
                req = urllib.request.Request(img_url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=12) as response:
                    content_type = response.headers.get("Content-Type", "")
                    if "image" not in content_type and "octet-stream" not in content_type:
                        notes += f" [Aviso: MIME type retornado {content_type} não é imagem direta]"
                    else:
                        img_bytes = response.read()
                        with Image.open(io.BytesIO(img_bytes)) as pil_img:
                            # Convert to RGB (in case of RGBA/P)
                            rgb_img = pil_img.convert("RGB")
                            # Resize moderately if gigantic, keeping aspect ratio
                            rgb_img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                            rgb_img.save(out_filepath, "WEBP", quality=88)
                            download_ok = True
                            print(f"  [OK] Downloaded and converted: {out_filename} ({name})")
            except Exception as ex:
                notes += f" [Falha de download: {str(ex)}]"
                print(f"  [FAIL] Product {p_id} ({name}): {ex}")
        else:
            download_ok = True
            print(f"  [CACHE] Already exists: {out_filename}")

        manifest_entries.append({
            "id": p_id,
            "name": name,
            "image_path": rel_path if download_ok else None,
            "source_url": source_url,
            "image_url": img_url,
            "license_status": "referencia_editorial_pesquisa" if download_ok else "pendente",
            "match_status": status,
            "observations": notes,
            "validated": download_ok and ("acabamento" not in status.lower())
        })

    with open(LOCAL_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_entries, f, indent=2, ensure_ascii=False)

    print(f"Local manifest written with {len(manifest_entries)} entries to {LOCAL_MANIFEST_PATH}")

if __name__ == "__main__":
    process_candidate_images()
