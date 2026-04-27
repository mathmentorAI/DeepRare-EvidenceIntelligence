import sys
import os
import json

# Add parent directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath("../claim-layer/src"))
sys.path.append(os.path.abspath("../claim-layer"))

from api.interface import Openai_api
from inference_engine import extraer_hechos_y_pregunta, inferir_hechos
from claimlayer import ClaimLayer
from claim_layer import IngestedDocument, IngestedClaim, IngestedFact
# from diagnosis import LocalEmbeddingProvider

class LocalEmbeddingProvider:
    def __init__(self, embedding_handler):
        self.embedding_handler = embedding_handler

    def embed(self, text: str) -> list[float]:
        return self.embedding_handler(text)

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY no encontrada en el entorno.")
        print("Iniciando MODO SIMULACIÓN (Mock) para demostrar la estructura del pipeline...\n")
        
        class MockAPI:
            def get_completion(self, sys_prompt, usr_prompt, seed=42):
                if "Extractor Epistemológico" in sys_prompt:
                    return '{"claims": ["Hecho de Estado Físico: El paciente presenta fiebre de 39 grados.", "Hecho Descriptivo: El paciente tiene manchas rojas en la piel."], "question": "¿Cuál es el diagnóstico?"}'
                elif "Motor de Inferencia" in sys_prompt:
                    return '{"inferred_fact": "El paciente podría tener una infección sistémica exantemática.", "inference_type": "Deductiva", "confidence": 0.95, "accepted": true}'
                return "**Sarampión** (Rank #1/5)\\nDiagnostic Reasoning: Cuadro febril con erupción maculopapular."
            def get_embedding(self, text, model="text-embedding-3-small"):
                return [0.1] * 1536
        api = MockAPI()
    else:
        print("✅ OPENAI_API_KEY detectada. Ejecutando pipeline real contra LLMs...\n")
        api = Openai_api(api_key, "gpt-4o-mini")

    texto_paciente = "Paciente de 5 años presenta fiebre persistente de 39 grados desde hace 3 días. Además se observan máculas eritematosas (manchas rojas) en el tronco y extremidades. ¿Cuál es el diagnóstico más probable?"
    
    print("================================================================")
    print("        INICIANDO TEST: PIPELINE EVIDENCE INTELLIGENCE")
    print("================================================================\n")
    print(f"🧑‍⚕️ CASO DEL PACIENTE:\n{texto_paciente}\n")
    
    print("----------------------------------------------------------------")
    print("[FASE 1] Extracción Ontológica (Hechos Crudos)")
    print("----------------------------------------------------------------")
    extraccion = extraer_hechos_y_pregunta(texto_paciente, api)
    hechos_base = extraccion.get("claims", [])
    pregunta = extraccion.get("question", "¿Cuál es el diagnóstico más probable?")
    print(f"Hechos extraídos:\n{json.dumps(hechos_base, indent=2, ensure_ascii=False)}\n")
    print(f"Pregunta extraída:\n{pregunta}\n")
    
    print("----------------------------------------------------------------")
    print("[FASE 2] Motor de Inferencia Epistemológico")
    print("----------------------------------------------------------------")
    evidencia_str = "\\n".join(hechos_base)
    inferencia_data = inferir_hechos(evidencia_str, pregunta, api)
    print(f"Inferencia generada:\n{json.dumps(inferencia_data, indent=2, ensure_ascii=False)}\n")
    
    print("----------------------------------------------------------------")
    print("[FASE 3 y 4] ClaimLayer: Resolución Determinista")
    print("----------------------------------------------------------------")
    provider = LocalEmbeddingProvider(api.get_embedding)
    cl = ClaimLayer(embedding_provider=provider)
    
    # Ingesting
    cl.ingest(hechos_base)
    print("✅ Hechos base ingestados con confianza absoluta (1.0).")
    
    if inferencia_data.get("accepted", False):
        cid = "inf_001"
        fact_text = inferencia_data.get("inferred_fact", "")
        confidence = float(inferencia_data.get("confidence", 0.7))
        doc_inferido = IngestedDocument(
            project_id="default",
            filename="motor_inferencia",
            entities=[],
            claims=[IngestedClaim(claim_id=cid, text=fact_text, confidence=confidence)],
            facts=[IngestedFact(claim_ref=cid, entity_ref="document", fact_type="statement", value=fact_text)]
        )
        cl.ingest([doc_inferido])
        print(f"✅ Hecho inferido ingestados con confianza penalizada ({confidence}).")
    
    cl.ingest(["Evidencia Externa: Revisión clínica indica posible rubeola o sarampión."])
    print("✅ Evidencias de herramientas externas ingestadas.\n")
    
    cl_result = cl.ask(pregunta)
    evidencias_recuperadas = []
    if "results" in cl_result and len(cl_result["results"]) > 0:
        for res in cl_result["results"]:
            evidencias_recuperadas.append(f"- {res['value']} (Confianza: {res.get('confidence', 1.0):.4f})")
            
    print("🔍 Evidencias validadas recuperadas por ClaimLayer:")
    print("\\n".join(evidencias_recuperadas) + "\n")
    
    print("----------------------------------------------------------------")
    print("[FASE 5] Última Milla Generativa")
    print("----------------------------------------------------------------")
    prompt_final = f"Evidencias validadas:\n{chr(10).join(evidencias_recuperadas)}\n\nTarea: Genera diagnóstico."
    respuesta = api.get_completion("You are a deterministic clinical generator.", prompt_final)
        
    print(f"🤖 Diagnóstico Final del Sistema:\n{respuesta}\n")
    print("================================================================")
    print("                 TEST COMPLETADO CON ÉXITO")
    print("================================================================")

if __name__ == '__main__':
    main()
