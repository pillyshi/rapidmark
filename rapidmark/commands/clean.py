"""Clean command for clearing generator cache."""

import typer
from rich.console import Console

from ..generator import generator_manager

console = Console()

app = typer.Typer(help="Clean generator cache")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Clean generator cache to force re-setup on next build."""
    try:
        generator_manager.cleanup_cache()
        console.print("✅ Generator cache cleaned")
    except Exception as e:
        console.print(f"❌ Failed to clean cache: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()