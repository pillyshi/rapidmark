"""CLI entry point for RapidMark."""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from . import __version__
from .commands import merge, init, build, clean

app = typer.Typer(
    name="rapidmark",
    help="RapidMark - Fast and efficient NLP annotation tool",
    rich_markup_mode="rich",
)

console = Console()

# Add subcommands
app.add_typer(init.app, name="init", help="Initialize new task definition files")
app.add_typer(build.app, name="build", help="Build HTML annotation tools")
app.add_typer(merge.app, name="merge", help="Merge annotation results")
app.add_typer(clean.app, name="clean", help="Clean generator cache")


def version_callback(value: bool):
    """Show version information."""
    if value:
        console.print(f"[bold blue]RapidMark[/bold blue] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, help="Show version and exit"
    ),
):
    """
    RapidMark - Fast and efficient NLP annotation tool for NER tasks.
    """
    pass


@app.command()
def info():
    """Display tool information and help."""
    console.print("[bold blue]RapidMark[/bold blue]", style="bold")
    console.print(f"Version: [green]{__version__}[/green]")
    console.print()
    console.print("🎯 [bold]Fast and efficient NLP annotation tool[/bold]")
    console.print()

    table = Table(title="Available Commands")
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")

    table.add_row("init", "Initialize new task definition files")
    table.add_row("build", "Build HTML annotation tools from task definitions")
    table.add_row("merge", "Merge annotation results from multiple annotators")
    table.add_row("clean", "Clean generator cache")
    table.add_row("info", "Show this information")

    console.print(table)
    console.print()
    console.print("Use [cyan]rapidmark COMMAND --help[/cyan] for command-specific help.")
    console.print()
    console.print("🚀 [dim]Quick start:[/dim]")
    console.print("   [cyan]rapidmark init --name my-task[/cyan]")
    console.print("   [cyan]rapidmark build my-task.rapidmark.json --worker alice[/cyan]")
    console.print("   [cyan]rapidmark clean[/cyan] [dim](if needed)[/dim]")


if __name__ == "__main__":
    app()
