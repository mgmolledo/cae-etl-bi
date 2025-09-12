
import os
import requests
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "boe_rd171": "https://www.boe.es/buscar/pdf/2004/BOE-A-2004-1848-consolidado.pdf",
    "insst_criterios": "https://www.insst.es/documents/94886/627464/Directrices_ITSS.pdf",
}

def download_sources():
    for name, url in SOURCES.items():
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            r.raise_for_status()
            file_path = RAW_DIR / f"{name}.pdf"
            with open(file_path, "wb") as f:
                f.write(r.content)
            print(f"Descargado: {name}")
        except Exception as e:
            print(f"Error con {name}: {e}")

if __name__ == "__main__":
    download_sources()
