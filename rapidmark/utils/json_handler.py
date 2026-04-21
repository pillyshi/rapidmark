"""JSON handling utilities for NLP Annotation Tool."""

import json
from typing import Dict, Any, Optional
from pathlib import Path


class JSONHandler:
    """Utilities for handling JSON files and data."""
    
    @staticmethod
    def load_json(file_path: Path) -> Dict[str, Any]:
        """
        Load JSON data from file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Loaded JSON data as dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: Path, indent: int = 2) -> None:
        """
        Save data to JSON file.
        
        Args:
            data: Data to save
            file_path: Output file path
            indent: JSON formatting indentation
        """
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_keys: list) -> bool:
        """
        Validate that JSON data contains required keys.
        
        Args:
            data: JSON data to validate
            required_keys: List of required top-level keys
            
        Returns:
            True if all required keys are present
        """
        return all(key in data for key in required_keys)
    
    @staticmethod
    def merge_json_files(file_paths: list, output_path: Path) -> None:
        """
        Merge multiple JSON files into one.
        
        Args:
            file_paths: List of JSON file paths to merge
            output_path: Output file path
        """
        merged_data = {}
        
        for file_path in file_paths:
            data = JSONHandler.load_json(Path(file_path))
            merged_data.update(data)
        
        JSONHandler.save_json(merged_data, output_path)