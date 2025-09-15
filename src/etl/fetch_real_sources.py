
import os
import requests
from pathlib import Path
import sys

def main():
    try:
        RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        
        print(f"Directorio de datos: {RAW_DIR}")
        
        SOURCES = {
            "boe_rd171": "https://www.boe.es/buscar/pdf/2004/BOE-A-2004-1848-consolidado.pdf",
            "insst_criterios": "https://www.insst.es/documents/94886/627464/Directrices_ITSS.pdf",
        }
        
        success_count = 0
        
        for name, url in SOURCES.items():
            try:
                print(f"Descargando {name}...")
                r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
                r.raise_for_status()
                
                file_path = RAW_DIR / f"{name}.pdf"
                with open(file_path, "wb") as f:
                    f.write(r.content)
                
                print(f"✓ Descargado: {name} ({len(r.content)} bytes)")
                success_count += 1
                
            except requests.exceptions.RequestException as e:
                print(f"✗ Error de red con {name}: {e}")
            except Exception as e:
                print(f"✗ Error con {name}: {e}")
        
        print(f"\nResumen: {success_count}/{len(SOURCES)} archivos descargados")
        
        if success_count == 0:
            print("⚠️  No se pudo descargar ningún archivo")
            sys.exit(1)
        else:
            print("✓ Proceso completado exitosamente")
            sys.exit(0)
            
    except Exception as e:
        print(f"✗ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
