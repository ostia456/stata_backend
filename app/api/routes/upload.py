"""
Route d'upload de fichiers
"""

import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any

from app.services.upload_service import UploadService
from app.core.exceptions import InvalidFileTypeError, FileTooLargeError, FileCorruptedError, UploadError

router = APIRouter(prefix="/upload", tags=["Upload"])
upload_service = UploadService()

# Stockage temporaire de la progression
upload_progress = {}


@router.post("")
async def upload_file(
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Upload un fichier CSV ou Excel
    
    - **file**: Fichier à analyser (CSV, XLSX, XLS)
    
    Retourne un file_id pour les requêtes ultérieures
    """
    try:
        # Lire le contenu du fichier
        content = await file.read()
        total_size = len(content)
        
        # Simuler la progression de lecture
        for percent in range(0, 101, 10):
            upload_progress[file.filename] = percent
            await asyncio.sleep(0.1)
        
        # Traiter l'upload
        result = await upload_service.process_upload(
            filename=file.filename,
            content=content
        )
        
        upload_progress[file.filename] = 100
        
        return result
        
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=415, detail=str(e))
    except FileTooLargeError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except FileCorruptedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UploadError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur inattendue: {str(e)}")


@router.get("/progress/{filename}")
async def get_upload_progress(filename: str) -> Dict[str, Any]:
    """
    Récupère la progression de l'upload d'un fichier
    """
    progress = upload_progress.get(filename, 0)
    return {"filename": filename, "progress": progress}


@router.get("/{file_id}/info")
async def get_file_info(file_id: str) -> Dict[str, Any]:
    """
    Récupère les informations d'un fichier uploadé
    """
    try:
        metadata = upload_service.get_metadata(file_id)
        return metadata
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{file_id}")
async def delete_file(file_id: str) -> Dict[str, str]:
    """
    Supprime un fichier uploadé
    """
    try:
        upload_service.delete_file(file_id)
        return {"status": "deleted", "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))