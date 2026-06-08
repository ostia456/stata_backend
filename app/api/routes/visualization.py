"""
Routes pour les visualisations Plotly
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
import pandas as pd
from app.services.upload_service import UploadService
from app.visualization import (
    HistogramGenerator, BoxplotGenerator, 
    HeatmapGenerator, MissingVisualizer
)
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/visualization", tags=["Visualization"])
upload_service = UploadService()


@router.get("/{file_id}/histograms")
async def get_histograms(
    file_id: str,
    column: Optional[str] = Query(None, description="Nom de la colonne (optionnel)")
) -> Dict[str, Any]:
    """
    Génère des histogrammes pour les colonnes numériques
    
    - **file_id**: Identifiant du fichier uploadé
    - **column**: Colonne spécifique (optionnel)
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        if column:
            if column not in df.columns:
                raise HTTPException(status_code=404, detail=f"Colonne '{column}' non trouvée")
            if not pd.api.types.is_numeric_dtype(df[column]):
                raise HTTPException(status_code=400, detail=f"Colonne '{column}' non numérique")
            
            result = HistogramGenerator.create_histogram(df[column])
        else:
            result = HistogramGenerator.create_grid_histograms(df)
        
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/boxplots")
async def get_boxplots(
    file_id: str,
    column: Optional[str] = Query(None, description="Nom de la colonne (optionnel)")
) -> Dict[str, Any]:
    """
    Génère des boxplots pour les colonnes numériques
    
    - **file_id**: Identifiant du fichier uploadé
    - **column**: Colonne spécifique (optionnel)
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        if column:
            if column not in df.columns:
                raise HTTPException(status_code=404, detail=f"Colonne '{column}' non trouvée")
            
            result = BoxplotGenerator.create_boxplot(df[column])
        else:
            result = BoxplotGenerator.create_multiple_boxplots(df)
        
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/correlation-heatmap")
async def get_correlation_heatmap(
    file_id: str,
    method: str = Query("both", description="pearson, spearman, or both")
) -> Dict[str, Any]:
    """
    Génère une heatmap de corrélation
    
    - **file_id**: Identifiant du fichier uploadé
    - **method**: Méthode de corrélation
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        if method == "both":
            result = HeatmapGenerator.create_both_heatmaps(df)
        elif method == "pearson":
            result = HeatmapGenerator.create_correlation_heatmap(df, "pearson")
        elif method == "spearman":
            result = HeatmapGenerator.create_correlation_heatmap(df, "spearman")
        else:
            raise HTTPException(status_code=400, detail=f"Méthode '{method}' non reconnue")
        
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/missing-heatmap")
async def get_missing_heatmap(file_id: str) -> Dict[str, Any]:
    """
    Génère une heatmap des valeurs manquantes
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = HeatmapGenerator.create_missing_heatmap(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/missing-bar")
async def get_missing_bar_chart(file_id: str) -> Dict[str, Any]:
    """
    Génère un graphique à barres des valeurs manquantes
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        result = MissingVisualizer.create_missing_bar_chart(df)
        result['file_id'] = file_id
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))