"""
Schémas Pydantic pour les tests de normalité
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ShapiroResult(BaseModel):
    """Résultat du test de Shapiro-Wilk"""
    test_statistic: Optional[float] = None
    p_value: Optional[float] = None
    is_normal: Optional[bool] = None
    sample_size: Optional[int] = None
    original_size: Optional[int] = None
    interpretation: Optional[str] = None
    recommendation: Optional[str] = None
    error: Optional[str] = None


class NormalityResponse(BaseModel):
    """Réponse complète des tests de normalité"""
    file_id: Optional[str] = None
    columns: List[str]
    results: Dict[str, ShapiroResult]
    normal_columns: List[str]
    non_normal_columns: List[str]
    summary: Dict[str, Any]
    recommendations: List[Dict[str, Any]]


class QQDataResponse(BaseModel):
    """Données pour Q-Q plot"""
    theoretical: List[float]
    observed: List[float]
    sample_size: int