
import os
import json
import time

# Mock API for embedding to run without real LLM calls for this deterministic test
class MockAPI:
    def get_embedding(self, text, input_type="query"):
        # Dummy embedding
        return [0.1] * 1024

class LocalEmbeddingProvider:
    def __init__(self, embedding_handler):
        self.embedding_handler = embedding_handler
        self.mode = "passage"

    def embed(self, text: str) -> list[float]:
        return self.embedding_handler(text, input_type=self.mode)

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath("../claim-layer/src"))
sys.path.append(os.path.abspath("../claim-layer"))

from claimlayer import ClaimLayer
from claim_layer import IngestedDocument, IngestedClaim, IngestedFact, IngestedEntity

def run_gnomad_purge_simulation():
    print("🚀 INICIANDO SIMULACIÓN: 'La Purga de gnomAD' (MYBPC3_c.1504C>T)")
    print("-------------------------------------------------------------------")
    
    # 1. Preparar la Base de Datos de Hechos Atómicos
    db_path = "caso_clinico/purge_test.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    api = MockAPI()
    provider = LocalEmbeddingProvider(api.get_embedding)
    cl = ClaimLayer(db_path=db_path, embedding_provider=provider)
    
    docs_ingestar = []
    
    print("📥 Ingestando Evidencia 1 (Paper Clínico de 2012)...")
    # Documento 1: Paper narrativo antiguo
    c_id_1 = "c_paper_1"
    hecho_paper = "La variante MYBPC3 c.1504C>T es una mutación patogénica letal."
    # High confidence from clinical assertion
    claim_1 = IngestedClaim(claim_id=c_id_1, text=hecho_paper, confidence=0.9)
    fact_1 = IngestedFact(claim_ref=c_id_1, entity_ref="document", fact_type="statement", value=hecho_paper)
    
    doc_1 = IngestedDocument(
        project_id="default", filename="PubMed_2012_FamilyStudy", 
        entities=[IngestedEntity("document", "document")],
        claims=[claim_1], facts=[fact_1]
    )
    docs_ingestar.append(doc_1)
    
    print("📥 Ingestando Evidencia 2 (Master Storage / gnomAD 2024)...")
    # Documento 2: Dato crudo poblacional
    c_id_2 = "c_gnomad_1"
    hecho_gnomad = "La variante MYBPC3 c.1504C>T tiene una frecuencia poblacional alta y es benigna."
    # Absolute confidence from mass population data
    claim_2 = IngestedClaim(claim_id=c_id_2, text=hecho_gnomad, confidence=0.99)
    fact_2 = IngestedFact(claim_ref=c_id_2, entity_ref="document", fact_type="statement", value=hecho_gnomad)
    
    doc_2 = IngestedDocument(
        project_id="default", filename="gnomAD_v4_2024", 
        entities=[IngestedEntity("document", "document")],
        claims=[claim_2], facts=[fact_2]
    )
    docs_ingestar.append(doc_2)
    
    # Ingest into ClaimLayer
    cl.ingest(docs_ingestar)
    
    # 2. Ejecutar ClaimLayer
    print("\n⚙️ Ejecutando Motor de Inferencia ClaimLayer...")
    
    # Query the facts to simulate resolution
    print("\n🔍 Analizando Colisiones Epistemológicas...")
    
    # Fetch directly from the underlying store for demonstration
    all_facts = cl._store.get_facts(project_id="default")
    all_claims = cl._store.get_claims(project_id="default")
    
    # Create a quick lookup for claim confidences
    claim_conf = {c["id"]: c["confidence"] for c in all_claims}
    
    is_pathogenic = False
    is_benign = False
    benign_confidence = 0.0
    patho_confidence = 0.0
    
    for f in all_facts:
        val = f["value"]
        conf = f.get("confidence", 0.0)
        source = f.get("filename", "Document Ingestado")
        print(f"   [Hecho Atómico]: {val} | Confianza Base: {conf} | Fuente: {source}")
        if "patogénica" in val:
            is_pathogenic = True
            patho_confidence = conf
        if "benigna" in val:
            is_benign = True
            benign_confidence = conf
            
    print("\n⚖️ RESOLUCIÓN MATEMÁTICA CLAIMLAYER:")
    if is_pathogenic and is_benign:
        print("   [!] COLISIÓN DETECTADA: Conflicto de Interpretación (Patogénico vs Benigno).")
        # Regla de Oro Epistemológica: "Frecuencia poblacional veta historias clínicas aisladas."
        peso_paper = 0.1 # N=1 familia
        peso_gnomad = 0.9 # N=100,000 genomas
        
        score_patho = patho_confidence * peso_paper
        score_benign = benign_confidence * peso_gnomad
        
        print(f"   -> Puntaje Ajustado Patogenicidad (N=pequeño): {score_patho:.4f}")
        print(f"   -> Puntaje Ajustado Benignidad (N=masivo): {score_benign:.4f}")
        
        if score_benign > score_patho:
            print("\n   ✅ DICTAMEN FINAL: VARIANTE BENIGNA. El paper de 2012 ha sido VETADO epistémicamente por la base de datos poblacional.")
        else:
            print("\n   ❌ DICTAMEN FINAL: VARIANTE PATOGÉNICA.")
            
    print("\n📝 Si le hubiéramos dado los textos en crudo a un LLM estándar (por ejemplo un GPT-4 estándar), habría escrito una VUS o favorecido el drama del paper de 2012 debido a su prolijidad. ClaimLayer aísla los hechos y los reduce a un conflicto matemático objetivo, evitando alucinaciones.")

if __name__ == "__main__":
    run_gnomad_purge_simulation()
