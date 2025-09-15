"""
CAE Aggressive Data Scraper - Scraping Agresivo para Datos Críticos
Extracción de datos críticos sobre incidencias, repeticiones y asignaciones
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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import threading

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CAEAggressiveScraper:
    """
    Scraper agresivo para obtener datos críticos de plataformas CAE
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
        
        # URLs específicas para datos críticos
        self.critical_endpoints = {
            'ctaima': {
                'base_url': 'https://www.ctaima.com',
                'incidents_endpoint': '/api/incidents',
                'workers_endpoint': '/api/workers',
                'assignments_endpoint': '/api/assignments',
                'stats_endpoint': '/api/stats'
            },
            'dokify': {
                'base_url': 'https://www.dokify.net',
                'incidents_endpoint': '/api/v1/incidents',
                'workers_endpoint': '/api/v1/workers',
                'assignments_endpoint': '/api/v1/assignments',
                'stats_endpoint': '/api/v1/stats'
            },
            '6conecta': {
                'base_url': 'https://www.6conecta.com',
                'incidents_endpoint': '/api/incidents',
                'workers_endpoint': '/api/workers',
                'assignments_endpoint': '/api/assignments',
                'stats_endpoint': '/api/stats'
            },
            'metacontratas': {
                'base_url': 'https://www.metacontratas.com',
                'incidents_endpoint': '/api/incidents',
                'workers_endpoint': '/api/workers',
                'assignments_endpoint': '/api/assignments',
                'stats_endpoint': '/api/stats'
            }
        }
        
        # Patrones para extraer datos críticos
        self.critical_patterns = {
            'incidents': [
                r'incidencias?[:\s]*(\d+)',
                r'incidents?[:\s]*(\d+)',
                r'problemas?[:\s]*(\d+)',
                r'issues?[:\s]*(\d+)',
                r'alertas?[:\s]*(\d+)',
                r'alerts?[:\s]*(\d+)'
            ],
            'workers': [
                r'trabajadores?[:\s]*(\d+)',
                r'workers?[:\s]*(\d+)',
                r'empleados?[:\s]*(\d+)',
                r'employees?[:\s]*(\d+)',
                r'usuarios?[:\s]*(\d+)',
                r'users?[:\s]*(\d+)'
            ],
            'assignments': [
                r'asignaciones?[:\s]*(\d+)',
                r'assignments?[:\s]*(\d+)',
                r'centros?[:\s]*(\d+)',
                r'centers?[:\s]*(\d+)',
                r'proyectos?[:\s]*(\d+)',
                r'projects?[:\s]*(\d+)'
            ],
            'rotations': [
                r'rotación[:\s]*(\d+)',
                r'rotation[:\s]*(\d+)',
                r'movimientos?[:\s]*(\d+)',
                r'movements?[:\s]*(\d+)',
                r'cambios?[:\s]*(\d+)',
                r'changes?[:\s]*(\d+)'
            ]
        }
    
    def setup_selenium_driver(self):
        """Configurar driver de Selenium para scraping avanzado"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            logger.warning(f"No se pudo configurar Selenium: {e}")
            return None
    
    def aggressive_endpoint_scraping(self, platform_name, endpoints):
        """
        Scraping agresivo de endpoints específicos
        """
        logger.info(f"Scraping agresivo de endpoints para {platform_name}...")
        
        try:
            base_url = endpoints['base_url']
            platform_data = {
                'platform_name': platform_name,
                'base_url': base_url,
                'scraping_date': self.scraping_date.isoformat(),
                'endpoints_data': {},
                'critical_data': {}
            }
            
            # Intentar acceder a endpoints específicos
            for endpoint_name, endpoint_url in endpoints.items():
                if endpoint_name == 'base_url':
                    continue
                
                full_url = base_url + endpoint_url
                
                try:
                    # Intentar con diferentes métodos
                    response = self.session.get(full_url, timeout=10)
                    
                    if response.status_code == 200:
                        platform_data['endpoints_data'][endpoint_name] = {
                            'url': full_url,
                            'status_code': response.status_code,
                            'content_type': response.headers.get('content-type', ''),
                            'content_length': len(response.content),
                            'data_preview': response.text[:500] if response.text else ''
                        }
                        
                        # Intentar parsear como JSON
                        try:
                            json_data = response.json()
                            platform_data['endpoints_data'][endpoint_name]['json_data'] = json_data
                        except:
                            pass
                    
                    elif response.status_code == 404:
                        platform_data['endpoints_data'][endpoint_name] = {
                            'url': full_url,
                            'status_code': response.status_code,
                            'note': 'Endpoint no encontrado'
                        }
                    
                    else:
                        platform_data['endpoints_data'][endpoint_name] = {
                            'url': full_url,
                            'status_code': response.status_code,
                            'note': f'Error {response.status_code}'
                        }
                    
                    # Pausa entre peticiones
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    platform_data['endpoints_data'][endpoint_name] = {
                        'url': full_url,
                        'error': str(e)
                    }
            
            return platform_data
            
        except Exception as e:
            logger.error(f"Error en scraping agresivo de {platform_name}: {e}")
            return None
    
    def deep_content_analysis(self, platform_name, base_url):
        """
        Análisis profundo del contenido para extraer datos críticos
        """
        logger.info(f"Análisis profundo de contenido para {platform_name}...")
        
        try:
            # Obtener página principal
            response = self.session.get(base_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Extraer datos críticos usando patrones
            critical_data = {}
            
            for data_type, patterns in self.critical_patterns.items():
                critical_data[data_type] = []
                
                for pattern in patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    if matches:
                        critical_data[data_type].extend(matches)
            
            # Buscar enlaces a páginas de estadísticas o datos
            stats_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                if any(keyword in href or keyword in text for keyword in 
                      ['estadisticas', 'stats', 'datos', 'data', 'metricas', 'metrics', 
                       'incidencias', 'incidents', 'trabajadores', 'workers']):
                    stats_links.append({
                        'text': link.get_text().strip(),
                        'href': urljoin(base_url, link.get('href'))
                    })
            
            # Buscar formularios o elementos que puedan contener datos
            forms_data = []
            for form in soup.find_all('form'):
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', ''),
                    'inputs': []
                }
                
                for input_tag in form.find_all('input'):
                    form_data['inputs'].append({
                        'name': input_tag.get('name', ''),
                        'type': input_tag.get('type', ''),
                        'placeholder': input_tag.get('placeholder', '')
                    })
                
                forms_data.append(form_data)
            
            # Buscar scripts que puedan contener datos
            scripts_data = []
            for script in soup.find_all('script'):
                script_content = script.string
                if script_content and any(keyword in script_content.lower() for keyword in 
                                        ['incidents', 'workers', 'assignments', 'stats', 'data']):
                    scripts_data.append(script_content[:1000])  # Primeros 1000 caracteres
            
            return {
                'critical_data': critical_data,
                'stats_links': stats_links,
                'forms_data': forms_data,
                'scripts_data': scripts_data,
                'page_size': len(response.content),
                'text_length': len(text_content)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis profundo de {platform_name}: {e}")
            return None
    
    def selenium_advanced_scraping(self, platform_name, base_url):
        """
        Scraping avanzado con Selenium para contenido dinámico
        """
        logger.info(f"Scraping avanzado con Selenium para {platform_name}...")
        
        driver = self.setup_selenium_driver()
        if not driver:
            return None
        
        try:
            driver.get(base_url)
            
            # Esperar a que la página cargue
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Buscar elementos que puedan contener datos críticos
            selenium_data = {
                'page_title': driver.title,
                'page_source_length': len(driver.page_source),
                'elements_found': {},
                'dynamic_content': {}
            }
            
            # Buscar elementos con datos numéricos
            number_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'incidencias') or contains(text(), 'trabajadores') or contains(text(), 'asignaciones')]")
            
            for element in number_elements:
                text = element.text
                selenium_data['elements_found'][text] = {
                    'tag': element.tag_name,
                    'class': element.get_attribute('class'),
                    'id': element.get_attribute('id')
                }
            
            # Buscar elementos con clases que sugieran datos
            data_classes = ['stats', 'metrics', 'data', 'numbers', 'count', 'total']
            for class_name in data_classes:
                elements = driver.find_elements(By.CLASS_NAME, class_name)
                if elements:
                    selenium_data['dynamic_content'][class_name] = []
                    for element in elements[:5]:  # Limitar a 5 elementos
                        selenium_data['dynamic_content'][class_name].append({
                            'text': element.text,
                            'tag': element.tag_name
                        })
            
            # Buscar enlaces a páginas de datos
            data_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'data') or contains(@href, 'stats') or contains(@href, 'metrics')]")
            selenium_data['data_links'] = []
            for link in data_links:
                selenium_data['data_links'].append({
                    'text': link.text,
                    'href': link.get_attribute('href')
                })
            
            return selenium_data
            
        except Exception as e:
            logger.error(f"Error en scraping con Selenium para {platform_name}: {e}")
            return None
        finally:
            driver.quit()
    
    def parallel_aggressive_scraping(self):
        """
        Scraping agresivo paralelo de todas las plataformas
        """
        logger.info("Iniciando scraping agresivo paralelo...")
        
        try:
            results = {}
            
            # Scraping paralelo de endpoints
            with ThreadPoolExecutor(max_workers=4) as executor:
                endpoint_futures = {
                    executor.submit(self.aggressive_endpoint_scraping, platform, endpoints): platform
                    for platform, endpoints in self.critical_endpoints.items()
                }
                
                for future in as_completed(endpoint_futures):
                    platform = endpoint_futures[future]
                    try:
                        result = future.result()
                        if result:
                            results[platform] = result
                    except Exception as e:
                        logger.error(f"Error en scraping de endpoints de {platform}: {e}")
            
            # Scraping paralelo de análisis profundo
            with ThreadPoolExecutor(max_workers=4) as executor:
                content_futures = {
                    executor.submit(self.deep_content_analysis, platform, endpoints['base_url']): platform
                    for platform, endpoints in self.critical_endpoints.items()
                }
                
                for future in as_completed(content_futures):
                    platform = content_futures[future]
                    try:
                        result = future.result()
                        if result and platform in results:
                            results[platform]['deep_analysis'] = result
                    except Exception as e:
                        logger.error(f"Error en análisis profundo de {platform}: {e}")
            
            # Scraping paralelo con Selenium
            with ThreadPoolExecutor(max_workers=2) as executor:
                selenium_futures = {
                    executor.submit(self.selenium_advanced_scraping, platform, endpoints['base_url']): platform
                    for platform, endpoints in self.critical_endpoints.items()
                }
                
                for future in as_completed(selenium_futures):
                    platform = selenium_futures[future]
                    try:
                        result = future.result()
                        if result and platform in results:
                            results[platform]['selenium_data'] = result
                    except Exception as e:
                        logger.error(f"Error en scraping con Selenium de {platform}: {e}")
            
            # Análisis agregado de datos críticos
            analysis = self.analyze_critical_data(results)
            
            self.data = {
                'scraping_date': self.scraping_date.isoformat(),
                'scraping_type': 'aggressive_parallel',
                'platforms_data': results,
                'critical_analysis': analysis,
                'methodology': {
                    'aggressive_scraping': True,
                    'parallel_processing': True,
                    'selenium_used': True,
                    'endpoint_testing': True,
                    'deep_content_analysis': True
                }
            }
            
            logger.info("✅ Scraping agresivo paralelo completado")
            return self.data
            
        except Exception as e:
            logger.error(f"Error en scraping agresivo paralelo: {e}")
            return None
    
    def analyze_critical_data(self, results):
        """
        Analizar datos críticos obtenidos
        """
        logger.info("Analizando datos críticos obtenidos...")
        
        try:
            analysis = {
                'total_platforms': len(results),
                'successful_scrapes': 0,
                'critical_data_found': {},
                'endpoints_accessible': {},
                'rotation_indicators': {},
                'incident_patterns': {},
                'worker_assignment_data': {}
            }
            
            for platform, data in results.items():
                if 'endpoints_data' in data:
                    analysis['successful_scrapes'] += 1
                    
                    # Analizar endpoints accesibles
                    accessible_endpoints = 0
                    for endpoint, endpoint_data in data['endpoints_data'].items():
                        if isinstance(endpoint_data, dict) and endpoint_data.get('status_code') == 200:
                            accessible_endpoints += 1
                    
                    analysis['endpoints_accessible'][platform] = accessible_endpoints
                    
                    # Analizar datos críticos
                    if 'deep_analysis' in data and 'critical_data' in data['deep_analysis']:
                        critical_data = data['deep_analysis']['critical_data']
                        
                        for data_type, values in critical_data.items():
                            if values:
                                if data_type not in analysis['critical_data_found']:
                                    analysis['critical_data_found'][data_type] = {}
                                analysis['critical_data_found'][data_type][platform] = values
                    
                    # Analizar indicadores de rotación
                    if 'deep_analysis' in data and 'critical_data' in data['deep_analysis']:
                        rotation_data = data['deep_analysis']['critical_data'].get('rotations', [])
                        if rotation_data:
                            analysis['rotation_indicators'][platform] = rotation_data
                    
                    # Analizar patrones de incidencias
                    if 'deep_analysis' in data and 'critical_data' in data['deep_analysis']:
                        incident_data = data['deep_analysis']['critical_data'].get('incidents', [])
                        if incident_data:
                            analysis['incident_patterns'][platform] = incident_data
                    
                    # Analizar datos de asignación de trabajadores
                    if 'deep_analysis' in data and 'critical_data' in data['deep_analysis']:
                        assignment_data = data['deep_analysis']['critical_data'].get('assignments', [])
                        if assignment_data:
                            analysis['worker_assignment_data'][platform] = assignment_data
            
            # Calcular métricas agregadas
            analysis['aggregate_metrics'] = {
                'total_endpoints_tested': sum(len(data.get('endpoints_data', {})) for data in results.values()),
                'total_endpoints_accessible': sum(analysis['endpoints_accessible'].values()),
                'platforms_with_critical_data': len([p for p in results.keys() if any(analysis['critical_data_found'].get(dt, {}).get(p) for dt in analysis['critical_data_found'])])
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando datos críticos: {e}")
            return None
    
    def save_critical_data(self):
        """Guardar datos críticos obtenidos"""
        try:
            output_dir = Path(__file__).resolve().parents[2] / "data" / "processed"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / "cae_critical_data_aggressive.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Datos críticos guardados en {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error guardando datos críticos: {e}")
            return None

def main():
    """Función principal para ejecutar el scraping agresivo"""
    logger.info("Iniciando scraping agresivo de datos críticos CAE...")
    
    scraper = CAEAggressiveScraper()
    
    # Ejecutar scraping agresivo
    critical_data = scraper.parallel_aggressive_scraping()
    
    if critical_data:
        # Guardar datos
        output_file = scraper.save_critical_data()
        
        logger.info("✅ Scraping agresivo de datos críticos completado")
        logger.info(f"Datos guardados en: {output_file}")
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("RESUMEN DEL SCRAPING AGRESIVO")
        print("="*60)
        print(f"Plataformas procesadas: {critical_data['critical_analysis']['total_platforms']}")
        print(f"Scraping exitoso: {critical_data['critical_analysis']['successful_scrapes']}")
        print(f"Endpoints accesibles: {critical_data['critical_analysis']['aggregate_metrics']['total_endpoints_accessible']}")
        print(f"Plataformas con datos críticos: {critical_data['critical_analysis']['aggregate_metrics']['platforms_with_critical_data']}")
        print("="*60)
        
        return critical_data
    else:
        logger.error("❌ Error en el scraping agresivo de datos críticos")
        return None

if __name__ == "__main__":
    main()


