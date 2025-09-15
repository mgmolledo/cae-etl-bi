"""
CAE Alternative Data Sources - Fuentes Alternativas de Datos
Búsqueda de datos críticos en fuentes alternativas y públicas
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import time
import logging
from urllib.parse import urljoin, urlparse
import re
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CAEAlternativeDataSources:
    """
    Búsqueda de datos críticos en fuentes alternativas
    """
    
    def __init__(self):
        self.data = {}
        self.scraping_date = datetime.now()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Fuentes alternativas de datos
        self.alternative_sources = {
            'boe': {
                'name': 'BOE - Boletín Oficial del Estado',
                'url': 'https://www.boe.es',
                'search_endpoint': '/buscar/',
                'description': 'Normativas y regulaciones CAE'
            },
            'insst': {
                'name': 'INSST - Instituto Nacional de Seguridad y Salud en el Trabajo',
                'url': 'https://www.insst.es',
                'search_endpoint': '/buscar',
                'description': 'Estadísticas de seguridad laboral'
            },
            'ine': {
                'name': 'INE - Instituto Nacional de Estadística',
                'url': 'https://www.ine.es',
                'search_endpoint': '/buscar/',
                'description': 'Estadísticas del sector construcción'
            },
            'ministerio_trabajo': {
                'name': 'Ministerio de Trabajo y Economía Social',
                'url': 'https://www.mites.gob.es',
                'search_endpoint': '/buscar/',
                'description': 'Políticas laborales y estadísticas'
            },
            'ccoo': {
                'name': 'CCOO - Comisiones Obreras',
                'url': 'https://www.ccoo.es',
                'search_endpoint': '/buscar/',
                'description': 'Informes sindicales sobre construcción'
            },
            'ugt': {
                'name': 'UGT - Unión General de Trabajadores',
                'url': 'https://www.ugt.es',
                'search_endpoint': '/buscar/',
                'description': 'Estudios sindicales sectoriales'
            }
        }
        
        # Términos de búsqueda específicos
        self.search_terms = {
            'cae_related': [
                'coordinación actividades empresariales',
                'CAE',
                'coordinación empresarial',
                'prevención riesgos laborales construcción',
                'coordinación seguridad construcción'
            ],
            'incidents_related': [
                'incidencias construcción',
                'accidentes construcción',
                'siniestralidad construcción',
                'incidencias laborales construcción',
                'accidentes laborales construcción'
            ],
            'rotation_related': [
                'rotación personal construcción',
                'movilidad trabajadores construcción',
                'trabajadores temporales construcción',
                'subcontratación construcción',
                'rotación empleados construcción'
            ],
            'productivity_related': [
                'productividad construcción',
                'eficiencia construcción',
                'rendimiento construcción',
                'productividad sector construcción',
                'eficiencia sector construcción'
            ]
        }
    
    def search_alternative_sources(self, source_name, source_info, search_terms):
        """
        Buscar datos en fuentes alternativas
        """
        logger.info(f"Buscando en {source_name}...")
        
        try:
            base_url = source_info['url']
            search_endpoint = source_info.get('search_endpoint', '/buscar/')
            
            source_data = {
                'source_name': source_name,
                'base_url': base_url,
                'search_endpoint': search_endpoint,
                'scraping_date': self.scraping_date.isoformat(),
                'search_results': {},
                'found_data': {}
            }
            
            # Buscar cada término
            for category, terms in search_terms.items():
                source_data['search_results'][category] = {}
                
                for term in terms:
                    try:
                        # Construir URL de búsqueda
                        search_url = base_url + search_endpoint
                        
                        # Parámetros de búsqueda
                        params = {
                            'q': term,
                            'tipo': 'all',
                            'buscar': 'Buscar'
                        }
                        
                        # Realizar búsqueda
                        response = self.session.get(search_url, params=params, timeout=15)
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            
                            # Extraer resultados de búsqueda
                            results = self.extract_search_results(soup, term)
                            
                            source_data['search_results'][category][term] = {
                                'url': response.url,
                                'status_code': response.status_code,
                                'results_count': len(results),
                                'results': results[:10]  # Limitar a 10 resultados
                            }
                            
                            # Buscar datos específicos en los resultados
                            critical_data = self.extract_critical_data_from_results(results, term)
                            if critical_data:
                                source_data['found_data'][term] = critical_data
                        
                        # Pausa entre búsquedas
                        time.sleep(random.uniform(2, 4))
                        
                    except Exception as e:
                        logger.warning(f"Error buscando '{term}' en {source_name}: {e}")
                        source_data['search_results'][category][term] = {
                            'error': str(e)
                        }
            
            return source_data
            
        except Exception as e:
            logger.error(f"Error buscando en {source_name}: {e}")
            return None
    
    def extract_search_results(self, soup, search_term):
        """
        Extraer resultados de búsqueda de una página
        """
        results = []
        
        try:
            # Buscar diferentes tipos de resultados
            result_selectors = [
                'div.resultado',
                'div.search-result',
                'div.result',
                'li.resultado',
                'li.search-result',
                'article',
                'div.entry',
                'div.post'
            ]
            
            for selector in result_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        result = {
                            'title': '',
                            'url': '',
                            'snippet': '',
                            'date': '',
                            'source': 'unknown'
                        }
                        
                        # Extraer título
                        title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])
                        if title_elem:
                            result['title'] = title_elem.get_text().strip()
                            if title_elem.name == 'a':
                                result['url'] = urljoin(soup.base.get('href', ''), title_elem.get('href', ''))
                        
                        # Extraer snippet
                        text_elem = element.find(['p', 'div', 'span'])
                        if text_elem:
                            result['snippet'] = text_elem.get_text().strip()[:200]
                        
                        # Extraer fecha
                        date_elem = element.find(['time', 'span.date', 'div.date'])
                        if date_elem:
                            result['date'] = date_elem.get_text().strip()
                        
                        if result['title']:
                            results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error extrayendo resultados de búsqueda: {e}")
            return []
    
    def extract_critical_data_from_results(self, results, search_term):
        """
        Extraer datos críticos de los resultados de búsqueda
        """
        critical_data = {
            'incidents': [],
            'workers': [],
            'assignments': [],
            'rotations': [],
            'productivity': [],
            'costs': []
        }
        
        try:
            for result in results:
                text = f"{result['title']} {result['snippet']}".lower()
                
                # Buscar números relacionados con incidencias
                incident_patterns = [
                    r'(\d+)\s*incidencias?',
                    r'(\d+)\s*accidentes?',
                    r'(\d+)\s*siniestros?',
                    r'(\d+)\s*problemas?'
                ]
                
                for pattern in incident_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        critical_data['incidents'].extend(matches)
                
                # Buscar números relacionados con trabajadores
                worker_patterns = [
                    r'(\d+)\s*trabajadores?',
                    r'(\d+)\s*empleados?',
                    r'(\d+)\s*personal',
                    r'(\d+)\s*operarios?'
                ]
                
                for pattern in worker_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        critical_data['workers'].extend(matches)
                
                # Buscar números relacionados con rotación
                rotation_patterns = [
                    r'(\d+)\s*rotación',
                    r'(\d+)\s*movilidad',
                    r'(\d+)\s*temporales?',
                    r'(\d+)\s*cambios?'
                ]
                
                for pattern in rotation_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        critical_data['rotations'].extend(matches)
                
                # Buscar números relacionados con productividad
                productivity_patterns = [
                    r'(\d+)\s*productividad',
                    r'(\d+)\s*eficiencia',
                    r'(\d+)\s*rendimiento',
                    r'(\d+)\s*eficacia'
                ]
                
                for pattern in productivity_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        critical_data['productivity'].extend(matches)
                
                # Buscar números relacionados con costes
                cost_patterns = [
                    r'(\d+)\s*euros?',
                    r'(\d+)\s*millones?',
                    r'(\d+)\s*costes?',
                    r'(\d+)\s*gastos?'
                ]
                
                for pattern in cost_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        critical_data['costs'].extend(matches)
            
            # Filtrar datos vacíos
            critical_data = {k: v for k, v in critical_data.items() if v}
            
            return critical_data if critical_data else None
            
        except Exception as e:
            logger.error(f"Error extrayendo datos críticos: {e}")
            return None
    
    def parallel_alternative_search(self):
        """
        Búsqueda paralela en fuentes alternativas
        """
        logger.info("Iniciando búsqueda paralela en fuentes alternativas...")
        
        try:
            results = {}
            
            # Búsqueda paralela en todas las fuentes
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(self.search_alternative_sources, source_name, source_info, self.search_terms): source_name
                    for source_name, source_info in self.alternative_sources.items()
                }
                
                for future in as_completed(futures):
                    source_name = futures[future]
                    try:
                        result = future.result()
                        if result:
                            results[source_name] = result
                    except Exception as e:
                        logger.error(f"Error en búsqueda de {source_name}: {e}")
            
            # Análisis agregado de datos encontrados
            analysis = self.analyze_alternative_data(results)
            
            self.data = {
                'scraping_date': self.scraping_date.isoformat(),
                'search_type': 'alternative_sources',
                'sources_data': results,
                'alternative_analysis': analysis,
                'methodology': {
                    'alternative_sources': True,
                    'parallel_search': True,
                    'public_data_only': True,
                    'official_sources': True
                }
            }
            
            logger.info("✅ Búsqueda en fuentes alternativas completada")
            return self.data
            
        except Exception as e:
            logger.error(f"Error en búsqueda paralela: {e}")
            return None
    
    def analyze_alternative_data(self, results):
        """
        Analizar datos encontrados en fuentes alternativas
        """
        logger.info("Analizando datos de fuentes alternativas...")
        
        try:
            analysis = {
                'total_sources': len(results),
                'successful_searches': 0,
                'total_results': 0,
                'critical_data_found': {},
                'data_categories': {},
                'source_effectiveness': {}
            }
            
            for source_name, source_data in results.items():
                if 'search_results' in source_data:
                    analysis['successful_searches'] += 1
                    
                    # Contar resultados totales
                    total_results = 0
                    for category, category_data in source_data['search_results'].items():
                        for term, term_data in category_data.items():
                            if isinstance(term_data, dict) and 'results_count' in term_data:
                                total_results += term_data['results_count']
                    
                    analysis['total_results'] += total_results
                    analysis['source_effectiveness'][source_name] = total_results
                    
                    # Analizar datos críticos encontrados
                    if 'found_data' in source_data:
                        for term, critical_data in source_data['found_data'].items():
                            for data_type, values in critical_data.items():
                                if values:
                                    if data_type not in analysis['critical_data_found']:
                                        analysis['critical_data_found'][data_type] = {}
                                    if source_name not in analysis['critical_data_found'][data_type]:
                                        analysis['critical_data_found'][data_type][source_name] = []
                                    analysis['critical_data_found'][data_type][source_name].extend(values)
                    
                    # Analizar categorías de datos
                    for category, category_data in source_data['search_results'].items():
                        if category not in analysis['data_categories']:
                            analysis['data_categories'][category] = 0
                        analysis['data_categories'][category] += len(category_data)
            
            # Calcular métricas agregadas
            analysis['aggregate_metrics'] = {
                'sources_with_data': len([s for s in results.keys() if 'found_data' in results[s] and results[s]['found_data']]),
                'total_critical_data_points': sum(len(values) for category in analysis['critical_data_found'].values() for values in category.values()),
                'most_effective_source': max(analysis['source_effectiveness'].items(), key=lambda x: x[1])[0] if analysis['source_effectiveness'] else None
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando datos alternativos: {e}")
            return None
    
    def save_alternative_data(self):
        """Guardar datos de fuentes alternativas"""
        try:
            output_dir = Path(__file__).resolve().parents[2] / "data" / "processed"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / "cae_alternative_sources_data.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Datos de fuentes alternativas guardados en {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error guardando datos alternativos: {e}")
            return None

def main():
    """Función principal para ejecutar la búsqueda en fuentes alternativas"""
    logger.info("Iniciando búsqueda en fuentes alternativas...")
    
    searcher = CAEAlternativeDataSources()
    
    # Ejecutar búsqueda en fuentes alternativas
    alternative_data = searcher.parallel_alternative_search()
    
    if alternative_data:
        # Guardar datos
        output_file = searcher.save_alternative_data()
        
        logger.info("✅ Búsqueda en fuentes alternativas completada")
        logger.info(f"Datos guardados en: {output_file}")
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("RESUMEN DE BÚSQUEDA EN FUENTES ALTERNATIVAS")
        print("="*60)
        print(f"Fuentes procesadas: {alternative_data['alternative_analysis']['total_sources']}")
        print(f"Búsquedas exitosas: {alternative_data['alternative_analysis']['successful_searches']}")
        print(f"Resultados totales: {alternative_data['alternative_analysis']['total_results']}")
        print(f"Fuentes con datos: {alternative_data['alternative_analysis']['aggregate_metrics']['sources_with_data']}")
        print(f"Datos críticos encontrados: {alternative_data['alternative_analysis']['aggregate_metrics']['total_critical_data_points']}")
        print("="*60)
        
        return alternative_data
    else:
        logger.error("❌ Error en la búsqueda en fuentes alternativas")
        return None

if __name__ == "__main__":
    main()


