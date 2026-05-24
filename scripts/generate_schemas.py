"""Generate JSON schemas from Pydantic models."""

import json
from pathlib import Path

from rapidmark.sdk.models import RapidmarkResult, RapidmarkTask

schema_dir = Path(__file__).parent.parent / "schema"
schema_dir.mkdir(exist_ok=True)

(schema_dir / "result.schema.json").write_text(
    json.dumps(RapidmarkResult.model_json_schema(), indent=2) + "\n"
)
print("Generated schema/result.schema.json")

(schema_dir / "task.schema.json").write_text(
    json.dumps(RapidmarkTask.model_json_schema(), indent=2) + "\n"
)
print("Generated schema/task.schema.json")
