import json
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from rapidmark.sdk.models.result import (
    EntityAnnotation,
    EntityGroup,
    TextResult,
    RapidmarkResult,
)


def make_result_data(task_type_hint="ner"):
    now = datetime.now(timezone.utc).isoformat()
    return {
        "task_id": "test_task",
        "result_version": 1,
        "worker": "alice",
        "exported_at": now,
        "texts": [
            {
                "id": "t1",
                "status": "completed",
                "entities": [
                    {"id": "e1", "start": 0, "end": 5, "quote": "Tokyo", "label_id": "LOC"},
                    {"id": "e2", "start": 10, "end": 15, "quote": "Alice", "label_id": "PER"},
                ],
                "groups": [],
            },
            {
                "id": "t2",
                "status": "pending",
                "entities": [],
                "groups": [],
            },
        ],
    }


def make_classification_data():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "task_id": "cls_task",
        "result_version": 1,
        "worker": None,
        "exported_at": now,
        "texts": [
            {"id": "t1", "status": "completed", "label_id": "positive"},
            {"id": "t2", "status": "completed", "label_id": "negative"},
            {"id": "t3", "status": "pending"},
        ],
    }


def test_result_v1_fields():
    result = RapidmarkResult.model_validate(make_result_data())
    assert result.task_id == "test_task"
    assert result.result_version == 1
    assert result.worker == "alice"
    assert len(result.texts) == 2


def test_get_text_result():
    result = RapidmarkResult.model_validate(make_result_data())
    t1 = result.get_text_result("t1")
    assert t1 is not None
    assert t1.status == "completed"
    assert len(t1.entities) == 2


def test_get_text_result_missing():
    result = RapidmarkResult.model_validate(make_result_data())
    assert result.get_text_result("nonexistent") is None


def test_get_all_entities():
    result = RapidmarkResult.model_validate(make_result_data())
    entities = result.get_all_entities()
    assert len(entities) == 2
    assert entities[0].label_id == "LOC"
    assert entities[0].quote == "Tokyo"


def test_filter_entities_by_label():
    result = RapidmarkResult.model_validate(make_result_data())
    loc = result.filter_entities_by_label("LOC")
    assert len(loc) == 1
    assert loc[0].quote == "Tokyo"


def test_get_completion_rate():
    result = RapidmarkResult.model_validate(make_result_data())
    assert result.get_completion_rate() == 0.5


def test_get_completion_rate_empty():
    data = make_result_data()
    data["texts"] = []
    result = RapidmarkResult.model_validate(data)
    assert result.get_completion_rate() == 0.0


def test_entity_group():
    data = make_result_data()
    data["texts"][0]["groups"] = [{"id": "g1", "entity_ids": ["e1", "e2"]}]
    result = RapidmarkResult.model_validate(data)
    assert result.texts[0].groups[0].entity_ids == ["e1", "e2"]


def test_classification_label_id():
    result = RapidmarkResult.model_validate(make_classification_data())
    assert result.texts[0].label_id == "positive"
    assert result.texts[2].label_id is None
    positive = result.filter_texts_by_label("positive")
    assert len(positive) == 1


def test_from_file(tmp_path):
    data = make_result_data()
    path = tmp_path / "test.result.rapidmark.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = RapidmarkResult.from_file(path)
    assert result.task_id == "test_task"
    assert result.result_version == 1


def test_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        RapidmarkResult.from_file("/nonexistent/path.json")


def test_from_file_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError):
        RapidmarkResult.from_file(path)


def test_old_format_raises_validation_error():
    old_data = {
        "task": {"id": "t", "name": "Task", "type": "ner"},
        "worker": "alice",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "texts": [],
    }
    with pytest.raises(ValidationError):
        RapidmarkResult.model_validate(old_data)


def test_extra_fields_ignored():
    data = make_result_data()
    data["unknown_field"] = "should be ignored"
    result = RapidmarkResult.model_validate(data)
    assert result.task_id == "test_task"
