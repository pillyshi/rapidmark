"""
Example 03: Complete NER Task Creation

This example demonstrates end-to-end NER task creation:
- Full task definition with NER labels
- RapidmarkText for texts to annotate
- RapidmarkTask to combine definition and texts
- RapidmarkTask.save() to write a .rapidmark.json file
"""

from pathlib import Path

from rapidmark.sdk import (
    RapidmarkLabel,
    RapidmarkTaskDefinition,
    RapidmarkText,
    RapidmarkTask,
)


# Step 1: Define NER labels
labels = [
    RapidmarkLabel(id="person", name="Person"),
    RapidmarkLabel(id="organization", name="Organization"),
    RapidmarkLabel(id="location", name="Location"),
    RapidmarkLabel(id="date", name="Date"),
    RapidmarkLabel(id="product", name="Product"),
]


# Step 2: Create task definition
task_definition = RapidmarkTaskDefinition(
    id="news_ner",
    name="News Article NER",
    description="Extract named entities from news articles: Person, Organization, Location, Date, and Product",
    labels=labels,
)


# Step 3: Define texts to annotate
texts = [
    RapidmarkText(
        id="news_001",
        content="Apple CEO Tim Cook announced the new iPhone 15 at the company's headquarters in Cupertino on September 12, 2023.",
        attributes={"source": "tech_news", "language": "en"}
    ),
    RapidmarkText(
        id="news_002",
        content="Microsoft's Satya Nadella met with European Union officials in Brussels to discuss AI regulations.",
        attributes={"source": "business_news", "language": "en"}
    ),
    RapidmarkText(
        id="news_003",
        content="Tesla announced plans to build a new Gigafactory in Mexico, with production starting in 2025.",
        attributes={"source": "automotive_news", "language": "en"}
    ),
    RapidmarkText(
        id="news_004",
        content="Google DeepMind researchers in London published a breakthrough paper on protein folding.",
        attributes={"source": "science_news", "language": "en"}
    ),
    RapidmarkText(
        id="news_005",
        content="Amazon Web Services opened a new data center in Tokyo, Japan, to serve growing Asian demand.",
        attributes={"source": "cloud_news", "language": "en"}
    ),
]


# Step 4: Create the complete task
task = RapidmarkTask(
    definition=task_definition,
    texts=texts,
)


if __name__ == "__main__":
    import json

    print("=== Complete NER Task ===\n")

    # Print task summary
    print(f"Task ID: {task.definition.id}")
    print(f"Task Name: {task.definition.name}")
    print(f"Description: {task.definition.description}")
    print(f"Labels: {len(task.definition.labels)}")
    print(f"Texts to annotate: {len(task.texts)}")

    # Print labels
    print("\nLabels:")
    for label in task.definition.labels:
        print(f"  - {label.id}: {label.name}")

    # Print texts
    print("\nTexts:")
    for text in task.texts:
        preview = text.content[:70] + "..." if len(text.content) > 70 else text.content
        print(f"  [{text.id}] {preview}")
        print(f"           Attributes: {text.attributes}")

    # Save to file
    output_dir = Path(__file__).parent
    output_path = output_dir / f"{task.definition.id}.rapidmark.json"

    task.save(output_path)
    print(f"\nTask saved to: {output_path}")

    # Verify the saved file
    print("\n=== Saved File Content (first 800 chars) ===")
    with open(output_path) as f:
        content = f.read()
        print(content[:800] + "..." if len(content) > 800 else content)
