"""
Schémas Pydantic pour les réponses du dataset
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class BasicInfo(BaseModel):
    """Informations basiques du dataset"""
    rows: int = Field(..., description="Nombre de lignes")
    columns: int = Field(..., description="Nombre de colonnes")
    total_cells: int = Field(..., description="Nombre total de cellules")
    memory_usage_mb: float = Field(..., description="Mémoire utilisée en MB")
    has_missing: bool = Field(..., description="Présence de valeurs manquantes")
    total_missing_cells: int = Field(..., description="Nombre de cellules manquantes")
    missing_percentage: float = Field(..., description="Pourcentage de valeurs manquantes")


class ColumnTypeInfo(BaseModel):
    """Information de type d'une colonne"""
    name: str
    detected_type: str
    dtype: str
    unique_count: int
    null_count: int
    null_percentage: float
    memory_usage_bytes: int


class DatasetOverviewResponse(BaseModel):
    """Réponse pour l'endpoint /overview"""
    file_id: Optional[str] = None
    rows: int
    columns: int
    memory_usage_mb: float
    column_types: Dict[str, str]
    numeric_columns: List[str]
    categorical_columns: List[str]
    text_columns: List[str]
    datetime_columns: List[str]
    boolean_columns: List[str]
    empty_columns: List[str]


class DatasetProfileResponse(BaseModel):
    """Réponse complète pour le profil du dataset"""
    file_id: Optional[str] = None
    basic_info: BasicInfo
    column_types: Dict[str, str]
    column_summary: Dict[str, List[str]]
    columns_detail: Dict[str, ColumnTypeInfo]
    memory_info: Dict[str, Any]
    sample_data: Dict[str, Any]