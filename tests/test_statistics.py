"""
Tests des statistiques descriptives
"""

import pytest
from app.core.statistics import StatisticsCalculator, DescriptiveStats


class TestStatisticsCalculator:
    """Tests pour StatisticsCalculator"""
    
    def test_numeric_stats_basic(self, sample_dataframe):
        """Test des statistiques de base"""
        stats = StatisticsCalculator.calculate_numeric_stats(sample_dataframe['numerical1'])
        
        assert 'count' in stats
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert stats['count'] > 0
    
    def test_numeric_stats_with_missing(self, sample_dataframe):
        """Test avec valeurs manquantes"""
        stats = StatisticsCalculator.calculate_numeric_stats(sample_dataframe['with_missing'])
        
        assert stats['null_count'] > 0
        assert stats['null_percentage'] > 0
        assert stats['count'] == len(sample_dataframe) - stats['null_count']
    
    def test_all_numeric_stats(self, sample_dataframe):
        """Test de toutes les colonnes numériques"""
        results = StatisticsCalculator.calculate_all_numeric_stats(sample_dataframe)
        
        assert len(results) == len(sample_dataframe.select_dtypes(include=['number']).columns)
        assert 'numerical1' in results
        assert 'numerical2' in results


class TestDescriptiveStats:
    """Tests pour DescriptiveStats"""
    
    def test_compute_all(self, sample_dataframe):
        """Test de compute_all"""
        stats = DescriptiveStats(sample_dataframe)
        result = stats.compute_all()
        
        assert 'numeric_columns' in result
        assert 'statistics' in result
        assert 'shape_info' in result
    
    def test_compute_for_column(self, sample_dataframe):
        """Test pour une colonne spécifique"""
        stats = DescriptiveStats(sample_dataframe)
        result = stats.compute_for_column('numerical1')
        
        assert 'mean' in result
        assert 'median' in result
    
    def test_get_fast_stats(self, sample_dataframe):
        """Test des stats rapides"""
        stats = DescriptiveStats(sample_dataframe)
        result = stats.get_fast_stats()
        
        assert 'description' in result
        assert 'medians' in result