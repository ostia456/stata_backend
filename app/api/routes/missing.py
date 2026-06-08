"""
Routes pour l'analyse des valeurs manquantes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.upload_service import UploadService
from app.core.missing_values import MissingValueAnalyzer
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/missing", tags=["Missing Values"])
upload_service = UploadService()


@router.get("/{file_id}")
async def analyze_missing_values(file_id: str) -> Dict[str, Any]:
    """
    Analyse complète des valeurs manquantes pour un dataset
    
    - **file_id**: Identifiant du fichier uploadé
    
    Retourne les statistiques détaillées sur les valeurs manquantes
    """
    try:
        # Récupérer le DataFrame
        df = upload_service.get_dataframe(file_id)
        
        # Analyser les valeurs manquantes
        analysis = MissingValueAnalyzer.analyze(df)
        
        # Ajouter le file_id
        analysis['file_id'] = file_id
        
        # Nettoyer pour JSON
        return clean_for_json(analysis)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")


@router.get("/{file_id}/summary")
async def get_missing_summary(file_id: str) -> Dict[str, Any]:
    """
    Version simplifiée de l'analyse des valeurs manquantes
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        summary = MissingValueAnalyzer.quick_analysis(df)
        summary['file_id'] = file_id
        return clean_for_json(summary)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/column/{column_name}")
async def get_column_missing(file_id: str, column_name: str) -> Dict[str, Any]:
    """
    Analyse des valeurs manquantes pour une colonne spécifique
    
    - **file_id**: Identifiant du fichier uploadé
    - **column_name**: Nom de la colonne à analyser
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        if column_name not in df.columns:
            raise HTTPException(status_code=404, detail=f"Colonne '{column_name}' non trouvée")
        
        # Analyse complète puis extraction de la colonne
        full_analysis = MissingValueAnalyzer.analyze(df)
        
        result = {
            'file_id': file_id,
            'column': column_name,
            'info': full_analysis['columns'].get(column_name, {}),
            'recommendation': next(
                (rec for rec in full_analysis['recommendations'] if rec.get('column') == column_name),
                None
            )
        }
        
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))