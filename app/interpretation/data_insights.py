"""
Génération d'insights automatiques en langage naturel
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime


class DataInsightsGenerator:
    """
    Générateur d'insights automatiques sur les données
    """
    
    @classmethod
    def generate_all_insights(cls, df: pd.DataFrame, analysis_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Génère tous les insights pour un dataset
        
        Args:
            df: DataFrame à analyser
            analysis_results: Résultats d'analyses pré-calculées (optionnel)
            
        Returns:
            Dictionnaire avec tous les insights
        """
        insights = {
            'summary': cls._generate_summary(df),
            'missing_insights': cls._missing_insights(df),
            'numeric_insights': cls._numeric_insights(df),
            'categorical_insights': cls._categorical_insights(df),
            'correlation_insights': cls._correlation_insights(df),
            'outlier_insights': cls._outlier_insights(df),
            'quality_insights': cls._quality_insights(df),
            'recommendations': cls._generate_recommendations(df),
            'executive_summary': None  # Sera rempli après
        }
        
        # Générer le résumé exécutif
        insights['executive_summary'] = cls._executive_summary(insights)
        
        return insights
    
    @classmethod
    def _generate_summary(cls, df: pd.DataFrame) -> str:
        """Génère un résumé général du dataset"""
        n_rows = len(df)
        n_cols = len(df.columns)
        n_numeric = len(df.select_dtypes(include=['number']).columns)
        n_categorical = len(df.select_dtypes(include=['object', 'category']).columns)
        
        total_missing = df.isna().sum().sum()
        missing_pct = (total_missing / df.size) * 100
        
        summary = f"Le dataset contient {n_rows} lignes et {n_cols} colonnes. "
        summary += f"Il comprend {n_numeric} colonnes numériques et {n_categorical} colonnes catégorielles. "
        
        if missing_pct > 0:
            summary += f"Le taux de valeurs manquantes est de {missing_pct:.1f}%. "
        else:
            summary += "Aucune valeur manquante n'a été détectée. "
        
        return summary
    
    @classmethod
    def _missing_insights(cls, df: pd.DataFrame) -> List[str]:
        """Génère des insights sur les valeurs manquantes"""
        insights = []
        
        for col in df.columns:
            missing_pct = (df[col].isna().sum() / len(df)) * 100
            if missing_pct > 50:
                insights.append(f" La colonne '{col}' contient {missing_pct:.1f}% de valeurs manquantes. Envisagez de la supprimer.")
            elif missing_pct > 30:
                insights.append(f" La colonne '{col}' a {missing_pct:.1f}% de valeurs manquantes. Une imputation est recommandée.")
            elif missing_pct > 10:
                insights.append(f" La colonne '{col}' présente {missing_pct:.1f}% de valeurs manquantes.")
        
        if not insights:
            insights.append(" Aucune colonne ne présente de valeurs manquantes significatives.")
        
        return insights
    
    @classmethod
    def _numeric_insights(cls, df: pd.DataFrame) -> List[str]:
        """Génère des insights sur les colonnes numériques"""
        insights = []
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            clean_data = df[col].dropna()
            if len(clean_data) == 0:
                continue
            
            skewness = clean_data.skew()
            kurtosis = clean_data.kurtosis()
            
            # Asymétrie
            if skewness > 1:
                insights.append(f" '{col}' a une forte asymétrie positive ({skewness:.2f}) - la majorité des valeurs sont faibles avec quelques valeurs élevées.")
            elif skewness < -1:
                insights.append(f" '{col}' a une forte asymétrie négative ({skewness:.2f}) - la majorité des valeurs sont élevées avec quelques valeurs faibles.")
            elif abs(skewness) > 0.5:
                direction = "positive" if skewness > 0 else "négative"
                insights.append(f" '{col}' présente une légère asymétrie {direction} ({skewness:.2f}).")
            
            # Aplatissement
            if kurtosis > 3:
                insights.append(f" '{col}' a une distribution pointue (kurtosis={kurtosis:.2f}) - présence de valeurs extrêmes.")
            elif kurtosis < -1:
                insights.append(f" '{col}' a une distribution aplatie - les valeurs sont plus dispersées que la normale.")
        
        if not insights:
            insights.append(" Toutes les colonnes numériques ont des distributions relativement symétriques.")
        
        return insights[:5]  # Limiter à 5 insights
    
    @classmethod
    def _categorical_insights(cls, df: pd.DataFrame) -> List[str]:
        """Génère des insights sur les colonnes catégorielles"""
        insights = []
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            unique_count = df[col].nunique()
            total_count = len(df)
            
            if unique_count == 1:
                insights.append(f" La colonne '{col}' a une seule valeur unique - elle n'apporte pas d'information.")
            elif unique_count == 2:
                # Variable binaire - compter les proportions
                value_counts = df[col].value_counts(normalize=True)
                most_frequent = value_counts.index[0]
                percentage = value_counts.iloc[0] * 100
                insights.append(f" '{col}' est binaire: {most_frequent} représente {percentage:.1f}% des valeurs.")
            elif unique_count < 10:
                insights.append(f" '{col}' a {unique_count} catégories différentes - bonne variable catégorielle.")
            elif unique_count > 50:
                insights.append(f" '{col}' a {unique_count} valeurs uniques - pourrait être un identifiant ou une variable texte.")
        
        return insights[:5]
    
    @classmethod
    def _correlation_insights(cls, df: pd.DataFrame) -> List[str]:
        """Génère des insights sur les corrélations"""
        insights = []
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            return [" Pas assez de colonnes numériques pour analyser les corrélations."]
        
        # Matrice de corrélation
        corr_matrix = df[numeric_cols].corr()
        
        # Trouver les corrélations fortes
        strong_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_corrs.append({
                        'col1': corr_matrix.columns[i],
                        'col2': corr_matrix.columns[j],
                        'value': corr_value
                    })
        
        for corr in strong_corrs[:5]:
            direction = "positive" if corr['value'] > 0 else "négative"
            strength = "très forte" if abs(corr['value']) > 0.9 else "forte"
            insights.append(f" Corrélation {strength} {direction} entre '{corr['col1']}' et '{corr['col2']}' (r={corr['value']:.2f})")
        
        # Identifier la meilleure corrélation avec la cible potentielle
        # Chercher une colonne "target" probable (Survived, target, etc.)
        target_keywords = ['survived', 'target', 'label', 'class', 'y']
        target_col = None
        for col in numeric_cols:
            if col.lower() in target_keywords:
                target_col = col
                break
        
        if target_col:
            correlations_with_target = []
            for col in numeric_cols:
                if col != target_col:
                    corr = abs(corr_matrix.loc[target_col, col])
                    correlations_with_target.append((col, corr))
            correlations_with_target.sort(key=lambda x: x[1], reverse=True)
            
            if correlations_with_target:
                best, best_corr = correlations_with_target[0]
                if best_corr > 0.3:
                    insights.append(f" La meilleure corrélation avec '{target_col}' est '{best}' (r={best_corr:.2f})")
        
        if not strong_corrs and not insights:
            insights.append(" Aucune corrélation forte détectée entre les variables numériques.")
        
        return insights
    
    @classmethod
    def _outlier_insights(cls, df: pd.DataFrame) -> List[str]:
        """Génère des insights sur les outliers"""
        insights = []
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            clean_data = df[col].dropna()
            if len(clean_data) == 0:
                continue
            
            # Détection IQR
            q1 = clean_data.quantile(0.25)
            q3 = clean_data.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            
            outliers = clean_data[(clean_data < lower) | (clean_data > upper)]
            outlier_pct = (len(outliers) / len(clean_data)) * 100
            
            if outlier_pct > 10:
                insights.append(f" '{col}' contient {outlier_pct:.1f}% d'outliers - valeurs extrêmes à vérifier.")
            elif outlier_pct > 5:
                insights.append(f"  '{col}' a {outlier_pct:.1f}% d'outliers.")
        
        if not insights:
            insights.append(" Aucune colonne ne présente d'outliers significatifs.")
        
        return insights
    
    @classmethod
    def _quality_insights(cls, df: pd.DataFrame) -> List[str]:
        """Génère des insights sur la qualité des données"""
        from ..core.data_quality import DataQualityScorer
        
        quality = DataQualityScorer.calculate_score(df)
        
        insights = []
        insights.append(f" Score de qualité global: {quality['total_score']}/100 (Grade {quality['grade']})")
        
        if quality['total_score'] >= 90:
            insights.append(" Les données sont de très bonne qualité et prêtes pour l'analyse.")
        elif quality['total_score'] >= 70:
            insights.append(" Les données sont de bonne qualité. Quelques nettoyages mineurs sont recommandés.")
        elif quality['total_score'] >= 50:
            insights.append(" La qualité des données est moyenne. Un nettoyage modéré est nécessaire.")
        else:
            insights.append(" La qualité des données est médiocre. Un nettoyage important est requis.")
        
        return insights
    
    @classmethod
    def _generate_recommendations(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Génère des recommandations d'action"""
        recommendations = []
        
        # Recommandations sur les valeurs manquantes
        for col in df.columns:
            missing_pct = (df[col].isna().sum() / len(df)) * 100
            if missing_pct > 50:
                recommendations.append({
                    'priority': 'high',
                    'category': 'missing_values',
                    'action': f"Supprimer la colonne '{col}'",
                    'reason': f"{missing_pct:.1f}% de valeurs manquantes"
                })
            elif missing_pct > 30:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'missing_values',
                    'action': f"Imputer les valeurs manquantes de '{col}'",
                    'reason': f"{missing_pct:.1f}% de valeurs manquantes"
                })
        
        # Recommandations sur les colonnes constantes
        for col in df.columns:
            if df[col].nunique() == 1:
                recommendations.append({
                    'priority': 'high',
                    'category': 'constant_column',
                    'action': f"Supprimer la colonne '{col}'",
                    'reason': "Valeur constante sur toutes les lignes"
                })
        
        # Recommandations sur les identifiants
        for col in df.columns:
            if df[col].nunique() == len(df):
                recommendations.append({
                    'priority': 'low',
                    'category': 'identifier',
                    'action': f"Considérer '{col}' comme identifiant",
                    'reason': "Valeurs uniques sur chaque ligne"
                })
        
        return recommendations
    
    @classmethod
    def _executive_summary(cls, insights: Dict[str, Any]) -> str:
        """
        Génère un résumé exécutif en langage naturel
        """
        summary_parts = []
        
        # Ajouter le résumé général
        summary_parts.append(insights['summary'])
        
        # Ajouter les points les plus importants
        if insights['missing_insights']:
            summary_parts.append(insights['missing_insights'][0])
        
        if insights['quality_insights']:
            summary_parts.append(insights['quality_insights'][0])
        
        if insights['correlation_insights']:
            summary_parts.append(insights['correlation_insights'][0])
        
        # Ajouter une recommandation principale
        if insights['recommendations']:
            high_priority = [r for r in insights['recommendations'] if r['priority'] == 'high']
            if high_priority:
                summary_parts.append(f"Action prioritaire: {high_priority[0]['action']}")
        
        return " ".join(summary_parts)


class SimpleInsightsGenerator:
    """
    Version simplifiée pour des insights rapides
    """
    
    @classmethod
    def quick_insights(cls, df: pd.DataFrame) -> List[str]:
        """
        Génère une liste rapide d'insights
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Liste d'insights textuels
        """
        insights = []
        
        # Taille du dataset
        insights.append(f" {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Valeurs manquantes
        total_missing = df.isna().sum().sum()
        if total_missing > 0:
            insights.append(f" {total_missing} cellules manquantes")
        
        # Doublons
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            insights.append(f" {duplicates} lignes dupliquées")
        
        # Colonnes numériques
        numeric_count = len(df.select_dtypes(include=['number']).columns)
        insights.append(f" {numeric_count} colonnes numériques")
        
        # Colonnes catégorielles
        categorical_count = len(df.select_dtypes(include=['object', 'category']).columns)
        insights.append(f" {categorical_count} colonnes catégorielles")
        
        return insights