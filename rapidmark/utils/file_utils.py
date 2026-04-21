"""File handling utilities for NLP Annotation Tool."""

from pathlib import Path
from typing import List, Optional
import shutil
import tempfile


class FileUtils:
    """Utilities for file operations."""
    
    @staticmethod
    def ensure_directory(directory: Path) -> None:
        """
        Ensure directory exists, create if it doesn't.
        
        Args:
            directory: Directory path to ensure exists
        """
        directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_files_by_pattern(directory: Path, pattern: str) -> List[Path]:
        """
        Get all files in directory matching pattern.
        
        Args:
            directory: Directory to search
            pattern: Glob pattern (e.g., '*.json')
            
        Returns:
            List of matching file paths
        """
        if not directory.exists():
            return []
        
        return list(directory.glob(pattern))
    
    @staticmethod
    def copy_file(source: Path, destination: Path) -> None:
        """
        Copy file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
        """
        # Ensure destination directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    
    @staticmethod
    def create_temp_file(suffix: str = '.html') -> Path:
        """
        Create a temporary file.
        
        Args:
            suffix: File suffix/extension
            
        Returns:
            Path to temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        temp_file.close()
        return Path(temp_file.name)
    
    @staticmethod
    def validate_file_extension(file_path: Path, allowed_extensions: List[str]) -> bool:
        """
        Validate that file has allowed extension.
        
        Args:
            file_path: File path to validate
            allowed_extensions: List of allowed extensions (e.g., ['.json', '.txt'])
            
        Returns:
            True if extension is allowed
        """
        return file_path.suffix.lower() in [ext.lower() for ext in allowed_extensions]
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """
        Get file size in bytes.
        
        Args:
            file_path: File path
            
        Returns:
            File size in bytes
        """
        if not file_path.exists():
            return 0
        return file_path.stat().st_size
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        Clean filename by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Cleaned filename
        """
        # Remove invalid characters for filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing whitespace and dots
        filename = filename.strip(' .')
        
        # Ensure filename is not empty
        if not filename:
            filename = 'untitled'
        
        return filename