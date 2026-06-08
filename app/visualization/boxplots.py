"""
Génération de boxplots interactifs avec Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class BoxplotGenerator:
    """
    Générateur de boxplots pour la détection d'outliers
    """
    
    @classmethod
    def create_boxplot(cls, series: pd.Series, title: str = None) -> Dict[str, Any]:
        """
        Crée un boxplot interactif
        
        Args:
            series: Série pandas à visualiser
            title: Titre du graphique
            
        Returns:
            Dictionnaire avec les données du graphique
        """
        clean_data = series.dropna()
        
        if len(clean_data) == 0:
            return {'error': 'Aucune donnée valide'}
        
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=clean_data,
            name=series.name,
            boxmean='sd',
            marker_color='#636EFA',
            boxpoints='outliers',
            jitter=0.3,
            pointpos=-1.8,
            hovertemplate='Valeur: %{y}<extra></extra>'
        ))
        
        # Mise en forme
        fig.update_layout(
            title=title or f'Boxplot de {series.name}',
            yaxis_title=series.name,
            template='plotly_white',
            height=500
        )
        
        # Statistiques
        stats = {
            'min': float(clean_data.min()),
            'q1': float(clean_data.quantile(0.25)),
            'median': float(clean_data.median()),
            'q3': float(clean_data.quantile(0.75)),
            'max': float(clean_data.max()),
            'iqr': float(clean_data.quantile(0.75) - clean_data.quantile(0.25)),
            'outliers_count': cls._count_outliers(clean_data)
        }
        
        return {
            'type': 'boxplot',
            'column': series.name,
            'plotly_json': fig.to_dict(),
            'stats': stats
        }
    
    @classmethod
    def create_multiple_boxplots(cls, df: pd.DataFrame, max_cols: int = 10) -> Dict[str, Any]:
        """
        Crée des boxplots pour plusieurs colonnes dans une même figure
        
        Args:
            df: DataFrame à analyser
            max_cols: Nombre maximum de colonnes
            
        Returns:
            Figure avec plusieurs boxplots
        """
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > max_cols:
            numeric_cols = numeric_cols[:max_cols]
        
        if len(numeric_cols) == 0:
            return {'error': 'Aucune colonne numérique'}
        
        fig = go.Figure()
        
        for col in numeric_cols:
            clean_data = df[col].dropna()
            if len(clean_data) > 0:
                fig.add_trace(go.Box(
                    y=clean_data,
                    name=col,
                    boxmean='sd'
                ))
        
        fig.update_layout(
            title='Boxplots des variables numériques',
            yaxis_title='Valeur',
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        return {
            'type': 'multiple_boxplots',
            'plotly_json': fig.to_dict(),
            'columns': list(numeric_cols)
        }
    
    @classmethod
    def _count_outliers(cls, data: pd.Series) -> int:
        """Compte les outliers avec la méthode IQR"""
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        return int(((data < lower) | (data > upper)).sum())