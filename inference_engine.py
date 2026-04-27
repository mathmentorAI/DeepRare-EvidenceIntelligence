import json
from api.interface import Openai_api

def extraer_hechos_y_pregunta(texto_crudo: str, api: Openai_api) -> dict:
    """Extrae las afirmaciones explícitas y la pregunta de un texto crudo."""
    system_prompt = """Eres un Extractor Epistemológico especializado en Medicina Genómica.
Tu objetivo es analizar el texto crudo proporcionado y descomponerlo en "Unidades de Evidencia" atómicas (hechos individuales). 

Para ser considerado un "hecho válido", la afirmación debe encajar en una de las siguientes categorías ontológicas:
1. Hecho de Estado Físico/Clínico: Descripciones objetivas sobre el mundo o el paciente (ej: "Presencia de quistes").
2. Hecho Genómico/Funcional: Características intrínsecas de una variante o gen (ej: "La mutación F508del causa pérdida de función").
3. Hecho Epidemiológico/Prevalencia: Datos sobre la frecuencia de una condición en una población.
4. Hecho Patogénico: Relación causal entre una variante y una enfermedad documentada en literatura.
5. Hecho Descriptivo: Atributos generales de una entidad.

REGLAS ESTRICTAS:
- Extrae cada hecho de forma atómica y autocontenida.
- IMPORTANTE: NO limites la extracción solo a hechos sobre "el paciente". Los hechos generales sobre la variante (ej: "F508del es patogénica") son FUNDAMENTALES y deben extraerse siempre.
- Convierte los pronombres en entidades explícitamente declaradas.
- NO deduzcas, NO asumas y NO conectes hechos. Limítate a lo explícitamente declarado.
- Si el texto contiene una interrogación o duda dirigida al sistema, extráela en el campo "question".

Devuelve EXCLUSIVAMENTE un JSON con esta estructura:
{
  "claims": ["Categoría: hecho extraído 1", "Categoría: hecho extraído 2"],
  "question": "pregunta extraída"
}"""
    
    prompt = f"Texto crudo:\n{texto_crudo}\n\nAsegúrate de devolver ÚNICAMENTE el JSON crudo, sin bloques de código ni markdown."
    
    response = api.get_completion(system_prompt, prompt)
    if not response:
        return {}

    try:
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
            
        return json.loads(cleaned_response.strip())
    except Exception as e:
        print(f"Failed to parse ontological extraction JSON: {e}")
        return {}

def inferir_hechos(evidencias_texto: str, pregunta: str, api: Openai_api) -> dict:
    """
    Epistemological Inference Engine.
    Takes base facts and a question, and infers a new fact while
    classifying it using the Epistemological Table rules.
    """
    system_prompt = """Eres un Motor de Inferencia Epistemológico. 
Se te darán unos "Hechos Base" y una "Pregunta". Tu objetivo es deducir un único nuevo hecho explícito que conecte los hechos base de forma que responda la pregunta directamente.

IMPORTANTE: Debes clasificar el tipo de inferencia que has usado basándote en la siguiente tabla de reglas:
- "Espacial" (Deduce relaciones de ubicación. Debe aceptarse. Confianza: 0.95)
- "Deductiva" (La conclusión emana necesariamente de las premisas. Debe aceptarse. Confianza: 0.95)
- "Sentido Común" (Se apoya en un cuerpo masivo de verdades obvias físicas. Debe aceptarse. Confianza: 0.70)
- "Causal" (Intenta separar la simple correlación de necesidad. Debe verificarse. Confianza: 0.60)
- "Narrativa" (Inventa conexiones lógicas para rellenar vacíos. NO debe aceptarse. Confianza: 0.1)

Debes devolver EXCLUSIVAMENTE un JSON válido con esta estructura:
{
  "inferred_fact": "<Tu deducción clara y concisa como un hecho afirmado>",
  "inference_type": "<Uno de los tipos listados arriba>",
  "confidence": <El valor numérico indicado arriba>,
  "accepted": <true si debe aceptarse, false si es Narrativa u otra no aceptable>
}"""

    user_prompt = f"Hechos Base:\n{evidencias_texto}\n\nPregunta a resolver:\n{pregunta}\n\nAsegúrate de devolver ÚNICAMENTE el JSON crudo, sin bloques de código ni markdown."
    
    response = api.get_completion(system_prompt, user_prompt)
    if not response:
        return {}

    try:
        # Clean up possible markdown formatting
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
            
        return json.loads(cleaned_response.strip())
    except Exception as e:
        print(f"Failed to parse epistemological inference JSON: {e}")
        print(f"Raw response was: {response}")
        return {}
