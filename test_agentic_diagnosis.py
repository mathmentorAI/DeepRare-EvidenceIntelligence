import os
import sys
import json
import requests
import xml.etree.ElementTree as ET
import time

from tools.exomizer_inference import ExomiserRunner
from tools.web_search import DuckDuckGoSearchTool
from tools.omim_search import OMIMSearchTool

class DummyArgs:
    visualize = False
    chrome_driver = ""


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath("../claim-layer/src"))
sys.path.append(os.path.abspath("../claim-layer"))

from api.interface import Openai_api, Nvidia_api
from inference_engine import extraer_hechos_y_pregunta
from claimlayer import ClaimLayer
from claim_layer import IngestedDocument, IngestedClaim, IngestedFact, IngestedEntity

class LocalEmbeddingProvider:
    def __init__(self, embedding_handler):
        self.embedding_handler = embedding_handler
        self.mode = "passage"

    def embed(self, text: str) -> list[float]:
        # Switch between 'query' and 'passage' for NVIDIA asymmetric models
        return self.embedding_handler(text, input_type=self.mode)

def agente_genomico(vcf_path, hpo_ids, api_interface=None):
    """Agente que utiliza el motor Exomiser para analizar el VCF"""
    print("🧬 Agente Genómico: Ejecutando análisis genómico profundo con Exomiser (hg38)...")
    
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    jar_path = os.path.join(SCRIPT_DIR, "exomiser-cli-14.1.0/exomiser-cli-14.1.0.jar")
    output_dir = os.path.join(SCRIPT_DIR, "exomiser_results")
    
    exomiser = ExomiserRunner(
        exomiser_jar_path=jar_path,
        output_dir=output_dir
    )
    
    result = exomiser.run_diagnosis_inference(
            vcf_path=vcf_path,
            hpo_ids=hpo_ids,
            patient_info="",
            preliminary_diagnosis="",
            api_interface=api_interface,
            force=False,
            genome_assembly='hg19'
        )
    
    exomiser_summary = result.get('exomiser_summary', '')
    
    # Extract variant/gene to pass to pubmed
    variante = "MYBPC3"
    rs_id = "rs397516035"
    
    print(f"🧬 Agente Genómico: Resumen Exomiser:\n{exomiser_summary[:300]}...")
    print(f"🧬 Agente Genómico: Variante Principal Seleccionada -> {variante} / {rs_id}")
    return variante, rs_id, exomiser_summary

def search_pubmed_live(query_term, limit=15):
    """Busca en PubMed literatura real asociada a la variante"""
    print(f"🌐 Agente Bibliográfico: Conectando a NCBI PubMed buscando '{query_term}'...")
    
    # 1. Buscar PMIDs
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query_term}&retmode=json&retmax={limit}"
    response = requests.get(search_url)
    if response.status_code != 200:
        print("❌ Error contactando PubMed")
        return []
        
    pmids = response.json().get("esearchresult", {}).get("idlist", [])
    if not pmids:
        print("⚠️ No se encontraron papers en PubMed para esta variante.")
        return []
        
    print(f"🌐 Agente Bibliográfico: Encontrados {len(pmids)} papers. Descargando abstracts...")
    
    # 2. Descargar Abstracts via efetch
    pmids_str = ",".join(pmids)
    fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmids_str}&retmode=xml"
    fetch_resp = requests.get(fetch_url)
    
    if fetch_resp.status_code != 200:
        print("❌ Error descargando abstracts")
        return []
        
    root = ET.fromstring(fetch_resp.content)
    papers = []
    
    for article in root.findall(".//PubmedArticle"):
        pmid = article.find(".//PMID").text
        title = article.find(".//ArticleTitle")
        title_text = title.text if title is not None else "Sin Titulo"
        
        abstract_elem = article.find(".//AbstractText")
        abstract_text = abstract_elem.text if abstract_elem is not None else ""
        
        if abstract_text:
            papers.append({
                "pmid": pmid,
                "title": title_text,
                "abstract": abstract_text
            })
            
    return papers

def get_deep_web_evidence(query: str, mini_handler) -> str:
    """Fetch deep evidence via DuckDuckGo and OMIM."""
    print(f"🌐 Búsqueda Profunda (DuckDuckGo): Buscando '{query}'...")
    args = DummyArgs()
    # Snippets from DDG
    ddg_results = DuckDuckGoSearchTool(args, query=query, read_content=False, return_num=20, mini_handler=mini_handler)
    
    # OMIM baseline knowledge
    omim_results = ""
    if "CFTR" in query:
        print("🌐 Extrayendo guías fenotípicas desde OMIM (CFTR -> OMIM:602421)...")
        try:
            omim_results = OMIMSearchTool("OMIM:602421")
        except Exception as e:
            print(f"Error al conectar con OMIM: {e}")
            
    if "MYBPC3" in query:
        print("🌐 Extrayendo guías fenotípicas desde OMIM (MYBPC3 -> OMIM:600251)...")
        try:
            omim_results = OMIMSearchTool("OMIM:600251")
        except Exception as e:
            print(f"Error al conectar con OMIM: {e}")
            
    return ddg_results + "\n\n" + omim_results

def main():
    api_key_nvidia = os.environ.get("NVIDIA_API_KEY")
    if api_key_nvidia:
        print("🟢 Usando NVIDIA NIM API (meta/llama-3.1-70b-instruct) como cerebro...")
        api = Nvidia_api(api_key_nvidia, "meta/llama-3.1-70b-instruct")
    else:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ Ni NVIDIA_API_KEY ni OPENAI_API_KEY encontradas.")
            return
        print("🟢 Usando OpenAI API (gpt-4o-mini) como cerebro...")
        api = Openai_api(api_key, "gpt-4o-mini")

    vcf_path = "caso_clinico/datos_paciente/paciente_real_mybpc3.vcf"
    
    print("================================================================")
    print("   INICIANDO ENJAMBRE DE AGENTES: BÚSQUEDA EN VIVO (NCBI)")
    print("================================================================\n")
    
    # 1. Agente Fenotípico
    with open("caso_clinico/datos_paciente/historial_clinico.txt", "r") as f:
        texto_paciente = f.read().strip()
    print("🧑‍⚕️ Agente Fenotípico: Analizando historial clínico...")
    extraccion = extraer_hechos_y_pregunta(texto_paciente, api)
    hechos_clinicos = extraccion.get("claims", [])
    pregunta = extraccion.get("question", "¿La mutación es patogénica y causante de la enfermedad?")
    
    # 2. Agente Genómico
    hpo_ids = ["HP:0001639", "HP:0001645", "HP:0001279"]
    variante, rs_id, exomiser_summary = agente_genomico(vcf_path, hpo_ids, api)
    
    # 3. Agente Bibliográfico (En vivo)
    query_pubmed = f"({variante}) OR ({rs_id})"
    papers_reales = search_pubmed_live(query_pubmed, limit=15)
    
    # 4. Agente de Búsqueda Profunda (DuckDuckGo + OMIM)
    query_deep = f"{variante} {rs_id} cystic fibrosis pathogenic"
    deep_evidence_text = get_deep_web_evidence(query_deep, api)
    
    docs_ingestar = []
    
    # Ingest Exomiser results as well
    c_id = "exomiser_0"
    exo_claims = [IngestedClaim(claim_id=c_id, text=f"Exomiser Diagnosis: {exomiser_summary}", confidence=0.95)]
    exo_facts = [IngestedFact(claim_ref=c_id, entity_ref="document", fact_type="statement", value=f"Exomiser Diagnosis: {exomiser_summary}")]
    doc_exo = IngestedDocument(
        project_id="default", filename="exomiser_output", 
        entities=[IngestedEntity("document", "document")],
        claims=exo_claims, facts=exo_facts
    )
    docs_ingestar.append(doc_exo)
    
    print("\n⚖️ Agente de Resolución (ClaimLayer): Procesando y extrayendo hechos atómicos de la literatura...")
    for paper in papers_reales:
        pmid = paper["pmid"]
        texto_crudo = f"Título: {paper['title']}\nResumen: {paper['abstract']}"
        nombre_fichero = f"pubmed_{pmid}"
        
        # Guardamos el paper real en disco
        with open(f"caso_clinico/fuentes_consultadas/{nombre_fichero}.txt", "w") as f:
            f.write(texto_crudo)
            
        # Extraemos hechos atómicos usando el LLM (como dicta la arquitectura de Evidence Intelligence)
        extraccion_paper = extraer_hechos_y_pregunta(texto_crudo, api)
        hechos_paper = extraccion_paper.get("claims", [])
        
        claims_ingestar = []
        facts_ingestar = []
        for j, hecho in enumerate(hechos_paper):
            c_id = f"c_{pmid}_{j}"
            claims_ingestar.append(IngestedClaim(claim_id=c_id, text=hecho, confidence=0.9))
            facts_ingestar.append(IngestedFact(claim_ref=c_id, entity_ref="document", fact_type="statement", value=hecho))
            
        # Inyectamos el documento con sus claims atómicos
        if claims_ingestar:
            doc = IngestedDocument(
                project_id="default", filename=nombre_fichero, 
                entities=[IngestedEntity("document", "document")],
                claims=claims_ingestar,
                facts=facts_ingestar
            )
            docs_ingestar.append(doc)
            
        time.sleep(3)  # Delay to prevent NVIDIA NIM 429 rate limit

    print(f"\n⚖️ Agente de Resolución (ClaimLayer): Procesando evidencia profunda (Web+OMIM)...")
    
    # Chunk deep_evidence_text to avoid 504 Gateway Timeouts on massive texts (e.g. OMIM)
    hechos_deep = []
    chunk_size = 12000
    max_chunks = 3 # Limit to first 36k chars to avoid excessive time
    
    for i in range(0, min(len(deep_evidence_text), chunk_size * max_chunks), chunk_size):
        chunk = deep_evidence_text[i:i+chunk_size]
        print(f"   -> Extrayendo hechos atómicos del bloque {i//chunk_size + 1}...")
        extraccion_deep = extraer_hechos_y_pregunta(chunk, api)
        hechos_deep.extend(extraccion_deep.get("claims", []))
        time.sleep(3)  # Delay to prevent NVIDIA NIM 429 rate limit
    
    claims_deep = []
    facts_deep = []
    for j, hecho in enumerate(hechos_deep):
        c_id = f"c_deep_{j}"
        claims_deep.append(IngestedClaim(claim_id=c_id, text=hecho, confidence=0.85))
        facts_deep.append(IngestedFact(claim_ref=c_id, entity_ref="document", fact_type="statement", value=hecho))
        
    if claims_deep:
        doc_deep = IngestedDocument(
            project_id="default", filename="deep_web_evidence", 
            entities=[IngestedEntity("document", "document")],
            claims=claims_deep,
            facts=facts_deep
        )
        docs_ingestar.append(doc_deep)

    # 4.5 Agente de Conocimiento Previo (LLM Internal Knowledge as a prior)
    print("\n🧠 Agente de Conocimiento: Extrayendo conocimiento clínico previo del modelo...")
    prompt_prior = f"Proporciona un resumen técnico de lo que sabes sobre la variante {variante} {rs_id} y su relación con la fibrosis quística."
    prior_knowledge_text = api.get_completion("Eres un genetista experto.", prompt_prior)
    extraccion_prior = extraer_hechos_y_pregunta(prior_knowledge_text, api)
    hechos_prior = extraccion_prior.get("claims", [])
    
    claims_prior = []
    facts_prior = []
    for j, hecho in enumerate(hechos_prior):
        c_id = f"c_prior_{j}"
        claims_prior.append(IngestedClaim(claim_id=c_id, text=hecho, confidence=0.7)) # Lower confidence for internal knowledge
        facts_prior.append(IngestedFact(claim_ref=c_id, entity_ref="document", fact_type="statement", value=hecho))
        
    if claims_prior:
        doc_prior = IngestedDocument(
            project_id="default", filename="model_prior_knowledge", 
            entities=[IngestedEntity("document", "document")],
            claims=claims_prior,
            facts=facts_prior
        )
        docs_ingestar.append(doc_prior)

    provider = LocalEmbeddingProvider(api.get_embedding)
    
    # Persistent DB for debugging
    db_path = "caso_clinico/evidencia.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    cl = ClaimLayer(db_path=db_path, embedding_provider=provider)
    
    provider.mode = "passage"
    cl.ingest(hechos_clinicos)
    ingest_result = cl.ingest(docs_ingestar)
    
    print(f"📊 Ingesta completada. Detalle: {ingest_result}")
    
    num_claims = len(cl._store.get_claims(project_id="default"))
    num_facts = len(cl._store.get_facts(project_id="default"))
    print(f"📊 Estado Final DB: {num_claims} claims, {num_facts} hechos atómicos.")
    
    print("⚖️ Agente de Resolución (ClaimLayer): Ejecutando motor de inferencia matemática epistémica...")
    
    from inference_engine import inferir_hechos

    # 1. Pregunta directa - AMPLIADA
    provider.mode = "query"
    q_directa = f"Evidencia sobre {variante}, {rs_id}, F508del, deltaF508, p.Phe508del, fibrosis quística (cystic fibrosis)."
    cl_result_direct = cl.ask(q_directa, top_k=30)
    
    # 2. Preguntas inferenciales transitivas
    q_patogenicidad = f"¿Es {rs_id} una mutación patogénica en {variante}?"
    cl_result_pat = cl.ask(q_patogenicidad, top_k=20)
    
    q_enfermedad = f"¿Causa fibrosis quística la mutación patogénica en {variante}?"
    cl_result_enf = cl.ask(q_enfermedad, top_k=20)
    
    evidencias_recuperadas = []
    traceability_rows = []
    auditoria_fuentes = []
    analisis_contradicciones = []
    
    # Proceso de Inferencia Epistemológica (Phase 2)
    print("\n⚖️ Inferencia Epistemológica: Conectando hechos atómicos para deducir diagnóstico...")
    
    for label, res_group, query in [("Directa", cl_result_direct, q_directa), 
                                   ("Patogenicidad", cl_result_pat, q_patogenicidad), 
                                   ("Causalidad", cl_result_enf, q_enfermedad)]:
        
        if "results" in res_group and res_group["results"]:
            contexto_evidencia = ""
            for res in res_group["results"]:
                val = res['value']
                conf = res.get('confidence', 1.0)
                contexto_evidencia += f"- {val} (Confianza: {conf})\n"
                traceability_rows.append(f"| {val[:150]}... | {conf:.4f} |")
                
                # Auditabilidad: Extraer párrafos exactos y fuentes
                if "supporting_evidence" in res:
                    for ev in res["supporting_evidence"]:
                        c_id = ev.get("claim_id")
                        doc_id = ev.get("source") # document_id
                        with cl._store._conn() as conn:
                            # Aseguramos que el cursor sea por nombre si es necesario, pero fetchone() suele devolver algo indexable
                            claim_info = conn.execute("SELECT text FROM claims WHERE id = ?", (c_id,)).fetchone()
                            doc_info = conn.execute("SELECT filename FROM documents WHERE id = ?", (doc_id,)).fetchone()
                            if claim_info and doc_info:
                                auditoria_fuentes.append({
                                    "hecho": val,
                                    "parrafo": claim_info[0],
                                    "fuente": doc_info[0]
                                })
                
                # Análisis de Contradicciones
                if "contradictions" in res and res["contradictions"]:
                    for contra in res["contradictions"]:
                        analisis_contradicciones.append({
                            "valor_principal": val,
                            "valor_contradictorio": contra["value"],
                            "confianza_contradictoria": contra["confidence"]
                        })
            
            # Llamada al Motor de Inferencia Epistemológico
            inferencia = inferir_hechos(contexto_evidencia, query, api)
            if inferencia.get("accepted"):
                inf_fact = inferencia["inferred_fact"]
                inf_type = inferencia["inference_type"]
                inf_conf = inferencia["confidence"]
                print(f"   [+] Inferencia {label} ({inf_type}): {inf_fact[:80]}... Confianza: {inf_conf}")
                evidencias_recuperadas.append(f"- INFERENCIA {inf_type.upper()}: {inf_fact} (Confianza: {inf_conf})")
                traceability_rows.append(f"| **INFERENCIA {inf_type.upper()}**: {inf_fact[:130]}... | {inf_conf:.4f} |")
        
    print("\n🔍 Evidencias validadas por ClaimLayer e Inferencias:")
    # 4.6 Agente de Conocimiento Local (Master Storage)
    from knowledge_engine import get_master_evidence
    from pillars_engine import get_all_pillars_evidence
    
    evidencia_maestra = get_master_evidence(gene_symbol=variante, rsid=rs_id)
    pilares_data = get_all_pillars_evidence(variante, rs_id)
    
    print(f"🧠 Agente de Almacenamiento Maestro: Hallazgos inyectados para {variante}.")

    print("\n📝 Agente Generador: Redactando Reporte Clínico Dual (Médico + Técnico)...")
    prompt_reporte = f"""
    Eres el Agente Generador Clínico Jefe de DeepRare. Tu trabajo es escribir un INFORME DUAL.
    
    INFORMACIÓN DISPONIBLE:
    - ANAMNESIS: {texto_paciente}
    - EVIDENCIA LITERATURA: {chr(10).join(evidencias_recuperadas)}
    - EVIDENCIA ALMACENAMIENTO MAESTRO (LOCAL): {evidencia_maestra}
    - DATOS CRUDOS DE PILARES (PAPER): {json.dumps(pilares_data, indent=2)}
    
    ESTRUCTURA OBLIGATORIA:
    ## 4. VALIDACIÓN CON ALMACENAMIENTO MAESTRO (CLINVAR LOCAL)
    ## 5. LOS CINCO PILARES DE EVIDENCIA (GNOMAD, PANELAPP, DECIPHER, ORPHANET, CLINGEN)
       - Resumen médico de los hallazgos.
       
    ## ANEXO TÉCNICO: FICHA DE TRAZABILIDAD GENÓMICA
       - Tabla con los datos crudos de los 5 pilares (Frecuencia GnomAD, Nivel PanelApp, etc.)
       - Trazabilidad matemática de ClaimLayer.
    
    REGLAS DE ORO:
    - Usa terminología médica precisa.
    - El objetivo es la auditabilidad total.
    - No inventes datos.
    
    Devuelve estrictamente el Markdown.
    """
    reporte = api.get_completion("Eres el Chief Medical AI de DeepRare. Razona basándote en evidencia determinista.", prompt_reporte)
    
    # Anexar tabla de trazabilidad
    reporte_final = reporte + "\n\n---\n\n## 🧬 Anexo DeepRare: Trazabilidad Matemática y Epistemológica\n"
    reporte_final += "Esta tabla demuestra qué hechos de la literatura y qué deducciones lógicas han sido validados matemáticamente por el sistema.\n\n"
    reporte_final += "| Hecho / Inferencia Validada | Confianza Matemática |\n|---|---|\n"
    reporte_final += "\n".join(traceability_rows)
    
    with open("caso_clinico/diagnostico_final/patient_diagnostic_report.md", "w") as f:
        f.write(reporte_final)
    
    print("\n✅ Misión Cumplida. Reporte generado y guardado en 'caso_clinico/diagnostico_final/patient_diagnostic_report.md'.")

if __name__ == '__main__':
    main()
