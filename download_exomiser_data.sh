#!/bin/bash
set -e

# Directorio de datos
DATA_DIR="exomiser-cli-14.1.0/data"
mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

echo "Descargando datos de Exomiser (2406) - Esto tomará tiempo..."

# Descargar y extraer hg19 (19GB+)
if [ ! -f "2406_hg19.zip" ] && [ ! -d "2406_hg19" ]; then
    echo "Descargando 2406_hg19.zip..."
    curl -O https://data.monarchinitiative.org/exomiser/latest/2406_hg19.zip
fi

if [ -f "2406_hg19.zip" ]; then
    echo "Extrayendo 2406_hg19.zip..."
    unzip -o 2406_hg19.zip
    # Opcional: borrar el zip para ahorrar espacio tras extraer
    rm 2406_hg19.zip
fi

# Descargar y extraer phenotype (6GB+)
if [ ! -f "2406_phenotype.zip" ] && [ ! -d "2406_phenotype" ]; then
    echo "Descargando 2406_phenotype.zip..."
    curl -O https://data.monarchinitiative.org/exomiser/latest/2406_phenotype.zip
fi

if [ -f "2406_phenotype.zip" ]; then
    echo "Extrayendo 2406_phenotype.zip..."
    unzip -o 2406_phenotype.zip
    # Opcional: borrar el zip para ahorrar espacio tras extraer
    rm 2406_phenotype.zip
fi

echo "¡Descarga y extracción completadas con éxito!"
