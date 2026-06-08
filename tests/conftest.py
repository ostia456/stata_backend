"""
Configuration des tests pytest
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Client de test FastAPI"""
    return TestClient(app)


@pytest.fixture
def sample_dataframe():
    """Crée un DataFrame de test"""
    np.random.seed(42)
    n = 100
    
    df = pd.DataFrame({
        'id': range(n),
        'numerical1': np.random.randn(n),
        'numerical2': np.random.randn(n) * 10,
        'categorical1': np.random.choice(['A', 'B', 'C'], n),
        'categorical2': np.random.choice(['X', 'Y'], n),
        'target': np.random.choice([0, 1], n, p=[0.6, 0.4]),
        'with_missing': np.random.choice([1, 2, np.nan], n, p=[0.45, 0.45, 0.1])
    })
    return df


@pytest.fixture
def sample_csv_file(sample_dataframe):
    """Crée un fichier CSV temporaire"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_dataframe.to_csv(f.name, index=False)
        return f.name


@pytest.fixture
def uploaded_file_id(client, sample_csv_file):
    """Upload un fichier et retourne son ID"""
    with open(sample_csv_file, 'rb') as f:
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.csv", f, "text/csv")}
        )
    
    # Nettoyer le fichier temporaire
    os.unlink(sample_csv_file)
    
    if response.status_code == 200:
        return response.json()['file_id']
    return None