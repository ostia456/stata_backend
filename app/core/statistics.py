"""
Calcul des statistiques descriptives
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class StatisticsCalculator:
    """
    Calculateur de statistiques descriptives pour les colonnes numériques
    """
    
    @classmethod
    def calculate_numeric_stats(cls, series: pd.Series) -> Dict[str, Any]:
        """
        Calcule toutes les statistiques pour une colonne numérique
        
        Args:
            series: Série pandas numérique
            
        Returns:
            Dictionnaire avec toutes les statistiques
        """
        # Vérifier si la colonne est vraiment numérique
        if not pd.api.types.is_numeric_dtype(series):
            return {
                'error': 'Colonne non numérique',
                'count': 0,
                'null_count': int(series.isna().sum()),
                'null_percentage': round((series.isna().sum() / len(series)) * 100, 2),
                'message': f'La colonne {series.name} contient des valeurs non numériques'
            }
        
        # Nettoyer les valeurs nulles
        clean_data = series.dropna()
        
        if len(clean_data) == 0:
            return {
                'count': 0,
                'null_count': int(series.isna().sum()),
                'null_percentage': round((series.isna().sum() / len(series)) * 100, 2),
                'error': 'Aucune donnée valide'
            }
        
        # Statistiques de base - Convertir en types Python natifs
        stats = {
            'count': int(len(clean_data)),
            'null_count': int(series.isna().sum()),
            'null_percentage': round((series.isna().sum() / len(series)) * 100, 2),
            'min': float(clean_data.min()),
            'max': float(clean_data.max()),
            'mean': float(clean_data.mean()),
            'median': float(clean_data.median()),
            'std': float(clean_data.std()),
            'var': float(clean_data.var()),
            'sum': float(clean_data.sum())
        }
        
        # Quartiles
        stats['q1'] = float(clean_data.quantile(0.25))
        stats['q2'] = stats['median']
        stats['q3'] = float(clean_data.quantile(0.75))
        stats['iqr'] = stats['q3'] - stats['q1']
        
        # Percentiles supplémentaires
        stats['percentile_5'] = float(clean_data.quantile(0.05))
        stats['percentile_95'] = float(clean_data.quantile(0.95))
        stats['percentile_99'] = float(clean_data.quantile(0.99))
        
        # Mesures de forme
        skew_val = clean_data.skew()
        kurt_val = clean_data.kurtosis()
        
        stats['skewness'] = float(skew_val) if not pd.isna(skew_val) else 0.0
        stats['kurtosis'] = float(kurt_val) if not pd.isna(kurt_val) else 0.0
        
        # Interprétation de l'asymétrie
        skew = stats['skewness']
        if skew > 1:
            stats['skewness_interpretation'] = 'forte asymétrie positive (queue à droite)'
        elif skew > 0.5:
            stats['skewness_interpretation'] = 'asymétrie positive modérée'
        elif skew < -1:
            stats['skewness_interpretation'] = 'forte asymétrie négative (queue à gauche)'
        elif skew < -0.5:
            stats['skewness_interpretation'] = 'asymétrie négative modérée'
        else:
            stats['skewness_interpretation'] = 'distribution approximativement symétrique'
        
        # Interprétation de l'aplatissement
        kurt = stats['kurtosis']
        if kurt > 3:
            stats['kurtosis_interpretation'] = 'distribution pointue (queues épaisses)'
        elif kurt < 3:
            stats['kurtosis_interpretation'] = 'distribution aplatie (queues fines)'
        else:
            stats['kurtosis_interpretation'] = 'distribution normale (mésokurtique)'
        
        return stats
    
    @classmethod
    def calculate_all_numeric_stats(cls, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Calcule les statistiques pour toutes les colonnes numériques
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire {colonne: statistiques}
        """
        # Ne sélectionner que les colonnes numériques
        numeric_cols = df.select_dtypes(include=['number']).columns
        results = {}
        
        for col in numeric_cols:
            results[col] = cls.calculate_numeric_stats(df[col])
        
        return results
    
    @classmethod
    def get_summary_table(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Retourne un DataFrame récapitulatif des statistiques
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            DataFrame avec les stats formatées
        """
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            return pd.DataFrame()
        
        summary_data = []
        for col in numeric_cols:
            stats = cls.calculate_numeric_stats(df[col])
            summary_data.append({
                'Colonne': col,
                'Count': stats['count'],
                'Nulls %': stats['null_percentage'],
                'Min': round(stats['min'], 2),
                'Max': round(stats['max'], 2),
                'Mean': round(stats['mean'], 2),
                'Median': round(stats['median'], 2),
                'Std': round(stats['std'], 2),
                'Skewness': round(stats['skewness'], 3),
                'Kurtosis': round(stats['kurtosis'], 3)
            })
        
        return pd.DataFrame(summary_data)


class DescriptiveStats:
    """
    Classe pour des statistiques complètes
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialise l'analyseur statistique
        
        Args:
            df: DataFrame à analyser
        """
        self.df = df
        self.numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    def compute_all(self) -> Dict[str, Any]:
        """
        Calcule toutes les statistiques descriptives
        
        Returns:
            Dictionnaire complet des statistiques
        """
        return {
            'numeric_columns': self.numeric_cols,
            'statistics': StatisticsCalculator.calculate_all_numeric_stats(self.df),
            'summary': self._get_summary(),
            'data_types': self._get_data_type_summary(),
            'shape_info': self._get_shape_info()
        }
    
    def compute_for_column(self, column: str) -> Dict[str, Any]:
        """
        Calcule les statistiques pour une colonne spécifique
        
        Args:
            column: Nom de la colonne
            
        Returns:
            Statistiques de la colonne
        """
        if column not in self.numeric_cols:
            return {
                'error': f'Colonne {column} non numérique ou inexistante',
                'column': column,
                'type': str(self.df[column].dtype) if column in self.df.columns else 'not_found',
                'message': 'Cette colonne contient des données non numériques'
            }
        
        return StatisticsCalculator.calculate_numeric_stats(self.df[column])
    
    def _get_summary(self) -> Dict[str, Any]:
        """Résumé global des statistiques"""
        if not self.numeric_cols:
            return {'message': 'Aucune colonne numérique trouvée'}
        
        describe_df = self.df[self.numeric_cols].describe()
        
        result = {}
        for col in self.numeric_cols:
            if col in describe_df.columns:
                result[col] = {
                    'count': int(describe_df.loc['count', col]),
                    'mean': float(describe_df.loc['mean', col]),
                    'std': float(describe_df.loc['std', col]),
                    'min': float(describe_df.loc['min', col]),
                    '25%': float(describe_df.loc['25%', col]),
                    '50%': float(describe_df.loc['50%', col]),
                    '75%': float(describe_df.loc['75%', col]),
                    'max': float(describe_df.loc['max', col])
                }
            else:
                result[col] = {
                    'count': 0,
                    'mean': 0,
                    'std': 0,
                    'min': 0,
                    '25%': 0,
                    '50%': 0,
                    '75%': 0,
                    'max': 0,
                    'error': 'Données non disponibles'
                }
        
        return result
    
    def _get_data_type_summary(self) -> Dict[str, int]:
        """Résumé des types de données"""
        type_counts = {}
        for dtype in ['int64', 'float64', 'object', 'datetime64', 'category', 'bool']:
            count = len(self.df.select_dtypes(include=[dtype]).columns)
            if count > 0:
                type_counts[dtype] = int(count)
        return type_counts
    
    def _get_shape_info(self) -> Dict[str, int]:
        """Informations sur la forme du dataset"""
        return {
            'rows': int(len(self.df)),
            'columns': int(len(self.df.columns)),
            'numeric_columns': int(len(self.numeric_cols)),
            'non_numeric_columns': int(len(self.df.columns) - len(self.numeric_cols))
        }
    
    def get_fast_stats(self) -> Dict[str, Any]:
        """
        Version rapide des statistiques (utilise pandas describe)
        
        Returns:
            Statistiques de base
        """
        if not self.numeric_cols:
            return {'error': 'Aucune colonne numérique', 'message': 'Le dataset ne contient pas de colonnes numériques'}
        
        description = self.df[self.numeric_cols].describe().to_dict()
        medians = self.df[self.numeric_cols].median().to_dict()
        
        description_clean = {}
        for col, stats_dict in description.items():
            description_clean[col] = {
                key: float(value) if isinstance(value, (np.floating, np.integer)) else value
                for key, value in stats_dict.items()
            }
        
        medians_clean = {
            col: float(val) if isinstance(val, (np.floating, np.integer)) else val
            for col, val in medians.items()
        }
        
        return {
            'description': description_clean,
            'medians': medians_clean,
            'numeric_columns': self.numeric_cols
        }