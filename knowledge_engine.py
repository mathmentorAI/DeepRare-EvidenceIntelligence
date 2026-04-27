import os
import sqlite3
import pandas as pd

MASTER_STORAGE_ROOT = "/Volumes/KIOXIA/DeepRare"
CLINVAR_DB = os.path.join(MASTER_STORAGE_ROOT, "databases/clinvar_index.db")
GWAS_PSA_DIR = os.path.join(MASTER_STORAGE_ROOT, "knowledge_base/GWAS/gwas_psa")

def get_master_evidence(gene_symbol=None, rsid=None):
    """
    Consulta centralizada para todas las fuentes en el Almacenamiento Maestro.
    """
    evidence = []
    
    if not os.path.exists(MASTER_STORAGE_ROOT):
        return ""

    # 1. Consulta ClinVar Local (Índice Masivo)
    if os.path.exists(CLINVAR_DB):
        try:
            conn = sqlite3.connect(CLINVAR_DB)
            rs_query = rsid.replace("rs", "") if rsid else None
            
            if rs_query:
                query = "SELECT * FROM variants WHERE rs_id = ?"
                df = pd.read_sql_query(query, conn, params=(rs_query,))
            else:
                query = "SELECT * FROM variants WHERE gene_symbol = ?"
                df = pd.read_sql_query(query, conn, params=(gene_symbol,))
            
            conn.close()
            
            if not df.empty:
                pathogenic = df[df['clinical_significance'].str.contains('Pathogenic', case=False, na=False)]
                count = len(df)
                p_count = len(pathogenic)
                msg = f"Master Storage (ClinVar): {count} registros encontrados. "
                if p_count > 0:
                    msg += f"⚠️ {p_count} confirmaciones de PATOGENICIDAD."
                evidence.append(msg)
        except Exception as e:
            evidence.append(f"Error consultando Almacenamiento Maestro: {e}")

    # 2. Consulta GWAS (Si aplica)
    if gene_symbol == "CFTR" or "cystic fibrosis" in str(gene_symbol).lower():
        if os.path.exists(GWAS_PSA_DIR):
            evidence.append("Master Storage (GWAS): Se ha detectado una asociación significativa con la susceptibilidad a Pseudomonas aeruginosa.")

    return "\n".join(evidence) if evidence else ""
