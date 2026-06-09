#!/bin/bash
# Installation de wkhtmltopdf pour la génération PDF
apt-get update
apt-get install -y wkhtmltopdf

# Lancement de l'application
uvicorn app.main:app --host 0.0.0.0 --port $PORT