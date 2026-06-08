"""
Routes pour les statistiques descriptives
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.upload_service import UploadService
from app.core.statistics import DescriptiveStats, StatisticsCalculator
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/statistics", tags=["Statistics"])
upload_service = UploadService()


@router.get("/{file_id}")
async def get_statistics(file_id: str) -> Dict[str, Any]:
    """
    Calcule toutes les statistiques descriptives pour un dataset
    
    - **file_id**: Identifiant du fichier uploadé
    
    Retourne les statistiques complètes (moyenne, médiane, écart-type, etc.)
    """
    try:
        # Récupérer le DataFrame
        df = upload_service.get_dataframe(file_id)
        
        # Calculer les statistiques
        stats = DescriptiveStats(df)
        result = stats.compute_all()
        
        # Ajouter le file_id
        result['file_id'] = file_id
        
        # Nettoyer pour JSON
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul des statistiques: {str(e)}")


@router.get("/{file_id}/fast")
async def get_fast_statistics(file_id: str) -> Dict[str, Any]:
    """
    Version rapide des statistiques (utilise pandas describe)
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        stats = DescriptiveStats(df)
        result = stats.get_fast_stats()
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/column/{column_name}")
async def get_column_statistics(file_id: str, column_name: str) -> Dict[str, Any]:
    """
    Calcule les statistiques pour une colonne spécifique
    
    - **file_id**: Identifiant du fichier uploadé
    - **column_name**: Nom de la colonne à analyser
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        if column_name not in df.columns:
            raise HTTPException(status_code=404, detail=f"Colonne '{column_name}' non trouvée")
        
        stats = DescriptiveStats(df)
        result = stats.compute_for_column(column_name)
        result['file_id'] = file_id
        result['column'] = column_name
        
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))