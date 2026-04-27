
import os
import json
import subprocess
from knowledge_engine import get_kioxia_evidence
from pillars_engine import get_all_pillars_evidence

VARIANTS = [
    {"gene": "MYBPC3", "rsid": "rs397516035", "phenotype": "Hipertrofia Cardíaca"},
    {"gene": "CFTR", "rsid": "rs113993960", "phenotype": "Infecciones Pulmonares"},
    {"gene": "PKD1", "rsid": "rs121908661", "phenotype": "Quistes Renales"}
]

HISTORIAL = """
PACIENTE COMPLEJO - INVESTIGACIÓN MULTISISTÉMICA
Edad: 35 años.
Síntomas: Disnea de esfuerzo, tos crónica productiva y hallazgos ecográficos de quistes renales bilaterales.
Antecedentes: Muerte súbita en la familia.
Objetivo: Determinar cuál de las variantes detectadas es la causa principal o si hay un cuadro de co-morbilidad genética.
"""

def run_variant_audit(variant):
    print(f"\n🚀 AUDITANDO VARIANTE: {variant['gene']} ({variant['rsid']})...")
    
    # 1. Datos de Kioxia y 5 Pilares
    kioxia = get_kioxia_evidence(variant['gene'], variant['rsid'])
    pillars = get_all_pillars_evidence(variant['gene'], variant['rsid'])
    
    # 2. Invocación al cerebro NIM (Simulada para el orquestador de stress o real vía test_agentic_diagnosis)
    # Para este stress test, usaremos el pipeline real pero configurado para esta variante
    # Nota: En un entorno real, haríamos el loop dentro de test_agentic_diagnosis
    return {
        "variant": variant,
        "kioxia": kioxia,
        "pillars": pillars
    }

def main():
    print("🔥 INICIANDO PRUEBA DE STRESS: AUDITORÍA TRIPLE 🔥")
    results = []
    for var in VARIANTS:
        res = run_variant_audit(var)
        results.append(res)
    
    # Generar Reporte de Stress
    report_path = "caso_clinico/diagnostico_final/STRESS_TEST_REPORT.md"
    with open(report_path, "w") as f:
        f.write("# 🌪️ INFORME DE STRESS: DIAGNÓSTICO DIFERENCIAL MULTI-VARIANTE\n\n")
        f.write(f"## CUADRO CLÍNICO\n{HISTORIAL}\n\n")
        
        for r in results:
            f.write(f"### 🧬 Auditoría: {r['variant']['gene']} ({r['variant']['rsid']})\n")
            f.write(f"- **Fenotipo Sospechado:** {r['variant']['phenotype']}\n")
            f.write(f"- **Kioxia Master Memory:** {r['kioxia']}\n")
            f.write(f"- **Pilar GnomAD:** {r['pillars']['gnomad']}\n")
            f.write(f"- **Pilar PanelApp:** {r['pillars']['panelapp']}\n")
            f.write(f"- **Pilar ClinGen:** {r['pillars']['clingen']}\n")
            f.write("\n---\n")
            
    print(f"\n✅ Prueba de stress completada. Reporte generado en: {report_path}")

if __name__ == "__main__":
    main()
