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
    print(f"Task Type: {results.task_info.task_type}")
    print(f"Task Title: {results.task_info.task_title}")
    print(f"Total Texts: {results.task_info.total_texts}")
    print(f"Completed: {results.task_info.completed_texts}")
    print(f"Completion Rate: {results.get_completion_rate():.1%}")

    # Step 3: Get all entities (raw access)
    print("\n=== All Entities ===")
    entities = results.get_all_entities()
    print(f"Total entities: {len(entities)}")

    # Show first few entities
    for entity in entities[:5]:
        print(f"  [{entity.label_id}] \"{entity.text}\" (pos: {entity.start}-{entity.end})")
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
            unique_texts = set(e.text for e in filtered)
            for text in list(unique_texts)[:5]:
                print(f"    - \"{text}\"")
            if len(unique_texts) > 5:
                print(f"    ... and {len(unique_texts) - 5} more unique values")

    # Step 6: Entity frequency analysis
    print("\n=== Most Common Entities ===")
    entity_texts = [entity.text for entity in entities]
    most_common = Counter(entity_texts).most_common(10)
    for text, count in most_common:
        print(f"  \"{text}\": {count} occurrences")

    # Step 7: Access results by text ID
    print("\n=== Results by Text ID ===")
    for text_id in list(results.results.keys())[:3]:
        text_result = results.get_text_result(text_id)
        if text_result:
            print(f"\n  Text ID: {text_id}")
            print(f"  Status: {text_result.status}")
            print(f"  Entities: {len(text_result.entities)}")
            for entity in text_result.entities[:3]:
                print(f"    - [{entity.label_id}] \"{entity.text}\"")


def create_mock_results() -> dict:
    """Create mock NER results for demonstration."""
    from datetime import datetime

    return {
        "taskInfo": {
            "taskType": "structured_extraction",
            "taskTitle": "News Article NER",
            "taskDescription": "Extract named entities from news articles",
            "taskId": "news_ner",
            "labels": [
                {"id": "person", "name": "Person"},
                {"id": "organization", "name": "Organization"},
                {"id": "location", "name": "Location"},
                {"id": "date", "name": "Date"},
                {"id": "product", "name": "Product"},
            ],
            "structures": [],
            "totalTexts": 3,
            "completedTexts": 3,
            "completionRate": 1.0,
            "totalAnnotations": 12,
            "totalComments": 0,
            "exportFormat": "unified_v1",
            "exportedAt": datetime.now().isoformat(),
            "version": "1.0"
        },
        "results": {
            "news_001": {
                "status": "completed",
                "attributes": {"source": "tech_news"},
                "entities": [
                    {"id": "e1", "start": 0, "end": 5, "text": "Apple", "labelId": "organization", "timestamp": datetime.now().isoformat()},
                    {"id": "e2", "start": 10, "end": 18, "text": "Tim Cook", "labelId": "person", "timestamp": datetime.now().isoformat()},
                    {"id": "e3", "start": 37, "end": 46, "text": "iPhone 15", "labelId": "product", "timestamp": datetime.now().isoformat()},
                    {"id": "e4", "start": 80, "end": 89, "text": "Cupertino", "labelId": "location", "timestamp": datetime.now().isoformat()},
                    {"id": "e5", "start": 93, "end": 111, "text": "September 12, 2023", "labelId": "date", "timestamp": datetime.now().isoformat()},
                ],
                "structures": []
            },
            "news_002": {
                "status": "completed",
                "attributes": {"source": "business_news"},
                "entities": [
                    {"id": "e6", "start": 0, "end": 9, "text": "Microsoft", "labelId": "organization", "timestamp": datetime.now().isoformat()},
                    {"id": "e7", "start": 12, "end": 25, "text": "Satya Nadella", "labelId": "person", "timestamp": datetime.now().isoformat()},
                    {"id": "e8", "start": 35, "end": 49, "text": "European Union", "labelId": "organization", "timestamp": datetime.now().isoformat()},
                    {"id": "e9", "start": 63, "end": 71, "text": "Brussels", "labelId": "location", "timestamp": datetime.now().isoformat()},
                ],
                "structures": []
            },
            "news_003": {
                "status": "completed",
                "attributes": {"source": "automotive_news"},
                "entities": [
                    {"id": "e10", "start": 0, "end": 5, "text": "Tesla", "labelId": "organization", "timestamp": datetime.now().isoformat()},
                    {"id": "e11", "start": 40, "end": 51, "text": "Gigafactory", "labelId": "product", "timestamp": datetime.now().isoformat()},
                    {"id": "e12", "start": 55, "end": 61, "text": "Mexico", "labelId": "location", "timestamp": datetime.now().isoformat()},
                ],
                "structures": []
            }
        }
    }


if __name__ == "__main__":
    import json
    import tempfile

    # Try to load real results file first
    example_results_path = Path(__file__).parent / "news_ner.result.rapidmark.json"

    if example_results_path.exists():
        demonstrate_ner_results_processing(example_results_path)
    else:
        print("Results file not found:", example_results_path)
        print("\nTo use this example with real data:")
        print("1. Run 03_complete_ner_task.py to create the task file")
        print("2. Annotate texts using the Rapidmark web interface")
        print("3. Export results to the same directory")
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
            temp_path.unlink()  # Clean up temp file

        print("\n=== Available Methods for NER Results ===")
        print("  - RapidmarkResults.from_file(path) - Load results from JSON file")
        print("  - results.get_all_entities() - Get all entity annotations")
        print("  - results.filter_entities_by_label(label_id) - Filter by label")
        print("  - results.get_text_result(text_id) - Get results for a specific text")
        print("  - results.get_completion_rate() - Get annotation completion rate")
