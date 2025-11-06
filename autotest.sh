#!/bin/bash

echo "🔁 Starte automatisierte Tests, Linting und Formatierung..."

echo "📦 Installiere Abhängigkeiten..."
pip install -r requirements.txt

echo "🧪 Führe Tests aus..."
pytest tests/
TEST_EXIT_CODE=$?

echo "🎨 Führe Black-Code-Formatierung durch..."
black netflix/ scripts/ tests/

echo "🔍 Führe Linting (flake8) durch..."
flake8 netflix/ scripts/ tests/
LINT_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
  echo "❌ Tests fehlgeschlagen!"
  exit $TEST_EXIT_CODE
fi

if [ $LINT_EXIT_CODE -ne 0 ]; then
  echo "⚠️ Linting-Fehler entdeckt!"
  exit $LINT_EXIT_CODE
fi

echo "✅ Alles erfolgreich abgeschlossen!"
