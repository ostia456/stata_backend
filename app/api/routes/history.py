"""
Routes pour l'historique des analyses
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional

from app.services.metadata_service import metadata_service
from app.services.upload_service import UploadService
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/history", tags=["History"])
upload_service = UploadService()


@router.get("/")
async def get_analysis_history(
    limit: int = Query(50, ge=1, le=100, description="Nombre maximum d'analyses")
) -> Dict[str, Any]:
    """
    Retourne l'historique des analyses
    
    - **limit**: Nombre maximum d'analyses à retourner
    """
    try:
        history = metadata_service.get_analysis_history(limit)
        return clean_for_json({
            'count': len(history),
            'limit': limit,
            'analyses': history
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_analyses() -> Dict[str, Any]:
    """
    Retourne toutes les analyses
    """
    try:
        analyses = metadata_service.get_all_analyses()
        return clean_for_json({
            'count': len(analyses),
            'analyses': analyses
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_history_statistics() -> Dict[str, Any]:
    """
    Retourne des statistiques sur l'historique des analyses
    """
    try:
        stats = metadata_service.get_statistics()
        return clean_for_json(stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{analysis_id}")
async def get_analysis_by_id(analysis_id: str) -> Dict[str, Any]:
    """
    Récupère une analyse par son ID
    
    - **analysis_id**: Identifiant de l'analyse
    """
    try:
        analysis = metadata_service.get_analysis_by_id(analysis_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Analyse {analysis_id} non trouvée")
        
        return clean_for_json(analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{file_id}")
async def get_analysis_by_file_id(file_id: str) -> Dict[str, Any]:
    """
    Récupère l'analyse par file_id
    
    - **file_id**: Identifiant du fichier
    """
    try:
        analysis = metadata_service.get_analysis_by_file_id(file_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Aucune analyse trouvée pour {file_id}")
        
        return clean_for_json(analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str) -> Dict[str, str]:
    """
    Supprime une analyse de l'historique
    
    - **analysis_id**: Identifiant de l'analyse
    """
    try:
        deleted = metadata_service.delete_analysis(analysis_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Analyse {analysis_id} non trouvée")
        
        return {"status": "success", "message": f"Analyse {analysis_id} supprimée"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))