"""
Middleware de sécurité : rate limiting, validation, sanitization
"""

import time
from collections import defaultdict
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple, Optional
import hashlib
import re

from ..config import Config


class RateLimiter:
    """
    Rate limiting pour prévenir les abus
    """
    
    def __init__(self):
        # Structure: {ip: [(timestamp, count), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        self.window_size = 60  # 60 secondes
        self.max_requests = 60  # 60 requêtes par minute
    
    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """
        Vérifie si le client a dépassé sa limite
        
        Returns:
            (allowed, remaining_requests)
        """
        now = time.time()
        window_start = now - self.window_size
        
        # Nettoyer les anciennes requêtes
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > window_start
        ]
        
        remaining = self.max_requests - len(self.requests[client_ip])
        
        if len(self.requests[client_ip]) >= self.max_requests:
            return False, remaining
        
        self.requests[client_ip].append(now)
        return True, remaining - 1


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de sécurité global
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = RateLimiter()
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        
        # Rate limiting
        allowed, remaining = self.rate_limiter.is_allowed(client_ip)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Trop de requêtes. Veuillez réessayer dans une minute."
            )
        
        # Ajouter les headers de rate limiting
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(self.rate_limiter.window_size)
        
        # Headers de sécurité
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class InputValidator:
    """
    Validation et nettoyage des entrées utilisateur
    """
    
    # Patterns de validation
    FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_.-]+$')
    FILE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9]{8}$')
    
    @classmethod
    def validate_filename(cls, filename: str) -> bool:
        """
        Valide le nom de fichier (prévention path traversal)
        """
        if not filename or len(filename) > 255:
            return False
        
        # Éviter les chemins relatifs
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        return bool(cls.FILENAME_PATTERN.match(filename))
    
    @classmethod
    def validate_file_id(cls, file_id: str) -> bool:
        """
        Valide le format du file_id
        """
        return bool(cls.FILE_ID_PATTERN.match(file_id)) if file_id else False
    
    @classmethod
    def sanitize_string(cls, value: str) -> str:
        """
        Nettoie une chaîne de caractères
        """
        if not value:
            return ""
        
        # Supprimer les caractères dangereux
        dangerous_chars = ['<', '>', '&', '"', "'", ';', '`', '$', '(', ')', '[', ']', '{', '}']
        for char in dangerous_chars:
            value = value.replace(char, '')
        
        # Limiter la longueur
        return value[:1000]
    
    @classmethod
    def validate_file_size(cls, content: bytes, max_size_mb: int = None) -> bool:
        """
        Valide la taille du fichier
        """
        max_size_mb = max_size_mb or Config.MAX_FILE_SIZE_MB
        max_bytes = max_size_mb * 1024 * 1024
        return len(content) <= max_bytes


class FileSecurity:
    """
    Sécurité pour les fichiers uploadés
    """
    
    # Signatures magiques pour validation des fichiers
    MAGIC_SIGNATURES = {
        '.csv': [b',', b';', b'\t', b'\n'],  # CSV peut commencer par séparateur
        '.xlsx': [b'PK\x03\x04'],  # Signature ZIP des fichiers Excel
        '.xls': [b'\xD0\xCF\x11\xE0', b'\x09\x08\x10\x00', b'\xFD\xFF\xFF\xFF']  # Signature OLE
    }
    
    # Types MIME autorisés
    ALLOWED_MIME_TYPES = {
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    
    @classmethod
    def validate_magic_signature(cls, content: bytes, extension: str) -> bool:
        """
        Vérifie la signature magique du fichier
        """
        extension = extension.lower()
        if extension not in cls.MAGIC_SIGNATURES:
            return True  # Si signature inconnue, on accepte
        
        signatures = cls.MAGIC_SIGNATURES[extension]
        
        # Vérifier les premiers octets
        for sig in signatures:
            if len(content) >= len(sig) and content[:len(sig)] == sig:
                return True
        
        return False
    
    @classmethod
    def validate_mime_type(cls, content: bytes, filename: str) -> bool:
        """
        Valide le type MIME du fichier
        """
        import magic
        
        try:
            mime = magic.from_buffer(content[:1024], mime=True)
            return mime in cls.ALLOWED_MIME_TYPES
        except:
            # Fallback: vérifier l'extension
            ext = filename.split('.')[-1].lower()
            return ext in ['csv', 'xlsx', 'xls']
    
    @classmethod
    def scan_for_malware(cls, content: bytes) -> bool:
        """
        Scan basique pour détecter du contenu malveillant
        """
        # Patterns suspects
        suspicious_patterns = [
            b'<script', b'javascript:', b'onerror=', b'onload=',
            b'<?php', b'<%', b'<jsp', b'<asp',
            b'powershell', b'cmd.exe', b'/bin/bash',
            b'exec(', b'eval(', b'system('
        ]
        
        content_lower = content.lower()
        for pattern in suspicious_patterns:
            if pattern.lower() in content_lower:
                return False
        
        return True


class APIKeyAuth(HTTPBearer):
    """
    Authentification par API Key (optionnel)
    """
    
    def __init__(self, api_key: str = None, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.api_key = api_key or Config.API_KEY if hasattr(Config, 'API_KEY') else None
    
    async def __call__(self, request: Request):
        # Si pas de clé configurée, on accepte toutes les requêtes
        if not self.api_key:
            return None
        
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if not credentials:
            raise HTTPException(status_code=403, detail="API Key manquante")
        
        if credentials.credentials != self.api_key:
            raise HTTPException(status_code=403, detail="API Key invalide")
        
        return credentials

import os
# Configuration de sécurité (à ajouter dans config.py)
def setup_security_config():
    """
    Configure les variables de sécurité dans Config
    """
    if not hasattr(Config, 'API_KEY'):
        import secrets
        Config.API_KEY = os.getenv('API_KEY', secrets.token_urlsafe(32))
    
    if not hasattr(Config, 'ENABLE_RATE_LIMITING'):
        Config.ENABLE_RATE_LIMITING = os.getenv('ENABLE_RATE_LIMITING', 'True').lower() == 'true'