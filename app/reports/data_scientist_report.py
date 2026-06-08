"""
Génération d'un rapport Data Scientist avec recommandations de prétraitement ML
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..core.ml_detector import MLProblemDetector
from ..core.advanced_analysis import AdvancedColumnAnalyzer
from ..core.categorical_analysis import CategoricalAnalyzer
from ..core.statistics import DescriptiveStats
from ..core.missing_values import MissingValueAnalyzer


class DataScientistReportGenerator:
    """
    Générateur de rapport spécialisé pour Data Scientist
    Recommandations de prétraitement avant Machine Learning
    """
    
    @classmethod
    def generate(cls, df: pd.DataFrame, file_id: str = None) -> Dict[str, Any]:
        """
        Génère un rapport complet pour Data Scientist
        
        Args:
            df: DataFrame à analyser
            file_id: Identifiant du fichier
            
        Returns:
            Rapport Data Scientist
        """
        # Détection ML
        ml_detection = MLProblemDetector.detect(df)
        
        # Analyse avancée
        advanced_analysis = AdvancedColumnAnalyzer.analyze_all(df)
        
        # Analyse catégorielle
        categorical_analysis = CategoricalAnalyzer.analyze(df)
        
        # Préparation recommandée
        preprocessing_steps = cls._generate_preprocessing_steps(df, ml_detection)
        
        # Pipeline ML recommandé
        ml_pipeline = cls._generate_ml_pipeline(df, ml_detection)
        
        # Features importantes potentielles
        important_features = cls._identify_important_features(df, ml_detection)
        
        return {
            'file_id': file_id,
            'generated_at': datetime.now().isoformat(),
            'ml_detection': ml_detection,
            'data_quality_assessment': cls._assess_data_quality(df, advanced_analysis),
            'preprocessing_steps': preprocessing_steps,
            'ml_pipeline': ml_pipeline,
            'important_features': important_features,
            'potential_issues': cls._identify_potential_issues(df, advanced_analysis),
            'readiness_score': cls._calculate_readiness_score(df, ml_detection),
            'summary': cls._generate_summary(ml_detection, preprocessing_steps)
        }
    
    @classmethod
    def _generate_preprocessing_steps(cls, df: pd.DataFrame, ml_detection: Dict) -> List[Dict[str, Any]]:
        """
        Génère les étapes de prétraitement recommandées
        """
        steps = []
        step_num = 1
        
        target_col = ml_detection.get('target_column')
        
        # 1. Gestion des valeurs manquantes
        missing_cols = df.columns[df.isna().any()].tolist()
        if missing_cols:
            for col in missing_cols[:5]:
                if col == target_col:
                    steps.append({
                        'step': step_num,
                        'action': 'Supprimer les lignes avec valeurs manquantes',
                        'column': col,
                        'method': 'dropna()',
                        'code': f"df = df.dropna(subset=['{col}'])",
                        'priority': 'high'
                    })
                else:
                    missing_pct = (df[col].isna().sum() / len(df)) * 100
                    if missing_pct < 5:
                        method = "Supprimer les lignes"
                        code = f"df = df.dropna(subset=['{col}'])"
                    elif missing_pct < 30:
                        method = "Imputer par la médiane/moyenne/mode"
                        if pd.api.types.is_numeric_dtype(df[col]):
                            code = f"df['{col}'] = df['{col}'].fillna(df['{col}'].median())"
                        else:
                            code = f"df['{col}'] = df['{col}'].fillna(df['{col}'].mode()[0])"
                    else:
                        method = "Supprimer la colonne"
                        code = f"df = df.drop(columns=['{col}'])"
                    
                    steps.append({
                        'step': step_num,
                        'action': 'Gérer les valeurs manquantes',
                        'column': col,
                        'method': method,
                        'code': code,
                        'priority': 'high' if missing_pct > 30 else 'medium'
                    })
            step_num += 1
        
        # 2. Encodage des variables catégorielles
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if target_col and target_col in categorical_cols:
            categorical_cols = [c for c in categorical_cols if c != target_col]
        
        for col in categorical_cols[:5]:
            n_unique = df[col].nunique()
            if n_unique <= 10:
                method = "One-Hot Encoding"
                code = f"df = pd.get_dummies(df, columns=['{col}'], drop_first=True)"
            else:
                method = "Label Encoding ou Target Encoding"
                code = f"from sklearn.preprocessing import LabelEncoder\nle = LabelEncoder()\ndf['{col}'] = le.fit_transform(df['{col}'])"
            
            steps.append({
                'step': step_num,
                'action': 'Encoder les variables catégorielles',
                'column': col,
                'method': method,
                'code': code,
                'priority': 'high' if n_unique <= 10 else 'medium'
            })
            step_num += 1
        
        # 3. Standardisation des variables numériques
        numeric_cols = df.select_dtypes(include=['number']).columns
        if target_col and target_col in numeric_cols:
            numeric_cols = [c for c in numeric_cols if c != target_col]
        
        if len(numeric_cols) > 0:
            steps.append({
                'step': step_num,
                'action': 'Standardiser les variables numériques',
                'column': 'Toutes les colonnes numériques',
                'method': 'StandardScaler',
                'code': "from sklearn.preprocessing import StandardScaler\nscaler = StandardScaler()\ndf[numeric_cols] = scaler.fit_transform(df[numeric_cols])",
                'priority': 'medium'
            })
            step_num += 1
        
        # 4. Suppression des colonnes problématiques
        constant_cols = []
        for col in df.columns:
            if df[col].nunique() == 1:
                constant_cols.append(col)
        
        for col in constant_cols:
            steps.append({
                'step': step_num,
                'action': 'Supprimer les colonnes constantes',
                'column': col,
                'method': 'drop()',
                'code': f"df = df.drop(columns=['{col}'])",
                'priority': 'high'
            })
            step_num += 1
        
        # 5. Gestion des outliers
        for col in numeric_cols:
            clean_data = df[col].dropna()
            if len(clean_data) > 0:
                q1 = clean_data.quantile(0.25)
                q3 = clean_data.quantile(0.75)
                iqr = q3 - q1
                outliers = clean_data[(clean_data < q1 - 1.5 * iqr) | (clean_data > q3 + 1.5 * iqr)]
                outlier_pct = (len(outliers) / len(clean_data)) * 100
                if outlier_pct > 10:
                    steps.append({
                        'step': step_num,
                        'action': 'Traiter les outliers',
                        'column': col,
                        'method': 'Clipping (bornage)',
                        'code': f"lower = df['{col}'].quantile(0.01)\nupper = df['{col}'].quantile(0.99)\ndf['{col}'] = df['{col}'].clip(lower, upper)",
                        'priority': 'medium'
                    })
                    step_num += 1
                    break
        
        return steps
    
    @classmethod
    def _generate_ml_pipeline(cls, df: pd.DataFrame, ml_detection: Dict) -> Dict[str, Any]:
        """
        Génère un pipeline ML recommandé
        """
        problem_type = ml_detection.get('problem_type', {}).get('type', 'unknown')
        
        pipeline = {
            'data_splitting': {
                'train_size': 0.8,
                'test_size': 0.2,
                'validation_size': 0.2,
                'code': "from sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)"
            },
            'cross_validation': {
                'folds': 5,
                'code': "from sklearn.model_selection import cross_val_score, StratifiedKFold\ncv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)"
            },
            'evaluation_metrics': []
        }
        
        if problem_type == 'binary_classification':
            pipeline['evaluation_metrics'] = [
                'Accuracy',
                'Precision',
                'Recall', 
                'F1-Score',
                'AUC-ROC'
            ]
            pipeline['code_example'] = """
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(classification_report(y_test, y_pred))
print(f"AUC-ROC: {roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]):.3f}")
"""
        elif problem_type == 'multi_class_classification':
            pipeline['evaluation_metrics'] = [
                'Accuracy',
                'Macro F1-Score',
                'Micro F1-Score',
                'Confusion Matrix'
            ]
            pipeline['code_example'] = """
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
"""
        elif problem_type == 'regression':
            pipeline['evaluation_metrics'] = [
                'RMSE (Root Mean Squared Error)',
                'MAE (Mean Absolute Error)',
                'R² Score',
                'Adjusted R²'
            ]
            pipeline['code_example'] = """
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.3f}")
print(f"MAE: {mean_absolute_error(y_test, y_pred):.3f}")
print(f"R²: {r2_score(y_test, y_pred):.3f}")
"""
        
        return pipeline
    
    @classmethod
    def _identify_important_features(cls, df: pd.DataFrame, ml_detection: Dict) -> List[Dict[str, Any]]:
        """
        Identifie les features potentiellement importantes
        """
        important_features = []
        target_col = ml_detection.get('target_column')
        
        if target_col and target_col in df.columns:
            # Corrélations avec la cible
            for col in df.columns:
                if col != target_col and pd.api.types.is_numeric_dtype(df[col]):
                    corr = df[col].corr(df[target_col])
                    if abs(corr) > 0.1:
                        important_features.append({
                            'feature': col,
                            'correlation': round(corr, 3),
                            'importance': 'high' if abs(corr) > 0.3 else 'medium' if abs(corr) > 0.15 else 'low',
                            'type': 'numeric'
                        })
        
        # Features catégorielles avec peu de classes
        for col in df.columns:
            if col != target_col and (df[col].dtype == 'object' or df[col].nunique() <= 10):
                if df[col].nunique() <= 10:
                    important_features.append({
                        'feature': col,
                        'importance': 'medium',
                        'type': 'categorical',
                        'unique_values': df[col].nunique()
                    })
        
        # Trier par importance
        important_features.sort(key=lambda x: x.get('importance', 'low'), reverse=True)
        
        return important_features[:10]
    
    @classmethod
    def _assess_data_quality(cls, df: pd.DataFrame, advanced_analysis: Dict) -> Dict[str, Any]:
        """
        Évalue la qualité des données pour le ML
        """
        summary = advanced_analysis.get('summary', {})
        
        return {
            'overall_score': summary.get('data_quality_score', 0),
            'issues_found': summary.get('problematic_columns_count', 0),
            'constant_columns': len(advanced_analysis.get('constant_columns', [])),
            'high_cardinality': len(advanced_analysis.get('high_cardinality_columns', [])),
            'missing_values_problematic': summary.get('columns_with_missing', 0) > 0,
            'ready_for_modeling': summary.get('data_quality_score', 0) >= 70
        }
    
    @classmethod
    def _identify_potential_issues(cls, df: pd.DataFrame, advanced_analysis: Dict) -> List[str]:
        """
        Identifie les problèmes potentiels pour le ML
        """
        issues = []
        
        # Colonnes constantes
        if advanced_analysis.get('constant_columns'):
            issues.append(f"Colonnes constantes à supprimer: {', '.join(advanced_analysis['constant_columns'][:3])}")
        
        # Haute cardinalité
        if advanced_analysis.get('extreme_cardinality_columns'):
            issues.append(f"Colonnes à très haute cardinalité: {', '.join(advanced_analysis['extreme_cardinality_columns'][:3])}")
        
        # Déséquilibre des classes
        ml_detection = MLProblemDetector.detect(df)
        target_analysis = ml_detection.get('target_analysis', {})
        if not target_analysis.get('is_balanced', True):
            issues.append("La classe cible est déséquilibrée - envisager SMOTE ou class_weight")
        
        # Valeurs manquantes
        missing_cols = df.columns[df.isna().any()].tolist()
        if missing_cols:
            issues.append(f"Valeurs manquantes dans {len(missing_cols)} colonnes")
        
        return issues
    
    @classmethod
    def _calculate_readiness_score(cls, df: pd.DataFrame, ml_detection: Dict) -> Dict[str, Any]:
        """
        Calcule un score de préparation pour le ML
        """
        score = 100
        reasons = []
        
        # Pénalité pour valeurs manquantes
        missing_pct = (df.isna().sum().sum() / df.size) * 100
        if missing_pct > 0:
            score -= min(30, missing_pct * 2)
            reasons.append(f"Valeurs manquantes: -{min(30, missing_pct * 2):.0f} points")
        
        # Pénalité pour colonnes constantes
        constant_cols = [col for col in df.columns if df[col].nunique() == 1]
        if constant_cols:
            score -= min(20, len(constant_cols) * 5)
            reasons.append(f"Colonnes constantes: -{min(20, len(constant_cols) * 5)} points")
        
        # Pénalité pour haute cardinalité
        high_card_cols = [col for col in df.columns if df[col].nunique() > 100]
        if high_card_cols:
            score -= min(15, len(high_card_cols) * 3)
            reasons.append(f"Haute cardinalité: -{min(15, len(high_card_cols) * 3)} points")
        
        # Bonus pour cible détectée
        if ml_detection.get('target_column'):
            score += 10
            reasons.append("Cible détectée automatiquement: +10 points")
        
        score = max(0, min(100, score))
        
        # Niveau
        if score >= 80:
            level = "Prêt pour le ML"
        elif score >= 60:
            level = "Nettoyage léger requis"
        elif score >= 40:
            level = "Nettoyage modéré requis"
        else:
            level = "Nettoyage majeur requis"
        
        return {
            'score': round(score, 1),
            'level': level,
            'reasons': reasons
        }
    
    @classmethod
    def _generate_summary(cls, ml_detection: Dict, preprocessing_steps: List) -> str:
        """
        Génère un résumé textuel
        """
        target = ml_detection.get('target_column', 'Non détectée')
        problem = ml_detection.get('problem_type', {}).get('message', 'Non déterminé')
        steps_count = len([s for s in preprocessing_steps if s.get('priority') == 'high'])
        
        return f"Problème identifié: {problem}. " \
               f"Cible: {target}. " \
               f"{steps_count} étapes de prétraitement prioritaires recommandées."