"""
Example 01: Basic NER Label Definition

This example demonstrates the fundamental building blocks for defining
Named Entity Recognition (NER) tasks with the Rapidmark SDK:
- Basic label definitions with RapidmarkLabel
- Simple task definition for NER (labels only, no structures)
"""

from rapidmark.sdk import (
    RapidmarkLabel,
    RapidmarkTaskDefinition,
)


# Step 1: Define NER labels
# NER tasks typically focus on identifying entities in text
# Common NER labels include Person, Organization, Location, Date, etc.
labels = [
    RapidmarkLabel(id="person", name="Person"),
    RapidmarkLabel(id="organization", name="Organization"),
    RapidmarkLabel(id="location", name="Location"),
    RapidmarkLabel(id="date", name="Date"),
    RapidmarkLabel(id="money", name="Money"),
    RapidmarkLabel(id="percent", name="Percent"),
]


# Step 2: Create a task definition for NER
# NER tasks typically don't use structures - just labels
# Set structures=[] to indicate this is a pure NER task
task_definition = RapidmarkTaskDefinition(
    id="basic_ner",
    name="Basic Named Entity Recognition",
    description="Identify and label named entities in text: Person, Organization, Location, Date, Money, and Percent",
    labels=labels,
)


if __name__ == "__main__":
    import json

    print("=== Basic NER Task Definition ===\n")

    # Print task summary
    print(f"Task ID: {task_definition.id}")
    print(f"Task Name: {task_definition.name}")
    print(f"Description: {task_definition.description}")
    print(f"Number of Labels: {len(task_definition.labels)}")
    # Print labels
    print("\nLabels:")
    for label in task_definition.labels:
        print(f"  - {label.id}: {label.name}")

    # Print the full task definition as JSON
    print("\n=== JSON Output ===")
    print(json.dumps(task_definition.model_dump(by_alias=True), indent=2, ensure_ascii=False))
