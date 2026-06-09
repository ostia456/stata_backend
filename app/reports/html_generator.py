"""
Génération de rapports HTML à partir des analyses
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape


class HTMLReportGenerator:
    """
    Générateur de rapports HTML
    """
    
    def __init__(self, templates_dir: str = None):
        """
        Initialise le générateur HTML
        
        Args:
            templates_dir: Dossier contenant les templates Jinja2
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def generate_report(self, analysis_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Génère un rapport HTML à partir des données d'analyse
        """
        # Préparer les données pour le template
        template_data = self._prepare_template_data(analysis_data)
        
        # Charger et rendre le template
        template = self.env.get_template("report_template.html")
        html_content = template.render(**template_data)
        
        # Sauvegarder si un chemin est fourni
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return html_content
    
    def _prepare_template_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prépare toutes les données pour le template Jinja2
        """
        # ============================================
        # 1. PROFIL DU DATASET
        # ============================================
        profile = analysis_data.get('profile', {})
        basic_info = profile.get('basic_info', {})
        column_types = profile.get('column_types', {})
        
        # ============================================
        # 2. STATISTIQUES DESCRIPTIVES
        # ============================================
        statistics_data = analysis_data.get('statistics', {})
        stats_dict = statistics_data.get('statistics', {})
        
        # Si stats_dict est vide, essayer de le calculer depuis profile
        if not stats_dict:
            numeric_cols = [col for col, t in column_types.items() if t == 'numeric']
            for col in numeric_cols:
                # Créer des stats minimales
                stats_dict[col] = {
                    'mean': 0,
                    'median': 0,
                    'std': 0,
                    'min': 0,
                    'max': 0,
                    'skewness': 0
                }
        
        # ============================================
        # 3. VALEURS MANQUANTES
        # ============================================
        missing_data = analysis_data.get('missing_values', {})
        missing_summary = missing_data.get('summary', {})
        missing_columns = missing_data.get('columns', {})
        
        # ============================================
        # 4. QUALITÉ
        # ============================================
        quality_data = analysis_data.get('quality', {})
        quality_score_data = quality_data.get('score', {})
        
        # ============================================
        # 5. CORRÉLATIONS
        # ============================================
        correlations_data = analysis_data.get('correlations', {})
        pearson_data = correlations_data.get('pearson', {})
        strong_correlations = pearson_data.get('strong_correlations', [])
        
        # ============================================
        # 6. NORMALITÉ
        # ============================================
        normality_data = analysis_data.get('normality', {})
        normality_results = normality_data.get('results', {})
        non_normal_columns = normality_data.get('non_normal_columns', [])
        
        # ============================================
        # 7. OUTLIERS
        # ============================================
        outliers_data = analysis_data.get('outliers', {})
        outliers_results = outliers_data.get('results', {})
        columns_with_outliers = outliers_data.get('columns_with_outliers', [])
        
        # ============================================
        # 8. INSIGHTS
        # ============================================
        insights_data = analysis_data.get('insights', {})
        
        # ============================================
        # 9. COMPTAGES
        # ============================================
        numeric_cols = sum(1 for t in column_types.values() if t == 'numeric')
        categorical_cols = sum(1 for t in column_types.values() if t == 'categorical')
        text_cols = sum(1 for t in column_types.values() if t == 'text')
        datetime_cols = sum(1 for t in column_types.values() if t == 'datetime')
        
        numeric_columns_list = [col for col, t in column_types.items() if t == 'numeric']
        categorical_columns_list = [col for col, t in column_types.items() if t == 'categorical']
        
        # ============================================
        # 10. PRÉPARATION MISSING COLUMNS
        # ============================================
        missing_columns_simple = {}
        for col, info in missing_columns.items():
            if info.get('missing_count', 0) > 0:
                missing_columns_simple[col] = {
                    'missing_count': info.get('missing_count', 0),
                    'missing_percentage': info.get('missing_percentage', 0),
                    'imputation_suggestion': info.get('imputation_suggestion', {})
                }
        
        # ============================================
        # 11. LISTES D'INSIGHTS
        # ============================================
        insights_list = []
        insights_list.extend(insights_data.get('missing_insights', []))
        insights_list.extend(insights_data.get('numeric_insights', []))
        insights_list.extend(insights_data.get('correlation_insights', []))
        
        missing_insights = insights_data.get('missing_insights', [])
        numeric_insights = insights_data.get('numeric_insights', [])
        correlation_insights = insights_data.get('correlation_insights', [])
        recommendations = insights_data.get('recommendations', [])
        
        # ============================================
        # 12. SCORES DÉTAILLÉS
        # ============================================
        components = quality_score_data.get('components', {})
        completeness_score = components.get('completeness', {}).get('score', 0)
        integrity_score = components.get('integrity', {}).get('score', 0)
        consistency_score = components.get('consistency', {}).get('score', 0)
        accuracy_score = components.get('accuracy', {}).get('score', 0)
        
        # ============================================
        # 13. POURCENTAGES
        # ============================================
        rows_missing_percentage = missing_summary.get('rows_missing_percentage', 0)
        
        # ============================================
        # 14. DEBUG - Afficher ce qui est passé au template
        # ============================================
        print(f"Données passées au template:")
        print(f"   - statistics: {len(stats_dict)} colonnes")
        print(f"   - normality: {len(normality_results)} colonnes")
        print(f"   - outliers: {len(outliers_results)} colonnes")
        print(f"   - histograms: {'OUI' if analysis_data.get('histograms') else 'NON'}")
        print(f"   - boxplots: {'OUI' if analysis_data.get('boxplots') else 'NON'}")
        print(f"   - pearson_heatmap: {'OUI' if analysis_data.get('pearson_heatmap') else 'NON'}")
        print(f"   - missing_heatmap: {'OUI' if analysis_data.get('missing_heatmap') else 'NON'}")
        
        # ============================================
        # 15. RETOUR FINAL
        # ============================================
        return {
            # En-tête
            'filename': analysis_data.get('file_id', 'unknown'),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'execution_time': analysis_data.get('execution_time_seconds', 0),
            
            # Aperçu
            'rows': basic_info.get('rows', 0),
            'columns': basic_info.get('columns', 0),
            'memory_mb': basic_info.get('memory_usage_mb', 0),
            
            # Types (compteurs)
            'numeric_cols': numeric_cols,
            'categorical_cols': categorical_cols,
            'text_cols': text_cols,
            'datetime_cols': datetime_cols,
            
            # Types (listes)
            'numeric_columns_list': numeric_columns_list,
            'categorical_columns_list': categorical_columns_list[:10],
            
            # Qualité
            'quality_score': quality_score_data.get('total_score', 0),
            'quality_grade': quality_score_data.get('grade', 'N/A'),
            'quality_interpretation': quality_score_data.get('interpretation', ''),
            'completeness_score': completeness_score,
            'integrity_score': integrity_score,
            'consistency_score': consistency_score,
            'accuracy_score': accuracy_score,
            
            # Résumé
            'executive_summary': insights_data.get('executive_summary', ''),
            
            # Valeurs manquantes
            'total_cells': missing_summary.get('total_cells', 0),
            'total_missing': missing_summary.get('total_missing', 0),
            'missing_percentage': missing_summary.get('total_missing_percentage', 0),
            'columns_with_missing': missing_summary.get('columns_with_missing', 0),
            'rows_with_missing': missing_summary.get('rows_with_missing', 0),
            'rows_missing_percentage': rows_missing_percentage,
            'missing_columns': missing_columns_simple,
            
            # Statistiques
            'statistics': stats_dict,
            
            # Corrélations
            'strong_correlations': strong_correlations[:10],
            
            # Normalité
            'normality': normality_results,
            'non_normal_count': len(non_normal_columns),
            
            # Outliers
            'outliers': outliers_results,
            'outliers_columns_count': len(columns_with_outliers),
            
            # Insights
            'insights_list': insights_list[:10],
            'missing_insights': missing_insights[:5],
            'numeric_insights': numeric_insights[:5],
            'correlation_insights': correlation_insights[:5],
            
            # Recommandations
            'recommendations': recommendations[:5],
            
            # ========== GRAPHIQUES ==========
            'histograms': analysis_data.get('histograms'),
            'boxplots': analysis_data.get('boxplots'),
            'pearson_heatmap': analysis_data.get('pearson_heatmap'),
            'missing_heatmap': analysis_data.get('missing_heatmap')
        }
    
    def generate_and_save(self, analysis_data: Dict[str, Any], file_id: str) -> str:
        """
        Génère et sauvegarde un rapport HTML
        """
        from ..config import Config
        
        output_dir = Config.HTML_REPORTS_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{file_id}_{timestamp}.html"
        output_path = output_dir / filename
        
        self.generate_report(analysis_data, str(output_path))
        
        return str(output_path)