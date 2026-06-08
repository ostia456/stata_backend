"""
Routes publiques pour l'API
Documentation claire, métriques, health check
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import platform
import psutil
import os

from ..config import Config
from ..services.upload_service import UploadService
from ..core.cache_manager import cache_manager

router = APIRouter(prefix="/public", tags=["Public API"])
upload_service = UploadService()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Vérifie l'état de santé de l'API
    
    Retourne le statut de l'application et de ses dépendances
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": Config.APP_NAME,
        "dependencies": {
            "database": "ok",
            "cache": "ok" if os.path.exists(Config.CACHE_DIR) else "warning",
            "storage": "ok" if os.path.exists(Config.UPLOAD_DIR) else "warning"
        }
    }


@router.get("/version")
async def get_version() -> Dict[str, Any]:
    """
    Retourne les informations de version de l'API
    
    - Version de l'application
 - Version de Python
    - Version des dépendances principales
    """
    import pandas as pd
    import fastapi
    import plotly
    
    return {
        "app": {
            "name": Config.APP_NAME,
            "version": "1.0.0",
            "environment": "production" if not Config.DEBUG else "development"
        },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation()
        },
        "dependencies": {
            "fastapi": fastapi.__version__,
            "pandas": pd.__version__,
            "plotly": plotly.__version__
        },
        "system": {
            "platform": platform.platform(),
            "processor": platform.processor() or "Unknown"
        }
    }


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Retourne les métriques de performance de l'API
    
    - Utilisation mémoire
    - Utilisation CPU
    - Nombre de fichiers analysés
    - Taille du cache
    """
    # Utilisation mémoire
    memory = psutil.virtual_memory()
    
    # Utilisation CPU
    cpu_percent = psutil.cpu_percent(interval=0.5)
    
    # Statistiques des fichiers
    uploaded_files = list(Config.UPLOAD_DIR.glob("*"))
    processed_files = list(Config.PROCESSED_DIR.glob("*.pkl"))
    
    # Taille du cache
    cache_size = 0
    for file in Config.CACHE_DIR.rglob("*"):
        if file.is_file():
            cache_size += file.stat().st_size
    
    return {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "memory_usage_percent": memory.percent,
            "memory_used_mb": round(memory.used / (1024 * 1024), 2),
            "memory_available_mb": round(memory.available / (1024 * 1024), 2),
            "cpu_usage_percent": cpu_percent
        },
        "application": {
            "uploaded_files_count": len(uploaded_files),
            "processed_files_count": len(processed_files),
            "cache_size_mb": round(cache_size / (1024 * 1024), 2),
            "cache_files_count": sum(1 for _ in Config.CACHE_DIR.rglob("*") if _.is_file())
        }
    }


@router.get("/stats")
async def get_global_stats() -> Dict[str, Any]:
    """
    Retourne les statistiques globales de l'API
    
    - Nombre total d'analyses
    - Types de fichiers les plus fréquents
    - Colonnes les plus analysées
    """
    # Compter les analyses dans le cache
    analysis_files = list(Config.CACHE_DIR.glob("analyses/*.pkl"))
    
    # Statistiques des types de fichiers
    uploaded_files = list(Config.TEMP_DIR.glob("*"))
    file_extensions = {}
    for f in uploaded_files:
        ext = f.suffix.lower()
        file_extensions[ext] = file_extensions.get(ext, 0) + 1
    
    # Métadonnées des rapports
    reports = list(Config.HTML_REPORTS_DIR.glob("*.html"))
    
    return {
        "timestamp": datetime.now().isoformat(),
        "analyses": {
            "total_analyses": len(analysis_files),
            "cached_analyses": len(analysis_files),
            "reports_generated": len(reports)
        },
        "files": {
            "total_uploads": len(uploaded_files),
            "by_extension": file_extensions,
            "temp_files": len(list(Config.TEMP_DIR.glob("*"))),
            "processed_files": len(list(Config.PROCESSED_DIR.glob("*")))
        },
        "cache": {
            "size_mb": round(sum(f.stat().st_size for f in analysis_files if f.is_file()) / (1024 * 1024), 2)
        }
    }


@router.get("/info")
async def get_api_info() -> Dict[str, Any]:
    """
    Retourne les informations générales sur l'API
    
    - Description
    - Endpoints disponibles
    - Limites et contraintes
    """
    return {
        "name": Config.APP_NAME,
        "description": "API d'exploration automatique de datasets (CSV/Excel)",
        "version": "1.0.0",
        "documentation": "/docs",
        "redoc": "/redoc",
        "limits": {
            "max_file_size_mb": Config.MAX_FILE_SIZE_MB,
            "max_rows_to_load": Config.MAX_ROWS_TO_LOAD,
            "max_columns_to_analyze": Config.MAX_COLUMNS_TO_ANALYZE,
            "supported_formats": list(Config.ALLOWED_EXTENSIONS)
        },
        "endpoints": {
            "upload": {
                "url": "/api/v1/upload",
                "method": "POST",
                "description": "Uploader un fichier CSV ou Excel"
            },
            "analysis": {
                "url": "/api/v1/analysis/run/{file_id}",
                "method": "POST",
                "description": "Lancer une analyse complète"
            },
            "reports": {
                "url": "/api/v1/reports/html/{file_id}",
                "method": "GET",
                "description": "Générer un rapport HTML"
            },
            "reports_pdf": {
                "url": "/api/v1/reports/pdf/{file_id}",
                "method": "GET",
                "description": "Générer un rapport PDF"
            },
            "health": {
                "url": "/api/v1/public/health",
                "method": "GET",
                "description": "Vérifier l'état de l'API"
            }
        }
    }


@router.get("/limits")
async def get_limits() -> Dict[str, Any]:
    """
    Retourne les limites et contraintes de l'API
    
    - Taille max des fichiers
    - Formats supportés
    - Rate limiting (si implémenté)
    """
    return {
        "upload": {
            "max_file_size_mb": Config.MAX_FILE_SIZE_MB,
            "max_file_size_bytes": Config.MAX_FILE_SIZE_BYTES,
            "allowed_extensions": list(Config.ALLOWED_EXTENSIONS),
            "allowed_mime_types": [
                "text/csv",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel"
            ]
        },
        "analysis": {
            "max_rows": Config.MAX_ROWS_TO_LOAD,
            "max_columns": Config.MAX_COLUMNS_TO_ANALYZE,
            "sampling_threshold": 50000,
            "sampling_strategy": "random"
        },
        "rate_limits": {
            "requests_per_minute": 60,
            "concurrent_requests": 10,
            "note": "Rate limiting non encore implémenté"
        }
    }


@router.get("/docs/info")
async def get_api_docs() -> Dict[str, Any]:
    """
    Retourne la documentation sommaire de l'API
    """
    return {
        "title": "AutoEDA API",
        "description": "API pour l'exploration automatique de données",
        "version": "1.0.0",
        "contact": {
            "name": "AutoEDA Team",
            "email": "support@autoeda.com"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        },
        "tags": [
            {
                "name": "Upload",
                "description": "Upload de fichiers"
            },
            {
                "name": "Analysis",
                "description": "Analyses statistiques"
            },
            {
                "name": "Reports",
                "description": "Génération de rapports"
            },
            {
                "name": "Public API",
                "description": "Informations publiques"
            }
        ]
    }