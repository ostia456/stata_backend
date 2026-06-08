"""
Routes pour l'analyse des colonnes catégorielles
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.upload_service import UploadService
from app.core.categorical_analysis import CategoricalAnalyzer
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/categorical", tags=["Categorical Analysis"])
upload_service = UploadService()


@router.get("/{file_id}")
async def get_categorical_analysis(file_id: str) -> Dict[str, Any]:
    """
    Analyse avancée des colonnes catégorielles
    
    - **file_id**: Identifiant du fichier uploadé
    
    Retourne l'analyse détaillée des colonnes catégorielles
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = CategoricalAnalyzer.analyze(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")


@router.get("/{file_id}/quick")
async def get_quick_categorical_analysis(file_id: str) -> Dict[str, Any]:
    """
    Version rapide de l'analyse catégorielle
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = CategoricalAnalyzer.quick_analysis(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/summary")
async def get_categorical_summary(file_id: str) -> Dict[str, Any]:
    """
    Retourne un résumé tabulaire des colonnes catégorielles
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        summary_df = CategoricalAnalyzer.get_categorical_summary_table(df)
        
        return clean_for_json({
            'file_id': file_id,
            'summary': summary_df.to_dict(orient='records') if not summary_df.empty else [],
            'columns': summary_df.columns.tolist() if not summary_df.empty else []
        })
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))