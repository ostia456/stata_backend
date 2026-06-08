"""
Gestion des gros datasets avec échantillonnage automatique
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SamplingConfig:
    """Configuration de l'échantillonnage"""
    max_rows_for_full_analysis: int = 50000      # Au-dessus, on échantillonne
    max_rows_for_correlations: int = 50000       # Corrélations sur échantillon
    max_rows_for_visualization: int = 10000      # Graphiques sur échantillon
    max_rows_for_normality: int = 5000           # Shapiro est limité à 5000
    max_rows_for_outliers: int = 50000           # Outliers sur échantillon
    random_seed: int = 42                        # Pour reproductibilité


class DataSampler:
    """
    Gestionnaire d'échantillonnage pour les gros datasets
    """
    
    def __init__(self, config: SamplingConfig = None):
        self.config = config or SamplingConfig()
    
    def needs_sampling(self, df: pd.DataFrame, threshold: int = None) -> bool:
        """
        Vérifie si le dataset a besoin d'être échantillonné
        
        Args:
            df: DataFrame à vérifier
            threshold: Seuil personnalisé
            
        Returns:
            True si l'échantillonnage est recommandé
        """
        threshold = threshold or self.config.max_rows_for_full_analysis
        return len(df) > threshold
    
    def get_sample(self, df: pd.DataFrame, max_rows: int = None, 
                   strategy: str = 'random') -> pd.DataFrame:
        """
        Retourne un échantillon du DataFrame
        
        Args:
            df: DataFrame original
            max_rows: Nombre max de lignes
            strategy: 'random' ou 'stratified'
            
        Returns:
            DataFrame échantillonné
        """
        max_rows = max_rows or self.config.max_rows_for_full_analysis
        
        if len(df) <= max_rows:
            return df
        
        if strategy == 'random':
            return df.sample(n=max_rows, random_state=self.config.random_seed)
        elif strategy == 'stratified':
            return self._stratified_sample(df, max_rows)
        else:
            return df.sample(n=max_rows, random_state=self.config.random_seed)
    
    def _stratified_sample(self, df: pd.DataFrame, max_rows: int) -> pd.DataFrame:
        """
        Échantillonnage stratifié basé sur la colonne cible probable
        """
        # Chercher une colonne cible probable
        target_col = self._find_target_column(df)
        
        if target_col and df[target_col].nunique() <= 10:
            # Échantillonnage stratifié par cible
            fractions = {}
            for value in df[target_col].unique():
                count = len(df[df[target_col] == value])
                fractions[value] = max(1, int(max_rows * (count / len(df))))
            
            samples = []
            for value, n in fractions.items():
                sample = df[df[target_col] == value].sample(
                    n=min(n, len(df[df[target_col] == value])),
                    random_state=self.config.random_seed
                )
                samples.append(sample)
            
            return pd.concat(samples)
        
        # Fallback vers aléatoire
        return df.sample(n=max_rows, random_state=self.config.random_seed)
    
    def _find_target_column(self, df: pd.DataFrame) -> Optional[str]:
        """Trouve une colonne cible potentielle pour stratification"""
        target_keywords = ['survived', 'target', 'label', 'class', 'y']
        
        for col in df.columns:
            if col.lower() in target_keywords:
                return col
        
        # Chercher une colonne binaire
        for col in df.columns:
            if df[col].nunique() == 2:
                return col
        
        return None
    
    def get_sampling_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Retourne des informations sur l'échantillonnage
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Informations sur l'échantillonnage
        """
        total_rows = len(df)
        needs_sampling = self.needs_sampling(df)
        
        return {
            'total_rows': total_rows,
            'needs_sampling': needs_sampling,
            'sampling_threshold': self.config.max_rows_for_full_analysis,
            'sampling_strategy': 'random' if needs_sampling else 'none',
            'sampled_rows': min(total_rows, self.config.max_rows_for_full_analysis),
            'sampling_percentage': round(
                min(100, (self.config.max_rows_for_full_analysis / total_rows) * 100), 2
            ) if needs_sampling else 100
        }


class LargeDatasetHandler:
    """
    Gestionnaire pour les gros datasets - décide quoi faire selon la taille
    """
    
    def __init__(self, config: SamplingConfig = None):
        self.sampler = DataSampler(config)
        self.config = config or SamplingConfig()
    
    def handle_analysis(self, df: pd.DataFrame, analysis_type: str) -> Tuple[pd.DataFrame, Dict]:
        """
        Prépare le DataFrame pour un type d'analyse spécifique
        
        Args:
            df: DataFrame original
            analysis_type: Type d'analyse ('statistics', 'correlations', etc.)
            
        Returns:
            Tuple (DataFrame à utiliser, métadonnées)
        """
        total_rows = len(df)
        
        # Définir les seuils selon le type d'analyse
        thresholds = {
            'full_analysis': self.config.max_rows_for_full_analysis,
            'correlations': self.config.max_rows_for_correlations,
            'visualization': self.config.max_rows_for_visualization,
            'normality': self.config.max_rows_for_normality,
            'outliers': self.config.max_rows_for_outliers
        }
        
        threshold = thresholds.get(analysis_type, self.config.max_rows_for_full_analysis)
        
        if total_rows <= threshold:
            return df, {
                'sampled': False,
                'original_rows': total_rows,
                'sampled_rows': total_rows,
                'sampling_percentage': 100,
                'analysis_type': analysis_type
            }
        
        # Échantillonner
        sampled_df = self.sampler.get_sample(df, threshold)
        
        return sampled_df, {
            'sampled': True,
            'original_rows': total_rows,
            'sampled_rows': len(sampled_df),
            'sampling_percentage': round((len(sampled_df) / total_rows) * 100, 2),
            'analysis_type': analysis_type,
            'warning': f"Dataset volumineux ({total_rows} lignes). " +
                       f"Analyse sur un échantillon de {len(sampled_df)} lignes."
        }
    
    def get_analysis_warning(self, df: pd.DataFrame, analysis_type: str) -> Optional[str]:
        """
        Retourne un avertissement si l'analyse est faite sur un échantillon
        """
        sampled_df, metadata = self.handle_analysis(df, analysis_type)
        
        if metadata['sampled']:
            return metadata['warning']
        return None


# Instance globale
large_dataset_handler = LargeDatasetHandler()