"""
Détection automatique du type de problème Machine Learning
et identification de la colonne cible potentielle
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


class MLProblemDetector:
    """
    Détecteur automatique du type de problème ML et de la colonne cible
    """
    
    # Mots-clés pour identifier la colonne cible
    TARGET_KEYWORDS = [
        'target', 'label', 'class', 'y', 'survived', 
        'price', 'value', 'score', 'rating', 'grade',
        'SalePrice', 'median_value', 'diagnosis'
    ]
    
    # Types de problèmes ML
    PROBLEM_TYPES = {
        'binary_classification': 'Classification binaire',
        'multi_class_classification': 'Classification multi-classe',
        'regression': 'Régression',
        'clustering': 'Clustering (non supervisé)',
        'unknown': 'Non déterminé'
    }
    
    @classmethod
    def detect(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Détecte le type de problème ML et la colonne cible
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec les résultats
        """
        # Identifier la colonne cible potentielle
        target_column, confidence = cls._find_target_column(df)
        
        if target_column:
            target_analysis = cls._analyze_target(df[target_column])
            problem_type = cls._determine_problem_type(df, target_column, target_analysis)
        else:
            target_analysis = None
            problem_type = cls._determine_problem_type(df, None, None)
        
        # Évaluer la qualité des features
        feature_quality = cls._analyze_features(df, target_column)
        
        # Suggestions de modèles
        model_suggestions = cls._suggest_models(problem_type.get('type', 'unknown'))
        
        return {
            'target_column': target_column,
            'target_confidence': confidence,
            'target_analysis': target_analysis,
            'problem_type': problem_type,
            'feature_analysis': feature_quality,
            'model_suggestions': model_suggestions,
            'ready_for_ml': cls._is_ready_for_ml(df, target_column, problem_type),
            'recommendations': cls._generate_recommendations(df, target_column, problem_type)
        }
    
    @classmethod
    def _find_target_column(cls, df: pd.DataFrame) -> Tuple[Optional[str], float]:
        """
        Trouve la colonne cible potentielle avec un score de confiance
        
        Returns:
            Tuple (nom_colonne, confidence_score)
        """
        scores = {}
        
        for col in df.columns:
            score = 0.0
            col_lower = col.lower()
            
            # 1. Par mots-clés (poids fort)
            for keyword in cls.TARGET_KEYWORDS:
                if keyword.lower() in col_lower:
                    score += 0.7
                    break
            
            # 2. Colonne binaire (classification)
            if df[col].nunique() == 2:
                score += 0.5
            
            # 3. Colonne avec peu de valeurs (3-20 classes)
            elif 2 < df[col].nunique() <= 20:
                score += 0.3
            
            # 4. Colonne numérique continue (régression)
            elif pd.api.types.is_numeric_dtype(df[col]) and df[col].nunique() > 20:
                score += 0.2
            
            # 5. Nombre de valeurs manquantes faible
            missing_pct = (df[col].isna().sum() / len(df)) * 100
            if missing_pct < 5:
                score += 0.1
            
            # 6. Position (souvent la dernière colonne est la cible)
            if col == df.columns[-1]:
                score += 0.1
            
            scores[col] = score
        
        if not scores:
            return None, 0.0
        
        best_col = max(scores, key=scores.get)
        best_score = scores[best_col]
        
        # Seuil minimum de confiance (0.3)
        if best_score < 0.3:
            return None, best_score
        
        return best_col, round(best_score, 2)
    
    @classmethod
    def _analyze_target(cls, series: pd.Series) -> Dict[str, Any]:
        """
        Analyse détaillée de la colonne cible
        """
        clean_data = series.dropna()
        unique_count = clean_data.nunique()
        
        result = {
            'name': series.name,
            'dtype': str(series.dtype),
            'unique_count': unique_count,
            'null_count': series.isna().sum(),
            'null_percentage': round((series.isna().sum() / len(series)) * 100, 2)
        }
        
        # Pour les valeurs numériques
        if pd.api.types.is_numeric_dtype(series) and len(clean_data) > 0:
            result['min'] = float(clean_data.min())
            result['max'] = float(clean_data.max())
            result['mean'] = float(clean_data.mean())
            result['median'] = float(clean_data.median())
            result['std'] = float(clean_data.std())
        
        # Distribution des valeurs
        value_counts = clean_data.value_counts()
        result['top_values'] = [
            {'value': str(v), 'count': int(c), 'percentage': round((c / len(clean_data)) * 100, 2)}
            for v, c in value_counts.head(5).items()
        ]
        
        # Déséquilibre des classes
        if unique_count <= 20:
            max_pct = max([v['percentage'] for v in result['top_values']])
            min_pct = min([v['percentage'] for v in result['top_values']])
            result['imbalance_ratio'] = round(min_pct / max_pct, 3) if max_pct > 0 else 0
            result['is_balanced'] = result['imbalance_ratio'] > 0.5
        
        return result
    
    @classmethod
    def _determine_problem_type(cls, df: pd.DataFrame, target_col: Optional[str],
                                target_analysis: Optional[Dict]) -> Dict[str, Any]:
        """
        Détermine le type de problème ML
        """
        if not target_col or not target_analysis:
            # Clustering potentiel
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) >= 2:
                return {
                    'type': 'clustering',
                    'message': 'Problème de clustering potentiel (non supervisé)',
                    'confidence': 'medium',
                    'suggestion': 'Utiliser K-Means, DBSCAN ou Hierarchical Clustering'
                }
            else:
                return {
                    'type': 'unknown',
                    'message': 'Type de problème non déterminé automatiquement',
                    'confidence': 'low',
                    'suggestion': 'Spécifier manuellement la colonne cible'
                }
        
        unique_count = target_analysis.get('unique_count', 0)
        
        # Classification binaire
        if unique_count == 2:
            return {
                'type': 'binary_classification',
                'message': 'Problème de classification binaire',
                'confidence': 'high',
                'target': target_col,
                'classes': [v['value'] for v in target_analysis.get('top_values', [])],
                'is_balanced': target_analysis.get('is_balanced', False)
            }
        
        # Classification multi-classe
        if 2 < unique_count <= 20:
            return {
                'type': 'multi_class_classification',
                'message': f'Problème de classification multi-classe ({unique_count} classes)',
                'confidence': 'high',
                'target': target_col,
                'num_classes': unique_count,
                'is_balanced': target_analysis.get('is_balanced', False)
            }
        
        # Régression
        if pd.api.types.is_numeric_dtype(df[target_col]):
            return {
                'type': 'regression',
                'message': 'Problème de régression (cible numérique continue)',
                'confidence': 'high',
                'target': target_col,
                'range': [target_analysis.get('min', 0), target_analysis.get('max', 0)]
            }
        
        return {
            'type': 'unknown',
            'message': 'Type de problème non déterminé',
            'confidence': 'low',
            'target': target_col
        }
    
    @classmethod
    def _analyze_features(cls, df: pd.DataFrame, target_col: Optional[str]) -> Dict[str, Any]:
        """
        Analyse la qualité des features pour le ML
        """
        # Exclure la cible
        features = df.drop(columns=[target_col]) if target_col and target_col in df.columns else df
        
        numeric_features = features.select_dtypes(include=['number']).columns
        categorical_features = features.select_dtypes(include=['object', 'category']).columns
        
        return {
            'total_features': len(features.columns),
            'numeric_features_count': len(numeric_features),
            'categorical_features_count': len(categorical_features),
            'numeric_features': list(numeric_features)[:10],
            'categorical_features': list(categorical_features)[:10],
            'has_missing': features.isna().any().any(),
            'missing_features_count': features.columns[features.isna().any()].shape[0]
        }
    
    @classmethod
    def _suggest_models(cls, problem_type: str) -> List[str]:
        """
        Suggère des modèles selon le type de problème
        """
        suggestions = {
            'binary_classification': [
                'Logistic Regression (baseline)',
                'Random Forest Classifier',
                'XGBoost Classifier',
                'LightGBM Classifier',
                'Support Vector Machine (SVM)'
            ],
            'multi_class_classification': [
                'Random Forest Classifier',
                'XGBoost Classifier',
                'K-Nearest Neighbors (KNN)',
                'Neural Network (MLP)'
            ],
            'regression': [
                'Linear Regression (baseline)',
                'Random Forest Regressor',
                'XGBoost Regressor',
                'LightGBM Regressor',
                'Ridge/Lasso Regression'
            ],
            'clustering': [
                'K-Means Clustering',
                'DBSCAN',
                'Hierarchical Clustering',
                'Gaussian Mixture Models (GMM)'
            ],
            'unknown': [
                'Explorer les données avec AutoML',
                'Consulter un expert métier',
                'Utiliser des techniques non supervisées'
            ]
        }
        
        return suggestions.get(problem_type, suggestions['unknown'])
    
    @classmethod
    def _is_ready_for_ml(cls, df: pd.DataFrame, target_col: Optional[str],
                         problem_type: Dict) -> Dict[str, Any]:
        """
        Vérifie si les données sont prêtes pour le ML
        """
        issues = []
        
        if not target_col:
            issues.append("Aucune colonne cible identifiée")
        
        if target_col:
            # Vérifier les valeurs manquantes dans la cible
            missing_target = df[target_col].isna().sum()
            if missing_target > 0:
                issues.append(f"La colonne cible '{target_col}' a {missing_target} valeurs manquantes")
        
        # Vérifier les colonnes non-numériques
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if target_col and target_col in categorical_cols:
            categorical_cols = categorical_cols.drop(target_col)
        if len(categorical_cols) > 0:
            issues.append(f"{len(categorical_cols)} colonnes catégorielles à encoder")
        
        return {
            'ready': len(issues) == 0,
            'issues': issues,
            'ready_level': 'high' if len(issues) == 0 else 'medium' if len(issues) <= 3 else 'low'
        }
    
    @classmethod
    def _generate_recommendations(cls, df: pd.DataFrame, target_col: Optional[str],
                                   problem_type: Dict) -> List[Dict[str, Any]]:
        """
        Génère des recommandations pour le ML
        """
        recommendations = []
        
        if target_col:
            recommendations.append({
                'priority': 1,
                'action': f"Utiliser '{target_col}' comme variable cible",
                'reason': f"Détecté automatiquement (confiance: {problem_type.get('confidence', 'medium')})"
            })
        
        # Recommandations sur les valeurs manquantes
        missing_cols = df.columns[df.isna().any()].tolist()
        for col in missing_cols[:3]:
            if col != target_col:
                recommendations.append({
                    'priority': 2,
                    'action': f"Imputer les valeurs manquantes de '{col}'",
                    'reason': f"{df[col].isna().sum()} valeurs manquantes"
                })
        
        # Recommandations sur l'encodage
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols[:3]:
            if col != target_col:
                if df[col].nunique() <= 10:
                    recommendations.append({
                        'priority': 2,
                        'action': f"Encoder '{col}' en One-Hot Encoding",
                        'reason': f"{df[col].nunique()} catégories"
                    })
                else:
                    recommendations.append({
                        'priority': 3,
                        'action': f"Encoder '{col}' avec LabelEncoder ou TargetEncoder",
                        'reason': f"Haute cardinalité ({df[col].nunique()} catégories)"
                    })
        
        # Recommandations sur la standardisation
        numeric_cols = df.select_dtypes(include=['number']).columns
        if target_col and target_col in numeric_cols:
            numeric_cols = numeric_cols.drop(target_col)
        if len(numeric_cols) > 0:
            recommendations.append({
                'priority': 3,
                'action': "Standardiser les variables numériques",
                'reason': f"{len(numeric_cols)} colonnes numériques"
            })
        
        # Trier par priorité
        recommendations.sort(key=lambda x: x['priority'])
        
        return recommendations