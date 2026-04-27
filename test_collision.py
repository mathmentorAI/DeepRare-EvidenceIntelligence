import os
import sys
import json

# Add parent directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath("../claim-layer/src"))
sys.path.append(os.path.abspath("../claim-layer"))

from api.interface import Openai_api
from inference_engine import extraer_hechos_y_pregunta, inferir_hechos
from claimlayer import ClaimLayer
from claim_layer import IngestedDocument, IngestedClaim, IngestedFact

class LocalEmbeddingProvider:
    def __init__(self, embedding_handler):
        self.embedding_handler = embedding_handler

    def embed(self, text: str) -> list[float]:
        return self.embedding_handler(text)

def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ OPENAI_API_KEY no encontrada.")
        return
    
    api = Openai_api(api_key, "gpt-4o-mini")

    texto_paciente = "Paciente acude a consulta para evaluación genética. Su secuenciación revela que es portador de la variante MYBPC3_c.1504C>T. ¿Es esta mutación la causa de una Miocardiopatía Hipertrófica y supone un riesgo letal para el paciente?"
    
    evidencia_paper_2012 = "La mutación MYBPC3_c.1504C>T es la causa de una Miocardiopatía Hipertrófica y supone un riesgo letal para el paciente."
    
    evidencia_bd_2024 = "La mutación MYBPC3_c.1504C>T no es la causa de una Miocardiopatía Hipertrófica y no supone un riesgo letal para el paciente."
    
    print("================================================================")
    print("   TEST DE COLISIÓN FRONTAL: LA PURGA DE gnomAD (MYBPC3)")
    print("================================================================\n")
    print(f"🧑‍⚕️ CASO DEL PACIENTE:\n{texto_paciente}\n")
    
    print("----------------------------------------------------------------")
    print("[FASE 1] Extracción Ontológica (Hechos Crudos)")
    print("----------------------------------------------------------------")
    extraccion = extraer_hechos_y_pregunta(texto_paciente, api)
    hechos_base = extraccion.get("claims", [])
    pregunta = extraccion.get("question", "¿Es esta mutación patogénica o benigna?")
    
    print(f"Hechos extraídos:\n{json.dumps(hechos_base, indent=2, ensure_ascii=False)}\n")
    print(f"Pregunta extraída:\n{pregunta}\n")
    
    print("----------------------------------------------------------------")
    print("[FASE 2] Motor de Inferencia Epistemológico")
    print("----------------------------------------------------------------")
    evidencia_str = "\\n".join(hechos_base + [evidencia_paper_2012, evidencia_bd_2024])
    inferencia_data = inferir_hechos(evidencia_str, pregunta, api)
    print(f"Inferencia generada a partir del conflicto:\n{json.dumps(inferencia_data, indent=2, ensure_ascii=False)}\n")
    
    print("----------------------------------------------------------------")
    print("[FASE 3 y 4] ClaimLayer: Resolución Determinista del Conflicto")
    print("----------------------------------------------------------------")
    provider = LocalEmbeddingProvider(api.get_embedding)
    cl = ClaimLayer(embedding_provider=provider)
    
    # Ingesting
    cl.ingest(hechos_base)
    print("✅ Hechos del paciente ingestados.")
    
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
        print(f"✅ Inferencia inyectada (Confianza: {confidence}).")
    doc_2012 = IngestedDocument(
        project_id="default",
        filename="paper_2012",
        entities=[],
        claims=[IngestedClaim(claim_id="c_2012", text=evidencia_paper_2012, confidence=0.1)],
        facts=[IngestedFact(claim_ref="c_2012", entity_ref="document", fact_type="statement", value=evidencia_paper_2012)]
    )
    
    doc_2024 = IngestedDocument(
        project_id="default",
        filename="gnomad_2024",
        entities=[],
        claims=[IngestedClaim(claim_id="c_2024", text=evidencia_bd_2024, confidence=1.0)],
        facts=[IngestedFact(claim_ref="c_2024", entity_ref="document", fact_type="statement", value=evidencia_bd_2024)]
    )
    
    cl.ingest([doc_2012, doc_2024])
    print("✅ Literatura (2012) inyectada con Confianza Epistemológica: 0.1 (Narrativa)")
    print("✅ Base de Datos (2024) inyectada con Confianza Epistemológica: 1.0 (Aritmética Poblacional)\n")
    
    cl_result = cl.ask(pregunta)
    evidencias_recuperadas = []
    if "results" in cl_result and len(cl_result["results"]) > 0:
        for res in cl_result["results"]:
            evidencias_recuperadas.append(f"- {res['value']} (Confianza Matemática Final: {res.get('confidence', 1.0):.4f})")
            
    print("🔍 Evidencias validadas recuperadas tras aplicar penalizaciones por contradicción:")
    print("\\n".join(evidencias_recuperadas) + "\n")
    
    print("----------------------------------------------------------------")
    print("[FASE 5] Última Milla Generativa (Evidence Intelligence)")
    print("----------------------------------------------------------------")
    prompt_final = f"Evidencias validadas matemáticamente:\n{chr(10).join(evidencias_recuperadas)}\n\nTarea: Responde la pregunta clínica basándote ESTRICTAMENTE en la evidencia validada de ClaimLayer."
    respuesta = api.get_completion("You are a deterministic clinical generator. Do not hallucinate outside the provided evidence.", prompt_final)
        
    print(f"🤖 Diagnóstico Final del Sistema ClaimLayer:\n{respuesta}\n")
    
    print("----------------------------------------------------------------")
    print("[BASE DE COMPARACIÓN] ¿Qué habría respondido RAG tradicional sin Evidence Intelligence?")
    print("----------------------------------------------------------------")
    prompt_basura = f"El paciente tiene mutación MYBPC3_c.1504C>T.\nEvidencia 1: {evidencia_paper_2012}\nEvidencia 2: {evidencia_bd_2024}\n\nPregunta: {pregunta}"
    respuesta_sucia = api.get_completion("Eres un asistente médico general. Usa la información provista para diagnosticar.", prompt_basura)
    print(f"🤡 Diagnóstico Clásico (LLM leyendo a lo bruto):\n{respuesta_sucia}\n")

if __name__ == '__main__':
    main()
