import json
import pytest
from datetime import datetime, timezone

from rapidmark.sdk.results import (
    EntityAnnotation,
    TextResult,
    TaskInfo,
    RapidmarkResults,
)


def make_result_data(task_type="ner"):
    now = datetime.now(timezone.utc).isoformat()
    return {
        "taskInfo": {
            "taskType": task_type,
            "taskTitle": "Test Task",
            "taskId": "test_task",
            "exportedAt": now,
            "exportFormat": "unified_v1",
            "totalTexts": 2,
            "completedTexts": 1,
        },
        "results": {
            "t1": {
                "status": "completed",
                "entities": [
                    {"id": "e1", "start": 0, "end": 5, "text": "Tokyo", "labelId": "LOC", "timestamp": now},
                    {"id": "e2", "start": 10, "end": 15, "text": "Alice", "labelId": "PER", "timestamp": now},
                ]
            },
            "t2": {
                "status": "pending",
                "entities": []
            }
        }
    }


def test_rapidmark_results_from_dict():
    data = make_result_data()
    results = RapidmarkResults.model_validate(data)
    assert results.task_info.task_type == "ner"
    assert results.task_info.task_title == "Test Task"
    assert len(results.results) == 2


def test_get_text_result():
    results = RapidmarkResults.model_validate(make_result_data())
    t1 = results.get_text_result("t1")
    assert t1 is not None
    assert t1.status == "completed"
    assert len(t1.entities) == 2


def test_get_all_entities():
    results = RapidmarkResults.model_validate(make_result_data())
    entities = results.get_all_entities()
    assert len(entities) == 2
    assert entities[0].label_id == "LOC"


def test_filter_entities_by_label():
    results = RapidmarkResults.model_validate(make_result_data())
    loc_entities = results.filter_entities_by_label("LOC")
    assert len(loc_entities) == 1
    assert loc_entities[0].text == "Tokyo"


def test_get_completion_rate():
    results = RapidmarkResults.model_validate(make_result_data())
    assert results.get_completion_rate() == 0.5


def test_from_file(tmp_path):
    data = make_result_data()
    path = tmp_path / "test.result.rapidmark.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    results = RapidmarkResults.from_file(path)
    assert results.task_info.task_id == "test_task"


def test_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        RapidmarkResults.from_file("/nonexistent/path.json")


def test_entity_annotation_camel_case():
    now = datetime.now(timezone.utc).isoformat()
    entity = EntityAnnotation.model_validate({
        "id": "e1", "start": 0, "end": 5, "text": "Tokyo",
        "labelId": "LOC", "timestamp": now
    })
    assert entity.label_id == "LOC"


def test_entity_annotation_snake_case():
    now = datetime.now(timezone.utc).isoformat()
    entity = EntityAnnotation.model_validate({
        "id": "e1", "start": 0, "end": 5, "text": "Tokyo",
        "label_id": "LOC", "timestamp": now
    })
    assert entity.label_id == "LOC"
