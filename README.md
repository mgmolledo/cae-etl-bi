
# CAE ETL & Business Intelligence

Repositorio de análisis de ineficiencias del sistema de Coordinación de Actividades Empresariales (CAE) en el sector de la construcción en España.

## 🎯 Objetivo
Construir un pipeline completo de analítica de datos (ETL → BI) usando fuentes oficiales (BOE, INSST, ITSS, FLC, etc.) para:
- Identificar ineficiencias del sistema CAE.
- Evaluar costes y cargas administrativas para pymes.
- Proponer un modelo alternativo basado en Certificado de Acceso Global integrado con la TPC.

## 🛠️ Estructura
- `src/etl/`: scripts de extracción y limpieza de datos.
- `notebooks/`: análisis exploratorio (EDA) y modelado.
- `docs/`: documentación de fuentes y metodología.
- `data/raw/`: datos brutos descargados automáticamente (CI).
- `data/processed/`: datasets procesados listos para análisis.

## 🚀 Tecnologías
- Python (pandas, requests, jupyter)
- Power BI / Tableau (dashboards)
- GitHub Actions (automatización de ETL)

## 📊 Flujo
1. Ingesta automática de fuentes públicas.
2. Limpieza y estandarización (CSV/Parquet).
3. Análisis exploratorio en Jupyter.
4. Modelado y visualización (dashboards BI).
5. Conclusiones y recomendaciones.

---
Este repositorio está diseñado como proyecto de portfolio profesional para demostrar capacidades de analista de datos senior (end-to-end).
