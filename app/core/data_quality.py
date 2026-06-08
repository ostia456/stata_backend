"""
Analyse de la qualité des données et calcul du score global
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


class DataQualityScorer:
    """
    Calculateur de score de qualité des données
    """
    
    # Pondérations des différents critères
    WEIGHTS = {
        'completeness': 0.35,      # Valeurs manquantes
        'integrity': 0.25,         # Doublons, cohérence
        'consistency': 0.20,       # Types de données, formats
        'accuracy': 0.20           # Outliers, valeurs extrêmes
    }
    
    @classmethod
    def calculate_score(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule le score global de qualité des données
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec le score et les détails
        """
        # Calculer chaque composante
        completeness_score = cls._completeness_score(df)
        integrity_score = cls._integrity_score(df)
        consistency_score = cls._consistency_score(df)
        accuracy_score = cls._accuracy_score(df)
        
        # Score pondéré
        total_score = (
            completeness_score * cls.WEIGHTS['completeness'] +
            integrity_score * cls.WEIGHTS['integrity'] +
            consistency_score * cls.WEIGHTS['consistency'] +
            accuracy_score * cls.WEIGHTS['accuracy']
        )
        
        total_score = round(total_score, 2)
        
        # Grade (A, B, C, D, F)
        grade = cls._get_grade(total_score)
        
        return {
            'total_score': total_score,
            'grade': grade,
            'components': {
                'completeness': {
                    'score': completeness_score,
                    'weight': cls.WEIGHTS['completeness'],
                    'weighted_score': round(completeness_score * cls.WEIGHTS['completeness'], 2),
                    'description': 'Valeurs manquantes'
                },
                'integrity': {
                    'score': integrity_score,
                    'weight': cls.WEIGHTS['integrity'],
                    'weighted_score': round(integrity_score * cls.WEIGHTS['integrity'], 2),
                    'description': 'Doublons et cohérence'
                },
                'consistency': {
                    'score': consistency_score,
                    'weight': cls.WEIGHTS['consistency'],
                    'weighted_score': round(consistency_score * cls.WEIGHTS['consistency'], 2),
                    'description': 'Types de données'
                },
                'accuracy': {
                    'score': accuracy_score,
                    'weight': cls.WEIGHTS['accuracy'],
                    'weighted_score': round(accuracy_score * cls.WEIGHTS['accuracy'], 2),
                    'description': 'Outliers et valeurs extrêmes'
                }
            },
            'interpretation': cls._get_interpretation(total_score, grade),
            'recommendations': cls._get_recommendations(
                completeness_score, integrity_score, 
                consistency_score, accuracy_score
            )
        }
    
    @classmethod
    def _completeness_score(cls, df: pd.DataFrame) -> float:
        """
        Score de complétude basé sur les valeurs manquantes
        """
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        missing_percentage = (missing_cells / total_cells) * 100
        
        # Plus il y a de manquants, plus le score est bas
        # 0% manquants = 100 points, 50% manquants = 0 points
        score = max(0, 100 - missing_percentage * 2)
        
        return round(score, 2)
    
    @classmethod
    def _integrity_score(cls, df: pd.DataFrame) -> float:
        """
        Score d'intégrité basé sur les doublons
        """
        # Doublons complets
        duplicate_rows = df.duplicated().sum()
        duplicate_percentage = (duplicate_rows / len(df)) * 100
        
        # Pénalité pour doublons (max -30 points)
        duplicate_penalty = min(30, duplicate_percentage * 2)
        
        # Vérifier les colonnes identifiants potentielles
        id_columns_penalty = 0
        for col in df.columns:
            # Si une colonne a toutes ses valeurs uniques, c'est probablement un ID
            if df[col].nunique() == len(df):
                id_columns_penalty += 5
        
        score = 100 - duplicate_penalty - min(20, id_columns_penalty)
        
        return round(max(0, score), 2)
    
    @classmethod
    def _consistency_score(cls, df: pd.DataFrame) -> float:
        """
        Score de consistance basé sur les types de données
        """
        penalty = 0
        
        for col in df.columns:
            # Vérifier les colonnes qui devraient être numériques mais sont en texte
            if df[col].dtype == 'object':
                # Tester si la colonne peut être convertie en numérique
                try:
                    numeric_test = pd.to_numeric(df[col], errors='coerce')
                    if numeric_test.notna().sum() > len(df) * 0.8:
                        penalty += 5
                except:
                    pass
                
                # Vérifier les dates stockées comme texte
                try:
                    date_test = pd.to_datetime(df[col], errors='coerce')
                    if date_test.notna().sum() > len(df) * 0.8:
                        penalty += 5
                except:
                    pass
            
            # Vérifier les colonnes avec trop de valeurs uniques pour être catégorielles
            if df[col].nunique() > 100 and df[col].dtype == 'object':
                penalty += 2
        
        score = max(0, 100 - min(40, penalty))
        
        return round(score, 2)
    
    @classmethod
    def _accuracy_score(cls, df: pd.DataFrame) -> float:
        """
        Score de précision basé sur les outliers
        """
        from .outliers import OutlierDetector
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            return 100.0
        
        total_outlier_penalty = 0
        total_values = 0
        
        for col in numeric_cols:
            clean_data = df[col].dropna()
            if len(clean_data) > 0:
                # Utiliser IQR pour détecter les outliers
                q1 = clean_data.quantile(0.25)
                q3 = clean_data.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                
                outliers = clean_data[(clean_data < lower) | (clean_data > upper)]
                outlier_pct = (len(outliers) / len(clean_data)) * 100
                
                # Pénalité proportionnelle au pourcentage d'outliers
                total_outlier_penalty += outlier_pct
                total_values += 1
        
        if total_values > 0:
            avg_outlier_pct = total_outlier_penalty / total_values
            # 0% outliers = 100 points, 50% outliers = 0 points
            score = max(0, 100 - avg_outlier_pct * 2)
        else:
            score = 100
        
        return round(score, 2)
    
    @classmethod
    def _get_grade(cls, score: float) -> str:
        """
        Détermine le grade en fonction du score
        """
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    @classmethod
    def _get_interpretation(cls, score: float, grade: str) -> str:
        """
        Interprétation du score de qualité
        """
        if grade == 'A':
            return "Qualité excellente - Les données sont prêtes pour l'analyse"
        elif grade == 'B':
            return "Bonne qualité - Quelques problèmes mineurs à corriger"
        elif grade == 'C':
            return "Qualité moyenne - Un nettoyage modéré est recommandé"
        elif grade == 'D':
            return "Qualité faible - Un nettoyage important est nécessaire"
        else:
            return "Qualité médiocre - Les données nécessitent un nettoyage majeur"
    
    @classmethod
    def _get_recommendations(cls, completeness: float, integrity: float, 
                             consistency: float, accuracy: float) -> List[Dict[str, Any]]:
        """
        Génère des recommandations basées sur les sous-scores
        """
        recommendations = []
        
        if completeness < 80:
            recommendations.append({
                'component': 'completeness',
                'issue': 'Trop de valeurs manquantes',
                'action': 'Imputer les valeurs manquantes ou supprimer les colonnes/lignes concernées',
                'priority': 'high' if completeness < 60 else 'medium'
            })
        
        if integrity < 80:
            recommendations.append({
                'component': 'integrity',
                'issue': 'Présence de doublons ou colonnes identifiantes',
                'action': 'Supprimer les lignes dupliquées et les colonnes identifiantes',
                'priority': 'high' if integrity < 60 else 'medium'
            })
        
        if consistency < 80:
            recommendations.append({
                'component': 'consistency',
                'issue': 'Types de données incohérents',
                'action': 'Convertir les colonnes vers les types appropriés',
                'priority': 'medium'
            })
        
        if accuracy < 80:
            recommendations.append({
                'component': 'accuracy',
                'issue': 'Présence d\'outliers ou valeurs extrêmes',
                'action': 'Appliquer un clipping, une transformation ou supprimer les outliers',
                'priority': 'high' if accuracy < 60 else 'medium'
            })
        
        return recommendations
    
    @classmethod
    def detailed_quality_report(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Rapport détaillé de qualité des données
        """
        from .missing_values import MissingValueAnalyzer
        
        # Score global
        quality_score = cls.calculate_score(df)
        
        # Analyse des doublons
        duplicates = df.duplicated()
        
        # Identification des problèmes par colonne
        column_issues = {}
        for col in df.columns:
            issues = []
            
            # Valeurs manquantes
            missing_pct = (df[col].isna().sum() / len(df)) * 100
            if missing_pct > 10:
                issues.append(f"{missing_pct:.1f}% valeurs manquantes")
            
            # Type inapproprié
            if df[col].dtype == 'object':
                try:
                    pd.to_numeric(df[col])
                    issues.append("Devrait être numérique")
                except:
                    pass
            
            # Valeurs constantes
            if df[col].nunique() == 1:
                issues.append("Valeur constante")
            
            # Trop de valeurs uniques
            if df[col].nunique() > 1000:
                issues.append(f"{df[col].nunique()} valeurs uniques (cantine)")
            
            if issues:
                column_issues[col] = issues
        
        return {
            'quality_score': quality_score,
            'duplicates': {
                'count': int(duplicates.sum()),
                'percentage': round((duplicates.sum() / len(df)) * 100, 2)
            },
            'column_issues': column_issues,
            'columns_with_issues': len(column_issues),
            'summary': {
                'total_issues': sum(len(issues) for issues in column_issues.values()),
                'most_problematic_column': max(column_issues.items(), key=lambda x: len(x[1]))[0] if column_issues else None
            }
        }


class QualityReportGenerator:
    """
    Générateur de rapport de qualité
    """
    
    @classmethod
    def generate(cls, df: pd.DataFrame, file_id: str = None) -> Dict[str, Any]:
        """
        Génère un rapport complet de qualité des données
        """
        quality_score = DataQualityScorer.calculate_score(df)
        detailed_report = DataQualityScorer.detailed_quality_report(df)
        
        return {
            'file_id': file_id,
            'quality_score': quality_score,
            'detailed_report': detailed_report,
            'passing': quality_score['total_score'] >= 70,
            'summary': cls._get_summary_text(quality_score, detailed_report)
        }
    
    @classmethod
    def _get_summary_text(cls, quality_score: Dict, detailed_report: Dict) -> str:
        """
        Génère un texte de résumé
        """
        score = quality_score['total_score']
        grade = quality_score['grade']
        
        text = f"Score de qualité: {score}/100 (Grade {grade}). "
        
        if detailed_report['duplicates']['count'] > 0:
            text += f"{detailed_report['duplicates']['count']} lignes dupliquées. "
        
        if detailed_report['columns_with_issues'] > 0:
            text += f"{detailed_report['columns_with_issues']} colonnes ont des problèmes."
        
        return text