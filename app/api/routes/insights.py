"""
Routes pour les insights automatiques
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List

from app.services.upload_service import UploadService
from app.interpretation.data_insights import DataInsightsGenerator, SimpleInsightsGenerator
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/insights", tags=["Insights"])
upload_service = UploadService()


@router.get("/{file_id}")
async def get_insights(
    file_id: str,
    detailed: bool = Query(True, description="Rapport détaillé ou rapide")
) -> Dict[str, Any]:
    """
    Génère des insights automatiques sur le dataset
    
    - **file_id**: Identifiant du fichier uploadé
    - **detailed**: True pour rapport détaillé, False pour version rapide
    
    Retourne des insights en langage naturel
    """
    try:
        df = upload_service.get_dataframe(file_id)
        
        if detailed:
            insights = DataInsightsGenerator.generate_all_insights(df)
        else:
            insights = {
                'quick_insights': SimpleInsightsGenerator.quick_insights(df)
            }
        
        insights['file_id'] = file_id
        return clean_for_json(insights)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


@router.get("/{file_id}/summary")
async def get_executive_summary(file_id: str) -> Dict[str, Any]:
    """
    Génère un résumé exécutif du dataset
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        insights = DataInsightsGenerator.generate_all_insights(df)
        
        return clean_for_json({
            'file_id': file_id,
            'executive_summary': insights['executive_summary'],
            'quality_grade': insights['quality_insights'][0] if insights['quality_insights'] else None,
            'key_recommendations': [r for r in insights['recommendations'] if r['priority'] == 'high'][:3]
        })
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/quick")
async def get_quick_insights(file_id: str) -> Dict[str, Any]:
    """
    Version rapide des insights
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        df = upload_service.get_dataframe(file_id)
        insights = SimpleInsightsGenerator.quick_insights(df)
        
        return clean_for_json({
            'file_id': file_id,
            'insights': insights
        })
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))