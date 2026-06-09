#!/bin/bash
# Installer les dépendances système pour Playwright
apt-get update
apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgbm1 \
    libasound2

# Installer Playwright et Chromium
pip install playwright
playwright install chromium

# Lancer l'application
uvicorn app.main:app --host 0.0.0.0 --port $PORT