"""
Route de health check
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check() -> Dict[str, Any]:
    """Vérifie que l'API est opérationnelle"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Vérifie que l'API est prête à recevoir des requêtes"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Vérifie que l'API est vivante"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }