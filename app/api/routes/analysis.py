"""
Routes d'analyse du dataset
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.services.upload_service import UploadService
from app.core.dataset_profiler import DatasetProfiler
from app.core.exceptions import UploadError

router = APIRouter(prefix="/analysis", tags=["Analysis"])
upload_service = UploadService()


@router.get("/{file_id}/overview")
async def get_dataset_overview(file_id: str) -> Dict[str, Any]:
    """
    Récupère une vue d'ensemble du dataset
    
    - **file_id**: Identifiant du fichier uploadé
    
    Retourne les statistiques globales et les types des colonnes
    """
    try:
        print(f"🔍 Récupération du DataFrame pour file_id: {file_id}")
        
        # Récupérer le DataFrame
        df = upload_service.get_dataframe(file_id)
        
        print(f"✅ DataFrame chargé: {df.shape}")
        print(f"   Colonnes: {df.columns.tolist()}")
        
        # Générer l'aperçu
        overview = DatasetProfiler.quick_overview(df, file_id)
        
        print(f"✅ Overview généré avec succès")
        
        return overview
        
    except UploadError as e:
        print(f"❌ UploadError: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")


@router.get("/{file_id}/profile")
async def get_dataset_profile(file_id: str) -> Dict[str, Any]:
    """
    Récupère le profil complet du dataset
    
    - **file_id**: Identifiant du fichier uploadé
    
    Retourne l'analyse détaillée de toutes les colonnes
    """
    try:
        # Récupérer le DataFrame
        df = upload_service.get_dataframe(file_id)
        
        # Générer le profil complet
        profile = DatasetProfiler.quick_profile(df, file_id)
        
        return profile
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")