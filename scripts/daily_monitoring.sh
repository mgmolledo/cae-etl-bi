#!/bin/bash

# Script de ejecución diaria del sistema de monitoreo CAE
# Ejecutar diariamente para capturar noticias y generar contenido

echo "🔍 Iniciando monitoreo diario CAE..."

# Crear directorio de datos si no existe
mkdir -p data

# Ejecutar sistema de monitoreo
echo "📊 Ejecutando sistema de monitoreo..."
python src/monitoring/cae_monitoring_system.py

# Generar resumen diario
echo "📋 Generando resumen diario..."
python -c "
from src.monitoring.cae_monitoring_system import CAEMonitoringSystem
import json
from datetime import datetime

monitor = CAEMonitoringSystem()
summary = monitor.get_daily_summary()

if summary:
    print(f'📊 Resumen diario - {datetime.now().strftime(\"%Y-%m-%d\")}:')
    print(f'   - Total noticias: {summary[\"total_news\"]}')
    print(f'   - Noticias CAE: {summary[\"cae_news\"]}')
    print(f'   - Relevancia promedio: {summary[\"avg_relevance\"]:.1f}')
    
    print(f'\\n🔝 Top noticias:')
    for i, (title, score, category) in enumerate(summary['top_news'], 1):
        print(f'   {i}. [{category}] {title} (Score: {score})')
    
    # Guardar resumen en archivo
    with open('data/daily_summary.json', 'w', encoding='utf-8') as f:
        json.dump({
            'date': datetime.now().isoformat(),
            'summary': summary
        }, f, indent=2, ensure_ascii=False)
    
    print(f'\\n✅ Resumen guardado en data/daily_summary.json')
else:
    print('❌ Error generando resumen')
"

# Generar ideas de contenido para LinkedIn
echo "💡 Generando ideas de contenido..."
python -c "
from src.monitoring.cae_monitoring_system import CAEMonitoringSystem
import json
from datetime import datetime

monitor = CAEMonitoringSystem()
content_ideas = monitor.generate_daily_content()

if content_ideas:
    print(f'💡 Ideas de contenido generadas: {len(content_ideas)}')
    
    for i, idea in enumerate(content_ideas, 1):
        print(f'\\n{i}. {idea[\"title\"]}')
        print(f'   Tipo: {idea[\"type\"]}')
        print(f'   Contenido: {idea[\"content\"][:100]}...')
    
    # Guardar ideas en archivo
    with open('data/content_ideas.json', 'w', encoding='utf-8') as f:
        json.dump({
            'date': datetime.now().isoformat(),
            'ideas': content_ideas
        }, f, indent=2, ensure_ascii=False)
    
    print(f'\\n✅ Ideas guardadas en data/content_ideas.json')
else:
    print('❌ No se generaron ideas de contenido')
"

# Verificar que la web esté funcionando
echo "🌐 Verificando web..."
if curl -s http://localhost:5000 > /dev/null; then
    echo "✅ Web funcionando correctamente"
else
    echo "⚠️ Web no está funcionando"
fi

echo "✅ Monitoreo diario completado"



