"""
Routes pour l'analyse de qualité des données
"""

import pandas as pd
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.upload_service import UploadService
from app.core.data_quality import DataQualityScorer, QualityReportGenerator
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/quality", tags=["Quality"])
upload_service = UploadService()


@router.get("/{file_id}")
async def get_quality_score(file_id: str) -> Dict[str, Any]:
    """
    Calcule le score de qualité des données
    
    - **file_id**: Identifiant du fichier uploadé
    
    Retourne le score global de qualité (0-100) et le grade
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = DataQualityScorer.calculate_score(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul: {str(e)}")


@router.get("/{file_id}/report")
async def get_quality_report(file_id: str) -> Dict[str, Any]:
    """
    Génère un rapport détaillé de qualité des données
    
    - **file_id**: Identifiant du fichier uploadé
    
    Retourne un rapport complet avec les problèmes identifiés
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = QualityReportGenerator.generate(df, file_id)
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


@router.get("/{file_id}/issues")
async def get_column_issues(file_id: str) -> Dict[str, Any]:
    """
    Identifie les problèmes par colonne
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        detailed = DataQualityScorer.detailed_quality_report(df)
        
        return clean_for_json({
            'file_id': file_id,
            'column_issues': detailed['column_issues'],
            'columns_with_issues': detailed['columns_with_issues'],
            'total_issues': detailed['summary']['total_issues'],
            'most_problematic_column': detailed['summary']['most_problematic_column']
        })
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))