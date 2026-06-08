"""
Module core - Analyses métier
"""

from .file_analyzer import FileAnalyzer
from .type_detector import TypeDetector
from .dataset_profiler import DatasetProfiler
from .exceptions import (
    AutoEDAException,
    UploadError,
    InvalidFileTypeError,
    FileTooLargeError,
    FileCorruptedError,
    AnalysisError,
    NotFoundError
)

__all__ = [
    'FileAnalyzer',
    'TypeDetector',
    'DatasetProfiler',
    'AutoEDAException',
    'UploadError',
    'InvalidFileTypeError',
    'FileTooLargeError',
    'FileCorruptedError',
    'AnalysisError',
    'NotFoundError'
]