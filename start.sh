#!/bin/bash
# Lancement direct de l'application sans installation système
uvicorn app.main:app --host 0.0.0.0 --port $PORT