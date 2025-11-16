from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from rich.console import Console
from rich.table import Table
import rich.box as rich_box

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
    
    def on_modified(self, event):
        self.callback()
    
    def on_created(self, event):
        self.callback()
    
    def on_deleted(self, event):
        self.callback()

class FileManager:
    def __init__(self, base_path="java_files"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.observer = Observer()
        self.file_changed = False
        
        event_handler = FileChangeHandler(self.on_file_change)
        self.observer.schedule(event_handler, self.base_path, recursive=True)
        self.observer.start()
    
    def on_file_change(self):
        self.file_changed = True

    def list_directory(self, path=None):
        current_path = self.base_path if path is None else Path(path)
        items = []
        
        # Add parent directory entry
        if current_path != self.base_path:
            items.append({
                "name": "..",
                "type": "DIR",
                "size": "-",
                "modified": "-"
            })
        
        for item in sorted(current_path.iterdir(), key=lambda x: (x.is_file(), x.name)):
            stat = item.stat()
            items.append({
                "name": item.name,
                "type": "DIR" if item.is_dir() else "FILE",
                "size": f"{stat.st_size/1024:.1f}KB" if item.is_file() else "-",
                "modified": "-"  # Can add modified time if needed
            })
        return items, str(current_path)
    
    def display_files_table(self, items, current_path):
        console = Console()
        table = Table(
            title=f"Directory: {current_path}",
            box=rich_box.DOUBLE_EDGE,
            header_style="bold magenta",
            title_style="bold cyan",
            border_style="bright_blue"
        )
        
        table.add_column("Type", width=8, style="bold green")
        table.add_column("Name", style="white")
        table.add_column("Size", width=12, justify="right")
        table.add_column("Actions", width=15, style="yellow")
        
        for item in items:
            action = "[bold]OPEN[/bold]" if item["type"] == "DIR" else "[cyan]VIEW[/cyan]"
            table.add_row(
                f"[bold]{item['type']}[/bold]",
                item["name"],
                item["size"],
                action
            )
        
        console.print(table)
    
    def check_for_changes(self):
        if self.file_changed:
            self.file_changed = False
            return True
        return False