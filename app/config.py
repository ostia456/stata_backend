"""
Configuration de l'application
"""

import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    """Configuration principale"""
    
    # Application
    APP_NAME = os.getenv("APP_NAME", "AutoEDA Backend")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("PORT", 8000))
    
    # Dossiers
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_DIR = BASE_DIR / "uploads"
    TEMP_DIR = UPLOAD_DIR / "temp"
    PROCESSED_DIR = UPLOAD_DIR / "processed"
    REPORTS_OUTPUT_DIR = BASE_DIR / "reports_output"
    HTML_REPORTS_DIR = REPORTS_OUTPUT_DIR / "html"
    PDF_REPORTS_DIR = REPORTS_OUTPUT_DIR / "pdf"
    CACHE_DIR = BASE_DIR / "cache"
    METADATA_DIR = BASE_DIR / "metadata"
    
    # Upload constraints
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 200))
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
    
    # Analysis constraints
    MAX_ROWS_TO_LOAD = int(os.getenv("MAX_ROWS_TO_LOAD", 10000))
    MAX_COLUMNS_TO_ANALYZE = int(os.getenv("MAX_COLUMNS_TO_ANALYZE", 50))
    
    # ========== SÉCURITÉ ==========
    # API Key (générée automatiquement si non définie)
    API_KEY = os.getenv('API_KEY', secrets.token_urlsafe(32))
    
    # Rate limiting
    ENABLE_RATE_LIMITING = os.getenv('ENABLE_RATE_LIMITING', 'True').lower() == 'true'
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60))
    
    # Validation
    MAX_FILENAME_LENGTH = 255
    
    # CORS (restreindre en production)
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    
    @classmethod
    def ensure_directories(cls):
        """Crée les dossiers nécessaires"""
        dirs = [
            cls.UPLOAD_DIR,
            cls.TEMP_DIR,
            cls.PROCESSED_DIR,
            cls.REPORTS_OUTPUT_DIR,
            cls.HTML_REPORTS_DIR,
            cls.PDF_REPORTS_DIR,
            cls.CACHE_DIR,
            cls.METADATA_DIR
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_allowed_extensions_tuple(cls):
        """Retourne les extensions autorisées pour FastAPI"""
        return tuple(cls.ALLOWED_EXTENSIONS)
    
    @classmethod
    def get_upload_path(cls, filename: str) -> Path:
        """Retourne le chemin complet pour sauvegarder un fichier"""
        return cls.TEMP_DIR / filename
    
    @classmethod
    def get_processed_path(cls, file_id: str) -> Path:
        """Retourne le chemin du fichier traité"""
        return cls.PROCESSED_DIR / f"{file_id}.pkl"


# Créer les dossiers au chargement
Config.ensure_directories()