"""
Schémas Pydantic pour les analyses statistiques
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class NumericStats(BaseModel):
    """Statistiques pour une colonne numérique"""
    count: int = Field(..., description="Nombre de valeurs non-nulles")
    null_count: int = Field(..., description="Nombre de valeurs nulles")
    null_percentage: float = Field(..., description="Pourcentage de valeurs nulles")
    min: float = Field(..., description="Valeur minimale")
    max: float = Field(..., description="Valeur maximale")
    mean: float = Field(..., description="Moyenne")
    median: float = Field(..., description="Médiane")
    std: float = Field(..., description="Écart-type")
    var: float = Field(..., description="Variance")
    sum: float = Field(..., description="Somme")
    q1: float = Field(..., description="Premier quartile (25%)")
    q2: float = Field(..., description="Deuxième quartile (50% = médiane)")
    q3: float = Field(..., description="Troisième quartile (75%)")
    iqr: float = Field(..., description="Écart interquartile (Q3 - Q1)")
    percentile_5: float = Field(..., description="5ème percentile")
    percentile_95: float = Field(..., description="95ème percentile")
    percentile_99: float = Field(..., description="99ème percentile")
    skewness: float = Field(..., description="Asymétrie")
    kurtosis: float = Field(..., description="Aplatissement")
    skewness_interpretation: str = Field(..., description="Interprétation de l'asymétrie")
    kurtosis_interpretation: str = Field(..., description="Interprétation de l'aplatissement")


class StatisticsResponse(BaseModel):
    """Réponse complète des statistiques"""
    file_id: Optional[str] = None
    numeric_columns: List[str]
    statistics: Dict[str, NumericStats]
    summary: Dict[str, Any]
    data_types: Dict[str, int]
    shape_info: Dict[str, int]


class FastStatsResponse(BaseModel):
    """Version rapide des statistiques"""
    file_id: Optional[str] = None
    description: Dict[str, Any]
    medians: Dict[str, float]
    numeric_columns: List[str]