"""
Middleware de logging
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("autoeda")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pour logger toutes les requêtes"""
    
    async def dispatch(self, request: Request, call_next):
        # Log la requête entrante
        logger.info(f"→ {request.method} {request.url.path}")
        
        # Exécuter la requête
        response = await call_next(request)
        
        # Log la réponse
        logger.info(f"← {request.method} {request.url.path} → {response.status_code}")
        
        return response