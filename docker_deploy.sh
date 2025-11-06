#!/bin/bash

set -e  # Beende bei Fehler

echo "🐳 Starte Docker Deployment..."

# 1. Stoppe alte Container (falls vorhanden)
echo "🛑 Stoppe alte laufende Container (falls vorhanden)..."
docker-compose down

# 2. Entferne alte Images (optional)
echo "🧹 Bereinige alte Images (optional)..."
docker image prune -f

# 3. Baue neue Images basierend auf den Dockerfiles
echo "🔨 Baue neue Docker-Images..."
docker-compose build

# 4. Starte alle Container im Hintergrund
echo "🚀 Starte neue Container..."
docker-compose up -d

# 5. Zeige laufende Container an
echo "📦 Laufende Container:"
docker ps

# 6. Zeige Logs-Auszug für Überprüfung
echo "📝 Log-Auszug:"
docker-compose logs --tail=10

echo "✅ Docker Deployment abgeschlossen!"
echo ""
echo "➡️ FastAPI Server erreichbar unter: http://localhost:8000"
echo "➡️ Streamlit Dashboard erreichbar unter: http://localhost:8501"
