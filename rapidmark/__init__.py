"""RapidMark - Fast and efficient NLP annotation tool for NER tasks."""

from .sdk.models import (
    RapidmarkLabel,
    RapidmarkTaskDefinition,
    RapidmarkText,
    RapidmarkTask,
)

from .sdk.results import (
    RapidmarkResults,
    EntityAnnotation,
    EntityGroup,
    TextResult,
    TaskMeta,
)

__version__ = "0.4.0"
__author__ = "pillyshi"

__all__ = [
    "RapidmarkLabel",
    "RapidmarkTaskDefinition",
    "RapidmarkText",
    "RapidmarkTask",
    "RapidmarkResults",
    "EntityAnnotation",
    "EntityGroup",
    "TextResult",
    "TaskMeta",
]
