"""RapidMark - Fast and efficient NLP annotation tool."""

from .sdk.models import (
    RapidmarkLabel,
    RapidmarkTaskDefinition,
    RapidmarkText,
    RapidmarkTask,
    RapidmarkResult,
    RapidmarkResults,
    TextResult,
    EntityAnnotation,
    EntityGroup,
)

__version__ = "0.4.0"
__author__ = "pillyshi"

__all__ = [
    "RapidmarkLabel",
    "RapidmarkTaskDefinition",
    "RapidmarkText",
    "RapidmarkTask",
    "RapidmarkResult",
    "RapidmarkResults",
    "TextResult",
    "EntityAnnotation",
    "EntityGroup",
]
