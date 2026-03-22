from pathlib import Path

from rich.console import Console
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .compiler import compile

console = Console()


class MarkbookHandler(FileSystemEventHandler):
    def __init__(self, input_path: Path, output_path: Path):
        self.input_path = input_path.resolve()
        self.output_path = output_path.resolve()

    def on_modified(self, event):
        if Path(event.src_path).resolve() == self.input_path:
            try:
                compile(self.input_path, self.output_path)
                console.print(f"[green]✓[/green] Rebuilt {self.output_path.name}")
            except Exception as e:
                console.print(f"[red]✗[/red] Error: {e}")


def watch(input_path: Path, output_path: Path) -> None:
    handler = MarkbookHandler(input_path, output_path)
    observer = Observer()
    observer.schedule(handler, str(input_path.parent), recursive=False)
    observer.start()
    console.print(f"[blue]Watching[/blue] {input_path.name} → {output_path.name}  (Ctrl+C to stop)")
    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
