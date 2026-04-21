"""
Example 02: NER with Hierarchical Labels

This example demonstrates how to define hierarchical NER labels
using parent-child relationships:
- Parent labels as broad categories
- Child labels with parentId for fine-grained classification
- Hierarchical structure for Location, Organization, and Person entities
"""

from rapidmark.sdk import (
    RapidmarkLabel,
    RapidmarkTaskDefinition,
)


# Step 1: Define parent labels (broad categories)
# These are the top-level entity types
parent_labels = [
    RapidmarkLabel(id="location", name="Location"),
    RapidmarkLabel(id="organization", name="Organization"),
    RapidmarkLabel(id="person", name="Person"),
]

# Step 2: Define child labels with parentId
# These provide fine-grained classification under each parent
location_children = [
    RapidmarkLabel(id="city", name="City", parentId="location"),
    RapidmarkLabel(id="country", name="Country", parentId="location"),
    RapidmarkLabel(id="state", name="State/Province", parentId="location"),
    RapidmarkLabel(id="address", name="Street Address", parentId="location"),
]

organization_children = [
    RapidmarkLabel(id="company", name="Company", parentId="organization"),
    RapidmarkLabel(id="government", name="Government Agency", parentId="organization"),
    RapidmarkLabel(id="educational", name="Educational Institution", parentId="organization"),
    RapidmarkLabel(id="nonprofit", name="Non-profit Organization", parentId="organization"),
]

person_children = [
    RapidmarkLabel(id="politician", name="Politician", parentId="person"),
    RapidmarkLabel(id="athlete", name="Athlete", parentId="person"),
    RapidmarkLabel(id="artist", name="Artist", parentId="person"),
    RapidmarkLabel(id="scientist", name="Scientist", parentId="person"),
]

# Step 3: Combine all labels
# Parent labels come first, then children
all_labels = (
    parent_labels
    + location_children
    + organization_children
    + person_children
)


# Step 4: Create the task definition
task_definition = RapidmarkTaskDefinition(
    id="hierarchical_ner",
    name="Hierarchical Named Entity Recognition",
    description="Fine-grained NER with hierarchical labels for Location, Organization, and Person entities",
    labels=all_labels,
)


if __name__ == "__main__":
    import json

    print("=== Hierarchical NER Task Definition ===\n")

    # Print task summary
    print(f"Task ID: {task_definition.id}")
    print(f"Task Name: {task_definition.name}")
    print(f"Total Labels: {len(task_definition.labels)}")

    # Group labels by parent for display
    print("\nLabel Hierarchy:")

    # Show parent labels and their children
    for parent_label in parent_labels:
        print(f"\n  {parent_label.name} ({parent_label.id})")
        children = [l for l in all_labels if l.parent_id == parent_label.id]
        for child in children:
            print(f"    └── {child.name} ({child.id})")

    # Print the full task definition as JSON
    print("\n=== JSON Output ===")
    print(json.dumps(task_definition.model_dump(by_alias=True), indent=2, ensure_ascii=False))
