"""
Gestionnaire de cache pour les analyses
Évite de recalculer les analyses pour les mêmes fichiers
"""

import hashlib
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ..config import Config


class CacheManager:
    """
    Gestionnaire de cache pour les résultats d'analyse
    """
    
    def __init__(self):
        """Initialise le gestionnaire de cache"""
        self.cache_dir = Config.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Dossiers spécifiques
        self.analysis_dir = self.cache_dir / "analyses"
        self.reports_dir = self.cache_dir / "reports"
        self.analysis_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
    
    def compute_file_hash(self, file_path: str) -> str:
        """
        Calcule le hash SHA256 d'un fichier
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            Hash du fichier
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Lire le fichier par chunks pour les gros fichiers
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()[:16]  # 16 caractères suffisent
    
    def compute_dataframe_hash(self, df) -> str:
        """
        Calcule un hash à partir d'un DataFrame
        
        Args:
            df: DataFrame pandas
            
        Returns:
            Hash du DataFrame
        """
        # Convertir en bytes
        df_bytes = pickle.dumps(df)
        return hashlib.sha256(df_bytes).hexdigest()[:16]
    
    def get_analysis_cache_key(self, file_id: str, analysis_type: str) -> Path:
        """
        Retourne le chemin du fichier de cache pour une analyse
        
        Args:
            file_id: Identifiant du fichier
            analysis_type: Type d'analyse (statistics, correlations, etc.)
            
        Returns:
            Chemin du fichier de cache
        """
        return self.analysis_dir / f"{file_id}_{analysis_type}.pkl"
    
    def save_analysis(self, file_id: str, analysis_type: str, data: Any) -> bool:
        """
        Sauvegarde un résultat d'analyse dans le cache
        
        Args:
            file_id: Identifiant du fichier
            analysis_type: Type d'analyse
            data: Données à sauvegarder
            
        Returns:
            True si sauvegardé, False sinon
        """
        try:
            cache_path = self.get_analysis_cache_key(file_id, analysis_type)
            with open(cache_path, 'wb') as f:
                pickle.dump({
                    'data': data,
                    'cached_at': datetime.now().isoformat(),
                    'file_id': file_id,
                    'analysis_type': analysis_type
                }, f)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du cache: {e}")
            return False
    
    def load_analysis(self, file_id: str, analysis_type: str) -> Optional[Any]:
        """
        Charge un résultat d'analyse depuis le cache
        
        Args:
            file_id: Identifiant du fichier
            analysis_type: Type d'analyse
            
        Returns:
            Données ou None si non trouvé
        """
        try:
            cache_path = self.get_analysis_cache_key(file_id, analysis_type)
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    cached = pickle.load(f)
                return cached['data']
            return None
        except Exception as e:
            print(f"Erreur lors du chargement du cache: {e}")
            return None
    
    def save_report(self, file_id: str, report_type: str, content: str) -> bool:
        """
        Sauvegarde un rapport dans le cache
        
        Args:
            file_id: Identifiant du fichier
            report_type: Type de rapport (html, pdf)
            content: Contenu du rapport
            
        Returns:
            True si sauvegardé, False sinon
        """
        try:
            cache_path = self.reports_dir / f"{file_id}_{report_type}.html" if report_type == 'html' else self.reports_dir / f"{file_id}_{report_type}.pdf"
            with open(cache_path, 'wb') as f:
                f.write(content if isinstance(content, bytes) else content.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du rapport: {e}")
            return False
    
    def load_report(self, file_id: str, report_type: str) -> Optional[bytes]:
        """
        Charge un rapport depuis le cache
        
        Args:
            file_id: Identifiant du fichier
            report_type: Type de rapport (html, pdf)
            
        Returns:
            Contenu du rapport ou None
        """
        try:
            cache_path = self.reports_dir / f"{file_id}_{report_type}.html" if report_type == 'html' else self.reports_dir / f"{file_id}_{report_type}.pdf"
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Erreur lors du chargement du rapport: {e}")
            return None
    
    def clear_file_cache(self, file_id: str) -> bool:
        """
        Supprime tous les caches associés à un fichier
        
        Args:
            file_id: Identifiant du fichier
            
        Returns:
            True si supprimé, False sinon
        """
        try:
            # Supprimer les analyses
            for cache_file in self.analysis_dir.glob(f"{file_id}_*.pkl"):
                cache_file.unlink()
            
            # Supprimer les rapports
            for cache_file in self.reports_dir.glob(f"{file_id}_*"):
                cache_file.unlink()
            
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression du cache: {e}")
            return False
    
    def get_cache_info(self, file_id: str) -> Dict[str, Any]:
        """
        Retourne les informations sur le cache d'un fichier
        
        Args:
            file_id: Identifiant du fichier
            
        Returns:
            Informations sur le cache
        """
        analysis_files = list(self.analysis_dir.glob(f"{file_id}_*.pkl"))
        report_files = list(self.reports_dir.glob(f"{file_id}_*"))
        
        return {
            'file_id': file_id,
            'cached_analyses': [f.stem.replace(f"{file_id}_", "") for f in analysis_files],
            'cached_reports': [f.stem.replace(f"{file_id}_", "") for f in report_files],
            'analysis_count': len(analysis_files),
            'report_count': len(report_files)
        }


# Instance globale
cache_manager = CacheManager()