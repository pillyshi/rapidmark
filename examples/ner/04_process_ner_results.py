"""
Example 04: Processing NER Annotation Results

This example demonstrates how to load and process NER annotation results:
- RapidmarkResult.from_file() to load results
- get_all_entities() for raw access to all entities
- filter_entities_by_label() to filter by label type
- Analyzing and summarizing NER results
"""

from pathlib import Path
from collections import Counter

from rapidmark.sdk import (
    RapidmarkResult,
)


def demonstrate_ner_results_processing(results_path: Path) -> None:
    """Demonstrate various ways to process NER annotation results."""

    print(f"Loading results from: {results_path}")
    result = RapidmarkResult.from_file(results_path)

    print("\n=== Task Information ===")
    print(f"Task ID:    {result.task_id}")
    print(f"Worker:     {result.worker or '(anonymous)'}")
    print(f"Total Texts: {len(result.texts)}")
    completed = sum(1 for t in result.texts if t.status == "completed")
    print(f"Completed:  {completed}")
    print(f"Completion Rate: {result.get_completion_rate():.1%}")

    print("\n=== All Entities ===")
    entities = result.get_all_entities()
    print(f"Total entities: {len(entities)}")

    for entity in entities[:5]:
        print(f"  [{entity.label_id}] \"{entity.quote}\" (pos: {entity.start}-{entity.end})")
    if len(entities) > 5:
        print(f"  ... and {len(entities) - 5} more")

    print("\n=== Entity Distribution by Label ===")
    label_counts = Counter(entity.label_id for entity in entities)
    for label_id, count in label_counts.most_common():
        print(f"  {label_id}: {count} entities")

    print("\n=== Entities by Label (Filtered) ===")
    for label_id in ["person", "organization", "location", "date"]:
        filtered = result.filter_entities_by_label(label_id)
        if filtered:
            print(f"\n  {label_id.upper()} ({len(filtered)} entities):")
            unique_quotes = set(e.quote for e in filtered)
            for quote in list(unique_quotes)[:5]:
                print(f"    - \"{quote}\"")
            if len(unique_quotes) > 5:
                print(f"    ... and {len(unique_quotes) - 5} more unique values")

    print("\n=== Most Common Entities ===")
    entity_quotes = [entity.quote for entity in entities]
    most_common = Counter(entity_quotes).most_common(10)
    for quote, count in most_common:
        print(f"  \"{quote}\": {count} occurrences")

    print("\n=== Results by Text ID ===")
    for text_result in result.texts[:3]:
        print(f"\n  Text ID: {text_result.id}")
        print(f"  Status: {text_result.status}")
        print(f"  Entities: {len(text_result.entities)}")
        for entity in text_result.entities[:3]:
            print(f"    - [{entity.label_id}] \"{entity.quote}\"")


def create_mock_results() -> dict:
    """Create mock NER results (canonical result v1) for demonstration."""
    from datetime import datetime

    return {
        "task_id": "news_ner",
        "result_version": 1,
        "worker": "alice",
        "exported_at": datetime.now().isoformat(),
        "texts": [
            {
                "id": "news_001",
                "status": "completed",
                "entities": [
                    {"id": "e1", "start": 0, "end": 5, "quote": "Apple", "label_id": "organization"},
                    {"id": "e2", "start": 10, "end": 18, "quote": "Tim Cook", "label_id": "person"},
                    {"id": "e3", "start": 37, "end": 46, "quote": "iPhone 15", "label_id": "product"},
                    {"id": "e4", "start": 80, "end": 89, "quote": "Cupertino", "label_id": "location"},
                    {"id": "e5", "start": 93, "end": 111, "quote": "September 12, 2023", "label_id": "date"},
                ],
                "groups": [],
            },
            {
                "id": "news_002",
                "status": "completed",
                "entities": [
                    {"id": "e6", "start": 0, "end": 9, "quote": "Microsoft", "label_id": "organization"},
                    {"id": "e7", "start": 12, "end": 25, "quote": "Satya Nadella", "label_id": "person"},
                    {"id": "e8", "start": 35, "end": 49, "quote": "European Union", "label_id": "organization"},
                    {"id": "e9", "start": 63, "end": 71, "quote": "Brussels", "label_id": "location"},
                ],
                "groups": [],
            },
            {
                "id": "news_003",
                "status": "completed",
                "entities": [
                    {"id": "e10", "start": 0, "end": 5, "quote": "Tesla", "label_id": "organization"},
                    {"id": "e11", "start": 40, "end": 51, "quote": "Gigafactory", "label_id": "product"},
                    {"id": "e12", "start": 55, "end": 61, "quote": "Mexico", "label_id": "location"},
                ],
                "groups": [],
            },
        ],
    }


if __name__ == "__main__":
    import json
    import tempfile

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

        print("\n" + "=" * 50)
        print("DEMO MODE: Using mock NER results")
        print("=" * 50)

        mock_data = create_mock_results()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(mock_data, f, indent=2)
            temp_path = Path(f.name)

        try:
            demonstrate_ner_results_processing(temp_path)
        finally:
            temp_path.unlink()

        print("\n=== Available Methods for NER Results ===")
        print("  - RapidmarkResult.from_file(path) - Load results from JSON file")
        print("  - result.get_all_entities() - Get all entity annotations")
        print("  - result.filter_entities_by_label(label_id) - Filter by label")
        print("  - result.get_text_result(text_id) - Get results for a specific text")
        print("  - result.get_completion_rate() - Get annotation completion rate")
