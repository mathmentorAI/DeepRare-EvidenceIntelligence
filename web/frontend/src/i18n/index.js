import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const en = {
  app: {
    subtitle: "Evidence Intelligence Platform"
  },
  nav: {
    home: "Home",
    hpo_extraction: "HPO Extraction",
    diagnosis: "Phenotype Diagnosis",
    gene_diagnosis: "Gene + Variant Diagnosis",
    settings: "Settings"
  },
  common: {
    cancel: "Cancel",
    save: "Save",
    clear: "Clear"
  },
  home: {
    welcome: "DeepRare Evidence Intelligence",
    description: "Deterministic clinical reasoning powered by ClaimLayer — Vetoing hallucinations with mathematical evidence.",
    get_started: "Start Analysis",
    configure_keys: "Configure API Keys",
    feature_hpo: "HPO Extraction",
    feature_hpo_desc: "Automatically extract phenotype terms from clinical text and map them to standardised HPO codes.",
    feature_diagnosis: "Phenotype Diagnosis",
    feature_diagnosis_desc: "Run deterministic multi-agent diagnosis from clinical phenotypes with full audit trail.",
    feature_gene: "Genomic Variant Analysis",
    feature_gene_desc: "Combine VCF data with Exomiser and ClaimLayer for evidence-backed variant prioritisation."
  },
  hpo: {
    title: "HPO Extraction",
    description: "Extract standardised Human Phenotype Ontology terms from free-text clinical notes.",
    input_label: "Clinical Notes",
    input_placeholder: "Paste patient clinical text here...",
    extract_btn: "Extract Phenotypes",
    extracting: "Extracting...",
    results_title: "Extracted HPO Terms",
    col_phenotype: "Phenotype",
    col_hpo_code: "HPO Code",
    col_hpo_desc: "Description",
    col_similarity: "Similarity",
    export_csv: "Export CSV",
    use_for_diagnosis: "Use for Diagnosis"
  },
  diagnosis: {
    title: "Evidence Intelligence Diagnosis",
    description: "Multi-agent genomic reasoning powered by ClaimLayer — mathematically resolving clinical conflicts.",
    clinical_text_label: "Clinical History / Case Report",
    clinical_text_placeholder: "Enter patient symptoms, history, and findings...",
    phenotypes_label: "Phenotypes (comma-separated)",
    phenotypes_placeholder: "e.g. Hypertrophic cardiomyopathy, Chest pain",
    hpo_ids_label: "HPO IDs (comma-separated)",
    hpo_ids_placeholder: "e.g. HP:0001639, HP:0001633",
    model_label: "Reasoning Model",
    search_label: "Search Engine",
    diagnose_btn: "Start Evidence Analysis",
    diagnosing: "Processing Claims...",
    results_title: "Top 5 Most Likely Rare Diseases",
    no_results: "No definitive diagnoses found within the epistemic threshold.",
    step_init: "Initialising Epistemic State",
    step_diagnosis: "Running Multi-Agent Claim Extraction",
    step_complete: "Final Deterministic Resolution",
    web_evidence: "Web Evidence",
    similar_cases: "Similar Cases",
    reflection: "Disease Reflection",
    final_diagnosis: "Final Validated Diagnosis"
  },
  gene: {
    title: "Gene + Variant Diagnosis",
    description: "Upload a VCF file to combine genomic variant analysis with phenotype-based Evidence Intelligence.",
    vcf_label: "VCF File (optional)",
    upload_vcf: "Upload VCF",
    mutation_title: "Prioritised Variants",
    col_gene: "Gene",
    col_position: "Position",
    col_change: "Change",
    col_consequence: "Consequence",
    col_impact: "Impact",
    col_freq: "gnomAD Freq.",
    col_pathogenicity: "Pathogenicity",
    variants_found: "{{count}} variant(s) found",
    show_less: "Show less"
  },
  settings: {
    title: "System Configuration",
    description: "Manage your API keys and reasoning model preferences.",
    api_keys: "Clinical Engine Keys",
    nvidia_key: "NVIDIA NIM API Key (Recommended)",
    openai_key: "OpenAI API Key (Embeddings / Fallback)",
    openai_note: "Required for semantic grounding in ClaimLayer.",
    anthropic_key: "Anthropic API Key",
    google_key: "Google API Key",
    deepseek_key: "DeepSeek API Key",
    key_placeholder: "Enter your secure API key...",
    validate_btn: "Validate",
    default_model: "Default Reasoning Model",
    language: "Interface Language",
    theme: "Aesthetic Theme",
    theme_light: "Clinical Light",
    theme_dark: "Evidence Dark (Recommended)",
    save: "Save Configuration",
    saved: "Configuration saved successfully."
  }
};

const es = {
  app: {
    subtitle: "Plataforma de Inteligencia de Evidencia"
  },
  nav: {
    home: "Inicio",
    hpo_extraction: "Extracción HPO",
    diagnosis: "Diagnóstico por Fenotipo",
    gene_diagnosis: "Diagnóstico Gen + Variante",
    settings: "Configuración"
  },
  common: {
    cancel: "Cancelar",
    save: "Guardar",
    clear: "Limpiar"
  },
  home: {
    welcome: "DeepRare Evidence Intelligence",
    description: "Razonamiento clínico determinista impulsado por ClaimLayer — Vetando alucinaciones con evidencia matemática.",
    get_started: "Iniciar Análisis",
    configure_keys: "Configurar Claves API",
    feature_hpo: "Extracción HPO",
    feature_hpo_desc: "Extrae automáticamente términos de fenotipo del texto clínico y los mapea a códigos HPO estandarizados.",
    feature_diagnosis: "Diagnóstico por Fenotipo",
    feature_diagnosis_desc: "Ejecuta diagnóstico multi-agente determinista desde fenotipos clínicos con trazabilidad completa.",
    feature_gene: "Análisis de Variantes Genómicas",
    feature_gene_desc: "Combina datos VCF con Exomiser y ClaimLayer para priorizar variantes con respaldo de evidencia."
  },
  hpo: {
    title: "Extracción HPO",
    description: "Extrae términos estandarizados de Ontología de Fenotipos Humanos de notas clínicas en texto libre.",
    input_label: "Notas Clínicas",
    input_placeholder: "Pega el texto clínico del paciente aquí...",
    extract_btn: "Extraer Fenotipos",
    extracting: "Extrayendo...",
    results_title: "Términos HPO Extraídos",
    col_phenotype: "Fenotipo",
    col_hpo_code: "Código HPO",
    col_hpo_desc: "Descripción",
    col_similarity: "Similitud",
    export_csv: "Exportar CSV",
    use_for_diagnosis: "Usar para Diagnóstico"
  },
  diagnosis: {
    title: "Diagnóstico Evidence Intelligence",
    description: "Razonamiento genómico multi-agente impulsado por ClaimLayer — resolviendo conflictos clínicos matemáticamente.",
    clinical_text_label: "Historia Clínica / Reporte de Caso",
    clinical_text_placeholder: "Introduce síntomas, historia y hallazgos del paciente...",
    phenotypes_label: "Fenotipos (separados por coma)",
    phenotypes_placeholder: "ej. Miocardiopatía hipertrófica, Dolor torácico",
    hpo_ids_label: "IDs HPO (separados por coma)",
    hpo_ids_placeholder: "ej. HP:0001639, HP:0001633",
    model_label: "Modelo de Razonamiento",
    search_label: "Motor de Búsqueda",
    diagnose_btn: "Iniciar Análisis de Evidencia",
    diagnosing: "Procesando Claims...",
    results_title: "Top 5 Enfermedades Raras Más Probables",
    no_results: "No se encontraron diagnósticos definitivos dentro del umbral epistémico.",
    step_init: "Inicializando Estado Epistémico",
    step_diagnosis: "Extracción de Claims Multi-Agente",
    step_complete: "Resolución Determinista Final",
    web_evidence: "Evidencia Web",
    similar_cases: "Casos Similares",
    reflection: "Reflexión sobre Enfermedad",
    final_diagnosis: "Diagnóstico Final Validado"
  },
  gene: {
    title: "Diagnóstico Gen + Variante",
    description: "Sube un archivo VCF para combinar el análisis de variantes genómicas con Evidence Intelligence.",
    vcf_label: "Archivo VCF (opcional)",
    upload_vcf: "Subir VCF",
    mutation_title: "Variantes Priorizadas",
    col_gene: "Gen",
    col_position: "Posición",
    col_change: "Cambio",
    col_consequence: "Consecuencia",
    col_impact: "Impacto",
    col_freq: "Frec. gnomAD",
    col_pathogenicity: "Patogenicidad",
    variants_found: "{{count}} variante(s) encontrada(s)",
    show_less: "Mostrar menos"
  },
  settings: {
    title: "Configuración del Sistema",
    description: "Gestiona tus claves API y preferencias del modelo de razonamiento.",
    api_keys: "Claves del Motor Clínico",
    nvidia_key: "NVIDIA NIM API Key (Recomendado)",
    openai_key: "OpenAI API Key (Embeddings / Alternativa)",
    openai_note: "Requerido para el grounding semántico en ClaimLayer.",
    anthropic_key: "Anthropic API Key",
    google_key: "Google API Key",
    deepseek_key: "DeepSeek API Key",
    key_placeholder: "Introduce tu clave API segura...",
    validate_btn: "Validar",
    default_model: "Modelo por Defecto",
    language: "Idioma de la Interfaz",
    theme: "Tema Estético",
    theme_light: "Clínico Claro",
    theme_dark: "Evidencia Oscuro (Recomendado)",
    save: "Guardar Configuración",
    saved: "Configuración guardada con éxito."
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: { en: { translation: en }, es: { translation: es } },
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  });

export default i18n;
