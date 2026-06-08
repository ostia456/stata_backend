"""
Service de gestion des métadonnées et historique des analyses
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from uuid import uuid4

from ..config import Config


class MetadataService:
    """
    Service pour gérer l'historique des analyses et les métadonnées
    """
    
    def __init__(self):
        self.metadata_file = Config.METADATA_DIR / "reports_metadata.json"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Crée le fichier de métadonnées s'il n'existe pas"""
        if not self.metadata_file.exists():
            self._save_metadata([])
    
    def _load_metadata(self) -> List[Dict[str, Any]]:
        """Charge les métadonnées depuis le fichier"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_metadata(self, metadata: List[Dict[str, Any]]):
        """Sauvegarde les métadonnées dans le fichier"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
    
    def add_analysis(self, file_id: str, filename: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ajoute une analyse à l'historique
        
        Args:
            file_id: Identifiant du fichier
            filename: Nom du fichier original
            results: Résultats de l'analyse
            
        Returns:
            Métadonnées de l'analyse ajoutée
        """
        metadata = self._load_metadata()
        
        # Extraire les informations clés
        quality = results.get('quality', {}).get('score', {})
        quality_score = quality.get('total_score', 0) if isinstance(quality, dict) else 0
        quality_grade = quality.get('grade', 'N/A') if isinstance(quality, dict) else 'N/A'
        
        profile = results.get('profile', {})
        basic_info = profile.get('basic_info', {})
        
        # Créer l'entrée d'historique
        entry = {
            'analysis_id': str(uuid4())[:8],
            'file_id': file_id,
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            'rows': basic_info.get('rows', 0),
            'columns': basic_info.get('columns', 0),
            'quality_score': quality_score,
            'quality_grade': quality_grade,
            'execution_time': results.get('execution_time_seconds', 0),
            'from_cache': results.get('from_cache', False),
            'report_generated': False,
            'report_path': None
        }
        
        metadata.append(entry)
        self._save_metadata(metadata)
        
        return entry
    
    def update_report_info(self, file_id: str, report_type: str, report_path: str):
        """
        Met à jour les informations de rapport pour une analyse
        
        Args:
            file_id: Identifiant du fichier
            report_type: Type de rapport ('html' ou 'pdf')
            report_path: Chemin du rapport
        """
        metadata = self._load_metadata()
        
        for entry in metadata:
            if entry['file_id'] == file_id:
                entry['report_generated'] = True
                entry[f'{report_type}_report_path'] = report_path
                entry[f'{report_type}_generated_at'] = datetime.now().isoformat()
                break
        
        self._save_metadata(metadata)
    
    def get_analysis_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retourne l'historique des analyses
        
        Args:
            limit: Nombre maximum d'analyses à retourner
            
        Returns:
            Liste des analyses (triées par date décroissante)
        """
        metadata = self._load_metadata()
        
        # Trier par timestamp décroissant
        metadata.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return metadata[:limit]
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une analyse par son ID
        
        Args:
            analysis_id: Identifiant de l'analyse
            
        Returns:
            Métadonnées de l'analyse ou None
        """
        metadata = self._load_metadata()
        
        for entry in metadata:
            if entry['analysis_id'] == analysis_id:
                return entry
        
        return None
    
    def get_analysis_by_file_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère l'analyse par file_id
        
        Args:
            file_id: Identifiant du fichier
            
        Returns:
            Métadonnées de l'analyse ou None
        """
        metadata = self._load_metadata()
        
        for entry in metadata:
            if entry['file_id'] == file_id:
                return entry
        
        return None
    
    def get_all_analyses(self) -> List[Dict[str, Any]]:
        """
        Retourne toutes les analyses
        
        Returns:
            Liste complète des analyses
        """
        return self._load_metadata()
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Supprime une analyse de l'historique
        
        Args:
            analysis_id: Identifiant de l'analyse
            
        Returns:
            True si supprimé, False sinon
        """
        metadata = self._load_metadata()
        
        for i, entry in enumerate(metadata):
            if entry['analysis_id'] == analysis_id:
                metadata.pop(i)
                self._save_metadata(metadata)
                return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne des statistiques sur l'historique
        
        Returns:
            Statistiques des analyses
        """
        metadata = self._load_metadata()
        
        if not metadata:
            return {
                'total_analyses': 0,
                'average_quality_score': 0,
                'best_quality': None,
                'worst_quality': None,
                'most_analyzed_file': None,
                'analyses_by_day': {},
                'reports_generated': 0
            }
        
        # Calculer la moyenne des scores
        scores = [e.get('quality_score', 0) for e in metadata if e.get('quality_score', 0) > 0]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Meilleur et pire score
        best = max(metadata, key=lambda x: x.get('quality_score', 0)) if metadata else None
        worst = min(metadata, key=lambda x: x.get('quality_score', 0)) if metadata else None
        
        # Fichier le plus analysé
        file_counts = {}
        for entry in metadata:
            filename = entry.get('filename', 'unknown')
            file_counts[filename] = file_counts.get(filename, 0) + 1
        most_analyzed = max(file_counts.items(), key=lambda x: x[1])[0] if file_counts else None
        
        # Analyses par jour
        analyses_by_day = {}
        for entry in metadata:
            date = entry.get('timestamp', '')[:10]
            analyses_by_day[date] = analyses_by_day.get(date, 0) + 1
        
        # Nombre de rapports générés
        reports_count = sum(1 for e in metadata if e.get('report_generated', False))
        
        return {
            'total_analyses': len(metadata),
            'average_quality_score': round(avg_score, 2),
            'best_quality': {
                'file': best.get('filename'),
                'score': best.get('quality_score'),
                'date': best.get('timestamp')
            } if best else None,
            'worst_quality': {
                'file': worst.get('filename'),
                'score': worst.get('quality_score'),
                'date': worst.get('timestamp')
            } if worst else None,
            'most_analyzed_file': most_analyzed,
            'analyses_by_day': analyses_by_day,
            'reports_generated': reports_count
        }


# Instance globale
metadata_service = MetadataService()