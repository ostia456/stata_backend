"""
Routes pour les analyses de corrélation
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional

from app.services.upload_service import UploadService
from app.core.correlations import CorrelationAnalyzer
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/correlations", tags=["Correlations"])
upload_service = UploadService()


@router.get("/{file_id}")
async def get_correlations(
    file_id: str,
    method: Optional[str] = Query(None, description="pearson, spearman, or both")
) -> Dict[str, Any]:
    """
    Calcule les matrices de corrélation pour un dataset
    
    - **file_id**: Identifiant du fichier uploadé
    - **method**: 'pearson', 'spearman', ou 'both' (défaut: 'both')
    
    Retourne les matrices de corrélation
    """
    try:
        # Récupérer le DataFrame
        df = upload_service.get_dataframe(file_id)
        
        # Calculer les corrélations selon la méthode demandée
        if method == 'pearson':
            result = CorrelationAnalyzer.calculate_pearson(df)
        elif method == 'spearman':
            result = CorrelationAnalyzer.calculate_spearman(df)
        else:  # both par défaut
            result = CorrelationAnalyzer.calculate_both(df)
        
        result['file_id'] = file_id
        
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul des corrélations: {str(e)}")


@router.get("/{file_id}/target/{target_column}")
async def get_correlations_with_target(
    file_id: str,
    target_column: str
) -> Dict[str, Any]:
    """
    Calcule les corrélations d'une colonne cible avec toutes les autres
    
    - **file_id**: Identifiant du fichier uploadé
    - **target_column**: Nom de la colonne cible
    
    Retourne les corrélations avec la cible
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        result = CorrelationAnalyzer.get_correlation_with_target(df, target_column)
        result['file_id'] = file_id
        
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/quick")
async def get_quick_correlations(
    file_id: str,
    method: str = Query("pearson", description="pearson or spearman")
) -> Dict[str, Any]:
    """
    Version rapide des corrélations
    
    - **file_id**: Identifiant du fichier uploadé
    - **method**: 'pearson' ou 'spearman'
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        result = CorrelationAnalyzer.quick_correlation(df, method)
        result['file_id'] = file_id
        
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))