"""
Schémas Pydantic pour les analyses de valeurs manquantes
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ColumnMissingInfo(BaseModel):
    """Informations sur les valeurs manquantes d'une colonne"""
    name: str
    dtype: str
    total_rows: int
    missing_count: int
    present_count: int
    missing_percentage: float
    present_percentage: float
    missing_pattern: str
    imputation_suggestion: Dict[str, Any]
    impact: str
    severity: str


class MissingSummary(BaseModel):
    """Résumé global des valeurs manquantes"""
    total_cells: int
    total_missing: int
    total_missing_percentage: float
    columns_with_missing: int
    columns_without_missing: int
    rows_with_missing: int
    rows_without_missing: int
    rows_missing_percentage: float


class MissingResponse(BaseModel):
    """Réponse complète pour l'analyse des valeurs manquantes"""
    file_id: Optional[str] = None
    summary: MissingSummary
    columns: Dict[str, ColumnMissingInfo]
    high_missing_columns: List[str]
    critical_missing_columns: List[str]
    missing_correlation: Dict[str, Any]
    recommendations: List[Dict[str, Any]]