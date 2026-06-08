"""
Routes pour l'analyse avancée des colonnes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.upload_service import UploadService
from app.core.advanced_analysis import AdvancedColumnAnalyzer, AdvancedAnalyzer
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/advanced", tags=["Advanced Analysis"])
upload_service = UploadService()


@router.get("/{file_id}")
async def get_advanced_analysis(file_id: str) -> Dict[str, Any]:
    """
    Analyse avancée des colonnes (constantes, quasi constantes, cardinalité, asymétrie)
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = AdvancedColumnAnalyzer.analyze_all(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse avancée: {str(e)}")


@router.get("/{file_id}/quick")
async def get_quick_advanced_analysis(file_id: str) -> Dict[str, Any]:
    """
    Version rapide de l'analyse avancée
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = AdvancedColumnAnalyzer.quick_analysis(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/problematic")
async def get_problematic_columns(file_id: str) -> Dict[str, Any]:
    """
    Retourne la liste des colonnes problématiques
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        problematic = AdvancedAnalyzer.get_problematic_columns(df)
        clean_cols = AdvancedAnalyzer.get_clean_columns(df)
        
        return clean_for_json({
            'file_id': file_id,
            'problematic_columns': problematic,
            'clean_columns': clean_cols,
            'problematic_count': len(problematic),
            'clean_count': len(clean_cols)
        })
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))