"""
Image resolver module for Empório da Música.
Strictly follows Section 4 of Master Prompt:
- Associates images exclusively by product ID.
- Uses downloaded and verified WebP local images from 'static/images/catalog/product_{id}.webp'.
- If product has no verified candidata, renders an ultra-refined, bespoke luxury SVG placeholder
  incorporating the instrument's name, category, and an authentic luthier silhouette icon.
- Never outputs raw broken HTML, hotlinks, or arbitrary paths.
"""

import os
import base64
from functools import lru_cache

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CATALOG_IMG_DIR = os.path.join(PROJECT_ROOT, "static", "images", "catalog")
HERO_IMG_PATH = os.path.join(PROJECT_ROOT, "static", "images", "hero_boutique.jpg")


def get_luxury_placeholder_svg(name: str, category: str, product_id: int) -> str:
    """
    Generates a dark luxury atelier SVG placeholder for instruments without validated photographs.
    Features: charcoal background (#13151b), gold brushed frame (#c5a880), instrument silhouette motif,
    and elegant typography matching the boutique identity.
    """
    # Category icon path or silhouette
    icons = {
        "Violões": '<path d="M150 70 C145 90 148 110 140 130 C125 150 115 175 115 200 C115 235 140 260 170 260 C200 260 225 235 225 200 C225 175 215 150 200 130 C192 110 195 90 190 70 Z" fill="none" stroke="#9e7d56" stroke-width="2.5"/><circle cx="170" cy="180" r="16" fill="none" stroke="#9e7d56" stroke-width="2"/><line x1="170" y1="50" x2="170" y2="240" stroke="#c5a880" stroke-width="1.2" stroke-dasharray="3,3"/>',
        "Guitarras": '<path d="M155 70 L185 70 L180 125 C195 145 220 170 220 205 C220 240 195 260 170 260 C145 260 120 240 120 205 C120 170 145 145 160 125 Z" fill="none" stroke="#9e7d56" stroke-width="2.5"/><line x1="170" y1="50" x2="170" y2="250" stroke="#c5a880" stroke-width="1.2"/>',
        "Baixos": '<path d="M155 60 L185 60 L180 120 C195 140 225 165 225 205 C225 245 195 265 170 265 C145 265 115 245 115 205 C115 165 145 140 160 120 Z" fill="none" stroke="#9e7d56" stroke-width="2.5"/><line x1="170" y1="40" x2="170" y2="255" stroke="#c5a880" stroke-width="1.4"/>',
        "Ukuleles": '<path d="M152 90 C148 105 150 120 145 135 C132 150 125 170 125 190 C125 220 145 240 170 240 C195 240 215 220 215 190 C215 170 208 150 195 135 C190 120 192 105 188 90 Z" fill="none" stroke="#9e7d56" stroke-width="2.2"/><circle cx="170" cy="175" r="13" fill="none" stroke="#9e7d56" stroke-width="1.8"/>',
        "Baterias e Percussão": '<ellipse cx="170" cy="140" rx="60" ry="24" fill="none" stroke="#9e7d56" stroke-width="2.5"/><path d="M110 140 L110 195 C110 215 230 215 230 195 L230 140" fill="none" stroke="#9e7d56" stroke-width="2.5"/>',
        "Teclados e Pianos": '<rect x="110" y="140" width="120" height="40" rx="3" fill="none" stroke="#9e7d56" stroke-width="2.2"/><line x1="130" y1="140" x2="130" y2="180" stroke="#9e7d56" stroke-width="1.5"/><line x1="150" y1="140" x2="150" y2="180" stroke="#9e7d56" stroke-width="1.5"/><line x1="170" y1="140" x2="170" y2="180" stroke="#9e7d56" stroke-width="1.5"/><line x1="190" y1="140" x2="190" y2="180" stroke="#9e7d56" stroke-width="1.5"/><line x1="210" y1="140" x2="210" y2="180" stroke="#9e7d56" stroke-width="1.5"/>',
    }
    icon_svg = icons.get(category, icons["Violões"])
    
    # Clean text to fit in SVG
    disp_name = (name[:28] + "..") if len(name) > 28 else name

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 320" width="100%" height="100%">
      <defs>
        <radialGradient id="bgGrad" cx="50%" cy="40%" r="65%">
          <stop offset="0%" stop-color="#1e222d"/>
          <stop offset="100%" stop-color="#0f1117"/>
        </radialGradient>
      </defs>
      <rect width="340" height="320" fill="url(#bgGrad)"/>
      <rect x="12" y="12" width="316" height="296" fill="none" stroke="#2a2e3a" stroke-width="1" stroke-dasharray="4,4"/>
      
      <g transform="translate(0, -10)">
        {icon_svg}
      </g>
      
      <text x="170" y="260" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-size="10.5" font-weight="600" letter-spacing="2" fill="#c5a880" text-transform="uppercase">{category.upper()}</text>
      <text x="170" y="278" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-size="12" font-weight="500" fill="#e8dfd5">{disp_name}</text>
      <text x="170" y="295" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-size="9" letter-spacing="1" fill="#7a8294">ATELIER &bull; ACERVO #{product_id}</text>
    </svg>"""
    
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


@lru_cache(maxsize=128)
def get_product_image_src(product_id: int, name: str, category: str) -> str:
    """
    Returns the exact image source for a given product ID:
    1. If a verified local webp file exists for this ID, returns base64 webp data URI.
    2. Otherwise, returns high-end bespoke SVG placeholder with category motif.
    """
    webp_path = os.path.join(CATALOG_IMG_DIR, f"product_{product_id}.webp")
    if os.path.exists(webp_path):
        try:
            with open(webp_path, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/webp;base64,{b64_data}"
        except Exception:
            pass

    return get_luxury_placeholder_svg(name, category, product_id)


def get_hero_banner_base64() -> str:
    """Return the hero boutique image base64 data URI."""
    if os.path.exists(HERO_IMG_PATH):
        try:
            with open(HERO_IMG_PATH, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/jpeg;base64,{b64_data}"
        except Exception:
            pass
    return ""
