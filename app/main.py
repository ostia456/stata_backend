"""
Point d'entrée principal de l'application FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import Config
from .api.router import api_router
from .middleware.logging import LoggingMiddleware
from .middleware.timing import TimingMiddleware
from app.middleware.security import SecurityMiddleware, InputValidator, FileSecurity
from app.config import Config

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application
    """
    # Démarrage
    print(f" Démarrage de {Config.APP_NAME}")
    print(f" Dossier d'upload: {Config.UPLOAD_DIR}")
    print(f" Max rows à charger: {Config.MAX_ROWS_TO_LOAD}")
    yield
    # Arrêt
    print(f"👋 Arrêt de {Config.APP_NAME}")



# Créer l'application FastAPI
app = FastAPI(
    title=Config.APP_NAME,
    description="API d'exploration automatique de datasets (CSV/Excel)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Ajouter après la création de l'app (avant les middlewares existants)
# Middleware de sécurité
if Config.ENABLE_RATE_LIMITING:
    app.add_middleware(SecurityMiddleware)
    print("🔒 Rate limiting activé")

# CORS restreint
if Config.ALLOWED_ORIGINS != ['*']:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )
    print(f"🔒 CORS restreint aux origines: {Config.ALLOWED_ORIGINS}")

# Ajouter CORS (pour permettre au frontend de communiquer)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajouter les middlewares personnalisés
app.add_middleware(LoggingMiddleware)
app.add_middleware(TimingMiddleware)

# Inclure les routes
app.include_router(api_router)


# Route racine simple
@app.get("/")
async def root():
    return {
        "name": Config.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "upload": "/api/v1/upload",
            "health": "/api/v1/health"
        }
    }