"""
Tests des corrélations
"""

import pytest
from app.core.correlations import CorrelationAnalyzer


class TestCorrelationAnalyzer:
    """Tests pour CorrelationAnalyzer"""
    
    def test_pearson_correlation(self, sample_dataframe):
        """Test de la corrélation de Pearson"""
        result = CorrelationAnalyzer.calculate_pearson(sample_dataframe)
        
        assert result['method'] == 'pearson'
        assert len(result['columns']) > 0
        assert 'matrix' in result
    
    def test_spearman_correlation(self, sample_dataframe):
        """Test de la corrélation de Spearman"""
        result = CorrelationAnalyzer.calculate_spearman(sample_dataframe)
        
        assert result['method'] == 'spearman'
        assert len(result['columns']) > 0
    
    def test_both_correlations(self, sample_dataframe):
        """Test des deux méthodes"""
        result = CorrelationAnalyzer.calculate_both(sample_dataframe)
        
        assert 'pearson' in result
        assert 'spearman' in result
        assert 'comparison' in result
    
    def test_strong_correlations_detection(self, sample_dataframe):
        """Test de détection des corrélations fortes"""
        result = CorrelationAnalyzer.calculate_pearson(sample_dataframe)
        
        strong_corrs = result.get('strong_correlations', [])
        # Vérifier que le format est correct
        for corr in strong_corrs:
            assert 'var1' in corr
            assert 'var2' in corr
            assert 'correlation' in corr
    
    def test_correlation_with_target(self, sample_dataframe):
        """Test des corrélations avec une cible"""
        result = CorrelationAnalyzer.get_correlation_with_target(sample_dataframe, 'target')
        
        assert result['target'] == 'target'
        assert 'correlations' in result
        assert len(result['correlations']) > 0