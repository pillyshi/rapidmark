"""Merge command for combining annotation results."""

import json
import datetime
import re
from typing import List, Optional, Dict, Any, Annotated
from pathlib import Path
from collections import defaultdict, Counter

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


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
            all_results = []
            for file_path in result_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
                    all_results.append({'file': file_path.name, 'data': result_data})

            progress.update(task, description="Merging annotations...")
            merged_results = _merge_annotations(all_results, strategy, min_agreement)

            if output is None:
                task_info = merged_results.get('taskInfo', {})
                task_title = task_info.get('taskTitle', 'merged_task')
                sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '', task_title.replace(' ', '_').lower())
                output_dir = result_files[0].parent
                output = output_dir / f"{sanitized_name}.merged.result.rapidmark.json"

            progress.update(task, description="Writing output...")
            _write_json_output(merged_results, output)

        console.print(f"[green]Successfully merged results:[/green] {output}")
        _display_merge_summary(merged_results, all_results)

    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON in result file: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _merge_annotations(all_results: List[Dict], strategy: str, min_agreement: float) -> Dict[str, Any]:
    """Merge annotations from multiple annotators based on strategy."""
    base_task_info = all_results[0]['data'].get('taskInfo', {})

    merged_result = {
        'taskInfo': {
            **base_task_info,
            'exportFormat': 'unified_v1',
            'workerName': None,
            'exportedAt': None,
            'mergeInfo': {
                'strategy': strategy,
                'minAgreement': min_agreement,
                'sourceFiles': [r['file'] for r in all_results],
                'totalAnnotators': len(all_results),
                'mergedAt': None
            }
        },
        'results': {}
    }

    all_text_ids = set()
    for result in all_results:
        all_text_ids.update(result['data'].get('results', {}).keys())

    for text_id in all_text_ids:
        merged_text_data = _merge_text_data(all_results, text_id, strategy, min_agreement)
        if merged_text_data:
            merged_result['results'][text_id] = merged_text_data

    return merged_result


def _merge_text_data(all_results: List[Dict], text_id: str, strategy: str, min_agreement: float) -> Dict[str, Any]:
    """Merge all data for a specific text."""
    text_data_list = []

    for result in all_results:
        text_data = result['data'].get('results', {}).get(text_id, {})
        if text_data:
            text_data = dict(text_data)
            text_data['sourceFile'] = result['file']
            text_data_list.append(text_data)

    if not text_data_list:
        return {}

    status_counts = Counter(td.get('status', 'pending') for td in text_data_list)
    merged_text: Dict[str, Any] = {'status': status_counts.most_common(1)[0][0]}

    all_entities = []
    for td in text_data_list:
        all_entities.extend(td.get('entities', []))

    if all_entities:
        merged_entities = _merge_entity_annotations(all_entities, len(all_results), strategy, min_agreement)
        if merged_entities:
            merged_text['entities'] = merged_entities

    all_comments = []
    for td in text_data_list:
        for comment in td.get('comments', []):
            comment_copy = comment.copy()
            comment_copy['sourceFile'] = td.get('sourceFile', 'unknown')
            all_comments.append(comment_copy)

    if all_comments:
        merged_text['comments'] = all_comments

    merged_text['mergeInfo'] = {
        'strategy': strategy,
        'minAgreement': min_agreement,
        'sourceCount': len(text_data_list),
        'sourceFiles': [td.get('sourceFile', 'unknown') for td in text_data_list]
    }

    return merged_text


def _merge_entity_annotations(entities: List[Dict], total_annotators: int, strategy: str, min_agreement: float) -> List[Dict]:
    """Merge entity annotations using the specified strategy."""
    if strategy == "union":
        return _merge_union(entities)
    elif strategy == "intersection":
        return _merge_intersection(entities, total_annotators)
    else:
        return _merge_majority(entities, total_annotators, min_agreement)


def _merge_union(annotations: List[Dict]) -> List[Dict]:
    """Union strategy: include all unique annotations."""
    unique: Dict = {}
    for ann in annotations:
        key = (ann.get('start'), ann.get('end'), ann.get('text', ''))
        if key not in unique:
            unique[key] = ann.copy()
    return list(unique.values())


def _merge_intersection(annotations: List[Dict], total_annotators: int) -> List[Dict]:
    """Intersection strategy: include only annotations agreed by all annotators."""
    counts: Dict = defaultdict(list)
    for ann in annotations:
        key = (ann.get('start'), ann.get('end'), ann.get('text', ''), ann.get('label'))
        counts[key].append(ann)
    return [ann_list[0] for ann_list in counts.values() if len(ann_list) == total_annotators]


def _merge_majority(annotations: List[Dict], total_annotators: int, min_agreement: float) -> List[Dict]:
    """Majority strategy: include annotations with sufficient agreement."""
    span_groups: Dict = defaultdict(list)
    for ann in annotations:
        span_key = (ann.get('start'), ann.get('end'), ann.get('text', ''))
        span_groups[span_key].append(ann)

    result = []
    for span_annotations in span_groups.values():
        label_counts = Counter(ann.get('label') for ann in span_annotations)
        most_common_label, count = label_counts.most_common(1)[0]
        if count / total_annotators >= min_agreement:
            base_ann = span_annotations[0].copy()
            base_ann['label'] = most_common_label
            base_ann['agreement'] = count / total_annotators
            base_ann['annotatorCount'] = count
            result.append(base_ann)

    return result


def _write_json_output(merged_results: Dict, output_path: Path):
    """Write merged results to JSON file."""
    current_time = datetime.datetime.now().isoformat()
    if 'taskInfo' in merged_results:
        merged_results['taskInfo']['exportedAt'] = current_time
        if 'mergeInfo' in merged_results['taskInfo']:
            merged_results['taskInfo']['mergeInfo']['mergedAt'] = current_time

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_results, f, indent=2, ensure_ascii=False)


def _display_merge_summary(merged_results: Dict, all_results: List[Dict]):
    """Display summary statistics of the merge operation."""
    table = Table(title="Merge Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    total_texts = len(set().union(*[r['data'].get('results', {}).keys() for r in all_results]))
    merged_texts = len(merged_results.get('results', {}))

    total_entities = 0
    total_comments = 0
    completed_texts = 0

    for text_data in merged_results.get('results', {}).values():
        if isinstance(text_data, dict):
            total_entities += len(text_data.get('entities', []))
            total_comments += len(text_data.get('comments', []))
            if text_data.get('status') == 'completed':
                completed_texts += 1

    merge_info = merged_results.get('taskInfo', {}).get('mergeInfo', {})

    table.add_row("Total Annotators", str(len(all_results)))
    table.add_row("Total Texts", str(total_texts))
    table.add_row("Merged Texts", str(merged_texts))
    table.add_row("Total Entities", str(total_entities))
    table.add_row("Total Comments", str(total_comments))
    table.add_row("Completed Texts", str(completed_texts))
    if merge_info:
        table.add_row("Strategy Used", merge_info.get('strategy', 'unknown'))
        table.add_row("Min Agreement", str(merge_info.get('minAgreement', 'unknown')))

    console.print(table)
