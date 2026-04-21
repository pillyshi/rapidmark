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
    TaskInfo
)

__version__ = "0.1.0"
__author__ = "pillyshi"

__all__ = [
    "RapidmarkLabel",
    "RapidmarkTaskDefinition",
    "RapidmarkText",
    "RapidmarkTask",
    "RapidmarkResults",
    "EntityAnnotation",
    "TextResult",
    "TaskInfo",
]
