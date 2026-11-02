"""
Image helper module for Empório da Música.
Maps every product in the catalog to its specific, high-resolution boutique photo
and converts images to clean base64 data URIs so they display instantly without
server path glitches, broken links, or raw HTML leaks.
"""

import os
import base64
from functools import lru_cache

IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "images", "products")
HERO_IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "images", "hero_boutique.jpg")
ACOUSTIC_IMG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "images", "hero_acoustic.png")


def get_product_photo_key(name: str, cat_name: str, specs: dict = None) -> str:
    """Determine the most accurate photo filename based on instrument name, specs, and category."""
    name_l = name.lower()
    specs_str = str(specs or {}).lower()

    if cat_name == "Violões":
        if "sunburst" in name_l or "sunburst" in specs_str:
            return "violao_sunburst.jpg"
        elif "preto" in name_l or "preto" in specs_str:
            return "violao_preto.jpg"
        elif "cedro" in name_l or "cedro" in specs_str:
            return "violao_cedro_folk.jpg"
        elif "7 cordas" in name_l:
            return "violao_concerto.jpg"
        elif "dreadnought" in name_l or "folk" in name_l or "gd20" in name_l:
            return "violao_dreadnought.jpg"
        elif "c40" in name_l or "c70" in name_l or "ac-39" in name_l or "rc-104" in name_l:
            return "violao_natural_clean.jpg"
        else:
            return "violao_cedro_folk.jpg"

    elif cat_name == "Ukuleles":
        if "sunburst" in name_l:
            return "ukulele_sunburst.jpg"
        elif "tenor" in name_l or "barítono" in name_l or "concert" in name_l:
            return "ukulele_premium.jpg"
        else:
            return "ukulele_natural.jpg"

    elif cat_name == "Guitarras":
        if "les paul" in name_l:
            return "guitarra_les_paul.jpg"
        elif "telecaster" in name_l:
            return "guitarra_telecaster.jpg"
        elif "ibanez" in name_l:
            return "guitarra_ibanez_metal.jpg"
        elif "prs" in name_l:
            return "guitarra_prs_verde.jpg"
        else:
            return "guitarra_strat_sunburst.jpg"

    elif cat_name == "Baixos":
        if "red" in specs_str or "red" in name_l:
            return "baixo_red.jpg"
        else:
            return "baixo_black.jpg"

    elif cat_name == "Baterias e Percussão":
        if "blue" in specs_str:
            return "bateria_blue.jpg"
        elif "wine red" in specs_str or "red" in specs_str:
            return "bateria_red.jpg"
        else:
            return "bateria_black.jpg"

    elif cat_name == "Teclados e Pianos":
        if "nord" in name_l:
            return "teclado_nord.jpg"
        elif "korg" in name_l:
            return "teclado_korg.jpg"
        else:
            return "teclado_yamaha.jpg"

    return "violao_natural_clean.jpg"


@lru_cache(maxsize=128)
def get_image_base64(filepath: str) -> str:
    """Read a local image and return it as a base64 data URI string."""
    if not os.path.exists(filepath):
        return ""
    ext = os.path.splitext(filepath)[1].lower().replace(".", "")
    if ext == "jpg":
        ext = "jpeg"
    with open(filepath, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{ext};base64,{data}"


def get_product_image_data_uri(name: str, cat_name: str, specs: dict = None) -> str:
    """Get the base64 data URI directly for a product card."""
    filename = get_product_photo_key(name, cat_name, specs)
    full_path = os.path.join(IMG_DIR, filename)
    if os.path.exists(full_path):
        return get_image_base64(full_path)
    # Fallback to acoustic hero
    if os.path.exists(ACOUSTIC_IMG_PATH):
        return get_image_base64(ACOUSTIC_IMG_PATH)
    return ""
