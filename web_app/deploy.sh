#!/bin/bash

# Script de despliegue para CAE Impact Web
# Despliega la aplicación web en un servidor

echo "🚀 Desplegando CAE Impact Web..."

# Crear directorio de datos si no existe
mkdir -p data

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Crear base de datos
echo "🗄️ Inicializando base de datos..."
python -c "
import sqlite3
from pathlib import Path

db_path = Path('data/cae_impact.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear tablas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS testimonials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        company_type TEXT,
        worker_type TEXT,
        experience TEXT,
        impact_score INTEGER,
        testimonial TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        verified BOOLEAN DEFAULT FALSE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS impact_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_size TEXT,
        workers_count INTEGER,
        annual_cost_euros INTEGER,
        hours_lost INTEGER,
        rotation_percentage REAL,
        satisfaction_score INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS signatures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        company TEXT,
        position TEXT,
        support_type TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()
print('✅ Base de datos inicializada')
"

# Verificar que los datos de análisis existen
echo "📊 Verificando datos de análisis..."
if [ ! -d "../data/processed" ]; then
    echo "❌ Error: Directorio de datos procesados no encontrado"
    echo "Ejecuta primero los algoritmos de análisis desde el directorio raíz"
    exit 1
fi

# Iniciar aplicación
echo "🌐 Iniciando aplicación web..."
echo "Acceso: http://localhost:5000"
echo "Presiona Ctrl+C para detener"

python app.py

