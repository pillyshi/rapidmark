import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from typer.testing import CliRunner

from rapidmark.commands.merge import app
from rapidmark.sdk.models import RapidmarkResult

runner = CliRunner()


def make_v1_result_file(
    tmp_path: Path,
    task_id: str,
    worker: str,
    texts_data: list,
    filename: str | None = None,
) -> Path:
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "task_id": task_id,
        "result_version": 1,
        "worker": worker,
        "exported_at": now,
        "texts": texts_data,
    }
    name = filename or f"{worker}.result.rapidmark.json"
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


TEXTS_ALICE = [
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
]

TEXTS_BOB = [
    {
        "id": "t1",
        "status": "completed",
        "entities": [
            {"id": "e1", "start": 0, "end": 5, "quote": "Tokyo", "label_id": "LOC"},
            {"id": "e3", "start": 20, "end": 25, "quote": "Japan", "label_id": "LOC"},
        ],
        "groups": [],
    },
    {
        "id": "t2",
        "status": "completed",
        "entities": [],
        "groups": [],
    },
]


def test_merge_majority_ner(tmp_path):
    make_v1_result_file(tmp_path, "task1", "alice", TEXTS_ALICE)
    make_v1_result_file(tmp_path, "task1", "bob", TEXTS_BOB)
    result = runner.invoke(app, ["--result-dir", str(tmp_path), "-s", "majority"])
    assert result.exit_code == 0
    output_file = next(tmp_path.glob("*.merged.result.rapidmark.json"))
    merged = RapidmarkResult.from_file(output_file)
    assert merged.task_id == "task1"
    assert merged.result_version == 1
    t1 = merged.get_text_result("t1")
    assert t1 is not None
    assert t1.status == "completed"
    # Tokyo agreed by both → present; Alice only by alice (1/2 = 0.5) → present at default threshold
    entity_quotes = {e.quote for e in t1.entities}
    assert "Tokyo" in entity_quotes


def test_merge_union_ner(tmp_path):
    make_v1_result_file(tmp_path, "task1", "alice", TEXTS_ALICE)
    make_v1_result_file(tmp_path, "task1", "bob", TEXTS_BOB)
    result = runner.invoke(app, ["--result-dir", str(tmp_path), "-s", "union"])
    assert result.exit_code == 0
    output_file = next(tmp_path.glob("*.merged.result.rapidmark.json"))
    merged = RapidmarkResult.from_file(output_file)
    t1 = merged.get_text_result("t1")
    assert t1 is not None
    entity_quotes = {e.quote for e in t1.entities}
    # Union includes all unique spans
    assert "Tokyo" in entity_quotes
    assert "Alice" in entity_quotes
    assert "Japan" in entity_quotes


def test_merge_intersection_ner(tmp_path):
    make_v1_result_file(tmp_path, "task1", "alice", TEXTS_ALICE)
    make_v1_result_file(tmp_path, "task1", "bob", TEXTS_BOB)
    result = runner.invoke(app, ["--result-dir", str(tmp_path), "-s", "intersection"])
    assert result.exit_code == 0
    output_file = next(tmp_path.glob("*.merged.result.rapidmark.json"))
    merged = RapidmarkResult.from_file(output_file)
    t1 = merged.get_text_result("t1")
    assert t1 is not None
    entity_quotes = {e.quote for e in t1.entities}
    # Only Tokyo+LOC is agreed by both annotators
    assert "Tokyo" in entity_quotes
    assert "Alice" not in entity_quotes
    assert "Japan" not in entity_quotes


def test_default_output_filename_uses_task_id(tmp_path):
    make_v1_result_file(tmp_path, "my_task_123", "alice", TEXTS_ALICE)
    make_v1_result_file(tmp_path, "my_task_123", "bob", TEXTS_BOB)
    result = runner.invoke(app, ["--result-dir", str(tmp_path)])
    assert result.exit_code == 0
    merged_files = list(tmp_path.glob("*.merged.result.rapidmark.json"))
    assert len(merged_files) == 1
    assert "my_task_123" in merged_files[0].name


def test_merged_output_validates_with_sdk(tmp_path):
    make_v1_result_file(tmp_path, "task1", "alice", TEXTS_ALICE)
    make_v1_result_file(tmp_path, "task1", "bob", TEXTS_BOB)
    runner.invoke(app, ["--result-dir", str(tmp_path)])
    output_file = next(tmp_path.glob("*.merged.result.rapidmark.json"))
    merged = RapidmarkResult.from_file(output_file)
    assert merged.result_version == 1
    assert merged.worker is None
    assert merged.exported_at is not None


def test_groups_omitted_in_merged_output(tmp_path):
    texts_with_groups = [
        {
            "id": "t1",
            "status": "completed",
            "entities": [
                {"id": "e1", "start": 0, "end": 5, "quote": "Tokyo", "label_id": "LOC"},
                {"id": "e2", "start": 10, "end": 15, "quote": "it", "label_id": "LOC"},
            ],
            "groups": [{"id": "g1", "entity_ids": ["e1", "e2"]}],
        }
    ]
    make_v1_result_file(tmp_path, "task1", "alice", texts_with_groups)
    make_v1_result_file(tmp_path, "task1", "bob", texts_with_groups)
    result = runner.invoke(app, ["--result-dir", str(tmp_path)])
    assert result.exit_code == 0
    output_file = next(tmp_path.glob("*.merged.result.rapidmark.json"))
    merged = RapidmarkResult.from_file(output_file)
    # Groups are omitted in merged output because entity IDs may differ across annotators
    for text in merged.texts:
        assert text.groups == []


def test_merge_summary_counts(tmp_path):
    make_v1_result_file(tmp_path, "task1", "alice", TEXTS_ALICE)
    make_v1_result_file(tmp_path, "task1", "bob", TEXTS_BOB)
    result = runner.invoke(app, ["--result-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "2" in result.output  # Total Annotators
    assert "Total Texts" in result.output
    assert "Merged Texts" in result.output
    assert "Total Entities" in result.output
    assert "Completed Texts" in result.output


def test_min_two_files_required(tmp_path):
    make_v1_result_file(tmp_path, "task1", "alice", TEXTS_ALICE)
    result = runner.invoke(app, ["--result-dir", str(tmp_path)])
    assert result.exit_code == 1
    assert "At least 2" in result.output


def test_no_files_found(tmp_path):
    result = runner.invoke(app, ["--result-dir", str(tmp_path)])
    assert result.exit_code == 1
    assert "No result files found" in result.output


def test_invalid_strategy(tmp_path):
    make_v1_result_file(tmp_path, "task1", "alice", TEXTS_ALICE)
    make_v1_result_file(tmp_path, "task1", "bob", TEXTS_BOB)
    result = runner.invoke(app, ["--result-dir", str(tmp_path), "-s", "invalid"])
    assert result.exit_code == 1
    assert "Invalid strategy" in result.output


def test_explicit_output_path(tmp_path):
    make_v1_result_file(tmp_path, "task1", "alice", TEXTS_ALICE)
    make_v1_result_file(tmp_path, "task1", "bob", TEXTS_BOB)
    out = tmp_path / "custom_output.result.rapidmark.json"
    result = runner.invoke(app, ["--result-dir", str(tmp_path), "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    merged = RapidmarkResult.from_file(out)
    assert merged.task_id == "task1"
