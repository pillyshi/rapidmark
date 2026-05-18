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
    TextResult,
    TaskMeta,
)

__version__ = "0.3.0"
__author__ = "pillyshi"

__all__ = [
    "RapidmarkLabel",
    "RapidmarkTaskDefinition",
    "RapidmarkText",
    "RapidmarkTask",
    "RapidmarkResults",
    "EntityAnnotation",
    "TextResult",
    "TaskMeta",
]
