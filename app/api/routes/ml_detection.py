"""
Routes pour la détection automatique du problème ML
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.upload_service import UploadService
from app.core.ml_detector import MLProblemDetector
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/ml-detection", tags=["ML Detection"])
upload_service = UploadService()


@router.get("/{file_id}")
async def detect_ml_problem(file_id: str) -> Dict[str, Any]:
    """
    Détecte automatiquement le type de problème ML et la colonne cible
    
    - **file_id**: Identifiant du fichier uploadé
    
    Retourne l'analyse du problème ML
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = MLProblemDetector.detect(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la détection: {str(e)}")


@router.get("/{file_id}/target")
async def get_target_suggestion(file_id: str) -> Dict[str, Any]:
    """
    Retourne la suggestion de colonne cible
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        target_col, confidence = MLProblemDetector._find_target_column(df)
        
        return clean_for_json({
            'file_id': file_id,
            'suggested_target': target_col,
            'confidence': confidence,
            'message': f"Colonne cible suggérée: {target_col}" if target_col else "Aucune colonne cible clairement identifiée"
        })
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/ready")
async def get_ml_readiness(file_id: str) -> Dict[str, Any]:
    """
    Vérifie si les données sont prêtes pour le ML
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        detection = MLProblemDetector.detect(df)
        
        return clean_for_json({
            'file_id': file_id,
            'ready': detection.get('ready_for_ml', {}),
            'recommendations': detection.get('recommendations', [])
        })
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))