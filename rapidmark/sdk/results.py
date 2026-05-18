"""
RapidMark result loading utilities.

Provides type-safe loading of .result.rapidmark.json annotation results.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Union, Dict, List, Optional, Any
from pydantic import AliasChoices, BaseModel, Field


class EntityGroup(BaseModel):
    """Entity group (co-reference cluster)."""
    id: str = Field(..., description="Group ID")
    entity_ids: List[str] = Field(
        ...,
        description="IDs of entities in this group",
        validation_alias=AliasChoices("entity_ids", "entityIds"),
        serialization_alias="entity_ids",
    )

    model_config = {"extra": "ignore", "populate_by_name": True}


class EntityAnnotation(BaseModel):
    """NER entity annotation result."""
    id: str = Field(..., description="Entity ID")
    start: int = Field(..., description="Start position")
    end: int = Field(..., description="End position")
    quote: str = Field(
        ...,
        description="Entity text",
        validation_alias=AliasChoices("quote", "text"),
    )
    label_id: str = Field(
        ...,
        description="Label ID",
        validation_alias=AliasChoices("labelId", "label_id"),
        serialization_alias="labelId",
    )

    model_config = {"extra": "ignore", "populate_by_name": True}


class TextResult(BaseModel):
    """Per-text annotation result."""
    id: str = Field(..., description="Text ID")
    status: str = Field(..., description="Status (pending, completed, excluded)")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Text attributes")
    entities: List[EntityAnnotation] = Field(default_factory=list, description="NER entity list")
    groups: List[EntityGroup] = Field(default_factory=list, description="Entity groups")
    label_id: Optional[str] = Field(
        default=None,
        description="Classification label ID (classification tasks only)",
        validation_alias=AliasChoices("label_id", "labelId"),
        serialization_alias="label_id",
    )

    model_config = {"extra": "ignore", "populate_by_name": True}


class TaskMeta(BaseModel):
    """Task metadata embedded in the result file."""
    id: str
    name: str
    type: str

    model_config = {"extra": "ignore"}


class RapidmarkResults(BaseModel):
    """Complete RapidMark result data."""
    task: TaskMeta
    worker: Optional[str] = None
    exported_at: datetime
    texts: List[TextResult]

    model_config = {"extra": "ignore", "populate_by_name": True}

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "RapidmarkResults":
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
        return next((t for t in self.texts if t.id == text_id), None)

    def get_all_entities(self) -> List[EntityAnnotation]:
        """Get all entity annotations across all texts."""
        entities = []
        for text in self.texts:
            entities.extend(text.entities)
        return entities

    def filter_entities_by_label(self, label_id: str) -> List[EntityAnnotation]:
        """Get all entities with the specified label ID."""
        return [e for e in self.get_all_entities() if e.label_id == label_id]

    def filter_texts_by_label(self, label_id: str) -> List[TextResult]:
        """Get all texts assigned the specified label ID (classification tasks)."""
        return [t for t in self.texts if t.label_id == label_id]

    def get_completion_rate(self) -> float:
        """Get completion rate (0.0-1.0)."""
        if not self.texts:
            return 0.0
        completed = sum(1 for t in self.texts if t.status == "completed")
        return completed / len(self.texts)
