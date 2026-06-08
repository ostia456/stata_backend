"""
Routes pour la génération de rapports HTML et PDF
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Dict, Any
import json

from app.services.upload_service import UploadService
from app.services.analysis_service import GlobalAnalysisService
from app.reports.html_generator import HTMLReportGenerator
from app.core.exceptions import UploadError
from app.config import Config
from app.utils import clean_for_json

router = APIRouter(prefix="/reports", tags=["Reports"])
upload_service = UploadService()
html_generator = HTMLReportGenerator()

# PDF optionnel - tentative d'import
PDF_AVAILABLE = False
pdf_generator = None

try:
    from app.reports.pdf_generator import PDFReportGenerator
    pdf_generator = PDFReportGenerator()
    PDF_AVAILABLE = True
    print("✅ Génération PDF disponible")
except ImportError as e:
    print(f"⚠️ Module PDF non trouvé: {e}")
except Exception as e:
    print(f"⚠️ Erreur initialisation PDF: {e}")

@router.get("/data-scientist/{file_id}")
async def get_data_scientist_report(file_id: str) -> Dict[str, Any]:
    """
    Génère un rapport spécialisé pour Data Scientist
    
    - **file_id**: Identifiant du fichier uploadé
    """
    try:
        from app.reports.data_scientist_report import DataScientistReportGenerator
        
        df = upload_service.get_dataframe(file_id)
        result = DataScientistReportGenerator.generate(df, file_id)
        return clean_for_json(result)
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")

@router.get("/html/{file_id}")
async def generate_html_report(
    file_id: str,
    download: bool = Query(False, description="Télécharger directement le fichier")
) -> Dict[str, Any]:
    """Génère un rapport HTML complet"""
    try:
        df = upload_service.get_dataframe(file_id)
        service = GlobalAnalysisService(df, file_id)
        analysis_result = service.run_complete_analysis()
        
        html_path = html_generator.generate_and_save(analysis_result, file_id)
        
        if download:
            return FileResponse(
                path=html_path,
                media_type="text/html",
                filename=f"report_{file_id}.html"
            )
        else:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            return {
                'file_id': file_id,
                'html_content': html_content,
                'report_path': html_path
            }
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.get("/html/{file_id}/download")
async def download_html_report(file_id: str) -> FileResponse:
    """Télécharge le rapport HTML"""
    try:
        df = upload_service.get_dataframe(file_id)
        service = GlobalAnalysisService(df, file_id)
        analysis_result = service.run_complete_analysis()
        
        html_path = html_generator.generate_and_save(analysis_result, file_id)
        
        return FileResponse(
            path=html_path,
            media_type="text/html",
            filename=f"autoeda_report_{file_id}.html"
        )
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== ENDPOINTS PDF (optionnels) ==========

@router.get("/pdf/{file_id}")
async def generate_pdf_report_endpoint(
    file_id: str,
    download: bool = Query(True, description="Télécharger directement le fichier")
):
    """Génère un rapport PDF complet"""
    if not PDF_AVAILABLE or pdf_generator is None:
        raise HTTPException(
            status_code=501, 
            detail="Génération PDF non disponible. Installez wkhtmltopdf et kaleido."
        )
    
    try:
        df = upload_service.get_dataframe(file_id)
        service = GlobalAnalysisService(df, file_id)
        analysis_result = service.run_complete_analysis()
        
        pdf_path = pdf_generator.generate_and_save(analysis_result, df, file_id)
        
        if download:
            return FileResponse(
                path=pdf_path,
                media_type="application/pdf",
                filename=f"autoeda_report_{file_id}.pdf"
            )
        else:
            return {
                'file_id': file_id,
                'report_path': pdf_path,
                'message': 'PDF généré avec succès'
            }
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur PDF: {str(e)}")


@router.get("/pdf/{file_id}/download")
async def download_pdf_report(file_id: str) -> FileResponse:
    """Télécharge le rapport PDF"""
    if not PDF_AVAILABLE or pdf_generator is None:
        raise HTTPException(status_code=501, detail="Génération PDF non disponible")
    
    try:
        df = upload_service.get_dataframe(file_id)
        service = GlobalAnalysisService(df, file_id)
        analysis_result = service.run_complete_analysis()
        
        pdf_path = pdf_generator.generate_and_save(analysis_result, df, file_id)
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"autoeda_report_{file_id}.pdf"
        )
        
    except UploadError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdf/{file_id}/status")
async def check_pdf_status(file_id: str) -> Dict[str, Any]:
    """Vérifie si un rapport PDF existe"""
    try:
        pdf_dir = Config.PDF_REPORTS_DIR
        pdf_files = list(pdf_dir.glob(f"{file_id}_*.pdf"))
        
        if pdf_files:
            latest = max(pdf_files, key=lambda x: x.stat().st_mtime)
            return {
                'file_id': file_id,
                'exists': True,
                'latest_report': str(latest),
                'generated_at': latest.stat().st_mtime
            }
        else:
            return {
                'file_id': file_id,
                'exists': False,
                'message': 'Aucun rapport PDF généré pour ce fichier'
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))