"""
Tests des endpoints API
"""

import pytest
import tempfile
import pandas as pd


class TestUploadEndpoint:
    """Tests pour l'endpoint d'upload"""
    
    def test_upload_valid_csv(self, client, sample_csv_file):
        """Test upload CSV valide"""
        with open(sample_csv_file, 'rb') as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("test.csv", f, "text/csv")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert 'file_id' in data
        assert data['status'] == 'uploaded'
    
    def test_upload_invalid_file(self, client):
        """Test upload fichier invalide"""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.txt", b"content", "text/plain")}
        )
        
        assert response.status_code == 415  # Unsupported media type
    
    def test_upload_empty_file(self, client):
        """Test upload fichier vide"""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("empty.csv", b"", "text/csv")}
        )
        
        assert response.status_code == 400  # Bad request


class TestAnalysisEndpoint:
    """Tests pour les endpoints d'analyse"""
    
    def test_analysis_overview(self, client, uploaded_file_id):
        """Test de l'aperçu"""
        if not uploaded_file_id:
            pytest.skip("Upload failed")
        
        response = client.get(f"/api/v1/analysis/{uploaded_file_id}/overview")
        
        assert response.status_code == 200
        data = response.json()
        assert 'rows' in data
        assert 'columns' in data
    
    def test_analysis_statistics(self, client, uploaded_file_id):
        """Test des statistiques"""
        if not uploaded_file_id:
            pytest.skip("Upload failed")
        
        response = client.get(f"/api/v1/statistics/{uploaded_file_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert 'statistics' in data
    
    def test_analysis_missing(self, client, uploaded_file_id):
        """Test des valeurs manquantes"""
        if not uploaded_file_id:
            pytest.skip("Upload failed")
        
        response = client.get(f"/api/v1/missing/{uploaded_file_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert 'summary' in data
    
    def test_analysis_correlations(self, client, uploaded_file_id):
        """Test des corrélations"""
        if not uploaded_file_id:
            pytest.skip("Upload failed")
        
        response = client.get(f"/api/v1/correlations/{uploaded_file_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert 'pearson' in data or 'error' in data


class TestHealthEndpoint:
    """Tests pour l'endpoint health"""
    
    def test_health_check(self, client):
        """Test health check"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
    
    def test_public_health(self, client):
        """Test health public"""
        response = client.get("/api/v1/public/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
    
    def test_version(self, client):
        """Test version endpoint"""
        response = client.get("/api/v1/public/version")
        
        assert response.status_code == 200
        data = response.json()
        assert 'version' in data['app']


class TestReportEndpoint:
    """Tests pour les endpoints de rapport"""
    
    def test_html_report_generation(self, client, uploaded_file_id):
        """Test génération HTML"""
        if not uploaded_file_id:
            pytest.skip("Upload failed")
        
        response = client.get(f"/api/v1/reports/html/{uploaded_file_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert 'html_content' in data or 'report_path' in data


class TestCacheEndpoint:
    """Tests pour les endpoints de cache"""
    
    def test_cache_info(self, client, uploaded_file_id):
        """Test info cache"""
        if not uploaded_file_id:
            pytest.skip("Upload failed")
        
        response = client.get(f"/api/v1/cache/{uploaded_file_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert 'cached_analyses' in data