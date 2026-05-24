"""
RapidMark result models (canonical result v1).
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Union, Optional, Literal
from pydantic import BaseModel, Field


class EntityGroup(BaseModel):
    """Entity group (co-reference cluster)."""
    id: str = Field(..., description="Group ID, unique within the text")
    entity_ids: list[str] = Field(..., description="Entity IDs belonging to this group")

    model_config = {"extra": "ignore"}


class EntityAnnotation(BaseModel):
    """NER entity annotation."""
    id: str = Field(..., description="Entity ID, unique within the text")
    start: int = Field(..., description="Start character offset (inclusive)")
    end: int = Field(..., description="End character offset (exclusive)")
    quote: str = Field(..., description="Entity surface string")
    label_id: str = Field(..., description="Label ID matching labels[].id in the task file")

    model_config = {"extra": "ignore"}


class TextResult(BaseModel):
    """Per-text annotation result."""
    id: str = Field(..., description="Text ID matching texts[].id in the task file")
    status: str = Field(..., description="Annotation status (pending, completed, excluded)")
    entities: list[EntityAnnotation] = Field(default_factory=list, description="NER entity annotations")
    groups: list[EntityGroup] = Field(default_factory=list, description="Entity co-reference groups")
    label_id: Optional[str] = Field(default=None, description="Assigned label ID (classification tasks only)")

    model_config = {"extra": "ignore"}


class RapidmarkResult(BaseModel):
    """Single RapidMark annotation result file (canonical result v1)."""
    task_id: str = Field(..., description="ID of the task this result belongs to")
    result_version: Literal[1] = Field(default=1, description="Schema version, always 1")
    worker: Optional[str] = Field(default=None, description="Annotator identifier")
    exported_at: datetime = Field(..., description="ISO 8601 UTC timestamp of export")
    texts: list[TextResult] = Field(..., description="Per-text annotation results")

    model_config = {"extra": "ignore"}

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "RapidmarkResult":
        """Load result from a .result.rapidmark.json file."""
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
        return next((t for t in self.texts if t.id == text_id), None)

    def get_all_entities(self) -> list[EntityAnnotation]:
        """Get all entity annotations across all texts."""
        entities = []
        for text in self.texts:
            entities.extend(text.entities)
        return entities

    def filter_entities_by_label(self, label_id: str) -> list[EntityAnnotation]:
        """Get all entities with the specified label ID."""
        return [e for e in self.get_all_entities() if e.label_id == label_id]

    def filter_texts_by_label(self, label_id: str) -> list[TextResult]:
        """Get all texts assigned the specified label ID (classification tasks)."""
        return [t for t in self.texts if t.label_id == label_id]

    def get_completion_rate(self) -> float:
        """Get completion rate (0.0-1.0)."""
        if not self.texts:
            return 0.0
        completed = sum(1 for t in self.texts if t.status == "completed")
        return completed / len(self.texts)


RapidmarkResults = list[RapidmarkResult]
