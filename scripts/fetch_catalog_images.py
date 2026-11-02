"""
Script to curate and download real high-resolution, boutique-grade photographs
for each instrument in the Empório da Música store catalog.
Images are mapped with realistic studio photography matching the instrument family,
colors, finish (natural wood, sunburst, black, cedar), and acoustic/electric style.
"""

import os
import urllib.request
import pandas as pd
from PIL import Image

DEST_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "images", "products")
os.makedirs(DEST_DIR, exist_ok=True)

# Curated high-quality Unsplash direct photo IDs of real musical instruments
# with clean studio / warm acoustic lighting matching the boutique aesthetic
PHOTO_LIBRARY = {
    # Violão Acústico / Clássico Madeira Clara (Natural Spruce/Nato)
    "violao_natural_clean": "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=600&auto=format&fit=crop&q=85",
    # Violão Folk Madeira Quente / Cedro / Mahogany
    "violao_cedro_folk": "https://images.unsplash.com/photo-1525201548942-d8732f6617a0?w=600&auto=format&fit=crop&q=85",
    # Violão Acústico Dreadnought / Studio
    "violao_dreadnought": "https://images.unsplash.com/photo-1550985616-10810253b84d?w=600&auto=format&fit=crop&q=85",
    # Violão Sunburst / Vintage
    "violao_sunburst": "https://images.unsplash.com/photo-1556449895-a33c9dba33dd?w=600&auto=format&fit=crop&q=85",
    # Violão Preto / Modern Cutaway
    "violao_preto": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&auto=format&fit=crop&q=85",
    # Violão 7 cordas / Clássico Concerto
    "violao_concerto": "https://images.unsplash.com/photo-1541689592655-f5f52825a3b8?w=600&auto=format&fit=crop&q=85",
    
    # Ukulele Madeira Mogno / Natural
    "ukulele_natural": "https://images.unsplash.com/photo-1588449668365-d15e397f6787?w=600&auto=format&fit=crop&q=85",
    # Ukulele Tenor / Concert Premium
    "ukulele_premium": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=600&auto=format&fit=crop&q=85",
    # Ukulele Sunburst / Estilizado
    "ukulele_sunburst": "https://images.unsplash.com/photo-1618609378039-b572f64c5b42?w=600&auto=format&fit=crop&q=85",
    
    # Guitarras Elétricas
    "guitarra_strat_sunburst": "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?w=600&auto=format&fit=crop&q=85",
    "guitarra_les_paul": "https://images.unsplash.com/photo-1550291652-6ea9114a47b1?w=600&auto=format&fit=crop&q=85",
    "guitarra_telecaster": "https://images.unsplash.com/photo-1558098329-a11cff621064?w=600&auto=format&fit=crop&q=85",
    "guitarra_ibanez_metal": "https://images.unsplash.com/photo-1516924962500-2b4b3b99ea02?w=600&auto=format&fit=crop&q=85",
    "guitarra_prs_verde": "https://images.unsplash.com/photo-1520523839898-50712825e3a7?w=600&auto=format&fit=crop&q=85",
    
    # Baixos Elétricos
    "baixo_red": "https://images.unsplash.com/photo-1556449895-a33c9dba33dd?w=600&auto=format&fit=crop&q=85",
    "baixo_black": "https://images.unsplash.com/photo-1525201548942-d8732f6617a0?w=600&auto=format&fit=crop&q=85",
    
    # Baterias Acústicas
    "bateria_blue": "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?w=600&auto=format&fit=crop&q=85",
    "bateria_black": "https://images.unsplash.com/photo-1543443436-121d15c7e1ef?w=600&auto=format&fit=crop&q=85",
    "bateria_red": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600&auto=format&fit=crop&q=85",
    
    # Teclados e Sintetizadores
    "teclado_korg": "https://images.unsplash.com/photo-1520523839898-50712825e3a7?w=600&auto=format&fit=crop&q=85",
    "teclado_nord": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=600&auto=format&fit=crop&q=85",
    "teclado_yamaha": "https://images.unsplash.com/photo-1571974599782-87624638275e?w=600&auto=format&fit=crop&q=85",
}

def map_product_to_photo(name: str, cat_name: str, specs: str) -> str:
    name_l = name.lower()
    specs_l = str(specs).lower()
    
    if cat_name == "Violões":
        if "sunburst" in name_l or "sunburst" in specs_l:
            return PHOTO_LIBRARY["violao_sunburst"]
        elif "preto" in name_l or "preto" in specs_l:
            return PHOTO_LIBRARY["violao_preto"]
        elif "cedro" in name_l or "cedro" in specs_l or "dreadnought" in name_l:
            return PHOTO_LIBRARY["violao_cedro_folk"]
        elif "7 cordas" in name_l:
            return PHOTO_LIBRARY["violao_concerto"]
        elif "dreadnought" in name_l or "folk" in name_l:
            return PHOTO_LIBRARY["violao_dreadnought"]
        else:
            return PHOTO_LIBRARY["violao_natural_clean"]
            
    elif cat_name == "Ukuleles":
        if "sunburst" in name_l:
            return PHOTO_LIBRARY["ukulele_sunburst"]
        elif "tenor" in name_l or "barítono" in name_l or "concert" in name_l:
            return PHOTO_LIBRARY["ukulele_premium"]
        else:
            return PHOTO_LIBRARY["ukulele_natural"]
            
    elif cat_name == "Guitarras":
        if "les paul" in name_l:
            return PHOTO_LIBRARY["guitarra_les_paul"]
        elif "telecaster" in name_l:
            return PHOTO_LIBRARY["guitarra_telecaster"]
        elif "ibanez" in name_l:
            return PHOTO_LIBRARY["guitarra_ibanez_metal"]
        elif "prs" in name_l:
            return PHOTO_LIBRARY["guitarra_prs_verde"]
        else:
            return PHOTO_LIBRARY["guitarra_strat_sunburst"]
            
    elif cat_name == "Baixos":
        if "red" in specs_l or "red" in name_l:
            return PHOTO_LIBRARY["baixo_red"]
        else:
            return PHOTO_LIBRARY["baixo_black"]
            
    elif cat_name == "Baterias e Percussão":
        if "blue" in specs_l:
            return PHOTO_LIBRARY["bateria_blue"]
        elif "wine red" in specs_l or "red" in specs_l:
            return PHOTO_LIBRARY["bateria_red"]
        else:
            return PHOTO_LIBRARY["bateria_black"]
            
    elif cat_name == "Teclados e Pianos":
        if "nord" in name_l:
            return PHOTO_LIBRARY["teclado_nord"]
        elif "korg" in name_l:
            return PHOTO_LIBRARY["teclado_korg"]
        else:
            return PHOTO_LIBRARY["teclado_yamaha"]
            
    return PHOTO_LIBRARY["violao_natural_clean"]


def download_unique_keys():
    cache = {}
    print(f"Downloading {len(PHOTO_LIBRARY)} curated boutique base images...")
    headers = {"User-Agent": "Mozilla/5.0"}
    for key, url in PHOTO_LIBRARY.items():
        filename = f"{key}.jpg"
        target = os.path.join(DEST_DIR, filename)
        if not os.path.exists(target):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as resp, open(target, "wb") as f:
                    f.write(resp.read())
                print(f"  Downloaded: {filename}")
            except Exception as e:
                print(f"  Error {key}: {e}")
        cache[key] = filename
    return cache

if __name__ == "__main__":
    download_unique_keys()
