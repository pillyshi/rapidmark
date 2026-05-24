"""
RapidMark SDK models.
"""

from .task import (
    RapidmarkLabel,
    RapidmarkTaskDefinition,
    RapidmarkText,
    RapidmarkTask,
)

from .result import (
    RapidmarkResult,
    RapidmarkResults,
    TextResult,
    EntityAnnotation,
    EntityGroup,
)

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
