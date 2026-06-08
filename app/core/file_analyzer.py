"""
Analyse des fichiers pour détection automatique
"""

import chardet
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from ..config import Config
from ..core.exceptions import FileCorruptedError


class FileAnalyzer:
    """
    Analyse et charge un fichier (CSV/Excel) avec détection automatique
    """
    
    @classmethod
    def detect_encoding(cls, file_path: str, sample_size: int = 10000) -> str:
        """
        Détecte l'encodage d'un fichier CSV
        
        Args:
            file_path: Chemin vers le fichier
            sample_size: Nombre d'octets à analyser
            
        Returns:
            Encodage détecté (ex: 'utf-8', 'latin1')
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read(sample_size)
            result = chardet.detect(raw_data)
            detected_encoding = result['encoding'] or 'utf-8'
            # Convertir les noms d'encodage pour pandas
            if detected_encoding.lower() == 'ascii':
                return 'utf-8'
            return detected_encoding
    
    @classmethod
    def detect_separator(cls, file_path: str, encoding: str) -> str:
        """
        Détecte le séparateur d'un fichier CSV
        
        Args:
            file_path: Chemin vers le fichier
            encoding: Encodage du fichier
            
        Returns:
            Séparateur détecté (',', ';', '\t', '|')
        """
        common_separators = [',', ';', '\t', '|']
        
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            first_line = f.readline()
            
            best_sep = ','
            best_count = 0
            
            for sep in common_separators:
                count = first_line.count(sep)
                if count > best_count:
                    best_count = count
                    best_sep = sep
        
        return best_sep
    
    @classmethod
    def load_csv(cls, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Charge un fichier CSV avec détection automatique
        
        Returns:
            Tuple (DataFrame, metadata)
        """
        metadata = {
            'file_type': 'csv',
            'encoding': None,
            'separator': None,
            'original_rows': None
        }
        
        # Détection encodage
        encoding = cls.detect_encoding(file_path)
        metadata['encoding'] = encoding
        
        # Détection séparateur
        separator = cls.detect_separator(file_path, encoding)
        metadata['separator'] = separator
        
        # Compter les lignes approximatives
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            line_count = sum(1 for _ in f)
            metadata['original_rows'] = line_count
        
        # Charger avec détection automatique d'erreurs
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                sep=separator,
                nrows=Config.MAX_ROWS_TO_LOAD if line_count > Config.MAX_ROWS_TO_LOAD else None,
                low_memory=False,
                encoding_errors='replace'  # Ignorer les caractères problématiques
            )
        except Exception as e:
            raise FileCorruptedError(f"Erreur lors du chargement CSV: {str(e)}")
        
        metadata['loaded_rows'] = len(df)
        metadata['truncated'] = line_count > Config.MAX_ROWS_TO_LOAD
        metadata['total_rows'] = line_count
        
        return df, metadata
    
    @classmethod
    def load_excel(cls, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Charge un fichier Excel
        
        Returns:
            Tuple (DataFrame, metadata)
        """
        metadata = {
            'file_type': 'excel',
            'sheets': [],
            'sheet_used': None,
            'original_rows': None
        }
        
        try:
            excel_file = pd.ExcelFile(file_path)
            metadata['sheets'] = excel_file.sheet_names
            metadata['sheet_used'] = excel_file.sheet_names[0]
            
            df = pd.read_excel(
                file_path,
                sheet_name=0,
                nrows=Config.MAX_ROWS_TO_LOAD
            )
            
        except Exception as e:
            raise FileCorruptedError(f"Erreur lors du chargement Excel: {str(e)}")
        
        metadata['loaded_rows'] = len(df)
        metadata['truncated'] = False
        metadata['total_rows'] = len(df)
        
        return df, metadata
    
    @classmethod
    def load_file(cls, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Charge un fichier avec détection automatique du type
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            Tuple (DataFrame, metadata)
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.csv':
            return cls.load_csv(str(file_path))
        elif extension in ['.xlsx', '.xls']:
            return cls.load_excel(str(file_path))
        else:
            raise FileCorruptedError(f"Type de fichier non supporté: {extension}")
    
    @classmethod
    def get_file_info(cls, file_path: str) -> Dict[str, Any]:
        """
        Retourne les informations basiques d'un fichier sans le charger
        """
        import os
        
        file_path = Path(file_path)
        file_size = os.path.getsize(file_path)
        
        info = {
            'filename': file_path.name,
            'extension': file_path.suffix.lower(),
            'size_bytes': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2)
        }
        
        if info['extension'] == '.csv':
            try:
                info['encoding'] = cls.detect_encoding(str(file_path))
            except:
                info['encoding'] = 'unknown'
        
        return info