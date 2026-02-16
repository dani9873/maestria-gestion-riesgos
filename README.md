# Proyecto de Maestría: Integración de Gestión de Riesgos

## Descripción
Implementación práctica de los 7 elementos clave de gestión de riesgos 
según ISO/IEC 27005, integrando aspectos de seguridad de la información 
(ISO 27001) y continuidad del negocio (ISO 22301).

## Estructura del Proyecto
- `scripts/`: Código fuente Python
- `data/`: Datos de entrada (inventarios, amenazas)
- `resultados/`: Salidas de cada día de trabajo
- `reportes/`: Reportes finales (CSV, PDF)
- `evidencias/`: Capturas de pantalla y logs

## Entorno
- Sistema Operativo: Kali Linux
- Python: 3.11+
- Entorno Virtual: venv

## Instalación
```bash
# Clonar repositorio
cd ~/maestria_gestion_riesgos

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Ejecución Diaria
### Día 1: Amenazas y Vulnerabilidades
```bash
python3 scripts/dia1_amenazas_vulnerabilidades.py
```

### Día 2: Activos y Valoración
```bash
python3 scripts/dia2_activos_valoracion.py
```

### Día 3: Análisis de Riesgos
```bash
python3 scripts/dia3_analisis_riesgos.py
```

### Día 4: Controles y Consolidación
```bash
python3 scripts/dia4_controles_consolidacion.py
```

## Autor
Daniel Escobar - Maestría en Seguridad de la Información

## Fecha
Febrero 2026
