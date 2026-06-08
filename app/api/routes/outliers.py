"""
Routes pour la détection d'outliers
"""
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional

from app.services.upload_service import UploadService
from app.core.outliers import OutlierDetector, OutlierTreatment
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/outliers", tags=["Outliers"])
upload_service = UploadService()


@router.get("/{file_id}")
async def detect_outliers(file_id: str) -> Dict[str, Any]:
    """
    Détecte les outliers dans toutes les colonnes numériques
    
    - **file_id**: Identifiant du fichier uploadé
    
    Retourne la détection d'outliers par IQR et Z-score
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = OutlierDetector.analyze_all_columns(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la détection: {str(e)}")


@router.get("/{file_id}/column/{column_name}")
async def detect_column_outliers(
    file_id: str,
    column_name: str,
    method: str = Query("both", description="iqr, zscore, or both")
) -> Dict[str, Any]:
    """
    Détecte les outliers dans une colonne spécifique
    
    - **file_id**: Identifiant du fichier uploadé
    - **column_name**: Nom de la colonne
    - **method**: Méthode de détection ('iqr', 'zscore', 'both')
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        if column_name not in df.columns:
            raise HTTPException(status_code=404, detail=f"Colonne '{column_name}' non trouvée")
        
        if not pd.api.types.is_numeric_dtype(df[column_name]):
            raise HTTPException(status_code=400, detail=f"Colonne '{column_name}' non numérique")
        
        if method == 'iqr':
            result = OutlierDetector.detect_iqr(df[column_name])
        elif method == 'zscore':
            result = OutlierDetector.detect_zscore(df[column_name])
        else:
            result = OutlierDetector.detect_both(df[column_name])
        
        result['column'] = column_name
        result['file_id'] = file_id
        
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/quick")
async def quick_outlier_analysis(file_id: str) -> Dict[str, Any]:
    """
    Version rapide de la détection d'outliers
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = OutlierDetector.quick_outlier_analysis(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/treatment/{column_name}")
async def suggest_outlier_treatment(
    file_id: str,
    column_name: str
) -> Dict[str, Any]:
    """
    Suggère un traitement pour les outliers d'une colonne
    
    - **file_id**: Identifiant du fichier uploadé
    - **column_name**: Nom de la colonne
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        if column_name not in df.columns:
            raise HTTPException(status_code=404, detail=f"Colonne '{column_name}' non trouvée")
        
        result = OutlierTreatment.suggest_treatment(df[column_name])
        result['column'] = column_name
        result['file_id'] = file_id
        
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))