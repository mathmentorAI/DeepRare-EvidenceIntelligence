
import os
import gzip
import sqlite3
import pandas as pd
from tqdm import tqdm

KIOXIA_PATH = "/Volumes/KIOXIA/DeepRare"
CLINVAR_GZ = os.path.join(KIOXIA_PATH, "knowledge_base/ClinVar/variant_summary.txt.gz")
DB_PATH = os.path.join(KIOXIA_PATH, "databases/clinvar_index.db")

def create_index():
    if not os.path.exists(CLINVAR_GZ):
        print(f"❌ Archivo no encontrado: {CLINVAR_GZ}")
        return

    print(f"🏗️ Creando índice ClinVar en {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla optimizada
    cursor.execute("DROP TABLE IF EXISTS variants")
    cursor.execute("""
        CREATE TABLE variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            allele_id TEXT,
            gene_symbol TEXT,
            rs_id TEXT,
            clinical_significance TEXT,
            phenotype_list TEXT,
            hgvs_c TEXT,
            hgvs_p TEXT,
            assembly TEXT
        )
    """)
    
    # Procesar por chunks para no saturar la RAM
    chunk_size = 50000
    try:
        with gzip.open(CLINVAR_GZ, 'rt') as f:
            # Leer header
            header = f.readline().strip().split('\t')
            # Mapear columnas de interés
            col_map = {
                'AlleleID': header.index('#AlleleID'),
                'GeneSymbol': header.index('GeneSymbol'),
                'RS# (dbSNP)': header.index('RS# (dbSNP)'),
                'ClinicalSignificance': header.index('ClinicalSignificance'),
                'PhenotypeList': header.index('PhenotypeList'),
                'Assembly': header.index('Assembly')
            }

            batch = []
            count = 0
            for line in tqdm(f, desc="Indexing ClinVar"):
                parts = line.strip().split('\t')
                if len(parts) <= max(col_map.values()): continue
                
                # Filtrar solo GRCh38 o GRCh37 según convenga (usamos ambos pero marcamos)
                batch.append((
                    parts[col_map['AlleleID']],
                    parts[col_map['GeneSymbol']],
                    parts[col_map['RS# (dbSNP)']],
                    parts[col_map['ClinicalSignificance']],
                    parts[col_map['PhenotypeList']],
                    "", # hgvs_c (placeholder)
                    "", # hgvs_p (placeholder)
                    parts[col_map['Assembly']]
                ))
                
                if len(batch) >= chunk_size:
                    cursor.executemany("INSERT INTO variants (allele_id, gene_symbol, rs_id, clinical_significance, phenotype_list, hgvs_c, hgvs_p, assembly) VALUES (?,?,?,?,?,?,?,?)", batch)
                    conn.commit()
                    batch = []
                    count += chunk_size

            if batch:
                cursor.executemany("INSERT INTO variants (allele_id, gene_symbol, rs_id, clinical_significance, phenotype_list, hgvs_c, hgvs_p, assembly) VALUES (?,?,?,?,?,?,?,?)", batch)
                conn.commit()

        # Crear índices para búsquedas instantáneas
        print("⚡ Creando índices de búsqueda...")
        cursor.execute("CREATE INDEX idx_gene ON variants(gene_symbol)")
        cursor.execute("CREATE INDEX idx_rs ON variants(rs_id)")
        conn.commit()
        print("✅ Indexación completada exitosamente.")

    except Exception as e:
        print(f"❌ Error durante la indexación: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    create_index()
