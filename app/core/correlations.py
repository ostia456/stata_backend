"""
Calcul des matrices de corrélation (Pearson et Spearman)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


class CorrelationAnalyzer:
    """
    Analyseur de corrélations entre variables numériques
    """
    
    # Seuil pour considérer une corrélation comme forte
    STRONG_CORRELATION_THRESHOLD = 0.7
    
    @classmethod
    def calculate_pearson(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule la matrice de corrélation de Pearson
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec la matrice et les analyses
        """
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            return {
                'error': 'Au moins 2 colonnes numériques sont nécessaires',
                'matrix': {},
                'strong_correlations': [],
                'columns': list(numeric_cols)
            }
        
        # Calculer la matrice de corrélation
        corr_matrix = df[numeric_cols].corr(method='pearson')
        
        # Analyser les corrélations fortes
        strong_correlations = cls._find_strong_correlations(corr_matrix)
        
        # Convertir en dictionnaire pour sérialisation
        matrix_dict = cls._matrix_to_dict(corr_matrix)
        
        return {
            'method': 'pearson',
            'columns': list(numeric_cols),
            'matrix': matrix_dict,
            'strong_correlations': strong_correlations,
            'summary': cls._get_correlation_summary(corr_matrix, strong_correlations)
        }
    
    @classmethod
    def calculate_spearman(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule la matrice de corrélation de Spearman (basée sur les rangs)
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec la matrice et les analyses
        """
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            return {
                'error': 'Au moins 2 colonnes numériques sont nécessaires',
                'matrix': {},
                'strong_correlations': [],
                'columns': list(numeric_cols)
            }
        
        # Calculer la matrice de corrélation de Spearman
        corr_matrix = df[numeric_cols].corr(method='spearman')
        
        # Analyser les corrélations fortes
        strong_correlations = cls._find_strong_correlations(corr_matrix)
        
        # Convertir en dictionnaire pour sérialisation
        matrix_dict = cls._matrix_to_dict(corr_matrix)
        
        return {
            'method': 'spearman',
            'columns': list(numeric_cols),
            'matrix': matrix_dict,
            'strong_correlations': strong_correlations,
            'summary': cls._get_correlation_summary(corr_matrix, strong_correlations)
        }
    
    @classmethod
    def calculate_both(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule les deux matrices de corrélation (Pearson et Spearman)
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec les deux analyses
        """
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            return {
                'error': 'Au moins 2 colonnes numériques sont nécessaires',
                'pearson': None,
                'spearman': None,
                'numeric_columns': list(numeric_cols)
            }
        
        pearson_result = cls.calculate_pearson(df)
        spearman_result = cls.calculate_spearman(df)
        
        # Comparer les différences entre Pearson et Spearman
        comparison = cls._compare_correlations(
            pearson_result['matrix'],
            spearman_result['matrix']
        )
        
        return {
            'numeric_columns': list(numeric_cols),
            'pearson': pearson_result,
            'spearman': spearman_result,
            'comparison': comparison
        }
    
    @classmethod
    def _find_strong_correlations(cls, corr_matrix: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identifie les paires de variables avec une forte corrélation
        
        Args:
            corr_matrix: Matrice de corrélation pandas
            
        Returns:
            Liste des corrélations fortes
        """
        strong_correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                
                if abs(corr_value) >= cls.STRONG_CORRELATION_THRESHOLD:
                    # Déterminer le type de corrélation
                    if corr_value > 0.9:
                        strength = "très forte"
                    elif corr_value > 0.7:
                        strength = "forte"
                    elif corr_value < -0.9:
                        strength = "très forte négative"
                    elif corr_value < -0.7:
                        strength = "forte négative"
                    else:
                        strength = "modérée"
                    
                    direction = "positive" if corr_value > 0 else "négative"
                    
                    strong_correlations.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': round(corr_value, 3),
                        'strength': strength,
                        'direction': direction,
                        'absolute_value': round(abs(corr_value), 3)
                    })
        
        # Trier par corrélation absolue décroissante
        strong_correlations.sort(key=lambda x: x['absolute_value'], reverse=True)
        
        return strong_correlations
    
    @classmethod
    def _matrix_to_dict(cls, corr_matrix: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Convertit une matrice de corrélation pandas en dictionnaire
        """
        result = {}
        for col in corr_matrix.columns:
            result[col] = {}
            for col2 in corr_matrix.columns:
                result[col][col2] = round(float(corr_matrix.loc[col, col2]), 3)
        return result
    
    @classmethod
    def _get_correlation_summary(cls, corr_matrix: pd.DataFrame, strong_corrs: List) -> Dict[str, Any]:
        """
        Génère un résumé des corrélations
        """
        # Extraire les valeurs de corrélation (sans la diagonale)
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                correlations.append(abs(corr_matrix.iloc[i, j]))
        
        if not correlations:
            return {
                'max_correlation': 0,
                'min_correlation': 0,
                'mean_correlation': 0,
                'num_strong_correlations': 0,
                'num_very_strong_correlations': 0
            }
        
        return {
            'max_correlation': round(max(correlations), 3),
            'min_correlation': round(min(correlations), 3),
            'mean_correlation': round(np.mean(correlations), 3),
            'num_strong_correlations': len(strong_corrs),
            'num_very_strong_correlations': sum(1 for c in strong_corrs if c['absolute_value'] > 0.9)
        }
    
    @classmethod
    def _compare_correlations(cls, pearson_matrix: Dict, spearman_matrix: Dict) -> Dict[str, Any]:
        """
        Compare les corrélations Pearson et Spearman pour détecter les relations non linéaires
        """
        differences = []
        
        for var1 in pearson_matrix:
            for var2 in pearson_matrix[var1]:
                if var1 < var2:  # Éviter les doublons
                    pearson_val = pearson_matrix[var1][var2]
                    spearman_val = spearman_matrix[var1][var2]
                    diff = abs(pearson_val - spearman_val)
                    
                    differences.append({
                        'var1': var1,
                        'var2': var2,
                        'pearson': pearson_val,
                        'spearman': spearman_val,
                        'difference': round(diff, 3)
                    })
        
        # Trier par différence décroissante
        differences.sort(key=lambda x: x['difference'], reverse=True)
        
        # Identifier les relations potentiellement non linéaires
        nonlinear_relations = [
            d for d in differences 
            if d['difference'] > 0.3 and abs(d['pearson']) < 0.7
        ]
        
        return {
            'max_difference': differences[0]['difference'] if differences else 0,
            'mean_difference': round(np.mean([d['difference'] for d in differences]), 3) if differences else 0,
            'potential_nonlinear': nonlinear_relations[:5],  # Top 5
            'all_differences': differences[:10]  # Top 10
        }
    
    @classmethod
    def get_correlation_with_target(cls, df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """
        Calcule les corrélations d'une colonne cible avec toutes les autres
        
        Args:
            df: DataFrame à analyser
            target_column: Nom de la colonne cible
            
        Returns:
            Corrélations avec la cible
        """
        if target_column not in df.columns:
            return {'error': f'Colonne {target_column} non trouvée'}
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if target_column not in numeric_cols:
            return {'error': f'Colonne {target_column} non numérique'}
        
        correlations = []
        
        for col in numeric_cols:
            if col != target_column:
                pearson_corr = df[target_column].corr(df[col], method='pearson')
                spearman_corr = df[target_column].corr(df[col], method='spearman')
                
                correlations.append({
                    'variable': col,
                    'pearson': round(pearson_corr, 3) if not pd.isna(pearson_corr) else 0,
                    'spearman': round(spearman_corr, 3) if not pd.isna(spearman_corr) else 0,
                    'absolute_pearson': round(abs(pearson_corr), 3) if not pd.isna(pearson_corr) else 0
                })
        
        # Trier par corrélation absolue décroissante
        correlations.sort(key=lambda x: x['absolute_pearson'], reverse=True)
        
        return {
            'target': target_column,
            'correlations': correlations,
            'best_predictor': correlations[0]['variable'] if correlations else None,
            'best_correlation': correlations[0]['pearson'] if correlations else 0
        }

    @classmethod
    def quick_correlation(cls, df: pd.DataFrame, method: str = 'pearson') -> Dict[str, Any]:
        """
        Version rapide pour les corrélations
        
        Args:
            df: DataFrame à analyser
            method: 'pearson' ou 'spearman'
        """
        if method == 'spearman':
            return cls.calculate_spearman(df)
        else:
            return cls.calculate_pearson(df)