"""
Visualisations spécifiques pour les valeurs manquantes
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, List


class MissingVisualizer:
    """
    Visualisations pour l'analyse des valeurs manquantes
    """
    
    @classmethod
    def create_missing_bar_chart(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Crée un graphique à barres des valeurs manquantes par colonne
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Graphique à barres
        """
        missing_counts = df.isna().sum()
        missing_pct = (missing_counts / len(df)) * 100
        
        # Filtrer les colonnes avec des manquants
        has_missing = missing_pct[missing_pct > 0]
        
        if len(has_missing) == 0:
            return {'message': 'Aucune valeur manquante détectée'}
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=has_missing.index,
            y=has_missing.values,
            text=[f"{v:.1f}%" for v in has_missing.values],
            textposition='outside',
            marker_color='#EF553B',
            hovertemplate='Colonne: %{x}<br>Manquants: %{y} ({pct:.1f}%)<extra></extra>',
            name='Valeurs manquantes'
        ))
        
        fig.update_layout(
            title='Valeurs manquantes par colonne',
            xaxis_title='Colonnes',
            yaxis_title='Nombre de valeurs manquantes',
            template='plotly_white',
            height=500
        )
        
        return {
            'type': 'missing_bar_chart',
            'plotly_json': fig.to_dict(),
            'columns_with_missing': len(has_missing),
            'total_missing': int(missing_counts.sum())
        }
    
    @classmethod
    def create_missing_percentage_chart(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Crée un graphique en donut du pourcentage global de valeurs manquantes
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Graphique en donut
        """
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        present_cells = total_cells - missing_cells
        
        missing_pct = (missing_cells / total_cells) * 100
        present_pct = (present_cells / total_cells) * 100
        
        fig = go.Figure(data=[go.Pie(
            labels=['Présentes', 'Manquantes'],
            values=[present_cells, missing_cells],
            hole=0.4,
            marker_colors=['#2ECC71', '#E74C3C'],
            textinfo='label+percent',
            hovertemplate='%{label}: %{value} cellules (%{percent})<extra></extra>'
        )])
        
        fig.update_layout(
            title=f'Complétude des données ({100-missing_pct:.1f}% complètes)',
            template='plotly_white',
            height=450
        )
        
        return {
            'type': 'missing_donut_chart',
            'plotly_json': fig.to_dict(),
            'completeness_percentage': round(100 - missing_pct, 2)
        }
    
    @classmethod
    def create_all_missing_visuals(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Crée toutes les visualisations des valeurs manquantes
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Liste des visualisations
        """
        visuals = []
        
        bar_chart = cls.create_missing_bar_chart(df)
        if 'error' not in bar_chart:
            visuals.append(bar_chart)
        
        donut_chart = cls.create_missing_percentage_chart(df)
        visuals.append(donut_chart)
        
        return visuals