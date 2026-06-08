"""
Routes pour l'analyse globale (agrège tous les résultats)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from app.services.metadata_service import metadata_service
from app.services.upload_service import UploadService
from app.services.analysis_service import GlobalAnalysisService
from app.core.exceptions import UploadError
from app.utils import clean_for_json

router = APIRouter(prefix="/analysis", tags=["Analysis"])

# Créer l'instance du service d'upload
upload_service = UploadService()


@router.post("/run/{file_id}")
async def run_complete_analysis(
    file_id: str,
    quick: bool = Query(False, description="Version rapide (True) ou complète (False)")
) -> Dict[str, Any]:
    """
    Exécute une analyse complète du dataset
    
    - **file_id**: Identifiant du fichier uploadé
    - **quick**: True pour une analyse rapide, False pour complète
    
    Retourne un rapport complet incluant toutes les analyses
    (statistiques, corrélations, normalité, outliers, qualité, insights)
    """
    try:
        # Récupérer le DataFrame
        df = upload_service.get_dataframe(file_id)
        
        # Récupérer les métadonnées du fichier
        metadata = upload_service.get_metadata(file_id)
        filename = metadata.get('original_filename', 'unknown')
        
        # Exécuter l'analyse
        service = GlobalAnalysisService(df, file_id)
        
        if quick:
            result = service.run_quick_analysis()
        else:
            result = service.run_complete_analysis()
            
            # Enregistrer dans l'historique (seulement pour analyse complète)
            metadata_service.add_analysis(file_id, filename, result)
        
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse globale: {str(e)}")

@router.get("/run/{file_id}")
async def run_complete_analysis_get(
    file_id: str,
    quick: bool = Query(False, description="Version rapide (True) ou complète (False)")
) -> Dict[str, Any]:
    """
    Version GET de l'analyse complète
    
    - **file_id**: Identifiant du fichier uploadé
    - **quick**: True pour une analyse rapide, False pour complète
    """
    return await run_complete_analysis(file_id, quick)