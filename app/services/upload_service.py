"""
Service de gestion des uploads
"""

import uuid
import pickle
from pathlib import Path
from typing import Dict, Any, Tuple

import pandas as pd

from ..config import Config
from ..core.file_analyzer import FileAnalyzer
from ..core.exceptions import UploadError, FileCorruptedError
from ..validators.file_validator import FileValidator


class UploadService:
    """Service de gestion des uploads de fichiers"""
    
    def __init__(self):
        self.file_analyzer = FileAnalyzer()
        self.validator = FileValidator()
    
    async def process_upload(self, filename: str, content: bytes) -> Dict[str, Any]:
        """
        Traite un fichier uploadé
        
        Args:
            filename: Nom du fichier
            content: Contenu du fichier en bytes
            
        Returns:
            Dictionnaire avec les métadonnées du fichier
        """
        # 1. Valider le fichier
        extension, base_name = self.validator.validate_file(filename, content)
        
        # 2. Générer un ID unique
        file_id = str(uuid.uuid4())[:8]
        
        # 3. Sauvegarder le fichier temporairement
        temp_path = Config.get_upload_path(f"{file_id}{extension}")
        temp_path.write_bytes(content)
        
        try:
            # 4. Analyser et charger le fichier
            df, metadata = self.file_analyzer.load_file(str(temp_path))
            
            # 5. Vérifier que le DataFrame n'est pas vide
            if df.empty:
                raise FileCorruptedError("Le fichier ne contient aucune donnée")
            
            # 6. Sauvegarder le DataFrame traité (pickle pour réutilisation)
            processed_path = Config.get_processed_path(file_id)
            with open(processed_path, 'wb') as f:
                pickle.dump(df, f)
            
            # 7. Nettoyer le fichier temporaire (optionnel, on garde pour débogage)
            # temp_path.unlink()
            
            # 8. Sauvegarder les métadonnées
            metadata.update({
                'file_id': file_id,
                'original_filename': filename,
                'extension': extension,
                'columns': len(df.columns),
                'rows': len(df),
                'columns_list': df.columns.tolist()
            })
            
            # Sauvegarder les métadonnées
            metadata_path = Config.METADATA_DIR / f"{file_id}_metadata.json"
            import json
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            return {
                'file_id': file_id,
                'filename': filename,
                'status': 'uploaded',
                'rows': len(df),
                'columns': len(df.columns),
                'size_mb': round(len(content) / (1024 * 1024), 2),
                'file_type': metadata['file_type'],
                'truncated': metadata.get('truncated', False),
                'total_rows': metadata.get('total_rows', len(df))
            }
            
        except Exception as e:
            # Nettoyer en cas d'erreur
            if temp_path.exists():
                temp_path.unlink()
            raise UploadError(f"Erreur lors du traitement du fichier: {str(e)}")
    
    def get_dataframe(self, file_id: str) -> pd.DataFrame:
        """
        Récupère le DataFrame associé à un file_id
        
        Args:
            file_id: Identifiant du fichier
            
        Returns:
            DataFrame pandas
        """
        processed_path = Config.get_processed_path(file_id)
        
        if not processed_path.exists():
            raise UploadError(f"Fichier {file_id} non trouvé")
        
        with open(processed_path, 'rb') as f:
            df = pickle.load(f)
        
        return df
    
    def get_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Récupère les métadonnées d'un fichier
        
        Args:
            file_id: Identifiant du fichier
            
        Returns:
            Dictionnaire des métadonnées
        """
        import json
        
        metadata_path = Config.METADATA_DIR / f"{file_id}_metadata.json"
        
        if not metadata_path.exists():
            raise UploadError(f"Métadonnées pour {file_id} non trouvées")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def delete_file(self, file_id: str):
        """
        Supprime un fichier et ses données associées
        """
        processed_path = Config.get_processed_path(file_id)
        metadata_path = Config.METADATA_DIR / f"{file_id}_metadata.json"
        
        if processed_path.exists():
            processed_path.unlink()
        
        if metadata_path.exists():
            metadata_path.unlink()