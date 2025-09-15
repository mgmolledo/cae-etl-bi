"""
Configuración de Alertas CAE
Sistema de monitoreo y alertas para contenido diario
"""

import json
from pathlib import Path

# Configuración de alertas por defecto
DEFAULT_ALERTS = {
    "google_news": [
        "CAE construcción",
        "Coordinación actividades empresariales",
        "Prevención riesgos laborales construcción",
        "Tarjeta profesional construcción",
        "FLC construcción",
        "ITSS construcción",
        "CNC construcción",
        "CEPYME construcción",
        "Seopan construcción",
        "UGT construcción",
        "CCOO construcción",
        "BIM construcción",
        "Digitalización construcción",
        "Innovación construcción",
        "Sostenibilidad construcción"
    ],
    
    "rss_feeds": [
        {
            "name": "El Economista - Empresas",
            "url": "https://www.eleconomista.es/rss/rss-empresas.php",
            "keywords": ["construcción", "obra", "edificación"]
        },
        {
            "name": "Expansión - Empresas", 
            "url": "https://www.expansion.com/rss/empresas.xml",
            "keywords": ["construcción", "infraestructura"]
        },
        {
            "name": "Cinco Días - Empresas",
            "url": "https://www.cincodias.com/rss/empresas.xml", 
            "keywords": ["construcción", "promoción"]
        },
        {
            "name": "El País - Construcción",
            "url": "https://rss.elpais.com/marcas/construccion.xml",
            "keywords": ["construcción", "vivienda"]
        }
    ],
    
    "official_sources": [
        {
            "name": "BOE",
            "url": "https://www.boe.es/rss/boe.php",
            "keywords": ["construcción", "trabajo", "prevención"]
        },
        {
            "name": "INE",
            "url": "https://www.ine.es/rss/rss_ine.xml",
            "keywords": ["construcción", "empleo"]
        },
        {
            "name": "Ministerio de Trabajo",
            "url": "https://www.mites.gob.es/rss/rss_mites.xml",
            "keywords": ["construcción", "prevención", "trabajo"]
        }
    ],
    
    "associations": [
        {
            "name": "CNC",
            "url": "https://www.cnc.es/rss",
            "keywords": ["construcción", "empresas"]
        },
        {
            "name": "CEPYME",
            "url": "https://www.cepyme.es/rss",
            "keywords": ["pymes", "construcción"]
        },
        {
            "name": "Seopan",
            "url": "https://www.seopan.es/rss",
            "keywords": ["obras públicas", "construcción"]
        }
    ]
}

# Configuración de categorización
CATEGORY_KEYWORDS = {
    "CAE": [
        "cae", "coordinación actividades", "prevención riesgos laborales",
        "tpc", "tarjeta profesional construcción", "flc", "fundación laboral construcción"
    ],
    "Licitaciones": [
        "licitación", "concurso", "contrato público", "adjudicación",
        "pliego", "oferta", "subasta"
    ],
    "Derechos Laborales": [
        "trabajador", "empleado", "derechos laborales", "condiciones trabajo",
        "salario", "jornada", "vacaciones", "despido"
    ],
    "Prácticas Abusivas": [
        "subcontrata", "práctica abusiva", "explotación", "precariedad",
        "trabajo irregular", "economía sumergida"
    ],
    "Reforma": [
        "reforma", "cambio", "modernización", "digitalización",
        "innovación", "transformación"
    ],
    "Seguridad": [
        "seguridad", "accidente", "riesgo", "prevención",
        "inspección", "sanción", "multa"
    ]
}

# Configuración de relevancia
RELEVANCE_KEYWORDS = {
    "high": [
        "cae", "coordinación actividades", "prevención riesgos", "construcción",
        "tpc", "flc", "itss"
    ],
    "medium": [
        "trabajador", "seguridad", "formación", "obra",
        "empresa", "sector", "empleo"
    ],
    "low": [
        "vivienda", "promoción", "inmobiliaria", "rehabilitación"
    ]
}

# Configuración de LinkedIn
LINKEDIN_TEMPLATES = {
    "CAE": """
🔍 ANÁLISIS CAE: {title}

{content}

💡 CONEXIÓN CON NUESTRA INVESTIGACIÓN:
Este caso confirma los hallazgos de nuestro análisis sobre el sistema CAE:
• €2.8B de costes innecesarios anuales
• 800% más accidentes por rotación excesiva
• 34% de rotaciones causadas por problemas CAE

🚀 SOLUCIÓN: VIDA (Verificación Inmediata Datos Acceso)
Un sistema que elimina estas ineficiencias y mejora la vida del trabajador.

📊 Análisis completo: [Enlace]
💬 ¿Has experimentado este problema? Comparte tu experiencia

#CAE #Construccion40 #VIDA #Innovacion #BusinessIntelligence
""",
    
    "Licitaciones": """
📋 LICITACIONES: {title}

{content}

🔗 CONEXIÓN CON CAE:
La fragmentación del sistema CAE afecta directamente a las licitaciones:
• Costes ocultos en gestión CAE
• Barreras de entrada para pymes
• Desigualdad competitiva

💡 VIDA eliminaría estos problemas con un sistema unificado.

📊 Análisis completo: [Enlace]

#Licitaciones #CAE #Transparencia #Construccion40
""",
    
    "Derechos Laborales": """
👷‍♂️ DERECHOS LABORALES: {title}

{content}

🔗 CONEXIÓN CON CAE:
El sistema CAE actual afecta directamente a los derechos del trabajador:
• Esperas innecesarias en la intemperie
• Rotación constante que genera inseguridad
• Pérdida de dignidad laboral

💡 VIDA respeta y protege los derechos del trabajador.

📊 Análisis completo: [Enlace]

#DerechosLaborales #CAE #Dignidad #Construccion40
""",
    
    "Prácticas Abusivas": """
⚠️ PRÁCTICAS ABUSIVAS: {title}

{content}

🔗 CONEXIÓN CON CAE:
La complejidad del sistema CAE facilita prácticas abusivas:
• Subcontratación para evitar CAE
• Prevención como excusa burocrática
• Explotación del trabajador

💡 VIDA elimina estas prácticas con transparencia total.

📊 Análisis completo: [Enlace]

#PracticasAbusivas #CAE #Transparencia #Construccion40
""",
    
    "Reforma": """
🚀 REFORMA: {title}

{content}

🔗 CONEXIÓN CON CAE:
Este caso se relaciona con nuestra propuesta de reforma integral del sector:
• Digitalización real vs. burocracia
• Innovación al servicio del trabajador
• Modernización del sector

💡 VIDA es parte de esta transformación necesaria.

📊 Análisis completo: [Enlace]

#Reforma #CAE #Innovacion #Construccion40
""",
    
    "Seguridad": """
🛡️ SEGURIDAD: {title}

{content}

🔗 CONEXIÓN CON CAE:
La seguridad real vs. la burocracia del CAE:
• Prevención efectiva vs. documentación
• Formación real vs. certificados
• Protección del trabajador

💡 VIDA mejora la seguridad real del trabajador.

📊 Análisis completo: [Enlace]

#Seguridad #CAE #Prevencion #Construccion40
"""
}

# Configuración de horarios
SCHEDULE_CONFIG = {
    "daily_monitoring": "08:00",
    "weekly_summary": "09:00",
    "content_generation": "10:00",
    "linkedin_posting": "11:00"
}

# Configuración de umbrales
THRESHOLDS = {
    "min_relevance_score": 5,
    "max_news_per_day": 50,
    "max_content_ideas": 10,
    "min_cae_relevance": 3
}

def save_config():
    """Guardar configuración en archivo JSON"""
    config = {
        "alerts": DEFAULT_ALERTS,
        "categories": CATEGORY_KEYWORDS,
        "relevance": RELEVANCE_KEYWORDS,
        "templates": LINKEDIN_TEMPLATES,
        "schedule": SCHEDULE_CONFIG,
        "thresholds": THRESHOLDS
    }
    
    config_path = Path("data/monitoring_config.json")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuración guardada en {config_path}")

if __name__ == "__main__":
    save_config()
    print("✅ Sistema de monitoreo CAE configurado")
    print("📊 Alertas configuradas:")
    print(f"   - Google News: {len(DEFAULT_ALERTS['google_news'])} keywords")
    print(f"   - RSS Feeds: {len(DEFAULT_ALERTS['rss_feeds'])} fuentes")
    print(f"   - Fuentes oficiales: {len(DEFAULT_ALERTS['official_sources'])} fuentes")
    print(f"   - Asociaciones: {len(DEFAULT_ALERTS['associations'])} fuentes")
    print(f"   - Categorías: {len(CATEGORY_KEYWORDS)} categorías")
    print(f"   - Templates LinkedIn: {len(LINKEDIN_TEMPLATES)} templates")

