"""
Exceptions personnalisées pour l'application
"""

class AutoEDAException(Exception):
    """Exception de base pour l'application"""
    pass

class UploadError(AutoEDAException):
    """Erreur liée à l'upload de fichier"""
    pass

class InvalidFileTypeError(UploadError):
    """Type de fichier non supporté"""
    pass

class FileTooLargeError(UploadError):
    """Fichier trop volumineux"""
    pass

class FileCorruptedError(UploadError):
    """Fichier corrompu ou illisible"""
    pass

class AnalysisError(AutoEDAException):
    """Erreur lors de l'analyse des données"""
    pass

class NotFoundError(AutoEDAException):
    """Ressource non trouvée"""
    pass