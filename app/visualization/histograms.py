"""
Génération d'histogrammes interactifs avec Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class HistogramGenerator:
    """
    Générateur d'histogrammes pour les colonnes numériques
    """
    
    @classmethod
    def create_histogram(cls, series: pd.Series, title: str = None, 
                         bins: int = 30, show_kde: bool = True) -> Dict[str, Any]:
        """
        Crée un histogramme interactif avec courbe KDE optionnelle
        
        Args:
            series: Série pandas à visualiser
            title: Titre du graphique
            bins: Nombre de bins
            show_kde: Afficher la courbe de densité
            
        Returns:
            Dictionnaire avec les données du graphique
        """
        clean_data = series.dropna()
        
        if len(clean_data) == 0:
            return {'error': 'Aucune donnée valide'}
        
        # Créer la figure
        fig = go.Figure()
        
        # Ajouter l'histogramme
        fig.add_trace(go.Histogram(
            x=clean_data,
            nbinsx=bins,
            name='Distribution',
            opacity=0.7,
            marker_color='#636EFA',
            hovertemplate='Valeur: %{x}<br>Fréquence: %{y}<extra></extra>'
        ))
        
        # Ajouter la courbe KDE si demandée
        if show_kde and len(clean_data) > 1:
            from scipy import stats
            kde = stats.gaussian_kde(clean_data)
            x_range = np.linspace(clean_data.min(), clean_data.max(), 100)
            y_kde = kde(x_range)
            
            # Normaliser pour correspondre à l'échelle de l'histogramme
            hist_counts, _ = np.histogram(clean_data, bins=bins)
            scale_factor = max(hist_counts) / max(y_kde) if max(y_kde) > 0 else 1
            
            fig.add_trace(go.Scatter(
                x=x_range,
                y=y_kde * scale_factor,
                mode='lines',
                name='Densité (KDE)',
                line=dict(color='#EF553B', width=2)
            ))
        
        # Mise en forme
        fig.update_layout(
            title=title or f'Distribution de {series.name}',
            xaxis_title=series.name,
            yaxis_title='Fréquence',
            template='plotly_white',
            hovermode='closest',
            bargap=0.05
        )
        
        # Statistiques pour l'annotation
        stats_text = cls._get_stats_text(clean_data)
        
        return {
            'type': 'histogram',
            'column': series.name,
            'plotly_json': fig.to_dict(),
            'stats': stats_text,
            'sample_size': len(clean_data)
        }
    
    @classmethod
    def create_all_histograms(cls, df: pd.DataFrame, max_cols: int = 10) -> List[Dict[str, Any]]:
        """
        Crée des histogrammes pour toutes les colonnes numériques
        
        Args:
            df: DataFrame à analyser
            max_cols: Nombre maximum de colonnes
            
        Returns:
            Liste des histogrammes
        """
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > max_cols:
            numeric_cols = numeric_cols[:max_cols]
        
        histograms = []
        for col in numeric_cols:
            histograms.append(cls.create_histogram(df[col]))
        
        return histograms
    
    @classmethod
    def create_grid_histograms(cls, df: pd.DataFrame, cols_per_row: int = 2) -> Dict[str, Any]:
        """
        Crée une grille d'histogrammes pour plusieurs colonnes
        
        Args:
            df: DataFrame à analyser
            cols_per_row: Nombre de colonnes par ligne
            
        Returns:
            Grille d'histogrammes
        """
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) == 0:
            return {'error': 'Aucune colonne numérique'}
        
        n_cols = len(numeric_cols)
        n_rows = (n_cols + cols_per_row - 1) // cols_per_row
        
        fig = make_subplots(
            rows=n_rows, cols=cols_per_row,
            subplot_titles=[str(col) for col in numeric_cols],
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        for i, col in enumerate(numeric_cols):
            row = i // cols_per_row + 1
            col_pos = i % cols_per_row + 1
            
            clean_data = df[col].dropna()
            if len(clean_data) > 0:
                fig.add_trace(
                    go.Histogram(x=clean_data, nbinsx=30, showlegend=False),
                    row=row, col=col_pos
                )
        
        fig.update_layout(
            title='Distribution des variables numériques',
            template='plotly_white',
            height=300 * n_rows,
            showlegend=False
        )
        
        return {
            'type': 'histogram_grid',
            'plotly_json': fig.to_dict(),
            'columns': list(numeric_cols)
        }
    
    @classmethod
    def _get_stats_text(cls, data: pd.Series) -> str:
        """Génère un texte avec les statistiques"""
        return f"Moyenne: {data.mean():.2f} | Médiane: {data.median():.2f} | Écart-type: {data.std():.2f}"