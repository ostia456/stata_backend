"""
Tests de normalité (Shapiro-Wilk) pour les colonnes numériques
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Optional
from collections import OrderedDict


class NormalityTester:
    """
    Testeur de normalité pour les colonnes numériques
    """
    
    # Seuil de significativité
    ALPHA = 0.05
    
    @classmethod
    def shapiro_test(cls, series: pd.Series, max_samples: int = 5000) -> Dict[str, Any]:
        """
        Applique le test de Shapiro-Wilk à une colonne
        
        Args:
            series: Série pandas à tester
            max_samples: Nombre max d'échantillons (Shapiro est limité à 5000)
            
        Returns:
            Dictionnaire avec les résultats du test
        """
        # Nettoyer les valeurs nulles
        clean_data = series.dropna()
        
        if len(clean_data) < 3:
            return {
                'error': 'Nombre insuffisant de valeurs (minimum 3)',
                'sample_size': len(clean_data),
                'is_normal': None,
                'p_value': None,
                'test_statistic': None
            }
        
        # Shapiro-Wilk est limité à 5000 échantillons
        if len(clean_data) > max_samples:
            # Prendre un échantillon aléatoire
            clean_data = clean_data.sample(n=max_samples, random_state=42)
        
        try:
            # Appliquer le test de Shapiro-Wilk
            statistic, p_value = stats.shapiro(clean_data)
            
            is_normal = p_value > cls.ALPHA
            
            # Interprétation
            if is_normal:
                interpretation = "Distribution normale (p-value > 0.05)"
                recommendation = "Aucune transformation nécessaire"
            else:
                interpretation = "Distribution non normale (p-value ≤ 0.05)"
                recommendation = cls._suggest_transformation(clean_data)
            
            return {
                'test_statistic': round(float(statistic), 4),
                'p_value': round(float(p_value), 6),
                'is_normal': bool(is_normal),
                'sample_size': int(len(clean_data)),
                'original_size': int(series.dropna().shape[0]),
                'interpretation': interpretation,
                'recommendation': recommendation
            }
            
        except Exception as e:
            return {
                'error': f'Erreur lors du test: {str(e)}',
                'is_normal': None,
                'p_value': None,
                'test_statistic': None
            }
    
    @classmethod
    def _suggest_transformation(cls, series: pd.Series) -> str:
        """
        Suggère une transformation pour normaliser la distribution
        """
        skewness = series.skew()
        kurtosis = series.kurtosis()
        
        suggestions = []
        
        # Asymétrie positive (queue à droite)
        if skewness > 1:
            suggestions.append("Transformation logarithmique (log) ou racine carrée (sqrt)")
        # Asymétrie négative (queue à gauche)
        elif skewness < -1:
            suggestions.append("Transformation exponentielle ou carrée")
        
        # Aplatissement (queues épaisses)
        if kurtosis > 3:
            suggestions.append("Transformation de Box-Cox")
        
        if not suggestions:
            suggestions.append("Standardisation (z-score) pour centrer et réduire")
        
        return suggestions[0]
    
    @classmethod
    def test_all_columns(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Applique le test de normalité à toutes les colonnes numériques
        
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
                'summary': {}
            }
        
        results = {}
        normal_columns = []
        non_normal_columns = []
        
        for col in numeric_cols:
            result = cls.shapiro_test(df[col])
            results[col] = result
            
            if result.get('is_normal') is True:
                normal_columns.append(col)
            elif result.get('is_normal') is False:
                non_normal_columns.append(col)
        
        return {
            'columns': list(numeric_cols),
            'results': results,
            'normal_columns': normal_columns,
            'non_normal_columns': non_normal_columns,
            'summary': cls._get_summary(normal_columns, non_normal_columns, results),
            'recommendations': cls._get_recommendations(results)
        }
    
    @classmethod
    def _get_summary(cls, normal_cols: List, non_normal_cols: List, results: Dict) -> Dict[str, Any]:
        """
        Génère un résumé des résultats
        """
        total = len(normal_cols) + len(non_normal_cols)
        
        if total == 0:
            return {'message': 'Aucune colonne testée'}
        
        # Trouver la colonne la plus normale (p-value la plus élevée)
        most_normal = None
        highest_p = -1
        
        # Trouver la colonne la moins normale (p-value la plus faible)
        least_normal = None
        lowest_p = 2
        
        for col, result in results.items():
            p_val = result.get('p_value')
            if p_val is not None:
                if p_val > highest_p:
                    highest_p = p_val
                    most_normal = col
                if p_val < lowest_p:
                    lowest_p = p_val
                    least_normal = col
        
        return {
            'total_columns_tested': total,
            'normal_columns_count': len(normal_cols),
            'non_normal_columns_count': len(non_normal_cols),
            'normal_percentage': round((len(normal_cols) / total) * 100, 1),
            'non_normal_percentage': round((len(non_normal_cols) / total) * 100, 1),
            'most_normal_column': most_normal,
            'most_normal_p_value': round(highest_p, 6) if most_normal else None,
            'least_normal_column': least_normal,
            'least_normal_p_value': round(lowest_p, 6) if least_normal else None
        }
    
    @classmethod
    def _get_recommendations(cls, results: Dict) -> List[Dict[str, Any]]:
        """
        Génère des recommandations basées sur les résultats
        """
        recommendations = []
        
        for col, result in results.items():
            if result.get('is_normal') is False and result.get('recommendation'):
                recommendations.append({
                    'column': col,
                    'issue': 'Distribution non normale',
                    'p_value': result.get('p_value'),
                    'recommendation': result.get('recommendation'),
                    'priority': 'high' if result.get('p_value', 1) < 0.01 else 'medium'
                })
        
        # Trier par p-value croissante (problèmes les plus graves d'abord)
        recommendations.sort(key=lambda x: x.get('p_value', 1))
        
        return recommendations
    
    @classmethod
    def test_single_column(cls, df: pd.DataFrame, column_name: str) -> Dict[str, Any]:
        """
        Teste une colonne spécifique
        
        Args:
            df: DataFrame à analyser
            column_name: Nom de la colonne
            
        Returns:
            Résultats du test
        """
        if column_name not in df.columns:
            return {'error': f'Colonne {column_name} non trouvée'}
        
        if not pd.api.types.is_numeric_dtype(df[column_name]):
            return {
                'error': f'Colonne {column_name} non numérique',
                'column': column_name,
                'dtype': str(df[column_name].dtype)
            }
        
        result = cls.shapiro_test(df[column_name])
        result['column'] = column_name
        
        # Ajouter des statistiques de distribution
        clean_data = df[column_name].dropna()
        if len(clean_data) > 0:
            result['distribution_stats'] = {
                'skewness': round(float(clean_data.skew()), 3),
                'kurtosis': round(float(clean_data.kurtosis()), 3),
                'mean': round(float(clean_data.mean()), 3),
                'median': round(float(clean_data.median()), 3)
            }
        
        return result
    
    @classmethod
    def quick_test(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Version rapide du test de normalité
        
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
            if len(clean_data) >= 3:
                # Version simplifiée avec échantillon réduit
                sample = clean_data if len(clean_data) <= 1000 else clean_data.sample(n=1000, random_state=42)
                try:
                    _, p_value = stats.shapiro(sample)
                    quick_results[col] = {
                        'is_normal': p_value > cls.ALPHA,
                        'p_value': round(float(p_value), 4)
                    }
                except:
                    quick_results[col] = {'error': 'Test impossible'}
            else:
                quick_results[col] = {'error': 'Échantillon trop petit'}
        
        return {
            'quick_results': quick_results,
            'normal_count': sum(1 for r in quick_results.values() if r.get('is_normal') is True),
            'non_normal_count': sum(1 for r in quick_results.values() if r.get('is_normal') is False)
        }


class NormalityVisualizer:
    """
    Préparation des données pour visualisation de la normalité
    """
    
    @classmethod
    def get_qq_data(cls, series: pd.Series, max_points: int = 1000) -> Dict[str, List]:
        """
        Prépare les données pour un Q-Q plot
        
        Args:
            series: Série à analyser
            max_points: Nombre max de points
            
        Returns:
            Dictionnaire avec les quantiles théoriques et observés
        """
        clean_data = series.dropna()
        
        if len(clean_data) < 3:
            return {'error': 'Données insuffisantes'}
        
        # Échantillonner si nécessaire
        if len(clean_data) > max_points:
            clean_data = clean_data.sample(n=max_points, random_state=42)
        
        # Trier les données
        sorted_data = np.sort(clean_data)
        
        # Calculer les quantiles théoriques (distribution normale)
        n = len(sorted_data)
        theoretical_quantiles = stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n)
        
        return {
            'theoretical': theoretical_quantiles.tolist(),
            'observed': sorted_data.tolist(),
            'sample_size': n
        }
    
    @classmethod
    def get_distribution_data(cls, series: pd.Series, bins: int = 30) -> Dict[str, Any]:
        """
        Prépare les données pour un histogramme avec courbe de densité normale
        
        Args:
            series: Série à analyser
            bins: Nombre de bins pour l'histogramme
            
        Returns:
            Données pour visualisation
        """
        clean_data = series.dropna()
        
        if len(clean_data) < 3:
            return {'error': 'Données insuffisantes'}
        
        # Histogramme
        hist_counts, hist_bins = np.histogram(clean_data, bins=bins, density=True)
        bin_centers = (hist_bins[:-1] + hist_bins[1:]) / 2
        
        # Courbe de densité normale théorique
        mean = clean_data.mean()
        std = clean_data.std()
        x_normal = np.linspace(clean_data.min(), clean_data.max(), 100)
        y_normal = stats.norm.pdf(x_normal, mean, std)
        
        # Densité empirique (KDE)
        try:
            from scipy.stats import gaussian_kde
            kde = gaussian_kde(clean_data)
            y_kde = kde(x_normal)
        except:
            y_kde = None
        
        return {
            'histogram': {
                'counts': hist_counts.tolist(),
                'bin_edges': hist_bins.tolist(),
                'bin_centers': bin_centers.tolist()
            },
            'normal_curve': {
                'x': x_normal.tolist(),
                'y': y_normal.tolist()
            },
            'kde_curve': {
                'x': x_normal.tolist(),
                'y': y_kde.tolist() if y_kde is not None else None
            },
            'stats': {
                'mean': float(mean),
                'std': float(std),
                'skewness': float(clean_data.skew()),
                'kurtosis': float(clean_data.kurtosis())
            },
            'sample_size': len(clean_data)
        }