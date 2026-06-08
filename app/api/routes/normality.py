"""
Routes pour les tests de normalité
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional

from app.services.upload_service import UploadService
from app.core.normality import NormalityTester, NormalityVisualizer
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/normality", tags=["Normality"])
upload_service = UploadService()


@router.get("/{file_id}")
async def test_normality(file_id: str) -> Dict[str, Any]:
    """
    Applique le test de Shapiro-Wilk à toutes les colonnes numériques
    
    - **file_id**: Identifiant du fichier uploadé
    
    Retourne les résultats des tests de normalité
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = NormalityTester.test_all_columns(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du test: {str(e)}")


@router.get("/{file_id}/column/{column_name}")
async def test_column_normality(file_id: str, column_name: str) -> Dict[str, Any]:
    """
    Teste la normalité d'une colonne spécifique
    
    - **file_id**: Identifiant du fichier uploadé
    - **column_name**: Nom de la colonne à tester
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = NormalityTester.test_single_column(df, column_name)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/quick")
async def quick_normality_test(file_id: str) -> Dict[str, Any]:
    """
    Version rapide du test de normalité
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = NormalityTester.quick_test(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/qq/{column_name}")
async def get_qq_data(
    file_id: str,
    column_name: str,
    max_points: int = Query(1000, description="Nombre max de points")
) -> Dict[str, Any]:
    """
    Récupère les données pour un Q-Q plot
    
    - **file_id**: Identifiant du fichier uploadé
    - **column_name**: Nom de la colonne
    - **max_points**: Nombre max de points
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        if column_name not in df.columns:
            raise HTTPException(status_code=404, detail=f"Colonne '{column_name}' non trouvée")
        
        result = NormalityVisualizer.get_qq_data(df[column_name], max_points)
        result['column'] = column_name
        result['file_id'] = file_id
        
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/distribution/{column_name}")
async def get_distribution_data(
    file_id: str,
    column_name: str,
    bins: int = Query(30, description="Nombre de bins")
) -> Dict[str, Any]:
    """
    Récupère les données pour visualiser la distribution
    
    - **file_id**: Identifiant du fichier uploadé
    - **column_name**: Nom de la colonne
    - **bins**: Nombre de bins pour l'histogramme
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        if column_name not in df.columns:
            raise HTTPException(status_code=404, detail=f"Colonne '{column_name}' non trouvée")
        
        result = NormalityVisualizer.get_distribution_data(df[column_name], bins)
        result['column'] = column_name
        result['file_id'] = file_id
        
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))