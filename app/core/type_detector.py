"""
Détection intelligente des types de colonnes
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List


class TypeDetector:
    """
    Détecteur automatique des types de colonnes
    """
    
    # Types possibles
    TYPE_NUMERIC = "numeric"
    TYPE_CATEGORICAL = "categorical"
    TYPE_TEXT = "text"
    TYPE_DATETIME = "datetime"
    TYPE_BOOLEAN = "boolean"
    TYPE_MIXED = "mixed"
    TYPE_EMPTY = "empty"
    
    @classmethod
    def detect(cls, series: pd.Series) -> str:
        """
        Détecte le type d'une colonne
        
        Args:
            series: Série pandas à analyser
            
        Returns:
            Type détecté (numeric, categorical, text, datetime, boolean, mixed, empty)
        """
        # Vider les valeurs nulles pour l'analyse
        clean_series = series.dropna()
        
        # Cas vide
        if len(clean_series) == 0:
            return cls.TYPE_EMPTY
        
        # 1. Détection booléenne
        if cls._is_boolean(clean_series):
            return cls.TYPE_BOOLEAN
        
        # 2. Détection numérique
        if pd.api.types.is_numeric_dtype(series):
            return cls.TYPE_NUMERIC
        
        # 3. Détection datetime
        if cls._is_datetime(clean_series):
            return cls.TYPE_DATETIME
        
        # 4. Détection catégorielle (peu de valeurs uniques)
        unique_count = clean_series.nunique()
        unique_ratio = unique_count / len(clean_series) if len(clean_series) > 0 else 1
        
        if unique_count <= 20 or unique_ratio < 0.05:
            return cls.TYPE_CATEGORICAL
        
        # 5. Détection de nombres stockés comme texte
        if cls._is_numeric_string(clean_series):
            return cls.TYPE_NUMERIC
        
        # 6. Par défaut : texte
        return cls.TYPE_TEXT
    
    @classmethod
    def _is_boolean(cls, series: pd.Series) -> bool:
        """Vérifie si la colonne contient des valeurs booléennes"""
        try:
            unique_values = set(series.astype(str).str.lower())
            boolean_patterns = {
                'true', 'false', '1', '0', 'yes', 'no', 
                'oui', 'non', 'vrai', 'faux', 't', 'f'
            }
            return unique_values.issubset(boolean_patterns)
        except Exception:
            return False
    
    @classmethod
    def _is_datetime(cls, series: pd.Series) -> bool:
        """Vérifie si la colonne peut être convertie en datetime"""
        try:
            # Échantillon de valeurs
            sample = series.head(100)
            pd.to_datetime(sample, errors='raise')
            return True
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def _is_numeric_string(cls, series: pd.Series) -> bool:
        """Vérifie si une colonne texte contient des nombres"""
        try:
            sample = series.head(100)
            # Vérifier si au moins 90% des valeurs sont numériques
            numeric_count = 0
            for val in sample:
                try:
                    float(str(val))
                    numeric_count += 1
                except (ValueError, TypeError):
                    pass
            return numeric_count / len(sample) > 0.9
        except Exception:
            return False
    
    @classmethod
    def analyze_all(cls, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyse toutes les colonnes d'un DataFrame
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec les détails de chaque colonne
        """
        results = {}
        
        for col in df.columns:
            series = df[col]
            detected_type = cls.detect(series)
            
            # Infos de base
            info = {
                'name': col,
                'detected_type': detected_type,
                'dtype': str(series.dtype),
                'unique_count': int(series.nunique()),
                'null_count': int(series.isna().sum()),
                'null_percentage': round((series.isna().sum() / len(df)) * 100, 2),
                'memory_usage_bytes': int(series.memory_usage(deep=True))
            }
            
            # Ajouter des infos spécifiques selon le type
            if detected_type == cls.TYPE_NUMERIC:
                clean = series.dropna()
                if len(clean) > 0:
                    info['min'] = float(clean.min())
                    info['max'] = float(clean.max())
                    info['mean'] = float(clean.mean())
                    info['median'] = float(clean.median())
            
            elif detected_type == cls.TYPE_CATEGORICAL:
                value_counts = series.value_counts()
                if len(value_counts) > 0:
                    info['top_value'] = str(value_counts.index[0])
                    info['top_frequency'] = int(value_counts.iloc[0])
                    info['unique_ratio'] = round(series.nunique() / len(series), 4)
            
            results[col] = info
        
        return results
    
    @classmethod
    def get_summary(cls, analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Retourne un résumé global de l'analyse des types
        
        Args:
            analysis: Résultat de analyze_all()
            
        Returns:
            Résumé global
        """
        summary = {
            cls.TYPE_NUMERIC: [],
            cls.TYPE_CATEGORICAL: [],
            cls.TYPE_TEXT: [],
            cls.TYPE_DATETIME: [],
            cls.TYPE_BOOLEAN: [],
            cls.TYPE_MIXED: [],
            cls.TYPE_EMPTY: []
        }
        
        for col, info in analysis.items():
            detected_type = info['detected_type']
            if detected_type in summary:
                summary[detected_type].append(col)
        
        return summary