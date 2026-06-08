"""
Validation des fichiers uploadés
"""

import os
from pathlib import Path
from typing import Tuple

from ..config import Config
from ..core.exceptions import InvalidFileTypeError, FileTooLargeError, FileCorruptedError
from app.middleware.security import InputValidator, FileSecurity

class FileValidator:
    """Validateur de fichiers"""
    
    @classmethod
    def validate_file(cls, filename: str, content: bytes) -> Tuple[str, str]:
        """
        Valide un fichier uploadé
        
        Args:
            filename: Nom du fichier
            content: Contenu du fichier en bytes
            
        Returns:
            Tuple (extension, nom_sans_extension)
            
        Raises:
            InvalidFileTypeError: Extension non supportée
            FileTooLargeError: Fichier trop volumineux
            FileCorruptedError: Fichier corrompu
        """
        # 1. Valider l'extension
        extension = cls._validate_extension(filename)
        
        # 2. Valider la taille
        cls._validate_size(content)
        
        # 3. Valider l'intégrité (basique)
        cls._validate_integrity(content, extension)
        
        # 4. Extraire le nom sans extension
        base_name = Path(filename).stem
        
        return extension, base_name
    
    @classmethod
    def _validate_extension(cls, filename: str) -> str:
        """Valide l'extension du fichier"""
        ext = Path(filename).suffix.lower()
        
        if ext not in Config.ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(
                f"Extension '{ext}' non supportée. "
                f"Extensions autorisées: {', '.join(Config.ALLOWED_EXTENSIONS)}"
            )
        
        return ext
    
    @classmethod
    def _validate_size(cls, content: bytes):
        """Valide la taille du fichier"""
        file_size = len(content)
        
        if file_size > Config.MAX_FILE_SIZE_BYTES:
            raise FileTooLargeError(
                f"Fichier trop volumineux: {file_size / (1024*1024):.2f} MB. "
                f"Taille maximale: {Config.MAX_FILE_SIZE_MB} MB"
            )
    
    @classmethod
    def _validate_integrity(cls, content: bytes, extension: str):
        """
        Valide l'intégrité basique du fichier
        Ne lit pas tout le fichier, juste vérifie qu'il n'est pas vide
        """
        if len(content) == 0:
            raise FileCorruptedError("Le fichier est vide")
        
        # Pour CSV, vérifier qu'il contient au moins un séparateur basique
        if extension == ".csv":
            try:
                first_chunk = content[:1000].decode('utf-8', errors='ignore')
                if ',' not in first_chunk and ';' not in first_chunk and '\t' not in first_chunk:
                    # Pas critique, juste un warning logique
                    pass
            except Exception:
                # Encodage peut poser problème, on ne bloque pas ici
                pass
    
    @classmethod
    def is_allowed_file(cls, filename: str) -> bool:
        """Vérifie si l'extension est autorisée (sans lever d'exception)"""
        ext = Path(filename).suffix.lower()
        return ext in Config.ALLOWED_EXTENSIONS
    
     
    @classmethod
    def validate_security(cls, filename: str, content: bytes) -> Tuple[str, str]:
        """
        Validation de sécurité complète
        """
        # Validation du nom
        if not InputValidator.validate_filename(filename):
            raise InvalidFileTypeError("Nom de fichier invalide")
        
        # Validation de la taille
        cls._validate_size(content)
        
        # Scan de contenu malveillant
        if not FileSecurity.scan_for_malware(content):
            raise FileCorruptedError("Contenu suspect détecté")
        
        # Validation de l'extension et signature
        extension = cls._validate_extension(filename)
        if not FileSecurity.validate_magic_signature(content, extension):
            # Ne pas bloquer, juste logger (parfois les signatures sont détectées tard)
            import logging
            logging.warning(f"Signature magique non détectée pour {filename}")
        
        return extension, Path(filename).stem