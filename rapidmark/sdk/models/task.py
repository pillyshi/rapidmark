"""
RapidMark SDK task models.
"""

import json
from pathlib import Path
from typing import Union, Optional, List, Any, Dict
from pydantic import BaseModel, Field, model_validator, ConfigDict


class RapidmarkLabel(BaseModel):
    """Label definition for annotation tasks."""
    id: str = Field(..., description="Unique identifier for the label")
    name: str = Field(..., description="Display name for the label")
    parent_id: Optional[str] = Field(
        None,
        description="Parent label ID for hierarchical structure",
        alias="parentId"
    )

    model_config = ConfigDict(extra="forbid")


class RapidmarkTaskDefinition(BaseModel):
    """Task definition."""
    id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Human-readable task name")
    type: str = Field(default="ner", description="Task type (ner, classification)")
    description: Optional[str] = Field(None, description="Task description")
    labels: List[RapidmarkLabel] = Field(default_factory=list, description="Available labels")

    model_config = ConfigDict(extra="forbid")


class RapidmarkText(BaseModel):
    """Text data for annotation."""
    id: str = Field(..., description="Unique text identifier")
    content: str = Field(..., description="Text content to be annotated")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional text attributes")

    model_config = ConfigDict(extra="forbid")


class RapidmarkTask(BaseModel):
    """Complete task definition with texts and metadata."""
    definition: RapidmarkTaskDefinition = Field(..., description="Task definition")
    texts: List[RapidmarkText] = Field(default_factory=list, description="Texts to annotate")

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode='after')
    def validate_unique_text_ids(self):
        text_ids = [text.id for text in self.texts]
        if len(set(text_ids)) != len(text_ids):
            raise ValueError("Duplicate text IDs found")
        return self

    def to_json(self) -> Dict[str, Any]:
        """Convert task to JSON format compatible with RapidMark frontend."""
        return self.model_dump(mode="python", by_alias=True)

    def save(self, out_path: Union[str, Path]) -> None:
        """Save task to a RapidMark JSON file."""
        if isinstance(out_path, str):
            out_path = Path(out_path).resolve()

        if out_path.is_dir():
            out_path = out_path / f"{self.definition.id}.rapidmark.json"

        task_json = self.to_json()
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(task_json, f, indent=2, ensure_ascii=False)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "RapidmarkTask":
        """Load task from a RapidMark JSON file."""
        if isinstance(file_path, str):
            file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Task file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.model_validate(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load task: {e}")

    def load_results(self, results_file: Union[str, Path]) -> "RapidmarkResult":
        """Load annotation results for this task."""
        from .result import RapidmarkResult
        return RapidmarkResult.from_file(results_file)
