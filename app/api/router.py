from fastapi import APIRouter
from app.api.routes import (
    upload, health, analysis, statistics, missing, correlations, normality,
    outliers,quality,insights,analysis_global,visualization,reports,cache,advanced,
    categorical,ml_detection,history
)
from app.api import public_routes
# Router principal
api_router = APIRouter(prefix="/api/v1")

# Inclure les routes
api_router.include_router(upload.router)
api_router.include_router(health.router)
api_router.include_router(analysis.router)
api_router.include_router(statistics.router)
api_router.include_router(missing.router)
api_router.include_router(correlations.router)
api_router.include_router(normality.router)
api_router.include_router(outliers.router)
api_router.include_router(quality.router)
api_router.include_router(insights.router)
api_router.include_router(analysis_global.router)
api_router.include_router(visualization.router)
api_router.include_router(reports.router)
api_router.include_router(cache.router)
api_router.include_router(advanced.router)
api_router.include_router(categorical.router)
api_router.include_router(ml_detection.router)
api_router.include_router(history.router)


# Routes publiques (sans préfixe api/v1 pour certaines)
api_router.include_router(public_routes.router)