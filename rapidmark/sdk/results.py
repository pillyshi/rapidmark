"""
RapidMark result loading utilities.

Provides type-safe loading of .result.rapidmark.json annotation results.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Union, Dict, List, Optional, Any
from pydantic import AliasChoices, BaseModel, Field


class EntityAnnotation(BaseModel):
    """NER entity annotation result."""
    id: str = Field(..., description="Entity ID")
    start: int = Field(..., description="Start position")
    end: int = Field(..., description="End position")
    text: str = Field(..., description="Entity text")
    label_id: str = Field(
        ...,
        description="Label ID",
        validation_alias=AliasChoices("labelId", "label_id"),
        serialization_alias="labelId"
    )
    timestamp: datetime = Field(..., description="Creation timestamp")

    model_config = {"extra": "ignore", "populate_by_name": True}


class TextResult(BaseModel):
    """Per-text annotation result."""
    status: str = Field(..., description="Status (pending, completed, excluded)")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Text attributes")
    entities: List[EntityAnnotation] = Field(default_factory=list, description="Entity list")

    model_config = {"extra": "ignore"}


class TaskInfo(BaseModel):
    """Task metadata."""
    task_type: str = Field(
        ...,
        description="Task type",
        validation_alias=AliasChoices("taskType", "task_type"),
        serialization_alias="taskType"
    )
    task_title: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("taskTitle", "task_title"),
        serialization_alias="taskTitle"
    )
    task_description: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("taskDescription", "task_description"),
        serialization_alias="taskDescription"
    )
    task_id: Optional[str] = Field(
        None,
        validation_alias=AliasChoices("taskId", "task_id"),
        serialization_alias="taskId"
    )
    labels: List[Dict[str, Any]] = Field(default_factory=list, description="Label definitions")
    total_texts: int = Field(
        default=0,
        validation_alias=AliasChoices("totalTexts", "total_texts"),
        serialization_alias="totalTexts"
    )
    completed_texts: int = Field(
        default=0,
        validation_alias=AliasChoices("completedTexts", "completed_texts"),
        serialization_alias="completedTexts"
    )
    completion_rate: float = Field(
        default=0.0,
        validation_alias=AliasChoices("completionRate", "completion_rate"),
        serialization_alias="completionRate"
    )
    total_annotations: int = Field(
        default=0,
        validation_alias=AliasChoices("totalAnnotations", "total_annotations"),
        serialization_alias="totalAnnotations"
    )
    total_comments: int = Field(
        default=0,
        validation_alias=AliasChoices("totalComments", "total_comments"),
        serialization_alias="totalComments"
    )
    export_format: str = Field(
        default="unified_v1",
        validation_alias=AliasChoices("exportFormat", "export_format"),
        serialization_alias="exportFormat"
    )
    exported_at: datetime = Field(
        ...,
        validation_alias=AliasChoices("exportedAt", "exported_at"),
        serialization_alias="exportedAt"
    )
    version: str = Field(default="1.0")

    model_config = {"extra": "ignore", "populate_by_name": True}


class RapidmarkResults(BaseModel):
    """Complete RapidMark result data."""
    task_info: TaskInfo = Field(
        ...,
        validation_alias=AliasChoices("taskInfo", "task_info"),
        serialization_alias="taskInfo"
    )
    results: Dict[str, TextResult] = Field(default_factory=dict)

    model_config = {"extra": "ignore", "populate_by_name": True}

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'RapidmarkResults':
        """
        Load results from a .result.rapidmark.json file.

        Args:
            file_path: Path to the results file

        Returns:
            RapidmarkResults instance
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Results file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.model_validate(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load results: {e}")

    def get_text_result(self, text_id: str) -> Optional[TextResult]:
        """Get result for a specific text ID."""
        return self.results.get(text_id)

    def get_all_entities(self) -> List[EntityAnnotation]:
        """Get all entity annotations across all texts."""
        entities = []
        for text_result in self.results.values():
            entities.extend(text_result.entities)
        return entities

    def filter_entities_by_label(self, label_id: str) -> List[EntityAnnotation]:
        """Get all entities with the specified label ID."""
        return [e for e in self.get_all_entities() if e.label_id == label_id]

    def get_completion_rate(self) -> float:
        """Get completion rate (0.0-1.0)."""
        if self.task_info.total_texts == 0:
            return 0.0
        return self.task_info.completed_texts / self.task_info.total_texts
