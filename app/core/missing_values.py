"""
Analyse des valeurs manquantes dans le dataset
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class MissingValueAnalyzer:
    """
    Analyseur de valeurs manquantes
    """
    
    # Seuils d'alerte
    THRESHOLD_WARNING = 10    # 10% - alerte modérée
    THRESHOLD_HIGH = 30       # 30% - alerte élevée
    THRESHOLD_CRITICAL = 50   # 50% - alerte critique
    
    @classmethod
    def analyze(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse complète des valeurs manquantes
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec toutes les infos sur les valeurs manquantes
        """
        total_cells = df.size
        total_missing = df.isna().sum().sum()
        total_missing_pct = (total_missing / total_cells) * 100
        
        # Analyse par colonne
        columns_analysis = cls._analyze_columns(df)
        
        # Identification des colonnes problématiques
        high_missing_cols = [
            col for col, info in columns_analysis.items()
            if info['missing_percentage'] >= cls.THRESHOLD_HIGH
        ]
        
        critical_missing_cols = [
            col for col, info in columns_analysis.items()
            if info['missing_percentage'] >= cls.THRESHOLD_CRITICAL
        ]
        
        # Matrice des corrélations entre valeurs manquantes
        missing_correlation = cls._missing_correlation_matrix(df)
        
        return {
            'summary': {
                'total_cells': total_cells,
                'total_missing': int(total_missing),
                'total_missing_percentage': round(total_missing_pct, 2),
                'columns_with_missing': int((df.isna().sum() > 0).sum()),
                'columns_without_missing': int((df.isna().sum() == 0).sum()),
                'rows_with_missing': int(df.isna().any(axis=1).sum()),
                'rows_without_missing': int((~df.isna().any(axis=1)).sum()),
                'rows_missing_percentage': round((df.isna().any(axis=1).sum() / len(df)) * 100, 2)
            },
            'columns': columns_analysis,
            'high_missing_columns': high_missing_cols,
            'critical_missing_columns': critical_missing_cols,
            'missing_correlation': missing_correlation,
            'recommendations': cls._generate_recommendations(columns_analysis)
        }
    
    @classmethod
    def _analyze_columns(cls, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyse détaillée par colonne
        """
        n_rows = len(df)
        results = {}
        
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_pct = (missing_count / n_rows) * 100
            
            # Détection du type de valeurs manquantes
            missing_pattern = cls._detect_missing_pattern(df[col])
            
            # Suggestion d'imputation
            imputation_suggestion = cls._suggest_imputation(df[col])
            
            # Impact potentiel
            impact = cls._estimate_impact(missing_pct, df[col].dtype)
            
            results[col] = {
                'name': col,
                'dtype': str(df[col].dtype),
                'total_rows': n_rows,
                'missing_count': int(missing_count),
                'present_count': int(n_rows - missing_count),
                'missing_percentage': round(missing_pct, 2),
                'present_percentage': round(100 - missing_pct, 2),
                'missing_pattern': missing_pattern,
                'imputation_suggestion': imputation_suggestion,
                'impact': impact,
                'severity': cls._get_severity(missing_pct)
            }
        
        return results
    
    @classmethod
    def _detect_missing_pattern(cls, series: pd.Series) -> str:
        """
        Détecte le motif des valeurs manquantes
        """
        missing_mask = series.isna()
        
        if missing_mask.sum() == 0:
            return "no_missing"
        
        # Convertir en indices numériques pour éviter les problèmes d'Index
        missing_indices = missing_mask[missing_mask].index.to_numpy()
        
        # Vérifier si les manquants sont à la fin (en prenant un échantillon)
        if len(missing_indices) > 0:
            last_idx = len(series) - 1
            if missing_indices[-1] > last_idx - missing_mask.sum():
                return "tail_missing"
        
        # Vérifier si les manquants sont au début
        if len(missing_indices) > 0 and missing_indices[0] < missing_mask.sum():
            return "head_missing"
        
        # Par défaut
        return "random_missing"
    
    @classmethod
    def _suggest_imputation(cls, series: pd.Series) -> Dict[str, Any]:
        """
        Suggère une méthode d'imputation basée sur le type et la distribution
        """
        missing_pct = (series.isna().sum() / len(series)) * 100
        
        # Trop de manquants, suggérer suppression
        if missing_pct > 50:
            return {
                'method': 'drop_column',
                'description': 'Plus de 50% de valeurs manquantes, envisagez de supprimer la colonne'
            }
        
        # Colonne numérique
        if pd.api.types.is_numeric_dtype(series):
            clean_data = series.dropna()
            if len(clean_data) > 0:
                try:
                    skewness = clean_data.skew()
                    
                    # Distribution symétrique -> moyenne
                    if abs(skewness) < 1:
                        return {
                            'method': 'mean',
                            'value': float(clean_data.mean()),
                            'description': 'Distribution symétrique, imputation par la moyenne'
                        }
                    # Distribution asymétrique -> médiane
                    else:
                        return {
                            'method': 'median',
                            'value': float(clean_data.median()),
                            'description': 'Distribution asymétrique, imputation par la médiane'
                        }
                except Exception:
                    return {
                        'method': 'median',
                        'value': float(clean_data.median()),
                        'description': 'Imputation par la médiane'
                    }
            else:
                return {
                    'method': 'constant',
                    'value': 0,
                    'description': 'Colonne vide, imputation par 0'
                }
        
        # Colonne catégorielle/texte
        else:
            mode_value = series.mode()
            if len(mode_value) > 0:
                # Convertir en string pour éviter les problèmes de sérialisation
                value = str(mode_value[0]) if mode_value[0] is not None else 'unknown'
                return {
                    'method': 'mode',
                    'value': value,
                    'description': 'Imputation par la valeur la plus fréquente (mode)'
                }
            else:
                return {
                    'method': 'constant',
                    'value': 'unknown',
                    'description': 'Imputation par "unknown"'
                }
    
    @classmethod
    def _estimate_impact(cls, missing_pct: float, dtype) -> str:
        """
        Estime l'impact des valeurs manquantes sur l'analyse
        """
        if missing_pct == 0:
            return "none"
        elif missing_pct < 5:
            return "very_low"
        elif missing_pct < 10:
            return "low"
        elif missing_pct < 30:
            return "medium"
        elif missing_pct < 50:
            return "high"
        else:
            return "critical"
    
    @classmethod
    def _get_severity(cls, missing_pct: float) -> str:
        """
        Retourne le niveau de sévérité
        """
        if missing_pct == 0:
            return "none"
        elif missing_pct < cls.THRESHOLD_WARNING:
            return "low"
        elif missing_pct < cls.THRESHOLD_HIGH:
            return "medium"
        elif missing_pct < cls.THRESHOLD_CRITICAL:
            return "high"
        else:
            return "critical"
    
    @classmethod
    def _missing_correlation_matrix(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule les corrélations entre les motifs de valeurs manquantes
        """
        # Créer une matrice binaire des valeurs manquantes
        missing_matrix = df.isna().astype(int)
        
        if missing_matrix.shape[1] <= 1:
            return {'message': 'Pas assez de colonnes pour calculer les corrélations'}
        
        try:
            # Calculer la matrice de corrélation
            corr_matrix = missing_matrix.corr()
            
            # Trouver les paires fortement corrélées (>0.7)
            strong_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_pairs.append({
                            'col1': corr_matrix.columns[i],
                            'col2': corr_matrix.columns[j],
                            'correlation': round(corr_value, 3),
                            'interpretation': 'positif' if corr_value > 0 else 'négatif'
                        })
            
            # Convertir en dict pour sérialisation
            matrix_dict = {}
            for col in corr_matrix.columns:
                matrix_dict[col] = {}
                for col2 in corr_matrix.columns:
                    matrix_dict[col][col2] = float(corr_matrix.loc[col, col2])
            
            return {
                'matrix': matrix_dict,
                'strong_correlations': strong_pairs
            }
        except Exception:
            return {'message': 'Erreur lors du calcul des corrélations'}
    
    @classmethod
    def _generate_recommendations(cls, columns_analysis: Dict) -> List[Dict[str, Any]]:
        """
        Génère des recommandations basées sur l'analyse
        """
        recommendations = []
        
        for col, info in columns_analysis.items():
            if info['severity'] == 'critical':
                recommendations.append({
                    'column': col,
                    'severity': 'critical',
                    'action': 'supprimer la colonne',
                    'reason': f"{info['missing_percentage']}% de valeurs manquantes",
                    'details': info['imputation_suggestion']
                })
            elif info['severity'] == 'high':
                recommendations.append({
                    'column': col,
                    'severity': 'high',
                    'action': 'imputer ou supprimer',
                    'reason': f"{info['missing_percentage']}% de valeurs manquantes",
                    'details': info['imputation_suggestion']
                })
            elif info['severity'] == 'medium':
                recommendations.append({
                    'column': col,
                    'severity': 'medium',
                    'action': 'imputer',
                    'reason': f"{info['missing_percentage']}% de valeurs manquantes",
                    'details': info['imputation_suggestion']
                })
        
        # Recommendation globale
        total_missing_cols = len([info for info in columns_analysis.values() if info['missing_count'] > 0])
        if total_missing_cols > 0:
            recommendations.insert(0, {
                'column': 'global',
                'severity': 'info',
                'action': 'nettoyer',
                'reason': f"{total_missing_cols} colonnes ont des valeurs manquantes",
                'details': {
                    'method': 'multiple',
                    'description': 'Traiter les valeurs manquantes avant l\'analyse'
                }
            })
        
        return recommendations
    
    @classmethod
    def get_missing_summary(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Retourne un DataFrame récapitulatif pour un affichage rapide
        """
        missing_count = df.isna().sum()
        missing_pct = (missing_count / len(df)) * 100
        
        summary_df = pd.DataFrame({
            'Colonne': df.columns,
            'Valeurs manquantes': missing_count.values,
            'Pourcentage': missing_pct.values.round(2),
            'Type': df.dtypes.values
        })
        
        # Trier par nombre de manquants décroissant
        summary_df = summary_df.sort_values('Valeurs manquantes', ascending=False)
        
        return summary_df
    
    @classmethod
    def quick_analysis(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Version rapide pour un aperçu des valeurs manquantes
        """
        return {
            'total_missing': int(df.isna().sum().sum()),
            'total_missing_percentage': round((df.isna().sum().sum() / df.size) * 100, 2),
            'columns_with_missing': int((df.isna().sum() > 0).sum()),
            'rows_with_missing': int(df.isna().any(axis=1).sum()),
            'worst_column': cls._get_worst_column(df),
            'columns_summary': {
                col: {
                    'missing_count': int(df[col].isna().sum()),
                    'missing_percentage': round((df[col].isna().sum() / len(df)) * 100, 2)
                }
                for col in df.columns if df[col].isna().sum() > 0
            }
        }
    
    @classmethod
    def _get_worst_column(cls, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Identifie la colonne avec le plus de valeurs manquantes
        """
        missing_counts = df.isna().sum()
        if missing_counts.sum() == 0:
            return None
        
        max_col = missing_counts.idxmax()
        max_count = missing_counts[max_col]
        
        return {
            'column': max_col,
            'missing_count': int(max_count),
            'missing_percentage': round((max_count / len(df)) * 100, 2)
        }