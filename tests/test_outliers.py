"""
Tests de détection d'outliers
"""

import pytest
import pandas as pd
import numpy as np
from app.core.outliers import OutlierDetector


class TestOutlierDetector:
    """Tests pour OutlierDetector"""
    
    def test_iqr_detection(self, sample_dataframe):
        """Test de détection IQR"""
        result = OutlierDetector.detect_iqr(sample_dataframe['numerical1'])
        
        assert result['method'] == 'iqr'
        assert 'outlier_count' in result
        assert 'outlier_percentage' in result
    
    def test_zscore_detection(self, sample_dataframe):
        """Test de détection Z-score"""
        result = OutlierDetector.detect_zscore(sample_dataframe['numerical1'])
        
        assert result['method'] == 'zscore'
        assert 'outlier_count' in result
    
    def test_both_detection(self, sample_dataframe):
        """Test des deux méthodes"""
        result = OutlierDetector.detect_both(sample_dataframe['numerical1'])
        
        assert 'iqr' in result
        assert 'zscore' in result
        assert 'comparison' in result
    
    def test_analyze_all_columns(self, sample_dataframe):
        """Test sur toutes les colonnes"""
        result = OutlierDetector.analyze_all_columns(sample_dataframe)
        
        assert 'columns' in result
        assert 'results' in result
        assert 'columns_with_outliers' in result
    
    def test_quick_outlier_analysis(self, sample_dataframe):
        """Test rapide"""
        result = OutlierDetector.quick_outlier_analysis(sample_dataframe)
        
        assert 'quick_results' in result
        assert 'columns_with_outliers' in result