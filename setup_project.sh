#!/bin/bash

echo "⚙️  Starte Projekt-Setup..."

# 1. Check: pyenv vorhanden?
if ! command -v pyenv &> /dev/null
then
    echo "❌ pyenv ist nicht installiert. Bitte zuerst pyenv installieren!"
    exit
fi

# 2. Environment erstellen
echo "🐍 Erstelle pyenv Umgebung..."
pyenv virtualenv 3.10.6 netflix_env

# 3. Lokale Umgebung verlinken
echo "🔗 Verlinke Umgebung..."
echo "📦 Erzeuge .python-version Datei..."
pyenv local netflix_env

# 4. direnv vorbereiten
echo "📦 Erzeuge .envrc Datei..."
echo 'layout pyenv' > .envrc
direnv allow

# 5. Abhängigkeiten installieren
echo "📦 Installiere Packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup abgeschlossen!"
