"""Merge command for combining annotation results."""

import json
import datetime
import re
from typing import List, Optional, Annotated
from pathlib import Path
from collections import Counter

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from rapidmark.sdk.models import RapidmarkResult, TextResult, EntityAnnotation


app = typer.Typer(help="Merge annotation results")
console = Console()


@app.callback(invoke_without_command=True)
def main(
    result_dir: Annotated[Path, typer.Option("--result-dir", help="Directory containing result files")],
    output: Annotated[Optional[Path], typer.Option("-o", "--output", help="Output file path")] = None,
    strategy: Annotated[str, typer.Option("-s", "--strategy", help="Merge strategy (majority/union/intersection)")] = "majority",
    min_agreement: Annotated[float, typer.Option("--min-agreement", help="Minimum agreement threshold (0.0-1.0)")] = 0.5,
):
    """
    Merge annotation results from multiple annotators.
    """
    result_files = list(result_dir.rglob("*.result.rapidmark.json"))

    if len(result_files) == 0:
        console.print(f"[red]Error:[/red] No result files found in {result_dir}")
        raise typer.Exit(1)

    if len(result_files) < 2:
        console.print("[red]Error:[/red] At least 2 result files are required for merging")
        raise typer.Exit(1)

    console.print(f"[blue]Merging {len(result_files)} result files[/blue]")

    valid_strategies = ["majority", "union", "intersection"]
    if strategy not in valid_strategies:
        console.print(f"[red]Error:[/red] Invalid strategy '{strategy}'. Must be one of {valid_strategies}")
        raise typer.Exit(1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Loading result files...", total=None)
            all_results: List[tuple[str, RapidmarkResult]] = []
            for file_path in result_files:
                result = RapidmarkResult.from_file(file_path)
                all_results.append((file_path.name, result))

            progress.update(task, description="Merging annotations...")
            merged = _merge_annotations(all_results, strategy, min_agreement)

            if output is None:
                task_id = all_results[0][1].task_id
                sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', task_id)
                output_dir = result_files[0].parent
                output = output_dir / f"{sanitized}.merged.result.rapidmark.json"

            progress.update(task, description="Writing output...")
            _write_json_output(merged, output)

        console.print(f"[green]Successfully merged results:[/green] {output}")
        _display_merge_summary(merged, all_results)

    except (ValueError, FileNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _merge_annotations(
    all_results: List[tuple[str, RapidmarkResult]],
    strategy: str,
    min_agreement: float,
) -> dict:
    """Merge annotations from multiple annotators based on strategy."""
    task_id = all_results[0][1].task_id

    all_text_ids: list[str] = []
    seen: set[str] = set()
    for _, result in all_results:
        for text in result.texts:
            if text.id not in seen:
                all_text_ids.append(text.id)
                seen.add(text.id)

    texts = []
    for text_id in all_text_ids:
        text_results = [
            tr
            for _, result in all_results
            for tr in result.texts
            if tr.id == text_id
        ]
        merged_text = _merge_text_data(text_id, text_results, strategy, min_agreement, len(all_results))
        texts.append(merged_text)

    return {
        "task_id": task_id,
        "result_version": 1,
        "worker": None,
        "exported_at": None,
        "texts": texts,
    }


def _merge_text_data(
    text_id: str,
    text_results: List[TextResult],
    strategy: str,
    min_agreement: float,
    total_annotators: int,
) -> dict:
    """Merge all data for a specific text."""
    status_counts = Counter(tr.status for tr in text_results)
    status = status_counts.most_common(1)[0][0]

    all_entities = [e for tr in text_results for e in tr.entities]
    merged_entities = _merge_entity_annotations(all_entities, total_annotators, strategy, min_agreement)

    return {
        "id": text_id,
        "status": status,
        "entities": merged_entities,
        "groups": [],
    }


def _merge_entity_annotations(
    entities: List[EntityAnnotation],
    total_annotators: int,
    strategy: str,
    min_agreement: float,
) -> list:
    """Merge entity annotations using the specified strategy."""
    if strategy == "union":
        return _merge_union(entities)
    elif strategy == "intersection":
        return _merge_intersection(entities, total_annotators)
    else:
        return _merge_majority(entities, total_annotators, min_agreement)


def _merge_union(annotations: List[EntityAnnotation]) -> list:
    """Union strategy: include all unique annotations."""
    seen: dict = {}
    for ann in annotations:
        key = (ann.start, ann.end, ann.quote)
        if key not in seen:
            seen[key] = {"id": ann.id, "start": ann.start, "end": ann.end, "quote": ann.quote, "label_id": ann.label_id}
    return list(seen.values())


def _merge_intersection(annotations: List[EntityAnnotation], total_annotators: int) -> list:
    """Intersection strategy: include only annotations agreed by all annotators."""
    from collections import defaultdict
    counts: dict = defaultdict(list)
    for ann in annotations:
        key = (ann.start, ann.end, ann.quote, ann.label_id)
        counts[key].append(ann)
    return [
        {"id": ann_list[0].id, "start": ann_list[0].start, "end": ann_list[0].end, "quote": ann_list[0].quote, "label_id": ann_list[0].label_id}
        for ann_list in counts.values()
        if len(ann_list) == total_annotators
    ]


def _merge_majority(annotations: List[EntityAnnotation], total_annotators: int, min_agreement: float) -> list:
    """Majority strategy: include annotations with sufficient agreement."""
    from collections import defaultdict
    span_groups: dict = defaultdict(list)
    for ann in annotations:
        span_key = (ann.start, ann.end, ann.quote)
        span_groups[span_key].append(ann)

    result = []
    for span_annotations in span_groups.values():
        label_counts = Counter(ann.label_id for ann in span_annotations)
        most_common_label, count = label_counts.most_common(1)[0]
        if count / total_annotators >= min_agreement:
            base = span_annotations[0]
            result.append({
                "id": base.id,
                "start": base.start,
                "end": base.end,
                "quote": base.quote,
                "label_id": most_common_label,
                "agreement": count / total_annotators,
                "annotatorCount": count,
            })

    return result


def _write_json_output(merged: dict, output_path: Path) -> None:
    """Write merged results to JSON file."""
    merged["exported_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)


def _display_merge_summary(merged: dict, all_results: List[tuple[str, RapidmarkResult]]) -> None:
    """Display summary statistics of the merge operation."""
    table = Table(title="Merge Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    texts = merged.get("texts", [])
    total_texts = len(set(
        tr.id
        for _, result in all_results
        for tr in result.texts
    ))
    merged_texts = len(texts)
    total_entities = sum(len(t.get("entities", [])) for t in texts)
    completed_texts = sum(1 for t in texts if t.get("status") == "completed")

    table.add_row("Total Annotators", str(len(all_results)))
    table.add_row("Total Texts", str(total_texts))
    table.add_row("Merged Texts", str(merged_texts))
    table.add_row("Total Entities", str(total_entities))
    table.add_row("Completed Texts", str(completed_texts))

    console.print(table)
