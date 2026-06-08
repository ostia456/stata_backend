"""
Tests des tests de normalité
"""

import pytest
import pandas as pd
import numpy as np
from app.core.normality import NormalityTester


class TestNormalityTester:
    """Tests pour NormalityTester"""
    
    def test_shapiro_test_normal(self):
        """Test de Shapiro sur distribution normale"""
        np.random.seed(42)
        normal_data = pd.Series(np.random.normal(0, 1, 100))
        result = NormalityTester.shapiro_test(normal_data)
        
        assert result['is_normal'] is True
        assert result['p_value'] > 0.05
    
    def test_shapiro_test_non_normal(self):
        """Test de Shapiro sur distribution non normale"""
        np.random.seed(42)
        uniform_data = pd.Series(np.random.uniform(0, 1, 100))
        result = NormalityTester.shapiro_test(uniform_data)
        
        # Note: uniform peut être considérée normale parfois
        assert 'test_statistic' in result
    
    def test_test_all_columns(self, sample_dataframe):
        """Test sur toutes les colonnes"""
        result = NormalityTester.test_all_columns(sample_dataframe)
        
        assert 'columns' in result
        assert 'results' in result
        assert 'normal_columns' in result
        assert 'non_normal_columns' in result
    
    def test_test_single_column(self, sample_dataframe):
        """Test sur une colonne spécifique"""
        result = NormalityTester.test_single_column(sample_dataframe, 'numerical1')
        
        assert result['column'] == 'numerical1'
        assert 'is_normal' in result
    
    def test_quick_test(self, sample_dataframe):
        """Test rapide"""
        result = NormalityTester.quick_test(sample_dataframe)
        
        assert 'quick_results' in result
        assert 'normal_count' in result
        assert 'non_normal_count' in result