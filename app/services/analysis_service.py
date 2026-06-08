"""
Service global d'analyse - Agrège tous les résultats d'analyse
"""

import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from ..core.sampling import large_dataset_handler, DataSampler
from ..core.cache_manager import cache_manager
from app.core.statistics import DescriptiveStats
from app.core.missing_values import MissingValueAnalyzer
from app.core.correlations import CorrelationAnalyzer
from app.core.normality import NormalityTester
from app.core.outliers import OutlierDetector
from app.core.data_quality import DataQualityScorer, QualityReportGenerator
from app.core.dataset_profiler import DatasetProfiler
from app.interpretation.data_insights import DataInsightsGenerator
from app.utils import clean_for_json


class GlobalAnalysisService:
    """
    Service global qui orchestre toutes les analyses
    """
    
    def __init__(self, df: pd.DataFrame, file_id: str = None):
        """
        Initialise le service avec un DataFrame
        
        Args:
            df: DataFrame à analyser
            file_id: Identifiant optionnel du fichier
        """
        self.df = df
        self.file_id = file_id
        self.analysis_cache = {}
    
    def run_complete_analysis(self, use_cache: bool = True, force_full: bool = False) -> Dict[str, Any]:
        """
        Exécute toutes les analyses avec gestion automatique des gros datasets
        
        Args:
            use_cache: Utiliser le cache si disponible
            force_full: Forcer l'analyse sur toutes les données (déconseillé pour gros fichiers)
        """
        start_time = datetime.now()
        
        # Informations sur la taille du dataset
        total_rows = len(self.df)
        sampling_info = large_dataset_handler.sampler.get_sampling_info(self.df)
        
        # Décider quelle version du DataFrame utiliser
        if force_full or not sampling_info['needs_sampling']:
            df_for_analysis = self.df
            sampling_metadata = {'sampled': False, 'original_rows': total_rows}
        else:
            df_for_analysis = large_dataset_handler.sampler.get_sample(self.df)
            sampling_metadata = {
                'sampled': True,
                'original_rows': total_rows,
                'sampled_rows': len(df_for_analysis),
                'sampling_percentage': sampling_info['sampling_percentage']
            }
            print(f" Échantillonnage: {total_rows} → {len(df_for_analysis)} lignes")
        
        # Vérifier le cache
        if use_cache:
            cached_result = cache_manager.load_analysis(self.file_id, "complete_analysis")
            if cached_result:
                print(f"📦 Résultat chargé depuis le cache pour {self.file_id}")
                return cached_result
        
        # Profil de base (sur données complètes pour les métadonnées)
        profile = DatasetProfiler.quick_profile(self.df, self.file_id)
        profile['sampling_info'] = sampling_info
        
        # Analyses sur données échantillonnées si nécessaire
        # Statistiques
        stats = cache_manager.load_analysis(self.file_id, "statistics")
        if stats is None:
            stats = DescriptiveStats(df_for_analysis).compute_all()
            cache_manager.save_analysis(self.file_id, "statistics", stats)
        
        # Valeurs manquantes (sur données complètes pour avoir les vrais comptes)
        missing = cache_manager.load_analysis(self.file_id, "missing")
        if missing is None:
            missing = MissingValueAnalyzer.analyze(self.df)
            cache_manager.save_analysis(self.file_id, "missing", missing)
        
        # Corrélations (sur échantillon si gros dataset)
        corr_df = large_dataset_handler.handle_analysis(self.df, 'correlations')[0]
        correlations = cache_manager.load_analysis(self.file_id, "correlations")
        if correlations is None:
            correlations = CorrelationAnalyzer.calculate_both(corr_df)
            cache_manager.save_analysis(self.file_id, "correlations", correlations)
        
        # Normalité (Shapiro limité à 5000)
        norm_df = large_dataset_handler.handle_analysis(self.df, 'normality')[0]
        normality = cache_manager.load_analysis(self.file_id, "normality")
        if normality is None:
            normality = NormalityTester.test_all_columns(norm_df)
            cache_manager.save_analysis(self.file_id, "normality", normality)
        
        # Outliers (sur échantillon)
        outliers_df = large_dataset_handler.handle_analysis(self.df, 'outliers')[0]
        outliers = cache_manager.load_analysis(self.file_id, "outliers")
        if outliers is None:
            outliers = OutlierDetector.analyze_all_columns(outliers_df)
            cache_manager.save_analysis(self.file_id, "outliers", outliers)
        
        # Qualité (sur données complètes)
        quality_score = cache_manager.load_analysis(self.file_id, "quality_score")
        if quality_score is None:
            quality_score = DataQualityScorer.calculate_score(self.df)
            cache_manager.save_analysis(self.file_id, "quality_score", quality_score)
        
        quality_report = cache_manager.load_analysis(self.file_id, "quality_report")
        if quality_report is None:
            quality_report = QualityReportGenerator.generate(self.df, self.file_id)
            cache_manager.save_analysis(self.file_id, "quality_report", quality_report)
        
        # Insights (sur échantillon pour la vitesse)
        insights_df = large_dataset_handler.handle_analysis(self.df, 'full_analysis')[0]
        insights = cache_manager.load_analysis(self.file_id, "insights")
        if insights is None:
            insights = DataInsightsGenerator.generate_all_insights(insights_df)
            cache_manager.save_analysis(self.file_id, "insights", insights)
        
        # ========== AJOUT : Données brutes pour les graphiques ==========
        # Limiter à 500 points max pour les graphiques
        raw_data = {}
        for col in self.df.columns:
            clean_data = self.df[col].dropna()
            if len(clean_data) > 500:
                raw_data[col] = clean_data.sample(n=500, random_state=42).tolist()
            else:
                raw_data[col] = clean_data.tolist()
        
        # Types de colonnes pour le frontend
        column_types = {
            col: 'numeric' if pd.api.types.is_numeric_dtype(self.df[col]) else 'categorical'
            for col in self.df.columns
        }
        
        # Colonnes numériques
        numeric_columns = self.df.select_dtypes(include=['number']).columns.tolist()
        
        # Détection ML (colonne cible)
        from ..core.ml_detector import MLProblemDetector
        ml_detection = MLProblemDetector.detect(self.df)
        
        # Calculer le temps d'exécution
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Assembler le rapport complet
        result = {
            'file_id': self.file_id,
            'execution_time_seconds': round(execution_time, 2),
            'from_cache': all([stats, missing, correlations, normality, outliers, quality_score, quality_report, insights]),
            'sampling_info': sampling_metadata,
            'generated_at': datetime.now().isoformat(),
            'profile': profile,
            'statistics': stats,
            'missing_values': missing,
            'correlations': correlations,
            'normality': normality,
            'outliers': outliers,
            'quality': {
                'score': quality_score,
                'report': quality_report
            },
            'insights': insights,
            'summary': self._generate_summary(
                profile, missing, correlations, quality_score, insights
            ),
            # ========== NOUVEAUX CHAMPS POUR LE FRONTEND ==========
            'raw_data': raw_data,
            'column_types': column_types,
            'numeric_columns': numeric_columns,
            'ml_detection': ml_detection
        }
        
        # Sauvegarder l'analyse complète en cache
        if use_cache:
            cache_manager.save_analysis(self.file_id, "complete_analysis", result)
        
        return result
    
    def run_quick_analysis(self) -> Dict[str, Any]:
        """
        Version rapide de l'analyse (pour les aperçus)
        
        Returns:
            Dictionnaire avec les résultats essentiels
        """
        # Profil de base
        profile = DatasetProfiler.quick_overview(self.df, self.file_id)
        
        # Statistiques rapides
        fast_stats = DescriptiveStats(self.df).get_fast_stats()
        
        # Résumé des valeurs manquantes
        missing_summary = MissingValueAnalyzer.quick_analysis(self.df)
        
        # Score de qualité rapide
        quality_score = DataQualityScorer.calculate_score(self.df)
        
        # Insights rapides
        quick_insights = DataInsightsGenerator.generate_all_insights(self.df)
        
        return {
            'file_id': self.file_id,
            'generated_at': datetime.now().isoformat(),
            'overview': profile,
            'quick_statistics': fast_stats,
            'missing_summary': missing_summary,
            'quality_score': quality_score['total_score'],
            'quality_grade': quality_score['grade'],
            'quick_insights': quick_insights['executive_summary']
        }
    
    def _generate_summary(self, profile: Dict, missing: Dict, 
                          correlations: Dict, quality_score: Dict,
                          insights: Dict) -> Dict[str, Any]:
        """
        Génère un résumé synthétique des analyses
        """
        return {
            'dataset_size': {
                'rows': profile.get('basic_info', {}).get('rows', 0),
                'columns': profile.get('basic_info', {}).get('columns', 0),
                'numeric_columns': len(profile.get('numeric_columns', []))
            },
            'data_quality': {
                'score': quality_score.get('total_score', 0),
                'grade': quality_score.get('grade', 'N/A'),
                'missing_percentage': missing.get('summary', {}).get('total_missing_percentage', 0)
            },
            'key_findings': {
                'best_predictor': self._find_best_predictor(correlations),
                'most_missing_column': missing.get('worst_column', {}).get('column'),
                'quality_interpretation': quality_score.get('interpretation', '')
            },
            'executive_summary': insights.get('executive_summary', '')
        }
    
    def _find_best_predictor(self, correlations: Dict) -> Optional[str]:
        """
        Trouve le meilleur prédicteur pour une cible potentielle
        """
        # Chercher une colonne cible probable
        target_keywords = ['survived', 'target', 'label', 'class', 'y', 'price', 'value']
        
        # Récupérer les corrélations Pearson
        pearson_data = correlations.get('pearson', {})
        if not pearson_data:
            return None
        
        # Chercher la cible
        target_col = None
        for col in pearson_data.get('columns', []):
            if col.lower() in target_keywords:
                target_col = col
                break
        
        if not target_col:
            # Prendre la première colonne numérique comme cible par défaut
            target_col = pearson_data.get('columns', [None])[0]
        
        if not target_col:
            return None
        
        # Trouver la meilleure corrélation
        matrix = pearson_data.get('matrix', {})
        if target_col in matrix:
            best_corr = -1
            best_col = None
            for col, value in matrix[target_col].items():
                if col != target_col and abs(value) > best_corr:
                    best_corr = abs(value)
                    best_col = col
            
            if best_col:
                return f"{best_col} (r={matrix[target_col][best_col]:.2f})"
        
        return None


def run_global_analysis(df: pd.DataFrame, file_id: str = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour exécuter une analyse globale complète
    
    Args:
        df: DataFrame à analyser
        file_id: Identifiant optionnel
        
    Returns:
        Rapport d'analyse complet
    """
    service = GlobalAnalysisService(df, file_id)
    result = service.run_complete_analysis()
    return clean_for_json(result)


def run_quick_analysis(df: pd.DataFrame, file_id: str = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour une analyse rapide
    
    Args:
        df: DataFrame à analyser
        file_id: Identifiant optionnel
        
    Returns:
        Rapport d'analyse rapide
    """
    service = GlobalAnalysisService(df, file_id)
    result = service.run_quick_analysis()
    return clean_for_json(result)