"""
Profil global du dataset
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

from .type_detector import TypeDetector


class DatasetProfiler:
    """
    Générateur de profil global pour un dataset
    """
    
    def __init__(self, df: pd.DataFrame, file_id: str = None):
        """
        Initialise le profileur
        
        Args:
            df: DataFrame à analyser
            file_id: Identifiant optionnel du fichier
        """
        self.df = df
        self.file_id = file_id
        self.type_analysis = None
        self.type_summary = None
    
    def profile(self) -> Dict[str, Any]:
        """
        Génère le profil complet du dataset
        
        Returns:
            Dictionnaire avec toutes les informations du dataset
        """
        # Analyser les types
        self.type_analysis = TypeDetector.analyze_all(self.df)
        self.type_summary = TypeDetector.get_summary(self.type_analysis)
        
        # Calculer les métriques
        return {
            'file_id': self.file_id,
            'basic_info': self._get_basic_info(),
            'column_types': self._get_column_types_dict(),
            'column_summary': self.type_summary,
            'columns_detail': self.type_analysis,
            'memory_info': self._get_memory_info(),
            'sample_data': self._get_sample_data()
        }
    
    def get_overview(self) -> Dict[str, Any]:
        """
        Version simplifiée pour l'endpoint /overview
        
        Returns:
            Vue d'ensemble du dataset
        """
        # Forcer l'analyse des types si pas encore faite
        if self.type_analysis is None:
            self.type_analysis = TypeDetector.analyze_all(self.df)
        
        if self.type_summary is None:
            self.type_summary = TypeDetector.get_summary(self.type_analysis)
        
        basic = self._get_basic_info()
        
        return {
            'file_id': self.file_id,
            'rows': basic['rows'],
            'columns': basic['columns'],
            'memory_usage_mb': basic['memory_usage_mb'],
            'column_types': self._get_column_types_dict(),
            'numeric_columns': self.type_summary.get(TypeDetector.TYPE_NUMERIC, []),
            'categorical_columns': self.type_summary.get(TypeDetector.TYPE_CATEGORICAL, []),
            'text_columns': self.type_summary.get(TypeDetector.TYPE_TEXT, []),
            'datetime_columns': self.type_summary.get(TypeDetector.TYPE_DATETIME, []),
            'boolean_columns': self.type_summary.get(TypeDetector.TYPE_BOOLEAN, []),
            'empty_columns': self.type_summary.get(TypeDetector.TYPE_EMPTY, [])
        }
    
    def _get_basic_info(self) -> Dict[str, Any]:
        """Informations basiques"""
        return {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'total_cells': self.df.size,
            'memory_usage_bytes': int(self.df.memory_usage(deep=True).sum()),
            'memory_usage_mb': round(self.df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            'has_missing': bool(self.df.isna().any().any()),
            'total_missing_cells': int(self.df.isna().sum().sum()),
            'missing_percentage': round((self.df.isna().sum().sum() / self.df.size) * 100, 2)
        }
    
    def _get_column_types_dict(self) -> Dict[str, str]:
        """
        Retourne un dictionnaire {nom_colonne: type_detecte}
        """
        if self.type_analysis is None:
            return {}
        return {
            col: info['detected_type'] 
            for col, info in self.type_analysis.items()
        }
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Informations détaillées sur la mémoire"""
        memory_by_type = {}
        
        for dtype in ['int64', 'float64', 'object', 'datetime64', 'category']:
            cols = self.df.select_dtypes(include=[dtype]).columns
            if len(cols) > 0:
                memory = self.df[cols].memory_usage(deep=True).sum()
                memory_by_type[dtype] = {
                    'columns': len(cols),
                    'memory_bytes': int(memory),
                    'memory_mb': round(memory / (1024 * 1024), 2)
                }
        
        return {
            'total_mb': round(self.df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            'by_type': memory_by_type,
            'per_column': {
                col: round(self.df[col].memory_usage(deep=True) / (1024 * 1024), 4)
                for col in self.df.columns
            }
        }
    
    def _get_sample_data(self, n_rows: int = 5) -> Dict[str, Any]:
        """Échantillon des données"""
        sample_df = self.df.head(n_rows)
        
        # Convertir en dict avec gestion des types non sérialisables
        sample_dict = {}
        for col in sample_df.columns:
            values = sample_df[col].tolist()
            # Convertir les valeurs non sérialisables
            sample_dict[col] = [
                str(v) if pd.isna(v) else 
                v.isoformat() if hasattr(v, 'isoformat') else
                float(v) if isinstance(v, (np.integer, np.floating)) else
                v for v in values
            ]
        
        return {
            'n_rows': n_rows,
            'data': sample_dict
        }
    
    @classmethod
    def quick_profile(cls, df: pd.DataFrame, file_id: str = None) -> Dict[str, Any]:
        """
        Méthode statique pour un profiling rapide
        
        Args:
            df: DataFrame à analyser
            file_id: Identifiant optionnel
            
        Returns:
            Profil du dataset
        """
        profiler = cls(df, file_id)
        return profiler.profile()
    
    @classmethod
    def quick_overview(cls, df: pd.DataFrame, file_id: str = None) -> Dict[str, Any]:
        """
        Méthode statique pour un aperçu rapide
        
        Args:
            df: DataFrame à analyser
            file_id: Identifiant optionnel
            
        Returns:
            Aperçu du dataset
        """
        profiler = cls(df, file_id)
        return profiler.get_overview()