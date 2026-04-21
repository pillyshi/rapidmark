"""Initialize new task definition files."""

import json
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console

app = typer.Typer(help="Initialize new task definition files")
console = Console()


def get_task_template(task_name: str) -> dict:
    """Get NER task template."""
    return {
        "definition": {
            "id": task_name,
            "name": task_name,
            "description": "",
            "type": "ner",
            "labels": [],
        }
    }


def load_texts_from_directory(texts_dir: Path) -> list:
    """Load all .txt files from directory recursively."""
    texts = []

    if not texts_dir.exists():
        console.print(f"[red]Error: Directory {texts_dir} does not exist[/red]")
        raise typer.Exit(1)

    if not texts_dir.is_dir():
        console.print(f"[red]Error: {texts_dir} is not a directory[/red]")
        raise typer.Exit(1)

    txt_files = list(texts_dir.rglob("*.txt"))

    if not txt_files:
        console.print(f"[yellow]Warning: No .txt files found in {texts_dir}[/yellow]")
        return texts

    console.print(f"[green]Found {len(txt_files)} .txt files in {texts_dir}[/green]")

    for txt_file in sorted(txt_files):
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if content:
                relative_path = txt_file.relative_to(texts_dir)
                text_id = str(relative_path.with_suffix(''))
                text_id = text_id.replace('/', '_').replace('\\', '_')

                texts.append({
                    "id": text_id,
                    "content": content,
                    "sourceFile": str(relative_path)
                })
                console.print(f"  [cyan]✓[/cyan] {relative_path} → {text_id}")
            else:
                console.print(f"  [yellow]⚠[/yellow] {txt_file.name} (empty file, skipped)")

        except Exception as e:
            console.print(f"  [red]✗[/red] {txt_file.name} (error: {e})")
            continue

    return texts


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Task name"),
    texts: Optional[Path] = typer.Option(None, "--texts", help="Directory containing .txt files to include"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path (default: {name}.rapidmark.json)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
):
    """Create a new NER task definition file."""

    if name is None:
        console.print(ctx.get_help())
        raise typer.Exit()

    if output is None:
        output = Path(f"{name}.rapidmark.json")

    if output.exists() and not force:
        console.print(f"[red]Error: File {output} already exists[/red]")
        console.print("Use --force to overwrite")
        raise typer.Exit(1)

    task_config = get_task_template(name)

    if texts is not None:
        console.print(f"[blue]Loading texts from directory: {texts}[/blue]")
        task_config["texts"] = load_texts_from_directory(texts)
    else:
        task_config["texts"] = [
            {
                "id": "sample_text_1",
                "content": "Please annotate this text."
            }
        ]

    try:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(task_config, f, indent=2, ensure_ascii=False)

        console.print(f"[green]✓ Created task definition: {output}[/green]")
        console.print(f"[blue]ℹ[/blue] Included {len(task_config['texts'])} text(s)")
        console.print(f"[blue]ℹ[/blue] You can now build the annotation tool with:")
        console.print(f"  [cyan]rapidmark build {output} --worker alice[/cyan]")

    except Exception as e:
        console.print(f"[red]Error writing file: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
