"""
Sistema de Monitoreo y Alertas CAE
Captura información diaria relevante para alimentar contenido
"""

import requests
import feedparser
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import logging
import time
import schedule

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CAEMonitoringSystem:
    """
    Sistema de monitoreo para capturar información diaria sobre CAE
    """
    
    def __init__(self):
        self.db_path = Path('data/cae_monitoring.db')
        self.init_database()
        
    def init_database(self):
        """Inicializar base de datos para monitoreo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de noticias capturadas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    source TEXT,
                    url TEXT,
                    published_date DATETIME,
                    category TEXT,
                    relevance_score INTEGER,
                    cae_related BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de alertas configuradas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT,
                    source TEXT,
                    active BOOLEAN DEFAULT TRUE,
                    last_check DATETIME,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de contenido generado
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_generated (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT,
                    title TEXT,
                    content TEXT,
                    linkedin_post TEXT,
                    source_news_id INTEGER,
                    published BOOLEAN DEFAULT FALSE,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Base de datos de monitoreo inicializada")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
    
    def setup_default_alerts(self):
        """Configurar alertas por defecto"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Alertas por defecto
            default_alerts = [
                ("CAE construcción", "google_news"),
                ("Coordinación actividades empresariales", "google_news"),
                ("Prevención riesgos laborales construcción", "google_news"),
                ("Tarjeta profesional construcción", "google_news"),
                ("FLC construcción", "google_news"),
                ("ITSS construcción", "google_news"),
                ("BOE construcción", "boe"),
                ("CNC construcción", "cnc"),
                ("CEPYME construcción", "cepyme"),
                ("Seopan", "seopan")
            ]
            
            for keyword, source in default_alerts:
                cursor.execute('''
                    INSERT OR IGNORE INTO alerts (keyword, source)
                    VALUES (?, ?)
                ''', (keyword, source))
            
            conn.commit()
            conn.close()
            logger.info("✅ Alertas por defecto configuradas")
            
        except Exception as e:
            logger.error(f"Error configurando alertas: {e}")
    
    def fetch_google_news(self, keyword, max_results=10):
        """Obtener noticias de Google News"""
        try:
            # Simulación de API de Google News (en producción usar API real)
            url = f"https://news.google.com/rss/search?q={keyword}&hl=es&gl=ES&ceid=ES:es"
            
            feed = feedparser.parse(url)
            news_items = []
            
            for entry in feed.entries[:max_results]:
                news_item = {
                    'title': entry.title,
                    'content': entry.summary if hasattr(entry, 'summary') else '',
                    'source': 'Google News',
                    'url': entry.link,
                    'published_date': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                    'category': self.categorize_content(entry.title + ' ' + entry.summary),
                    'relevance_score': self.calculate_relevance(entry.title + ' ' + entry.summary),
                    'cae_related': self.is_cae_related(entry.title + ' ' + entry.summary)
                }
                news_items.append(news_item)
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error obteniendo noticias de Google: {e}")
            return []
    
    def fetch_rss_feeds(self):
        """Obtener noticias de feeds RSS"""
        try:
            rss_feeds = [
                "https://www.eleconomista.es/rss/rss-empresas.php",
                "https://www.expansion.com/rss/empresas.xml",
                "https://www.cincodias.com/rss/empresas.xml",
                "https://rss.elpais.com/marcas/construccion.xml"
            ]
            
            all_news = []
            
            for feed_url in rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries:
                        if self.is_construction_related(entry.title + ' ' + entry.summary):
                            news_item = {
                                'title': entry.title,
                                'content': entry.summary if hasattr(entry, 'summary') else '',
                                'source': feed.feed.title if hasattr(feed.feed, 'title') else 'RSS Feed',
                                'url': entry.link,
                                'published_date': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                                'category': self.categorize_content(entry.title + ' ' + entry.summary),
                                'relevance_score': self.calculate_relevance(entry.title + ' ' + entry.summary),
                                'cae_related': self.is_cae_related(entry.title + ' ' + entry.summary)
                            }
                            all_news.append(news_item)
                            
                except Exception as e:
                    logger.error(f"Error procesando feed {feed_url}: {e}")
                    continue
            
            return all_news
            
        except Exception as e:
            logger.error(f"Error obteniendo feeds RSS: {e}")
            return []
    
    def categorize_content(self, text):
        """Categorizar contenido por tema"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['cae', 'coordinación actividades', 'prevención riesgos']):
            return 'CAE'
        elif any(word in text_lower for word in ['licitación', 'concurso', 'contrato público']):
            return 'Licitaciones'
        elif any(word in text_lower for word in ['trabajador', 'empleado', 'derechos laborales']):
            return 'Derechos Laborales'
        elif any(word in text_lower for word in ['subcontrata', 'práctica abusiva', 'explotación']):
            return 'Prácticas Abusivas'
        elif any(word in text_lower for word in ['reforma', 'cambio', 'modernización']):
            return 'Reforma'
        else:
            return 'General'
    
    def calculate_relevance(self, text):
        """Calcular relevancia del contenido"""
        text_lower = text.lower()
        score = 0
        
        # Palabras clave de alta relevancia
        high_relevance = ['cae', 'coordinación actividades', 'prevención riesgos', 'construcción']
        for word in high_relevance:
            if word in text_lower:
                score += 3
        
        # Palabras clave de media relevancia
        medium_relevance = ['trabajador', 'seguridad', 'formación', 'tpc']
        for word in medium_relevance:
            if word in text_lower:
                score += 2
        
        # Palabras clave de baja relevancia
        low_relevance = ['obra', 'empresa', 'sector']
        for word in low_relevance:
            if word in text_lower:
                score += 1
        
        return min(score, 10)  # Máximo 10
    
    def is_cae_related(self, text):
        """Determinar si el contenido está relacionado con CAE"""
        text_lower = text.lower()
        cae_keywords = [
            'cae', 'coordinación actividades empresariales', 'prevención riesgos laborales',
            'tpc', 'tarjeta profesional construcción', 'flc', 'fundación laboral construcción'
        ]
        return any(keyword in text_lower for keyword in cae_keywords)
    
    def is_construction_related(self, text):
        """Determinar si el contenido está relacionado con construcción"""
        text_lower = text.lower()
        construction_keywords = [
            'construcción', 'obra', 'edificación', 'infraestructura', 'ingeniería civil',
            'arquitectura', 'promoción inmobiliaria', 'rehabilitación'
        ]
        return any(keyword in text_lower for keyword in construction_keywords)
    
    def save_news_items(self, news_items):
        """Guardar noticias en la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in news_items:
                cursor.execute('''
                    INSERT OR IGNORE INTO news_items 
                    (title, content, source, url, published_date, category, relevance_score, cae_related)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['title'], item['content'], item['source'], item['url'],
                    item['published_date'], item['category'], item['relevance_score'], item['cae_related']
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Guardadas {len(news_items)} noticias")
            
        except Exception as e:
            logger.error(f"Error guardando noticias: {e}")
    
    def generate_daily_content(self):
        """Generar contenido diario basado en noticias"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener noticias relevantes del día
            cursor.execute('''
                SELECT * FROM news_items 
                WHERE DATE(timestamp) = DATE('now') 
                AND relevance_score >= 5
                ORDER BY relevance_score DESC
                LIMIT 5
            ''')
            
            news_items = cursor.fetchall()
            
            content_ideas = []
            
            for item in news_items:
                content_idea = {
                    'type': 'LinkedIn Post',
                    'title': f"Análisis: {item[1]}",
                    'content': self.generate_linkedin_post(item),
                    'source_news_id': item[0]
                }
                content_ideas.append(content_idea)
            
            # Guardar ideas de contenido
            for idea in content_ideas:
                cursor.execute('''
                    INSERT INTO content_generated 
                    (content_type, title, content, source_news_id)
                    VALUES (?, ?, ?, ?)
                ''', (idea['type'], idea['title'], idea['content'], idea['source_news_id']))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Generadas {len(content_ideas)} ideas de contenido")
            return content_ideas
            
        except Exception as e:
            logger.error(f"Error generando contenido: {e}")
            return []
    
    def generate_linkedin_post(self, news_item):
        """Generar post de LinkedIn basado en noticia"""
        title = news_item[1]
        content = news_item[2]
        category = news_item[6]
        
        if category == 'CAE':
            post = f"""🔍 ANÁLISIS CAE: {title}

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

#CAE #Construccion40 #VIDA #Innovacion #BusinessIntelligence"""
        
        elif category == 'Licitaciones':
            post = f"""📋 LICITACIONES: {title}

{content}

🔗 CONEXIÓN CON CAE:
La fragmentación del sistema CAE afecta directamente a las licitaciones:
• Costes ocultos en gestión CAE
• Barreras de entrada para pymes
• Desigualdad competitiva

💡 VIDA eliminaría estos problemas con un sistema unificado.

📊 Análisis completo: [Enlace]

#Licitaciones #CAE #Transparencia #Construccion40"""
        
        else:
            post = f"""📰 ACTUALIDAD: {title}

{content}

🔍 CONEXIÓN CON NUESTRA INVESTIGACIÓN:
Este caso se relaciona con nuestro análisis del sector construcción y las ineficiencias sistémicas que identificamos.

📊 Análisis completo: [Enlace]

#Construccion40 #Investigacion #DatosOficiales"""
        
        return post
    
    def run_daily_monitoring(self):
        """Ejecutar monitoreo diario"""
        logger.info("🔍 Iniciando monitoreo diario...")
        
        try:
            # Obtener noticias de Google News
            all_news = []
            
            # Obtener alertas activas
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT keyword FROM alerts WHERE active = TRUE")
            keywords = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Buscar noticias para cada keyword
            for keyword in keywords:
                news = self.fetch_google_news(keyword)
                all_news.extend(news)
            
            # Obtener noticias de RSS
            rss_news = self.fetch_rss_feeds()
            all_news.extend(rss_news)
            
            # Eliminar duplicados
            unique_news = []
            seen_titles = set()
            for item in all_news:
                if item['title'] not in seen_titles:
                    unique_news.append(item)
                    seen_titles.add(item['title'])
            
            # Guardar noticias
            self.save_news_items(unique_news)
            
            # Generar contenido
            content_ideas = self.generate_daily_content()
            
            logger.info(f"✅ Monitoreo completado: {len(unique_news)} noticias, {len(content_ideas)} ideas de contenido")
            
            return {
                'news_count': len(unique_news),
                'content_ideas': len(content_ideas),
                'cae_related': len([n for n in unique_news if n['cae_related']])
            }
            
        except Exception as e:
            logger.error(f"Error en monitoreo diario: {e}")
            return None
    
    def get_daily_summary(self):
        """Obtener resumen diario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Estadísticas del día
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_news,
                    COUNT(CASE WHEN cae_related = TRUE THEN 1 END) as cae_news,
                    AVG(relevance_score) as avg_relevance
                FROM news_items 
                WHERE DATE(timestamp) = DATE('now')
            ''')
            
            stats = cursor.fetchone()
            
            # Noticias más relevantes
            cursor.execute('''
                SELECT title, relevance_score, category
                FROM news_items 
                WHERE DATE(timestamp) = DATE('now')
                ORDER BY relevance_score DESC
                LIMIT 5
            ''')
            
            top_news = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_news': stats[0],
                'cae_news': stats[1],
                'avg_relevance': stats[2],
                'top_news': top_news
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen: {e}")
            return None

# Configurar tareas programadas
def setup_scheduled_tasks():
    """Configurar tareas programadas"""
    monitor = CAEMonitoringSystem()
    
    # Monitoreo diario a las 8:00 AM
    schedule.every().day.at("08:00").do(monitor.run_daily_monitoring)
    
    # Resumen semanal los lunes a las 9:00 AM
    schedule.every().monday.at("09:00").do(monitor.generate_daily_content)

if __name__ == "__main__":
    # Inicializar sistema
    monitor = CAEMonitoringSystem()
    monitor.setup_default_alerts()
    
    # Ejecutar monitoreo inicial
    result = monitor.run_daily_monitoring()
    
    if result:
        print(f"✅ Monitoreo completado:")
        print(f"   - Noticias encontradas: {result['news_count']}")
        print(f"   - Ideas de contenido: {result['content_ideas']}")
        print(f"   - Noticias CAE: {result['cae_related']}")
    
    # Mostrar resumen
    summary = monitor.get_daily_summary()
    if summary:
        print(f"\n📊 Resumen diario:")
        print(f"   - Total noticias: {summary['total_news']}")
        print(f"   - Noticias CAE: {summary['cae_news']}")
        print(f"   - Relevancia promedio: {summary['avg_relevance']:.1f}")
        
        print(f"\n🔝 Top noticias:")
        for i, (title, score, category) in enumerate(summary['top_news'], 1):
            print(f"   {i}. [{category}] {title} (Score: {score})")

