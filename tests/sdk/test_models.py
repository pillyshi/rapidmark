import json
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from rapidmark.sdk.models import (
    RapidmarkLabel,
    RapidmarkTaskDefinition,
    RapidmarkText,
    RapidmarkTask,
)


def test_rapidmark_label_basic():
    label = RapidmarkLabel(id="PERSON", name="Person")
    assert label.id == "PERSON"
    assert label.name == "Person"
    assert label.parent_id is None


def test_rapidmark_label_with_parent():
    label = RapidmarkLabel(id="POLITICIAN", name="Politician", parentId="PERSON")
    assert label.parent_id == "POLITICIAN" or label.parent_id == "PERSON"


def test_rapidmark_label_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        RapidmarkLabel(id="x", name="x", unknown_field="y")


def test_rapidmark_task_definition_basic():
    task_def = RapidmarkTaskDefinition(
        id="my_task",
        name="My NER Task",
        labels=[
            RapidmarkLabel(id="PERSON", name="Person"),
            RapidmarkLabel(id="ORG", name="Organization"),
        ]
    )
    assert task_def.id == "my_task"
    assert task_def.type == "ner"
    assert len(task_def.labels) == 2


def test_rapidmark_task_definition_defaults():
    task_def = RapidmarkTaskDefinition(id="t", name="n")
    assert task_def.type == "ner"
    assert task_def.description is None
    assert task_def.labels == []


def test_rapidmark_text_basic():
    text = RapidmarkText(id="t1", content="Hello world")
    assert text.id == "t1"
    assert text.content == "Hello world"
    assert text.attributes == {}


def test_rapidmark_task_unique_text_ids():
    task = RapidmarkTask(
        definition=RapidmarkTaskDefinition(id="task", name="Task"),
        texts=[
            RapidmarkText(id="t1", content="Text 1"),
            RapidmarkText(id="t2", content="Text 2"),
        ]
    )
    assert len(task.texts) == 2


def test_rapidmark_task_duplicate_text_ids_raises():
    with pytest.raises(ValidationError):
        RapidmarkTask(
            definition=RapidmarkTaskDefinition(id="task", name="Task"),
            texts=[
                RapidmarkText(id="t1", content="Text 1"),
                RapidmarkText(id="t1", content="Duplicate"),
            ]
        )


def test_rapidmark_task_to_json():
    task = RapidmarkTask(
        definition=RapidmarkTaskDefinition(
            id="ner_task",
            name="NER Task",
            labels=[RapidmarkLabel(id="PERSON", name="Person")],
        ),
        texts=[RapidmarkText(id="t1", content="Hello")]
    )
    data = task.to_json()
    assert data["definition"]["id"] == "ner_task"
    assert len(data["texts"]) == 1


def test_rapidmark_task_save_and_load(tmp_path):
    task = RapidmarkTask(
        definition=RapidmarkTaskDefinition(
            id="save_test",
            name="Save Test",
            labels=[RapidmarkLabel(id="LOC", name="Location")],
        ),
        texts=[RapidmarkText(id="t1", content="Tokyo is a city.")]
    )
    out_path = tmp_path / "save_test.rapidmark.json"
    task.save(out_path)

    loaded = RapidmarkTask.from_file(out_path)
    assert loaded.definition.id == "save_test"
    assert loaded.texts[0].content == "Tokyo is a city."


def _write_result_file(tmp_path, task_id: str) -> "Path":
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "task_id": task_id,
        "result_version": 1,
        "worker": "alice",
        "exported_at": now,
        "texts": [],
    }
    path = tmp_path / f"{task_id}.result.rapidmark.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _make_task(task_id: str) -> RapidmarkTask:
    return RapidmarkTask(
        definition=RapidmarkTaskDefinition(id=task_id, name="Test Task"),
        texts=[],
    )


def test_load_results_matching_task_id(tmp_path):
    task = _make_task("my_task")
    result_path = _write_result_file(tmp_path, "my_task")
    result = task.load_results(result_path)
    assert result.task_id == "my_task"


def test_load_results_mismatched_task_id(tmp_path):
    task = _make_task("task_a")
    result_path = _write_result_file(tmp_path, "task_b")
    with pytest.raises(ValueError, match="task_b") as exc_info:
        task.load_results(result_path)
    assert "task_a" in str(exc_info.value)
    assert "task_b" in str(exc_info.value)


def test_load_results_file_not_found(tmp_path):
    task = _make_task("my_task")
    with pytest.raises(FileNotFoundError):
        task.load_results(tmp_path / "nonexistent.result.rapidmark.json")
