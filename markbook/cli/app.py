from pathlib import Path

import typer
from rich.console import Console

from markbook.compiler import compile
from markbook.watcher import watch as watch_file

app = typer.Typer(help="markbook — compile Markdown DSL to Jupyter Notebooks")
console = Console()


@app.command()
def build(
    input: Path = typer.Argument(..., help="Path to .md source file"),
    output: Path = typer.Option(None, "--output", "-o", help="Output .ipynb path"),
):
    if not input.exists():
        console.print(f"[red]Error:[/red] File not found: {input}")
        raise typer.Exit(1)

    if output is None:
        output = input.with_suffix(".ipynb")

    try:
        compile(input, output)
        console.print(f"[green]✓[/green] Built {output}")
    except Exception as e:
        console.print(f"[red]✗[/red] {e}")
        raise typer.Exit(1)


@app.command()
def watch(
    input: Path = typer.Argument(..., help="Path to .md source file"),
    output: Path = typer.Option(None, "--output", "-o", help="Output .ipynb path"),
):
    if not input.exists():
        console.print(f"[red]Error:[/red] File not found: {input}")
        raise typer.Exit(1)

    if output is None:
        output = input.with_suffix(".ipynb")

    # Initial build
    try:
        compile(input, output)
        console.print(f"[green]✓[/green] Initial build → {output}")
    except Exception as e:
        console.print(f"[red]✗[/red] {e}")

    watch_file(input, output)
