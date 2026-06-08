"""
Détection des outliers par les méthodes IQR et Z-score
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


class OutlierDetector:
    """
    Détecteur d'outliers pour les colonnes numériques
    """
    
    # Seuils par défaut
    IQR_MULTIPLIER = 1.5  # Facteur pour IQR (1.5 = outliers modérés, 3 = extrêmes)
    ZSCORE_THRESHOLD = 3   # Seuil Z-score (3 écarts-types)
    
    @classmethod
    def detect_iqr(cls, series: pd.Series, multiplier: float = None) -> Dict[str, Any]:
        """
        Détecte les outliers par la méthode IQR (écart interquartile)
        
        Args:
            series: Série pandas à analyser
            multiplier: Facteur multiplicateur pour IQR (défaut: 1.5)
            
        Returns:
            Dictionnaire avec les résultats de détection
        """
        multiplier = multiplier or cls.IQR_MULTIPLIER
        
        # Nettoyer les valeurs nulles
        clean_data = series.dropna()
        
        if len(clean_data) == 0:
            return {
                'error': 'Aucune donnée valide',
                'method': 'iqr',
                'outlier_count': 0,
                'outlier_percentage': 0
            }
        
        # Calculer les quartiles
        q1 = clean_data.quantile(0.25)
        q3 = clean_data.quantile(0.75)
        iqr = q3 - q1
        
        # Déterminer les bornes
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr
        
        # Identifier les outliers
        outliers = clean_data[(clean_data < lower_bound) | (clean_data > upper_bound)]
        outlier_indices = outliers.index.tolist()
        
        # Statistiques sur les outliers
        outlier_values = outliers.tolist()
        
        return {
            'method': 'iqr',
            'multiplier': multiplier,
            'q1': float(q1),
            'q3': float(q3),
            'iqr': float(iqr),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'outlier_count': int(len(outliers)),
            'outlier_percentage': round((len(outliers) / len(clean_data)) * 100, 2),
            'outlier_indices': outlier_indices[:100],  # Limiter à 100 indices
            'outlier_values': [float(v) for v in outlier_values[:100]],
            'total_valid_values': len(clean_data)
        }
    
    @classmethod
    def detect_zscore(cls, series: pd.Series, threshold: float = None) -> Dict[str, Any]:
        """
        Détecte les outliers par la méthode Z-score
        
        Args:
            series: Série pandas à analyser
            threshold: Seuil Z-score (défaut: 3)
            
        Returns:
            Dictionnaire avec les résultats de détection
        """
        threshold = threshold or cls.ZSCORE_THRESHOLD
        
        # Nettoyer les valeurs nulles
        clean_data = series.dropna()
        
        if len(clean_data) == 0:
            return {
                'error': 'Aucune donnée valide',
                'method': 'zscore',
                'outlier_count': 0,
                'outlier_percentage': 0
            }
        
        # Calculer moyenne et écart-type
        mean = clean_data.mean()
        std = clean_data.std()
        
        if std == 0:
            return {
                'error': 'Écart-type nul, toutes les valeurs sont identiques',
                'method': 'zscore',
                'outlier_count': 0,
                'outlier_percentage': 0,
                'mean': float(mean),
                'std': 0
            }
        
        # Calculer les Z-scores
        z_scores = np.abs((clean_data - mean) / std)
        
        # Identifier les outliers
        outlier_mask = z_scores > threshold
        outliers = clean_data[outlier_mask]
        outlier_indices = outliers.index.tolist()
        
        # Statistiques sur les Z-scores
        max_zscore = float(z_scores.max())
        mean_zscore = float(z_scores.mean())
        
        return {
            'method': 'zscore',
            'threshold': threshold,
            'mean': float(mean),
            'std': float(std),
            'max_zscore': max_zscore,
            'mean_zscore': round(mean_zscore, 3),
            'outlier_count': int(len(outliers)),
            'outlier_percentage': round((len(outliers) / len(clean_data)) * 100, 2),
            'outlier_indices': outlier_indices[:100],
            'outlier_values': [float(v) for v in outliers.tolist()[:100]],
            'total_valid_values': len(clean_data)
        }
    
    @classmethod
    def detect_both(cls, series: pd.Series) -> Dict[str, Any]:
        """
        Détecte les outliers par les deux méthodes (IQR et Z-score)
        
        Args:
            series: Série pandas à analyser
            
        Returns:
            Dictionnaire avec les résultats des deux méthodes
        """
        iqr_result = cls.detect_iqr(series)
        zscore_result = cls.detect_zscore(series)
        
        # Comparer les deux méthodes
        iqr_outliers = set(iqr_result.get('outlier_indices', []))
        zscore_outliers = set(zscore_result.get('outlier_indices', []))
        
        common_outliers = iqr_outliers.intersection(zscore_outliers)
        
        return {
            'column': series.name if hasattr(series, 'name') else 'unknown',
            'iqr': iqr_result,
            'zscore': zscore_result,
            'comparison': {
                'iqr_only_count': len(iqr_outliers - zscore_outliers),
                'zscore_only_count': len(zscore_outliers - iqr_outliers),
                'common_count': len(common_outliers),
                'common_outliers': list(common_outliers)[:50],
                'agreement_rate': round(len(common_outliers) / max(len(iqr_outliers), len(zscore_outliers), 1) * 100, 2)
            }
        }
    
    @classmethod
    def analyze_all_columns(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Détecte les outliers dans toutes les colonnes numériques
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec les résultats par colonne
        """
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            return {
                'error': 'Aucune colonne numérique trouvée',
                'columns': [],
                'results': {}
            }
        
        results = {}
        columns_with_outliers = []
        columns_without_outliers = []
        
        for col in numeric_cols:
            result = cls.detect_both(df[col])
            results[col] = result
            
            # Vérifier s'il y a des outliers
            has_outliers = (
                result['iqr'].get('outlier_count', 0) > 0 or
                result['zscore'].get('outlier_count', 0) > 0
            )
            
            if has_outliers:
                columns_with_outliers.append(col)
            else:
                columns_without_outliers.append(col)
        
        return {
            'columns': list(numeric_cols),
            'results': results,
            'columns_with_outliers': columns_with_outliers,
            'columns_without_outliers': columns_without_outliers,
            'summary': cls._get_summary(results, columns_with_outliers),
            'recommendations': cls._get_recommendations(results)
        }
    
    @classmethod
    def _get_summary(cls, results: Dict, columns_with_outliers: List) -> Dict[str, Any]:
        """
        Génère un résumé des détections d'outliers
        """
        total_cols = len(results)
        
        # Compter les outliers totaux
        total_iqr_outliers = sum(
            r['iqr'].get('outlier_count', 0) for r in results.values()
        )
        total_zscore_outliers = sum(
            r['zscore'].get('outlier_count', 0) for r in results.values()
        )
        
        # Colonne avec le plus d'outliers
        worst_column_iqr = None
        max_iqr_outliers = 0
        
        worst_column_zscore = None
        max_zscore_outliers = 0
        
        for col, result in results.items():
            iqr_count = result['iqr'].get('outlier_count', 0)
            if iqr_count > max_iqr_outliers:
                max_iqr_outliers = iqr_count
                worst_column_iqr = col
            
            zscore_count = result['zscore'].get('outlier_count', 0)
            if zscore_count > max_zscore_outliers:
                max_zscore_outliers = zscore_count
                worst_column_zscore = col
        
        return {
            'total_columns_analyzed': total_cols,
            'columns_with_outliers': len(columns_with_outliers),
            'columns_without_outliers': total_cols - len(columns_with_outliers),
            'total_iqr_outliers': total_iqr_outliers,
            'total_zscore_outliers': total_zscore_outliers,
            'worst_column_iqr': worst_column_iqr,
            'worst_column_iqr_count': max_iqr_outliers,
            'worst_column_zscore': worst_column_zscore,
            'worst_column_zscore_count': max_zscore_outliers
        }
    
    @classmethod
    def _get_recommendations(cls, results: Dict) -> List[Dict[str, Any]]:
        """
        Génère des recommandations basées sur la détection
        """
        recommendations = []
        
        for col, result in results.items():
            iqr_pct = result['iqr'].get('outlier_percentage', 0)
            zscore_pct = result['zscore'].get('outlier_percentage', 0)
            
            # Seuils d'alerte
            if iqr_pct > 10 or zscore_pct > 10:
                severity = 'high'
                action = 'investiguer et traiter'
            elif iqr_pct > 5 or zscore_pct > 5:
                severity = 'medium'
                action = 'envisager un traitement'
            elif iqr_pct > 0 or zscore_pct > 0:
                severity = 'low'
                action = 'surveiller'
            else:
                continue
            
            # Suggestion de traitement
            if result['iqr'].get('outlier_percentage', 0) > 0:
                suggestion = cls._suggest_outlier_treatment(result)
            else:
                suggestion = "Aucun traitement nécessaire"
            
            recommendations.append({
                'column': col,
                'severity': severity,
                'action': action,
                'iqr_outliers_pct': iqr_pct,
                'zscore_outliers_pct': zscore_pct,
                'suggestion': suggestion
            })
        
        # Trier par sévérité
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return recommendations
    
    @classmethod
    def _suggest_outlier_treatment(cls, result: Dict[str, Any]) -> str:
        """
        Suggère un traitement pour les outliers
        """
        suggestions = []
        
        iqr_result = result.get('iqr', {})
        zscore_result = result.get('zscore', {})
        
        iqr_pct = iqr_result.get('outlier_percentage', 0)
        
        if iqr_pct < 5:
            suggestions.append("Conserver les outliers (peu nombreux)")
        elif iqr_pct < 10:
            suggestions.append("Envisager un clipping (bornage) ou une transformation")
        else:
            suggestions.append("Envisager une suppression ou transformation robuste")
        
        # Vérifier si les outliers sont extrêmes
        if iqr_result.get('multiplier') == 1.5 and iqr_pct > 0:
            suggestions.append("Essayer avec multiplier=3.0 pour identifier les outliers extrêmes")
        
        return " | ".join(suggestions)
    
    @classmethod
    def quick_outlier_analysis(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Version rapide de l'analyse d'outliers
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Résumé rapide
        """
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            return {'message': 'Aucune colonne numérique'}
        
        quick_results = {}
        
        for col in numeric_cols:
            clean_data = df[col].dropna()
            if len(clean_data) > 0:
                # IQR rapide
                q1 = clean_data.quantile(0.25)
                q3 = clean_data.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                iqr_outliers = clean_data[(clean_data < lower) | (clean_data > upper)]
                
                quick_results[col] = {
                    'has_outliers': len(iqr_outliers) > 0,
                    'outlier_count': len(iqr_outliers),
                    'outlier_percentage': round((len(iqr_outliers) / len(clean_data)) * 100, 2),
                    'min': float(clean_data.min()),
                    'max': float(clean_data.max())
                }
        
        return {
            'quick_results': quick_results,
            'columns_with_outliers': [col for col, r in quick_results.items() if r['has_outliers']],
            'total_outliers': sum(r['outlier_count'] for r in quick_results.values())
        }


class OutlierTreatment:
    """
    Suggestions de traitement pour les outliers
    """
    
    @classmethod
    def suggest_treatment(cls, series: pd.Series) -> Dict[str, Any]:
        """
        Suggère un traitement approprié pour les outliers
        
        Args:
            series: Série à analyser
            
        Returns:
            Suggestions de traitement
        """
        detection = OutlierDetector.detect_both(series)
        
        iqr_pct = detection['iqr'].get('outlier_percentage', 0)
        zscore_pct = detection['zscore'].get('outlier_percentage', 0)
        
        # Déterminer la meilleure approche
        if iqr_pct == 0 and zscore_pct == 0:
            return {
                'needs_treatment': False,
                'message': 'Aucun outlier détecté'
            }
        
        treatments = []
        
        # 1. Clipping (bornage)
        bounds = detection['iqr']
        treatments.append({
            'method': 'clipping',
            'description': 'Remplacer les outliers par les bornes',
            'code': f"df['{series.name}'] = df['{series.name}'].clip({bounds['lower_bound']:.2f}, {bounds['upper_bound']:.2f})"
        })
        
        # 2. Transformation logarithmique (pour asymétrie positive)
        treatments.append({
            'method': 'log_transform',
            'description': 'Appliquer une transformation logarithmique',
            'code': f"df['{series.name}'] = np.log1p(df['{series.name}'])"
        })
        
        # 3. Suppression
        treatments.append({
            'method': 'remove',
            'description': 'Supprimer les lignes contenant des outliers',
            'code': f"# Identifier les outliers\nq1 = df['{series.name}'].quantile(0.25)\nq3 = df['{series.name}'].quantile(0.75)\niqr = q3 - q1\nlower = q1 - 1.5 * iqr\nupper = q3 + 1.5 * iqr\ndf_clean = df[(df['{series.name}'] >= lower) & (df['{series.name}'] <= upper)]"
        })
        
        return {
            'needs_treatment': True,
            'outlier_percentage': max(iqr_pct, zscore_pct),
            'treatments': treatments,
            'recommended': treatments[0]  # Clipping par défaut
        }