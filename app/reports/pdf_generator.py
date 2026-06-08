"""
Génération de rapports PDF complets avec toutes les analyses
"""

import os
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import pdfkit
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .html_generator import HTMLReportGenerator
from ..config import Config
from ..core.ml_detector import MLProblemDetector
from ..core.advanced_analysis import AdvancedColumnAnalyzer
from ..core.categorical_analysis import CategoricalAnalyzer


class PDFReportGenerator:
    """
    Générateur de rapports PDF complets avec toutes les analyses
    """
    
    def __init__(self):
        self.html_generator = HTMLReportGenerator()
        
        # Configurer wkhtmltopdf
        possible_paths = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        ]
        
        self.wkhtmltopdf_path = None
        for path in possible_paths:
            if os.path.exists(path):
                self.wkhtmltopdf_path = path
                break
        
        if self.wkhtmltopdf_path:
            self.config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
        else:
            self.config = None
        
        # Configurer kaleido pour Plotly
        try:
            pio.kaleido.scope.default_format = "png"
            pio.kaleido.scope.default_width = 800
            pio.kaleido.scope.default_height = 500
            self.kaleido_available = True
        except Exception:
            self.kaleido_available = False
    
    def _fig_to_base64(self, fig) -> Optional[str]:
        if not self.kaleido_available:
            return None
        try:
            img_bytes = fig.to_image(format="png", width=800, height=500, scale=2)
            return base64.b64encode(img_bytes).decode('utf-8')
        except Exception:
            return None
    
    def _create_histograms_image(self, df) -> Optional[str]:
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) == 0:
                return None
            
            numeric_cols = numeric_cols[:6]
            n_cols = min(2, len(numeric_cols))
            n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
            
            fig = make_subplots(
                rows=n_rows, cols=n_cols,
                subplot_titles=numeric_cols,
                vertical_spacing=0.15,
                horizontal_spacing=0.1
            )
            
            for i, col in enumerate(numeric_cols):
                row = i // n_cols + 1
                col_pos = i % n_cols + 1
                clean_data = df[col].dropna()
                if len(clean_data) > 0:
                    fig.add_trace(
                        go.Histogram(x=clean_data, nbinsx=30, name=str(col), showlegend=False),
                        row=row, col=col_pos
                    )
            
            fig.update_layout(
                title="Distributions des variables numériques",
                height=400 * n_rows,
                showlegend=False,
                template='plotly_white'
            )
            return self._fig_to_base64(fig)
        except Exception:
            return None
    
    def _create_boxplots_image(self, df) -> Optional[str]:
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()[:8]
            if len(numeric_cols) == 0:
                return None
            
            fig = go.Figure()
            for col in numeric_cols:
                clean_data = df[col].dropna()
                if len(clean_data) > 0:
                    fig.add_trace(go.Box(y=clean_data, name=col, boxmean='sd'))
            
            fig.update_layout(
                title="Boxplots des variables numériques",
                height=500,
                template='plotly_white'
            )
            return self._fig_to_base64(fig)
        except Exception:
            return None
    
    def _create_correlation_heatmap_image(self, df) -> Optional[str]:
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) < 2:
                return None
            
            corr_matrix = df[numeric_cols].corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 10}
            ))
            
            fig.update_layout(
                title="Matrice de corrélation (Pearson)",
                width=700,
                height=600,
                template='plotly_white'
            )
            return self._fig_to_base64(fig)
        except Exception:
            return None
    
    def _create_missing_heatmap_image(self, df) -> Optional[str]:
        try:
            sample_df = df.head(100) if len(df) > 100 else df
            missing_matrix = sample_df.isna().astype(int)
            
            fig = go.Figure(data=go.Heatmap(
                z=missing_matrix.values.T,
                x=sample_df.index,
                y=sample_df.columns,
                colorscale=[[0, '#2ecc71'], [1, '#e74c3c']],
                showscale=True,
                colorbar=dict(title="Manquant")
            ))
            
            fig.update_layout(
                title="Carte des valeurs manquantes (échantillon)",
                height=max(400, len(sample_df.columns) * 25),
                width=800,
                template='plotly_white'
            )
            return self._fig_to_base64(fig)
        except Exception:
            return None
    
    def _prepare_complete_data(self, analysis_data: Dict[str, Any], df,
                                histograms=None, boxplots=None,
                                pearson_heatmap=None, missing_heatmap=None) -> Dict[str, Any]:
        """Prépare TOUTES les données pour le template"""
        
        # Analyses supplémentaires
        ml_detection = MLProblemDetector.detect(df)
        advanced_analysis = AdvancedColumnAnalyzer.analyze_all(df)
        categorical_analysis = CategoricalAnalyzer.analyze(df)
        
        # Extraire les données ML détaillées
        target_column = ml_detection.get('target_column')
        problem_type = ml_detection.get('problem_type', {})
        model_suggestions = ml_detection.get('model_suggestions', [])
        ml_recommendations = ml_detection.get('recommendations', [])
        ml_ready = ml_detection.get('ready_for_ml', {})
        feature_analysis = ml_detection.get('feature_analysis', {})
        target_analysis = ml_detection.get('target_analysis', {})
        
        # Générer les étapes de prétraitement ML
        preprocessing_steps = []
        step_num = 1
        
        if target_column:
            preprocessing_steps.append({
                'step': step_num,
                'action': f"Utiliser '{target_column}' comme variable cible",
                'reason': f"Détecté automatiquement (confiance: {problem_type.get('confidence', 'medium')})"
            })
            step_num += 1
        
        # Valeurs manquantes
        missing_cols = df.columns[df.isna().any()].tolist()
        for col in missing_cols[:5]:
            if col != target_column:
                missing_pct = (df[col].isna().sum() / len(df)) * 100
                if missing_pct < 5:
                    action = "Supprimer les lignes"
                    code = f"df = df.dropna(subset=['{col}'])"
                elif missing_pct < 30:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        action = "Imputer par la médiane"
                        code = f"df['{col}'] = df['{col}'].fillna(df['{col}'].median())"
                    else:
                        action = "Imputer par le mode"
                        code = f"df['{col}'] = df['{col}'].fillna(df['{col}'].mode()[0])"
                else:
                    action = "Supprimer la colonne"
                    code = f"df = df.drop(columns=['{col}'])"
                
                preprocessing_steps.append({
                    'step': step_num,
                    'action': f"Gérer les valeurs manquantes de '{col}'",
                    'method': action,
                    'code': code,
                    'reason': f"{missing_pct:.1f}% de valeurs manquantes"
                })
                step_num += 1
        
        # Encodage catégoriel
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in cat_cols[:5]:
            if col != target_column:
                if df[col].nunique() <= 10:
                    method = "One-Hot Encoding"
                    code = f"df = pd.get_dummies(df, columns=['{col}'], drop_first=True)"
                else:
                    method = "Target Encoding"
                    code = f"from category_encoders import TargetEncoder\nte = TargetEncoder()\ndf['{col}_encoded'] = te.fit_transform(df['{col}'], df['{target_column}'])"
                
                preprocessing_steps.append({
                    'step': step_num,
                    'action': f"Encoder la variable '{col}'",
                    'method': method,
                    'code': code,
                    'reason': f"{df[col].nunique()} catégories"
                })
                step_num += 1
        
        # Scaling
        preprocessing_steps.append({
            'step': step_num,
            'action': "Standardiser les variables numériques",
            'method': "StandardScaler",
            'code': "from sklearn.preprocessing import StandardScaler\nscaler = StandardScaler()\ndf[numeric_cols] = scaler.fit_transform(df[numeric_cols])",
            'reason': "Améliore les performances des modèles"
        })
        
        # Extraire les données existantes
        profile = analysis_data.get('profile', {})
        basic_info = profile.get('basic_info', {})
        column_types = profile.get('column_types', {})
        stats_dict = analysis_data.get('statistics', {}).get('statistics', {})
        missing_data = analysis_data.get('missing_values', {})
        missing_summary = missing_data.get('summary', {})
        missing_columns = missing_data.get('columns', {})
        quality_score_data = analysis_data.get('quality', {}).get('score', {})
        correlations_data = analysis_data.get('correlations', {})
        pearson_data = correlations_data.get('pearson', {})
        strong_correlations = pearson_data.get('strong_correlations', [])
        normality_data = analysis_data.get('normality', {})
        normality_results = normality_data.get('results', {})
        outliers_data = analysis_data.get('outliers', {})
        outliers_results = outliers_data.get('results', {})
        insights_data = analysis_data.get('insights', {})
        
        # Compter les types
        numeric_cols = sum(1 for t in column_types.values() if t == 'numeric')
        categorical_cols = sum(1 for t in column_types.values() if t == 'categorical')
        text_cols = sum(1 for t in column_types.values() if t == 'text')
        datetime_cols = sum(1 for t in column_types.values() if t == 'datetime')
        
        numeric_columns_list = [col for col, t in column_types.items() if t == 'numeric']
        categorical_columns_list = [col for col, t in column_types.items() if t == 'categorical']
        
        # Données manquantes
        missing_columns_simple = {}
        for col, info in missing_columns.items():
            if info.get('missing_count', 0) > 0:
                missing_columns_simple[col] = {
                    'missing_count': info.get('missing_count', 0),
                    'missing_percentage': info.get('missing_percentage', 0),
                    'imputation_suggestion': info.get('imputation_suggestion', {})
                }
        
        # Scores qualité
        components = quality_score_data.get('components', {})
        
        # Analyses avancées
        constant_columns = advanced_analysis.get('constant_columns', [])
        quasi_constant_columns = advanced_analysis.get('quasi_constant_columns', [])
        id_columns = advanced_analysis.get('id_columns', [])
        high_cardinality_columns = advanced_analysis.get('high_cardinality_columns', [])
        highly_skewed_columns = advanced_analysis.get('highly_skewed_columns', [])
        advanced_summary = advanced_analysis.get('summary', {})
        
        # Analyses catégorielles
        categorical_columns_found = categorical_analysis.get('columns', [])
        categorical_summary = categorical_analysis.get('summary', {})
        categorical_insights = categorical_analysis.get('insights', [])
        
        # Insights
        insights_list = []
        insights_list.extend(insights_data.get('missing_insights', []))
        insights_list.extend(insights_data.get('numeric_insights', []))
        insights_list.extend(insights_data.get('correlation_insights', []))
        recommendations = insights_data.get('recommendations', [])
        
        return {
            # En-tête
            'filename': analysis_data.get('file_id', 'unknown'),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'execution_time': analysis_data.get('execution_time_seconds', 0),
            
            # Aperçu
            'rows': basic_info.get('rows', 0),
            'columns': basic_info.get('columns', 0),
            'memory_mb': basic_info.get('memory_usage_mb', 0),
            'numeric_cols': numeric_cols,
            'categorical_cols': categorical_cols,
            'text_cols': text_cols,
            'datetime_cols': datetime_cols,
            'numeric_columns_list': numeric_columns_list,
            'categorical_columns_list': categorical_columns_list[:10],
            
            # Qualité
            'quality_score': quality_score_data.get('total_score', 0),
            'quality_grade': quality_score_data.get('grade', 'N/A'),
            'quality_interpretation': quality_score_data.get('interpretation', ''),
            'completeness_score': components.get('completeness', {}).get('score', 0),
            'integrity_score': components.get('integrity', {}).get('score', 0),
            'consistency_score': components.get('consistency', {}).get('score', 0),
            'accuracy_score': components.get('accuracy', {}).get('score', 0),
            
            # Résumé
            'executive_summary': insights_data.get('executive_summary', ''),
            
            # Valeurs manquantes
            'total_cells': missing_summary.get('total_cells', 0),
            'total_missing': missing_summary.get('total_missing', 0),
            'missing_percentage': missing_summary.get('total_missing_percentage', 0),
            'columns_with_missing': missing_summary.get('columns_with_missing', 0),
            'rows_with_missing': missing_summary.get('rows_with_missing', 0),
            'rows_missing_percentage': missing_summary.get('rows_missing_percentage', 0),
            'missing_columns': missing_columns_simple,
            
            # Statistiques
            'statistics': stats_dict,
            
            # Corrélations
            'strong_correlations': strong_correlations[:10],
            
            # Normalité
            'normality': normality_results,
            'non_normal_count': len(normality_data.get('non_normal_columns', [])),
            
            # Outliers
            'outliers': outliers_results,
            'outliers_columns_count': len(outliers_data.get('columns_with_outliers', [])),
            
            # Analyses avancées
            'constant_columns': constant_columns,
            'quasi_constant_columns': quasi_constant_columns,
            'id_columns': id_columns,
            'high_cardinality_columns': high_cardinality_columns,
            'highly_skewed_columns': highly_skewed_columns,
            'advanced_quality_score': advanced_summary.get('data_quality_score', 0),
            'advanced_problematic_count': advanced_summary.get('problematic_columns_count', 0),
            
            # Analyses catégorielles
            'categorical_columns': categorical_columns_found,
            'categorical_binary_columns': categorical_summary.get('binary_columns', []),
            'categorical_balanced_columns': categorical_summary.get('balanced_columns', []),
            'categorical_insights': categorical_insights[:5],
            'categorical_analysis': categorical_analysis.get('analysis', {}),
            
            # Détection ML
            'ml_target_column': target_column,
            'ml_problem_type': problem_type.get('message', 'Non déterminé'),
            'ml_problem_confidence': problem_type.get('confidence', 'N/A'),
            'ml_model_suggestions': model_suggestions[:5],
            'ml_recommendations': ml_recommendations[:5],
            'ml_ready': ml_ready.get('ready', False),
            'ml_ready_level': ml_ready.get('ready_level', 'N/A'),
            'ml_issues': ml_ready.get('issues', []),
            'ml_target_analysis': target_analysis,
            'ml_feature_analysis': feature_analysis,
            'ml_preprocessing_steps': preprocessing_steps[:10],
            
            # Insights
            'insights_list': insights_list[:10],
            'recommendations': recommendations[:8],
            
            # Graphiques
            'histograms': histograms,
            'boxplots': boxplots,
            'pearson_heatmap': pearson_heatmap,
            'missing_heatmap': missing_heatmap
        }

    def generate_pdf(self, analysis_data: Dict[str, Any], df, output_path: str = None) -> bytes:
        """Génère un PDF complet avec toutes les analyses"""
        
        if not self.config:
            raise Exception("wkhtmltopdf non installé")
        
        print("📊 Génération des graphiques pour le PDF...")
        
        # Générer les images
        histograms_img = self._create_histograms_image(df)
        boxplots_img = self._create_boxplots_image(df)
        heatmap_img = self._create_correlation_heatmap_image(df)
        missing_img = self._create_missing_heatmap_image(df)
        
        # Préparer toutes les données avec les images
        template_data = self._prepare_complete_data(
            analysis_data, df,
            histograms=histograms_img,
            boxplots=boxplots_img,
            pearson_heatmap=heatmap_img,
            missing_heatmap=missing_img
        )
        
        # Générer le HTML
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        templates_dir = Path(__file__).parent.parent / "templates"
        env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template("report_compact.html")
        html_content = template.render(**template_data)
        
        # Sauvegarder le HTML de debug
        if output_path:
            debug_path = Path(output_path).parent / f"debug_{Path(output_path).stem}.html"
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"📄 HTML de débogage: {debug_path}")
        
        # Options PDF
        options = {
            'page-size': 'A4',
            'margin-top': '15mm',
            'margin-right': '10mm',
            'margin-bottom': '15mm',
            'margin-left': '10mm',
            'encoding': "UTF-8",
            'enable-local-file-access': None,
            'images': None,
            'javascript-delay': 5000,
            'load-error-handling': 'ignore',
        }
        
        if output_path:
            try:
                pdfkit.from_string(html_content, output_path, options=options, configuration=self.config)
                print("✅ PDF généré avec succès")
            except Exception as e:
                print(f"❌ ERREUR PDFKIT: {e}")
                import traceback
                traceback.print_exc()
                raise
            with open(output_path, 'rb') as f:
                return f.read()
        else:
            return pdfkit.from_string(html_content, False, options=options, configuration=self.config)
    
    def generate_and_save(self, analysis_data: Dict[str, Any], df, file_id: str) -> str:
        """Génère et sauvegarde le PDF"""
        output_dir = Config.PDF_REPORTS_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{file_id}_{timestamp}.pdf"
        output_path = output_dir / filename
        
        self.generate_pdf(analysis_data, df, str(output_path))
        
        return str(output_path)