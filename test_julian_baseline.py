
import os
import sys

# Import the API from our main repo to avoid missing OPENAI_API_KEY
sys.path.append(os.path.abspath("../DeepRare"))
from api.interface import Nvidia_api

def test_original_deeprare_baseline():
    print("🚀 EJECUTANDO DEEPRARE ORIGINAL (RAG Clásico sin ClaimLayer)")
    print("Repositorio: https://github.com/julianig72/DeepRare")
    print("-------------------------------------------------------------------")
    
    api_key_nvidia = os.environ.get("NVIDIA_API_KEY")
    api = Nvidia_api(api_key_nvidia, "meta/llama-3.1-70b-instruct")
    print("Usando NVIDIA NIM API como cerebro.")

    # La misma evidencia conflictiva que usamos en nuestra prueba
    evidencia_recuperada = """
[EVIDENCE 1 - PubMed 2012]: En 2012, estudiamos una familia devastada por la muerte súbita. Analizamos a los miembros y todos los afectados presentaban la variante c.1504C>T en el gen MYBPC3. Concluimos inequívocamente que esta mutación es la causa letal de la Miocardiopatía Hipertrófica en esta familia.

[EVIDENCE 2 - gnomAD 2024]: La variante rs397515974 (MYBPC3 c.1504C>T) tiene una frecuencia alélica alta en poblaciones control sanas (0.05 en gnomAD) y se clasifica como benigna poblacionalmente.
    """
    
    # Prompt original de DeepRare (Simplificado para el núcleo de diagnóstico)
    # En DeepRare Original, el LLM lee los abstracts en crudo y saca conclusiones.
    prompt_sistema = """You are a medical AI assistant diagnosing rare diseases based on genetic variants.
Analyze the provided evidence carefully and provide a clinical diagnostic report.
Determine if the variant is Pathogenic, Benign, or VUS (Variant of Uncertain Significance)."""

    prompt_usuario = f"""
Patient variant: MYBPC3 c.1504C>T (rs397515974)
Suspected phenotype: Hypertrophic cardiomyopathy

Recovered Evidence (Web/PubMed):
{evidencia_recuperada}

Write your final diagnostic report and explicitly state the pathogenicity classification.
"""
    
    print("\n🧠 LLM (DeepRare Original) Procesando la evidencia en crudo...")
    respuesta = api.get_completion(prompt_sistema, prompt_usuario)
    
    print("\n================== REPORTE GENERADO ==================")
    print(respuesta)
    print("======================================================\n")

if __name__ == "__main__":
    test_original_deeprare_baseline()
