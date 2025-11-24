setup:
	chmod +x setup_project.sh
	./setup_project.sh

install:
	pip install -e .

# Führt Unit-Tests mit pytest im "tests/"-Verzeichnis aus
test:
	pytest tests/

run:
	python run_pipeline.py --ticker MSFT --epochs 5

# 🔍 Code-Qualität prüfen
# Führt Flake8 aus, um Stil- und Syntaxprobleme in definierten Ordnern zu finden
lint:
	flake8 netflix/ scripts/


# 🧹 Code automatisch formatieren
# Formatiert den Code nach dem Black-Styleguide in allen relevanten Ordnern
format:
	black netflix/ scripts/ tests/

# 🧼 Bytecode-Dateien löschen
# Entfernt alle .pyc-Dateien im Projektverzeichnis
clean:
	find . -type f -name "*.pyc" -delete

# 🐳 Docker Deployment per Shell-Skript
docker:
	chmod +x docker_deploy.sh
	./docker_deploy.sh
