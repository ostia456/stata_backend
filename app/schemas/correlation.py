"""
Schémas Pydantic pour les analyses de corrélation
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class StrongCorrelation(BaseModel):
    """Corrélation forte entre deux variables"""
    var1: str
    var2: str
    correlation: float
    strength: str
    direction: str
    absolute_value: float


class CorrelationMatrix(BaseModel):
    """Matrice de corrélation"""
    method: str
    columns: List[str]
    matrix: Dict[str, Dict[str, float]]
    strong_correlations: List[StrongCorrelation]
    summary: Dict[str, Any]


class CorrelationResponse(BaseModel):
    """Réponse complète pour les corrélations"""
    numeric_columns: List[str]
    pearson: Optional[CorrelationMatrix] = None
    spearman: Optional[CorrelationMatrix] = None
    comparison: Optional[Dict[str, Any]] = None


class TargetCorrelationResponse(BaseModel):
    """Corrélations avec une colonne cible"""
    target: str
    correlations: List[Dict[str, Any]]
    best_predictor: Optional[str] = None
    best_correlation: Optional[float] = None