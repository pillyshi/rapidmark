"""
Example: Classification Task — Create, Save, and Process Results

Demonstrates:
- Building a classification task with RapidmarkTask
- Saving it to a .rapidmark.json file
- Loading annotation results (result v1) with RapidmarkResult
- Analyzing results with filter_texts_by_label() and get_completion_rate()
"""

from pathlib import Path

from rapidmark.sdk import (
    RapidmarkLabel,
    RapidmarkTaskDefinition,
    RapidmarkText,
    RapidmarkTask,
    RapidmarkResult,
)


def create_sentiment_task(out_path: Path) -> RapidmarkTask:
    task = RapidmarkTask(
        definition=RapidmarkTaskDefinition(
            id="sentiment",
            name="Sentiment Analysis",
            type="classification",
            description="Classify the sentiment of each review",
            labels=[
                RapidmarkLabel(id="positive", name="Positive"),
                RapidmarkLabel(id="negative", name="Negative"),
                RapidmarkLabel(id="neutral", name="Neutral"),
            ],
        ),
        texts=[
            RapidmarkText(
                id="r001",
                content="I absolutely love this product! Best purchase I've made all year.",
                attributes={"source": "amazon"},
            ),
            RapidmarkText(
                id="r002",
                content="Terrible quality. Broke after two days. Complete waste of money.",
                attributes={"source": "amazon"},
            ),
            RapidmarkText(
                id="r003",
                content="It works as described. Nothing special, nothing terrible.",
                attributes={"source": "amazon"},
            ),
        ],
    )
    task.save(out_path)
    print(f"Task saved: {out_path}")
    print(f"  Task ID:  {task.definition.id}")
    print(f"  Labels:   {[l.name for l in task.definition.labels]}")
    print(f"  Texts:    {len(task.texts)}")
    return task


def process_results(results_path: Path) -> None:
    print(f"\nLoading results: {results_path}")
    result = RapidmarkResult.from_file(results_path)

    print(f"\n=== Result Summary ===")
    print(f"Task ID:         {result.task_id}")
    print(f"Worker:          {result.worker or '(anonymous)'}")
    print(f"Completion Rate: {result.get_completion_rate():.0%}")

    print(f"\n=== Label Distribution ===")
    for label_id in ["positive", "negative", "neutral"]:
        texts = result.filter_texts_by_label(label_id)
        print(f"  {label_id}: {len(texts)} text(s)")

    print(f"\n=== Per-Text Results ===")
    for text_result in result.texts:
        label = text_result.label_id or "(unlabeled)"
        print(f"  [{text_result.id}] status={text_result.status}  label={label}")


if __name__ == "__main__":
    import tempfile

    example_dir = Path(__file__).parent

    with tempfile.TemporaryDirectory() as tmp:
        task_path = Path(tmp) / "sentiment.rapidmark.json"
        create_sentiment_task(task_path)

    results_path = example_dir / "sentiment.alice.result.rapidmark.json"
    if results_path.exists():
        process_results(results_path)
    else:
        print(f"\nResults file not found: {results_path}")
        print("Annotate the task with the Rapidmark web interface first,")
        print("then export results as sentiment.{worker}.result.rapidmark.json")
