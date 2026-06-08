"""
Analyse avancée des colonnes catégorielles
- Value counts
- Mode (valeur la plus fréquente)
- Entropie (désordre)
- Fréquences
- Équilibre des classes
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from collections import Counter


class CategoricalAnalyzer:
    """
    Analyseur de colonnes catégorielles
    """
    
    @classmethod
    def analyze(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse toutes les colonnes catégorielles
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec toutes les analyses
        """
        categorical_cols = cls._get_categorical_columns(df)
        
        if not categorical_cols:
            return {
                'has_categorical': False,
                'columns': [],
                'analysis': {},
                'summary': {'message': 'Aucune colonne catégorielle trouvée'}
            }
        
        results = {}
        for col in categorical_cols:
            results[col] = cls._analyze_column(df[col])
        
        return {
            'has_categorical': True,
            'columns': categorical_cols,
            'analysis': results,
            'summary': cls._generate_summary(results),
            'insights': cls._generate_insights(results)
        }
    
    @classmethod
    def _get_categorical_columns(cls, df: pd.DataFrame) -> List[str]:
        """
        Identifie les colonnes catégorielles
        """
        categorical = []
        
        for col in df.columns:
            # Types object ou category
            if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                categorical.append(col)
            # Types booléens
            elif df[col].dtype == 'bool':
                categorical.append(col)
            # Colonnes numériques avec peu de valeurs uniques (catégorielles implicites)
            elif pd.api.types.is_numeric_dtype(df[col]) and df[col].nunique() <= 10:
                categorical.append(col)
        
        return categorical
    
    @classmethod
    def _analyze_column(cls, series: pd.Series) -> Dict[str, Any]:
        """
        Analyse détaillée d'une colonne catégorielle
        """
        clean_data = series.dropna()
        n_total = len(series)
        n_valid = len(clean_data)
        n_unique = clean_data.nunique()
        
        # Value counts
        value_counts = clean_data.value_counts()
        
        # Mode (valeur la plus fréquente)
        mode_value = value_counts.index[0] if len(value_counts) > 0 else None
        mode_count = value_counts.iloc[0] if len(value_counts) > 0 else 0
        mode_percentage = (mode_count / n_valid) * 100 if n_valid > 0 else 0
        
        # Deuxième valeur la plus fréquente
        second_mode_value = value_counts.index[1] if len(value_counts) > 1 else None
        second_mode_count = value_counts.iloc[1] if len(value_counts) > 1 else 0
        second_mode_percentage = (second_mode_count / n_valid) * 100 if n_valid > 0 else 0
        
        # Distribution complète (top 5)
        distribution = []
        for i, (value, count) in enumerate(value_counts.head(10).items()):
            distribution.append({
                'value': str(value),
                'count': int(count),
                'percentage': round((count / n_valid) * 100, 2)
            })
        
        # Entropie (mesure de désordre)
        entropy = cls._calculate_entropy(value_counts, n_valid)
        max_entropy = np.log2(n_unique) if n_unique > 0 else 0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Équilibre des classes
        balance_ratio = (value_counts.min() / value_counts.max()) if len(value_counts) > 1 else 1
        is_balanced = balance_ratio > 0.5
        
        # Détection de classe majoritaire écrasante
        is_dominant = mode_percentage > 80
        
        return {
            'name': series.name,
            'dtype': str(series.dtype),
            'total_rows': n_total,
            'valid_rows': n_valid,
            'null_count': n_total - n_valid,
            'null_percentage': round(((n_total - n_valid) / n_total) * 100, 2) if n_total > 0 else 0,
            'unique_count': n_unique,
            'mode': {
                'value': str(mode_value) if mode_value is not None else None,
                'count': mode_count,
                'percentage': round(mode_percentage, 2)
            },
            'second_mode': {
                'value': str(second_mode_value) if second_mode_value is not None else None,
                'count': second_mode_count,
                'percentage': round(second_mode_percentage, 2)
            } if second_mode_value else None,
            'distribution': distribution,
            'entropy': round(entropy, 4),
            'normalized_entropy': round(normalized_entropy, 4),
            'balance_ratio': round(balance_ratio, 4),
            'is_balanced': is_balanced,
            'is_dominant': is_dominant,
            'recommendation': cls._get_recommendation(
                n_unique, mode_percentage, is_balanced, is_dominant
            )
        }
    
    @classmethod
    def _calculate_entropy(cls, value_counts: pd.Series, total: int) -> float:
        """
        Calcule l'entropie de Shannon
        """
        if total == 0:
            return 0
        
        probabilities = value_counts / total
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        return entropy
    
    @classmethod
    def _get_recommendation(cls, n_unique: int, mode_percentage: float, 
                            is_balanced: bool, is_dominant: bool) -> str:
        """
        Génère une recommandation pour la colonne
        """
        if is_dominant:
            return "⚠️ Classe très majoritaire (>80%) - peut être peu informative"
        if is_balanced and 2 <= n_unique <= 10:
            return "✅ Excellente variable catégorielle (classes équilibrées)"
        if n_unique == 2:
            return "✅ Variable binaire - idéale pour classification"
        if n_unique <= 10:
            return "✅ Bonne variable catégorielle (peu de classes)"
        if n_unique <= 50:
            return "ℹ️ Variable catégorielle avec modérément de classes"
        return "⚠️ Beaucoup de classes - encoder avec précaution"
    
    @classmethod
    def _generate_summary(cls, results: Dict) -> Dict[str, Any]:
        """
        Génère un résumé global
        """
        binary_cols = []
        balanced_cols = []
        dominant_cols = []
        
        for col, analysis in results.items():
            if analysis['unique_count'] == 2:
                binary_cols.append(col)
            if analysis['is_balanced']:
                balanced_cols.append(col)
            if analysis['is_dominant']:
                dominant_cols.append(col)
        
        return {
            'total_categorical_columns': len(results),
            'binary_columns': binary_cols,
            'binary_count': len(binary_cols),
            'balanced_columns': balanced_cols,
            'balanced_count': len(balanced_cols),
            'dominant_columns': dominant_cols,
            'dominant_count': len(dominant_cols)
        }
    
    @classmethod
    def _generate_insights(cls, results: Dict) -> List[str]:
        """
        Génère des insights textuels
        """
        insights = []
        
        for col, analysis in results.items():
            if analysis['unique_count'] == 2:
                mode = analysis['mode']
                other_pct = 100 - mode['percentage']
                insights.append(
                    f"🏷️ '{col}' est binaire : {mode['value']} ({mode['percentage']:.1f}%) / "
                    f"autre ({other_pct:.1f}%)"
                )
            elif analysis['is_dominant']:
                mode = analysis['mode']
                insights.append(
                    f"⚠️ '{col}' est dominé par '{mode['value']}' ({mode['percentage']:.1f}%)"
                )
            elif analysis['is_balanced']:
                insights.append(
                    f"✅ '{col}' a des classes bien équilibrées ({analysis['unique_count']} catégories)"
                )
        
        return insights[:10]
    
    @classmethod
    def quick_analysis(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Version rapide de l'analyse catégorielle
        """
        results = cls.analyze(df)
        
        return {
            'has_categorical': results['has_categorical'],
            'categorical_columns_count': len(results.get('columns', [])),
            'summary': results.get('summary', {}),
            'top_insights': results.get('insights', [])[:5]
        }
    
    @classmethod
    def get_categorical_summary_table(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Retourne un DataFrame récapitulatif pour les colonnes catégorielles
        """
        results = cls.analyze(df)
        
        if not results['has_categorical']:
            return pd.DataFrame()
        
        summary_data = []
        for col, analysis in results['analysis'].items():
            summary_data.append({
                'Colonne': col,
                'Valeurs uniques': analysis['unique_count'],
                'Mode': analysis['mode']['value'],
                'Fréquence mode': f"{analysis['mode']['percentage']:.1f}%",
                'Entropie': analysis['entropy'],
                'Équilibrée': '✅' if analysis['is_balanced'] else '❌'
            })
        
        return pd.DataFrame(summary_data)