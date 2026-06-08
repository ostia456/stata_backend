"""
Routes pour la gestion du cache
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.core.cache_manager import cache_manager
from app.services.upload_service import UploadService
from app.core.exceptions import UploadError

router = APIRouter(prefix="/cache", tags=["Cache"])
upload_service = UploadService()


@router.get("/{file_id}")
async def get_cache_info(file_id: str) -> Dict[str, Any]:
    """
    Récupère les informations de cache pour un fichier
    
    - **file_id**: Identifiant du fichier
    """
    try:
        # Vérifier que le fichier existe
        upload_service.get_metadata(file_id)
        
        info = cache_manager.get_cache_info(file_id)
        return info
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{file_id}")
async def clear_file_cache(file_id: str) -> Dict[str, str]:
    """
    Supprime le cache pour un fichier
    
    - **file_id**: Identifiant du fichier
    """
    try:
        success = cache_manager.clear_file_cache(file_id)
        if success:
            return {"status": "success", "message": f"Cache supprimé pour {file_id}"}
        else:
            return {"status": "warning", "message": f"Aucun cache trouvé pour {file_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/all")
async def clear_all_cache() -> Dict[str, str]:
    """
    Supprime tout le cache
    """
    try:
        import shutil
        if cache_manager.analysis_dir.exists():
            shutil.rmtree(cache_manager.analysis_dir)
            cache_manager.analysis_dir.mkdir()
        if cache_manager.reports_dir.exists():
            shutil.rmtree(cache_manager.reports_dir)
            cache_manager.reports_dir.mkdir()
        
        return {"status": "success", "message": "Cache complet supprimé"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))