"""
Example 04: Processing NER Annotation Results

This example demonstrates how to load and process NER annotation results:
- RapidmarkResults.from_file() to load results
- get_all_entities() for raw access to all entities
- filter_entities_by_label() to filter by label type
- Analyzing and summarizing NER results
"""

from pathlib import Path
from collections import Counter

from rapidmark.sdk import (
    RapidmarkResults,
)


def demonstrate_ner_results_processing(results_path: Path) -> None:
    """Demonstrate various ways to process NER annotation results."""

    # Step 1: Load results from file
    print(f"Loading results from: {results_path}")
    results = RapidmarkResults.from_file(results_path)

    # Step 2: Access task metadata
    print("\n=== Task Information ===")
    print(f"Task ID:    {results.task.id}")
    print(f"Task Name:  {results.task.name}")
    print(f"Task Type:  {results.task.type}")
    print(f"Worker:     {results.worker or '(anonymous)'}")
    print(f"Total Texts: {len(results.texts)}")
    completed = sum(1 for t in results.texts if t.status == "completed")
    print(f"Completed:  {completed}")
    print(f"Completion Rate: {results.get_completion_rate():.1%}")

    # Step 3: Get all entities (raw access)
    print("\n=== All Entities ===")
    entities = results.get_all_entities()
    print(f"Total entities: {len(entities)}")

    # Show first few entities
    for entity in entities[:5]:
        print(f"  [{entity.label_id}] \"{entity.quote}\" (pos: {entity.start}-{entity.end})")
    if len(entities) > 5:
        print(f"  ... and {len(entities) - 5} more")

    # Step 4: Entity distribution by label
    print("\n=== Entity Distribution by Label ===")
    label_counts = Counter(entity.label_id for entity in entities)
    for label_id, count in label_counts.most_common():
        print(f"  {label_id}: {count} entities")

    # Step 5: Filter entities by specific labels
    print("\n=== Entities by Label (Filtered) ===")
    for label_id in ["person", "organization", "location", "date"]:
        filtered = results.filter_entities_by_label(label_id)
        if filtered:
            print(f"\n  {label_id.upper()} ({len(filtered)} entities):")
            unique_quotes = set(e.quote for e in filtered)
            for quote in list(unique_quotes)[:5]:
                print(f"    - \"{quote}\"")
            if len(unique_quotes) > 5:
                print(f"    ... and {len(unique_quotes) - 5} more unique values")

    # Step 6: Entity frequency analysis
    print("\n=== Most Common Entities ===")
    entity_quotes = [entity.quote for entity in entities]
    most_common = Counter(entity_quotes).most_common(10)
    for quote, count in most_common:
        print(f"  \"{quote}\": {count} occurrences")

    # Step 7: Access results by text ID
    print("\n=== Results by Text ID ===")
    for text_result in results.texts[:3]:
        print(f"\n  Text ID: {text_result.id}")
        print(f"  Status: {text_result.status}")
        print(f"  Entities: {len(text_result.entities)}")
        for entity in text_result.entities[:3]:
            print(f"    - [{entity.label_id}] \"{entity.quote}\"")


def create_mock_results() -> dict:
    """Create mock NER results for demonstration."""
    from datetime import datetime

    return {
        "task": {
            "id": "news_ner",
            "name": "News Article NER",
            "type": "ner",
        },
        "worker": "alice",
        "exported_at": datetime.now().isoformat(),
        "texts": [
            {
                "id": "news_001",
                "status": "completed",
                "attributes": {"source": "tech_news"},
                "entities": [
                    {"id": "e1", "start": 0, "end": 5, "quote": "Apple", "labelId": "organization"},
                    {"id": "e2", "start": 10, "end": 18, "quote": "Tim Cook", "labelId": "person"},
                    {"id": "e3", "start": 37, "end": 46, "quote": "iPhone 15", "labelId": "product"},
                    {"id": "e4", "start": 80, "end": 89, "quote": "Cupertino", "labelId": "location"},
                    {"id": "e5", "start": 93, "end": 111, "quote": "September 12, 2023", "labelId": "date"},
                ],
            },
            {
                "id": "news_002",
                "status": "completed",
                "attributes": {"source": "business_news"},
                "entities": [
                    {"id": "e6", "start": 0, "end": 9, "quote": "Microsoft", "labelId": "organization"},
                    {"id": "e7", "start": 12, "end": 25, "quote": "Satya Nadella", "labelId": "person"},
                    {"id": "e8", "start": 35, "end": 49, "quote": "European Union", "labelId": "organization"},
                    {"id": "e9", "start": 63, "end": 71, "quote": "Brussels", "labelId": "location"},
                ],
            },
            {
                "id": "news_003",
                "status": "completed",
                "attributes": {"source": "automotive_news"},
                "entities": [
                    {"id": "e10", "start": 0, "end": 5, "quote": "Tesla", "labelId": "organization"},
                    {"id": "e11", "start": 40, "end": 51, "quote": "Gigafactory", "labelId": "product"},
                    {"id": "e12", "start": 55, "end": 61, "quote": "Mexico", "labelId": "location"},
                ],
            },
        ],
    }


if __name__ == "__main__":
    import json
    import tempfile

    # Try to load real results file first
    # The filename format is: {task_id}.{worker}.result.rapidmark.json
    example_results_path = Path(__file__).parent / "news_ner.alice.result.rapidmark.json"

    if example_results_path.exists():
        demonstrate_ner_results_processing(example_results_path)
    else:
        print("Results file not found:", example_results_path)
        print("\nTo use this example with real data:")
        print("1. Run 03_complete_ner_task.py to create the task file")
        print("2. Annotate texts using the Rapidmark web interface")
        print("3. Export results (filename: news_ner.{worker}.result.rapidmark.json)")
        print("4. Run this script again")

        # Create mock data for demonstration
        print("\n" + "=" * 50)
        print("DEMO MODE: Using mock NER results")
        print("=" * 50)

        # Write mock results to a temporary file
        mock_data = create_mock_results()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(mock_data, f, indent=2)
            temp_path = Path(f.name)

        try:
            demonstrate_ner_results_processing(temp_path)
        finally:
            temp_path.unlink()

        print("\n=== Available Methods for NER Results ===")
        print("  - RapidmarkResults.from_file(path) - Load results from JSON file")
        print("  - results.get_all_entities() - Get all entity annotations")
        print("  - results.filter_entities_by_label(label_id) - Filter by label")
        print("  - results.get_text_result(text_id) - Get results for a specific text")
        print("  - results.get_completion_rate() - Get annotation completion rate")
