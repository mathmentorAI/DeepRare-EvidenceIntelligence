
import os
import requests
import gzip
import shutil

# Configuración de Rutas en KIOXIA
KIOXIA_PATH = "/Volumes/KIOXIA/DeepRare"
KB_PATH = os.path.join(KIOXIA_PATH, "knowledge_base")
CLINVAR_PATH = os.path.join(KB_PATH, "ClinVar")
GWAS_PATH = os.path.join(KB_PATH, "GWAS")

def download_file(url, dest_path):
    print(f"📥 Descargando: {url} -> {dest_path}")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Descarga completada: {dest_path}")
    else:
        print(f"❌ Error al descargar {url}: Status {response.status_code}")

def setup():
    # 1. ClinVar Variant Summary
    clinvar_url = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
    clinvar_file = os.path.join(CLINVAR_PATH, "variant_summary.txt.gz")
    if not os.path.exists(clinvar_file):
        download_file(clinvar_url, clinvar_file)
    else:
        print("ℹ️ ClinVar ya presente en Kioxia.")

    # 2. GWAS Cystic Fibrosis (GCST003006)
    # Nota: Usamos una URL directa del FTP de EBI
    gwas_url = "https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/GCST003001-GCST004000/GCST003006/harmonised/26101730-GCST003006-EFO_0000398.h.tsv.gz"
    gwas_file = os.path.join(GWAS_PATH, "cystic_fibrosis_gwas.tsv.gz")
    if not os.path.exists(gwas_file):
        download_file(gwas_url, gwas_file)
    else:
        print("ℹ️ GWAS CF ya presente en Kioxia.")

if __name__ == "__main__":
    # Asegurar que los directorios existen
    os.makedirs(CLINVAR_PATH, exist_ok=True)
    os.makedirs(GWAS_PATH, exist_ok=True)
    setup()
