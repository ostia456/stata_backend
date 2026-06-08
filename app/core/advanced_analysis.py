"""
Analyse avancée des colonnes :
- Variables constantes
- Variables quasi constantes
- Variables à forte cardinalité
- Variables fortement asymétriques
- Colonnes ID inutiles
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


class AdvancedColumnAnalyzer:
    """
    Analyse avancée des colonnes pour détecter les problèmes potentiels
    """
    
    # Seuils de détection
    CONSTANT_THRESHOLD = 1                    # 1 valeur unique = constante
    QUASI_CONSTANT_RATIO = 0.95               # 95% de la même valeur
    HIGH_CARDINALITY_THRESHOLD = 100          # Plus de 100 valeurs uniques
    EXTREME_CARDINALITY_THRESHOLD = 1000      # Plus de 1000 valeurs uniques
    HIGH_SKEWNESS_THRESHOLD = 2               # Asymétrie > 2
    ID_COLUMN_RATIO = 0.95                    # 95% de valeurs uniques
    
    @classmethod
    def analyze_all(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse avancée de toutes les colonnes
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec toutes les analyses
        """
        results = {
            'constant_columns': [],
            'quasi_constant_columns': [],
            'high_cardinality_columns': [],
            'extreme_cardinality_columns': [],
            'highly_skewed_columns': [],
            'id_columns': [],
            'columns_detail': {},
            'summary': {},
            'recommendations': []
        }
        
        for col in df.columns:
            col_analysis = cls._analyze_column(df[col])
            results['columns_detail'][col] = col_analysis
            
            # Catégoriser
            if col_analysis['is_constant']:
                results['constant_columns'].append(col)
            
            if col_analysis['is_quasi_constant']:
                results['quasi_constant_columns'].append(col)
            
            if col_analysis['is_high_cardinality']:
                results['high_cardinality_columns'].append(col)
            
            if col_analysis['is_extreme_cardinality']:
                results['extreme_cardinality_columns'].append(col)
            
            if col_analysis['is_highly_skewed']:
                results['highly_skewed_columns'].append(col)
            
            if col_analysis['is_id_column']:
                results['id_columns'].append(col)
        
        # Générer le résumé et les recommandations
        results['summary'] = cls._generate_summary(results)
        results['recommendations'] = cls._generate_recommendations(results, df)
        
        return results
    
    @classmethod
    def _analyze_column(cls, series: pd.Series) -> Dict[str, Any]:
        """
        Analyse avancée d'une colonne spécifique
        """
        clean_data = series.dropna()
        n_total = len(series)
        n_valid = len(clean_data)
        n_unique = clean_data.nunique()
        unique_ratio = n_unique / n_valid if n_valid > 0 else 0
        
        # Détection constante
        is_constant = n_unique == 1
        is_quasi_constant = (clean_data.value_counts().iloc[0] / n_valid) >= cls.QUASI_CONSTANT_RATIO if n_valid > 0 else False
        
        # Détection cardinalité
        is_high_cardinality = n_unique > cls.HIGH_CARDINALITY_THRESHOLD
        is_extreme_cardinality = n_unique > cls.EXTREME_CARDINALITY_THRESHOLD
        
        # Détection colonne ID (presque toutes les valeurs sont uniques)
        is_id_column = unique_ratio >= cls.ID_COLUMN_RATIO and n_unique > 10
        
        # Détection asymétrie (uniquement pour numériques)
        is_highly_skewed = False
        skewness = None
        if pd.api.types.is_numeric_dtype(series) and n_valid > 0:
            skewness = float(clean_data.skew())
            is_highly_skewed = abs(skewness) > cls.HIGH_SKEWNESS_THRESHOLD
        
        # Valeur dominante
        most_frequent_value = None
        most_frequent_pct = 0
        if n_valid > 0:
            value_counts = clean_data.value_counts()
            most_frequent_value = str(value_counts.index[0])
            most_frequent_pct = (value_counts.iloc[0] / n_valid) * 100
        
        return {
            'name': series.name,
            'dtype': str(series.dtype),
            'total_rows': n_total,
            'valid_rows': n_valid,
            'null_count': n_total - n_valid,
            'null_percentage': round(((n_total - n_valid) / n_total) * 100, 2) if n_total > 0 else 0,
            'unique_count': n_unique,
            'unique_ratio': round(unique_ratio, 4),
            'is_constant': is_constant,
            'is_quasi_constant': is_quasi_constant,
            'is_high_cardinality': is_high_cardinality,
            'is_extreme_cardinality': is_extreme_cardinality,
            'is_id_column': is_id_column,
            'is_highly_skewed': is_highly_skewed,
            'skewness': skewness,
            'most_frequent_value': most_frequent_value,
            'most_frequent_percentage': round(most_frequent_pct, 2),
            'recommendation': cls._get_column_recommendation(
                is_constant, is_quasi_constant, is_high_cardinality, 
                is_extreme_cardinality, is_id_column, is_highly_skewed
            )
        }
    
    @classmethod
    def _get_column_recommendation(cls, is_constant: bool, is_quasi_constant: bool,
                                   is_high_cardinality: bool, is_extreme_cardinality: bool,
                                   is_id_column: bool, is_highly_skewed: bool) -> str:
        """Génère une recommandation pour la colonne"""
        if is_constant:
            return "❌ À supprimer (colonne constante)"
        if is_quasi_constant:
            return "⚠️ Peu informative (valeur dominante >95%)"
        if is_id_column:
            return "ℹ️ Colonne identifiant - à exclure de l'analyse"
        if is_extreme_cardinality:
            return "⚠️ Cardinalité extrême (>1000) - risque de surapprentissage"
        if is_high_cardinality:
            return "⚠️ Haute cardinalité (>100) - encoder avec précaution"
        if is_highly_skewed:
            return "📊 Forte asymétrie - transformation recommandée"
        return "✅ Colonne acceptable pour l'analyse"
    
    @classmethod
    def _generate_summary(cls, results: Dict) -> Dict[str, Any]:
        """Génère un résumé des détections"""
        total_cols = (len(results['constant_columns']) + len(results['quasi_constant_columns']) + 
                      len([c for c in results['columns_detail'] if c not in results['constant_columns'] and 
                           c not in results['quasi_constant_columns']]))
        
        return {
            'total_columns_analyzed': len(results['columns_detail']),
            'problematic_columns_count': (
                len(results['constant_columns']) +
                len(results['quasi_constant_columns']) +
                len(results['extreme_cardinality_columns'])
            ),
            'constant_columns_count': len(results['constant_columns']),
            'quasi_constant_columns_count': len(results['quasi_constant_columns']),
            'high_cardinality_columns_count': len(results['high_cardinality_columns']),
            'extreme_cardinality_columns_count': len(results['extreme_cardinality_columns']),
            'highly_skewed_columns_count': len(results['highly_skewed_columns']),
            'id_columns_count': len(results['id_columns']),
            'data_quality_score': max(0, 100 - (
                len(results['constant_columns']) * 10 +
                len(results['quasi_constant_columns']) * 5 +
                len(results['extreme_cardinality_columns']) * 8 +
                len(results['high_cardinality_columns']) * 3
            ))
        }
    
    @classmethod
    def _generate_recommendations(cls, results: Dict, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Génère des recommandations d'action"""
        recommendations = []
        
        # Colonnes constantes
        for col in results['constant_columns']:
            recommendations.append({
                'column': col,
                'severity': 'high',
                'action': 'supprimer',
                'reason': 'Colonne constante (toutes les valeurs sont identiques)',
                'priority': 1
            })
        
        # Colonnes quasi constantes
        for col in results['quasi_constant_columns']:
            info = results['columns_detail'][col]
            recommendations.append({
                'column': col,
                'severity': 'medium',
                'action': 'évaluer',
                'reason': f"Colonne quasi constante ({info['most_frequent_percentage']:.1f}% de '{info['most_frequent_value']}')",
                'priority': 2
            })
        
        # Colonnes ID
        for col in results['id_columns']:
            info = results['columns_detail'][col]
            recommendations.append({
                'column': col,
                'severity': 'low',
                'action': 'exclure',
                'reason': f"Colonne identifiant ({info['unique_count']} valeurs uniques sur {info['valid_rows']})",
                'priority': 3
            })
        
        # Colonnes à forte cardinalité
        for col in results['extreme_cardinality_columns']:
            info = results['columns_detail'][col]
            recommendations.append({
                'column': col,
                'severity': 'high',
                'action': 'encoder spécialement',
                'reason': f"Cardinalité extrême ({info['unique_count']} valeurs uniques)",
                'priority': 1
            })
        
        for col in results['high_cardinality_columns']:
            if col not in results['extreme_cardinality_columns']:
                info = results['columns_detail'][col]
                recommendations.append({
                    'column': col,
                    'severity': 'medium',
                    'action': 'encoder avec précaution',
                    'reason': f"Haute cardinalité ({info['unique_count']} valeurs uniques)",
                    'priority': 2
                })
        
        # Colonnes asymétriques
        for col in results['highly_skewed_columns']:
            info = results['columns_detail'][col]
            recommendations.append({
                'column': col,
                'severity': 'medium',
                'action': 'transformer',
                'reason': f"Forte asymétrie (skewness={info['skewness']:.2f})",
                'priority': 2
            })
        
        # Trier par priorité
        recommendations.sort(key=lambda x: x['priority'])
        
        return recommendations
    
    @classmethod
    def quick_analysis(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Version rapide de l'analyse avancée
        """
        results = cls.analyze_all(df)
        
        return {
            'has_problematic_columns': results['summary']['problematic_columns_count'] > 0,
            'constant_columns': results['constant_columns'],
            'quasi_constant_columns': results['quasi_constant_columns'],
            'high_cardinality_columns': results['high_cardinality_columns'],
            'id_columns': results['id_columns'],
            'summary': results['summary'],
            'top_recommendations': results['recommendations'][:5]
        }


class AdvancedAnalyzer:
    """
    Analyseur avancé à intégrer dans le service global
    """
    
    @classmethod
    def run_advanced_analysis(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Exécute l'analyse avancée complète
        """
        return AdvancedColumnAnalyzer.analyze_all(df)
    
    @classmethod
    def get_problematic_columns(cls, df: pd.DataFrame) -> List[str]:
        """
        Retourne la liste des colonnes problématiques
        """
        results = AdvancedColumnAnalyzer.analyze_all(df)
        
        problematic = []
        problematic.extend(results['constant_columns'])
        problematic.extend(results['quasi_constant_columns'])
        problematic.extend(results['extreme_cardinality_columns'])
        
        return list(set(problematic))
    
    @classmethod
    def get_clean_columns(cls, df: pd.DataFrame) -> List[str]:
        """
        Retourne la liste des colonnes propres à l'analyse
        """
        problematic = cls.get_problematic_columns(df)
        return [col for col in df.columns if col not in problematic]