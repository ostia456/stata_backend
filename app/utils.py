"""
Fonctions utilitaires pour l'application
"""

import numpy as np
import pandas as pd
from typing import Any, Dict, List


def convert_numpy_types(obj: Any) -> Any:
    """
    Convertit les types numpy en types Python natifs pour la sérialisation JSON
    
    Args:
        obj: Objet à convertir
        
    Returns:
        Objet avec types Python natifs
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    else:
        return obj


def clean_for_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nettoie un dictionnaire pour le rendre sérialisable en JSON
    
    Args:
        data: Dictionnaire à nettoyer
        
    Returns:
        Dictionnaire sérialisable
    """
    return convert_numpy_types(data)