"""Build command for generating HTML annotation tools."""

import typer
from typing_extensions import Annotated
from pathlib import Path
from typing import Optional
from rich.console import Console

from ..generator import generator_manager

console = Console()

app = typer.Typer(help="Build annotation tool HTML from task definition")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    worker: Annotated[str, typer.Option("--worker", help="Worker name for personalized HTML")],
    task_file: Optional[Path] = typer.Argument(None, help="Path to task definition JSON file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output HTML file path"),
    result: Optional[Path] = typer.Option(None, "--result", "-r", help="Path to result JSON file to embed in HTML"),
):
    """
    Build HTML annotation tool from task definition file.

    Examples:
        rapidmark build task.rapidmark.json --worker alice
        rapidmark build task.rapidmark.json --worker alice --result alice.result.rapidmark.json
        rapidmark build task.rapidmark.json --output my-tool.html
    """

    if task_file is None:
        console.print(ctx.get_help())
        raise typer.Exit()

    if not task_file.exists():
        console.print(f"❌ Task file not found: {task_file}")
        raise typer.Exit(1)

    if not task_file.suffix == '.json' and not task_file.name.endswith('.rapidmark.json'):
        console.print(f"❌ Task file must be a JSON file: {task_file}")
        raise typer.Exit(1)

    if result is not None and not result.exists():
        console.print(f"❌ Result file not found: {result}")
        raise typer.Exit(1)

    if output is None:
        if task_file.name.endswith('.rapidmark.json'):
            base_name = task_file.name[:-len('.rapidmark.json')]
        else:
            base_name = task_file.stem

        if worker:
            output_name = f"{base_name}.{worker}.rapidmark.html"
        else:
            output_name = f"{base_name}.rapidmark.html"

        output = task_file.parent / output_name

    try:
        generator_manager.build_html(
            task_file=task_file,
            output_file=output,
            worker_name=worker,
            result_file=result,
        )

        console.print(f"🎉 Success! HTML tool generated at: {output}")
        if worker:
            console.print(f"👤 Personalized for worker: {worker}")
        if result:
            console.print(f"📊 Results embedded from: {result}")

    except Exception as e:
        console.print(f"❌ Build failed: {e}")
        raise typer.Exit(1)




if __name__ == "__main__":
    app()
