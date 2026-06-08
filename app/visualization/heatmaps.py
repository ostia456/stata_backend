"""
Génération de heatmaps de corrélation avec Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class HeatmapGenerator:
    """
    Générateur de heatmaps pour les matrices de corrélation
    """
    
    @classmethod
    def create_correlation_heatmap(cls, df: pd.DataFrame, method: str = 'pearson') -> Dict[str, Any]:
        """
        Crée une heatmap de corrélation interactive
        
        Args:
            df: DataFrame à analyser
            method: Méthode de corrélation ('pearson' ou 'spearman')
            
        Returns:
            Dictionnaire avec les données du graphique
        """
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            return {'error': 'Au moins 2 colonnes numériques nécessaires'}
        
        # Calculer la matrice de corrélation
        corr_matrix = df[numeric_cols].corr(method=method)
        
        # Créer la heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hovertemplate='%{x} ↔ %{y}<br>Corrélation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'Matrice de corrélation - {method.capitalize()}',
            width=600,
            height=500,
            template='plotly_white'
        )
        
        return {
            'type': 'correlation_heatmap',
            'method': method,
            'plotly_json': fig.to_dict(),
            'columns': list(numeric_cols)
        }
    
    @classmethod
    def create_both_heatmaps(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Crée les deux heatmaps (Pearson et Spearman)
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire avec les deux heatmaps
        """
        return {
            'pearson': cls.create_correlation_heatmap(df, 'pearson'),
            'spearman': cls.create_correlation_heatmap(df, 'spearman')
        }
    
    @classmethod
    def create_missing_heatmap(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Crée une heatmap des valeurs manquantes
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Heatmap des NaN
        """
        # Créer une matrice binaire des valeurs manquantes
        missing_matrix = df.isna().astype(int)
        
        fig = go.Figure(data=go.Heatmap(
            z=missing_matrix.values.T,
            x=df.index,
            y=df.columns,
            colorscale=[[0, 'lightgreen'], [1, 'darkred']],
            showscale=True,
            colorbar=dict(title="Manquant"),
            hovertemplate='Ligne: %{x}<br>Colonne: %{y}<br>Manquant: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Carte des valeurs manquantes',
            xaxis_title='Index des lignes',
            yaxis_title='Colonnes',
            template='plotly_white',
            height=max(400, len(df.columns) * 20),
            width=800
        )
        
        return {
            'type': 'missing_heatmap',
            'plotly_json': fig.to_dict(),
            'missing_percentage': round((df.isna().sum().sum() / df.size) * 100, 2)
        }