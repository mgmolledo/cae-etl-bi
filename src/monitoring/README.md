# Sistema de Monitoreo CAE

## 🎯 Objetivo

Sistema automatizado para capturar información diaria relevante sobre CAE y el sector construcción, generando contenido semanal para LinkedIn y alimentando la plataforma web.

## 🚀 Características

### **Monitoreo Automático**
- **Google News**: Búsqueda automática con keywords relevantes
- **RSS Feeds**: Medios especializados y fuentes oficiales
- **Categorización**: Clasificación automática por temas
- **Relevancia**: Scoring automático de relevancia

### **Generación de Contenido**
- **Posts LinkedIn**: Generación automática basada en noticias
- **Templates**: Plantillas específicas por categoría
- **Conexión CAE**: Vinculación con nuestra investigación
- **Call-to-Action**: Inclusión de enlaces y hashtags

### **Fuentes Monitoreadas**
- **Medios**: El Economista, Expansión, Cinco Días, El País
- **Oficiales**: BOE, INE, Ministerio de Trabajo
- **Asociaciones**: CNC, CEPYME, Seopan
- **Sectoriales**: Revistas especializadas

## 📊 Categorías de Contenido

### **CAE**
- Coordinación de Actividades Empresariales
- Prevención de Riesgos Laborales
- Tarjeta Profesional de la Construcción
- Fundación Laboral de la Construcción

### **Licitaciones**
- Contratos públicos
- Concursos y subastas
- Pliegos de condiciones
- Adjudicaciones

### **Derechos Laborales**
- Condiciones de trabajo
- Salarios y jornadas
- Despidos y contrataciones
- Negociación colectiva

### **Prácticas Abusivas**
- Subcontratación irregular
- Economía sumergida
- Explotación laboral
- Precariedad

### **Reforma**
- Modernización del sector
- Digitalización
- Innovación tecnológica
- Transformación

### **Seguridad**
- Accidentes laborales
- Inspecciones
- Sanciones
- Prevención

## 🛠️ Instalación

```bash
# Instalar dependencias
pip install requests feedparser schedule

# Configurar alertas
python src/monitoring/monitoring_config.py

# Ejecutar monitoreo
python src/monitoring/cae_monitoring_system.py
```

## 📅 Ejecución Diaria

```bash
# Ejecutar script diario
bash scripts/daily_monitoring.sh

# O programar con cron
0 8 * * * /path/to/scripts/daily_monitoring.sh
```

## 📈 Outputs

### **Base de Datos**
- `data/cae_monitoring.db`: Noticias y contenido
- `data/daily_summary.json`: Resumen diario
- `data/content_ideas.json`: Ideas de contenido

### **Contenido Generado**
- Posts LinkedIn listos para publicar
- Ideas de contenido semanal
- Resúmenes de noticias relevantes
- Estadísticas de monitoreo

## 🎯 Estrategia de Contenido

### **Semana 1**: CAE - Impacto económico
### **Semana 2**: CAE - Aspectos humanos
### **Semana 3**: Licitaciones - Transparencia
### **Semana 4**: Licitaciones - Competencia
### **Semana 5**: Prácticas abusivas - Subcontratación
### **Semana 6**: Prácticas abusivas - Prevención
### **Semana 7**: Derechos laborales - Dignidad
### **Semana 8**: Derechos laborales - Seguridad
### **Semana 9**: Reforma integral - Propuesta
### **Semana 10**: Reforma integral - Implementación

## 🔧 Configuración

### **Alertas Personalizadas**
```python
# Añadir nuevas alertas
monitor = CAEMonitoringSystem()
monitor.add_alert("nueva keyword", "fuente")
```

### **Templates Personalizados**
```python
# Modificar templates en monitoring_config.py
LINKEDIN_TEMPLATES["NuevaCategoria"] = "Template personalizado"
```

### **Umbrales de Relevancia**
```python
# Ajustar umbrales
THRESHOLDS["min_relevance_score"] = 6
```

## 📊 Métricas

- **Noticias capturadas** por día
- **Noticias CAE** relevantes
- **Ideas de contenido** generadas
- **Relevancia promedio** de noticias
- **Categorización** automática

## 🚀 Próximos Pasos

1. **Integración con LinkedIn API** para publicación automática
2. **Análisis de sentimiento** de noticias
3. **Predicción de tendencias** del sector
4. **Dashboard en tiempo real** de monitoreo
5. **Alertas por email** de noticias críticas

---

**Sistema diseñado para mantener el foco en CAE mientras exploramos sinuosamente otros temas del sector construcción.**

