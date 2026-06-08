"""
Middleware de mesure des temps d'exécution
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("autoeda")


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware pour mesurer le temps d'exécution des requêtes"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        elapsed_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(elapsed_time)
        
        if elapsed_time > 1.0:  # Plus d'une seconde
            logger.warning(f"⚠️ Requête lente: {request.method} {request.url.path} - {elapsed_time:.3f}s")
        else:
            logger.debug(f"⏱️ {request.method} {request.url.path} - {elapsed_time:.3f}s")
        
        return response