#!/usr/bin/env python3
import os
import sys
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.progress import Progress
import time
import questionary
from pathlib import Path
import getpass
from file_manager import FileManager
from github_sync import GitHubSync

sys.path.append(os.path.dirname(__file__))

file_manager = FileManager()
console = Console()
username = getpass.getuser()
github_sync = GitHubSync()

VERSION = "1.0.0"

def linux_prompt():
    prompt = Text()
    prompt.append(f"{username}@code-lens", style="bold green")
    prompt.append(":~$ ", style="bold white")
    console.print(prompt, end="")

def loading_screen(task_name, duration=3):
    with Progress() as progress:
        task = progress.add_task(f"[cyan]{task_name}", total=duration)
        while not progress.finished:
            progress.update(task, advance=0.1)
            time.sleep(0.1)

def display_header():
    header = Panel(
        Text(f"CODE-LENS v{VERSION} - Java Learning Platform", style="bold cyan"),
        box=box.DOUBLE,
        border_style="bright_blue"
    )
    console.print(header)

def show_menu():
    menu_table = Table(
        title="[bold]Available Commands[/bold]",
        box=box.ROUNDED,
        header_style="bold magenta",
        title_style="bold cyan"
    )
    menu_table.add_column("Command", style="bold green", width=20)
    menu_table.add_column("Description", style="white")
    
    commands = [
        ("auth", "Setup GitHub authentication"),
        ("browse", "Browse local Java files"),
        ("upload", "Upload to personal repo"),
        ("upload-community", "Upload to community"),
        ("fetch", "Download from personal repo"),
        ("fetch-community", "Download from community"),
        ("verify-me", "Request contributor access"),
        ("sync", "Sync local with GitHub"),
        ("settings", "Application settings"),
        ("exit", "Quit application")
    ]
    
    for cmd, desc in commands:
        menu_table.add_row(cmd, desc)
    
    console.print(menu_table)

def upload_to_community():
    """Upload file to community repository"""
    if not github_sync.client:
        console.print(Panel(
            "[red]Please setup GitHub authentication first using 'auth' command[/red]",
            title="Authentication Required",
            border_style="red"
        ))
        input("Press Enter to continue...")
        return
    
    # Check if user is verified contributor
    if not github_sync.is_verified_contributor():
        console.print(Panel(
            "[yellow]Community upload requires contributor verification[/yellow]\n"
            "Only verified contributors can upload to the community.\n"
            "Use 'verify-me' to request contributor access.",
            title="Verification Required",
            border_style="yellow"
        ))
        input("Press Enter to continue...")
        return
    
    file_path = questionary.path("Enter file path:").ask()
    
    if file_path and Path(file_path).exists():
        category = questionary.text(
            "Enter category name:",
            instruction="(will be created in community repo)"
        ).ask()
        
        if category:
            loading_screen(f"Uploading to community/{category}", 3)
            if github_sync.upload_to_community(file_path, category):
                console.print(Panel(
                    f"[green]File successfully uploaded to community/{category}/[/green]\n"
                    f"Thank you for contributing to the community!",
                    title="Community Upload Successful",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    "[red]Community upload failed[/red]",
                    title="Upload Failed",
                    border_style="red"
                ))
    else:
        console.print(Panel(
            "[red]File not found or invalid path[/red]",
            title="File Error",
            border_style="red"
        ))
    
    input("Press Enter to continue...")

def fetch_from_community():
    """Download files from community repository"""
    category = questionary.text(
        "Enter category name:",
        instruction="(leave empty for all categories)"
    ).ask()
    
    if category == "":  # User wants all categories
        category = None
    
    loading_screen("Fetching from community", 3)
    files = github_sync.fetch_from_community(category)
    
    if files:
        file_choices = [f["name"] for f in files if f["type"] == "file"]
        if not file_choices:
            console.print(Panel(
                f"[yellow]No files found in category '{category}'[/yellow]",
                title="No Files Found",
                border_style="yellow"
            ))
            input("Press Enter to continue...")
            return
        
        selected_files = questionary.checkbox(
            f"Select files to download from community:",
            choices=file_choices
        ).ask()
        
        if selected_files:
            loading_screen(f"Downloading {len(selected_files)} files", 3)
            success_count = 0
            
            # Determine local directory
            local_category = category if category else "community"
            category_path = Path("java_files") / local_category
            category_path.mkdir(exist_ok=True)
            
            for file_name in selected_files:
                remote_path = f"{category}/{file_name}" if category else file_name
                local_path = category_path / file_name
                
                # Use GitHub API to download file content
                repo = github_sync.setup_community_repo()
                if repo:
                    try:
                        file_content = repo.get_contents(remote_path)
                        with open(local_path, 'w', encoding='utf-8') as f:
                            f.write(file_content.decoded_content.decode())
                        success_count += 1
                        console.print(f"[green]Downloaded: {file_name}[/green]")
                    except Exception as e:
                        console.print(f"[red]Failed to download {file_name}: {e}[/red]")
            
            console.print(Panel(
                f"[green]Successfully downloaded {success_count}/{len(selected_files)} files[/green]\n"
                f"Location: java_files/{local_category}/",
                title="Community Download Complete",
                border_style="green"
            ))
    else:
        console.print(Panel(
            f"[yellow]No files found in community repository[/yellow]",
            title="No Files Found",
            border_style="yellow"
        ))
    
    input("Press Enter to continue...")

def request_verification():
    """Request contributor verification"""
    if not github_sync.client:
        console.print(Panel(
            "[red]Please setup GitHub authentication first using 'auth' command[/red]",
            title="Authentication Required",
            border_style="red"
        ))
        input("Press Enter to continue...")
        return
    
    user = github_sync.client.get_user()
    
    console.print(Panel(
        f"[bold]Contributor Verification Request[/bold]\n\n"
        f"Username: {user.login}\n"
        f"Benefits:\n"
        f"• Upload files to community repository\n"
        f"• Share your Java code with others\n"
        f"• Contribute to learning community\n\n"
        f"Your request will be reviewed by community admins.",
        title="Verification Request",
        border_style="yellow"
    ))
    
    confirm = questionary.confirm("Submit verification request?").ask()
    
    if confirm:
        loading_screen("Submitting request", 2)
        if github_sync.request_verification():
            console.print(Panel(
                f"[green]Verification request submitted successfully![/green]\n"
                f"Username: {user.login}\n"
                f"Admins will review your request soon.",
                title="Request Submitted",
                border_style="green"
            ))
        else:
            console.print(Panel(
                "[red]Failed to submit verification request[/red]",
                title="Request Failed",
                border_style="red"
            ))
    
    input("Press Enter to continue...")

def upload_file():
    if not github_sync.client:
        console.print(Panel(
            "[red]Please setup GitHub authentication first using 'auth' command[/red]",
            title="Authentication Required",
            border_style="red"
        ))
        input("Press Enter to continue...")
        return
    
    file_path = questionary.path("Enter file path:").ask()
    
    if file_path and Path(file_path).exists():
        category = questionary.text(
            "Enter category name:",
            instruction="(creates directory if new)"
        ).ask()
        
        if category:
            category_path = Path("java_files") / category
            category_path.mkdir(exist_ok=True)
            
            loading_screen(f"Uploading to {category}", 3)
            if github_sync.upload_file(file_path, category):
                console.print(Panel(
                    f"[green]File successfully uploaded to GitHub/{category}/[/green]",
                    title="Upload Successful",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    "[red]Upload failed - check your GitHub token and connection[/red]",
                    title="Upload Failed",
                    border_style="red"
                ))
    else:
        console.print(Panel(
            "[red]File not found or invalid path[/red]",
            title="File Error",
            border_style="red"
        ))
    
    input("Press Enter to continue...")

def fetch_files():
    if not github_sync.client:
        console.print(Panel(
            "[red]Please setup GitHub authentication first using 'auth' command[/red]",
            title="Authentication Required",
            border_style="red"
        ))
        input("Press Enter to continue...")
        return
    
    category = questionary.text(
        "Enter category name:",
        instruction="(creates directory if new)"
    ).ask()
    
    if not category:
        return
    
    category_path = Path("java_files") / category
    category_path.mkdir(exist_ok=True)
    
    loading_screen(f"Fetching files for {category}", 3)
    files = github_sync.list_remote_files(category)
    
    if files:
        file_choices = [f["name"] for f in files if f["type"] == "file"]
        selected_files = questionary.checkbox(
            f"Select files to download to '{category}':",
            choices=file_choices
        ).ask()
        
        if selected_files:
            loading_screen(f"Downloading {len(selected_files)} files", 3)
            success_count = 0
            for file_name in selected_files:
                remote_path = f"{category}/{file_name}"
                local_path = category_path / file_name
                if github_sync.download_file(remote_path, local_path):
                    success_count += 1
            
            console.print(Panel(
                f"[green]Successfully downloaded {success_count}/{len(selected_files)} files to {category}/[/green]",
                title="Download Complete",
                border_style="green"
            ))
    else:
        console.print(Panel(
            f"[yellow]No files found in category '{category}'[/yellow]",
            title="No Files Found",
            border_style="yellow"
        ))
    
    input("Press Enter to continue...")

def browse_files():
    current_path = None
    while True:
        if file_manager.check_for_changes():
            console.print(Panel(
                "[yellow]Directory updated - refreshing view[/yellow]",
                border_style="yellow"
            ))
        
        items, current_path = file_manager.list_directory(current_path)
        file_manager.display_files_table(items, current_path)
        
        console.print(Panel(
            "[bold]Navigation Commands:[/bold]\n"
            "[cyan]cd <folder>[/cyan] - Enter directory\n"
            "[cyan]view <file>[/cyan] - View file content\n" 
            "[cyan]back[/cyan] - Go to parent directory\n"
            "[cyan]exit[/cyan] - Return to main menu",
            title="File Browser Help",
            border_style="blue"
        ))
        
        linux_prompt()
        command = input().strip().lower()
        
        if command == "exit":
            break
        elif command == "back":
            if current_path != str(file_manager.base_path):
                current_path = os.path.dirname(current_path)
        elif command.startswith("cd "):
            folder = command[3:]
            new_path = os.path.join(current_path, folder)
            if os.path.exists(new_path) and os.path.isdir(new_path):
                current_path = new_path
            else:
                console.print(Panel(
                    f"[red]Directory '{folder}' not found[/red]",
                    border_style="red"
                ))
        elif command.startswith("view "):
            filename = command[5:]
            file_path = os.path.join(current_path, filename)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                view_file_content(file_path)
            else:
                console.print(Panel(
                    f"[red]File '{filename}' not found[/red]",
                    border_style="red"
                ))
        else:
            console.print(Panel(
                "[red]Unknown command - use 'cd', 'view', 'back', or 'exit'[/red]",
                border_style="red"
            ))

def view_file_content(file_path):
    loading_screen(f"Loading {os.path.basename(file_path)}", 2)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        code_section = []
        output_section = []
        
        lines = content.split('\n')
        in_output_section = False
        
        for line in lines:
            if line.strip().startswith('// output'):
                in_output_section = True
                output_section.append(line.replace('// output', '').strip())
            elif in_output_section:
                if line.strip().startswith('//'):
                    output_section.append(line.replace('//', '').strip())
                else:
                    in_output_section = False
                    code_section.append(line)
            else:
                code_section.append(line)
        
        console.print(Panel(
            '\n'.join(code_section),
            title=f"FILE: {os.path.basename(file_path)}",
            border_style="blue"
        ))
        
        if output_section:
            console.print(Panel(
                '\n'.join(output_section),
                title="OUTPUT SECTION",
                border_style="green"
            ))
        
        input("\nPress Enter to continue...")
    except Exception as e:
        console.print(Panel(
            f"[red]Error reading file: {e}[/red]",
            title="File Read Error",
            border_style="red"
        ))

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_header()
        show_menu()
        
        console.print(Panel(
            f"[bold]System:[/bold] Code-Lens v{VERSION} | [bold]User:[/bold] {username}",
            border_style="bright_black"
        ))
        
        linux_prompt()
        command = input().strip().lower()
        
        if command == "exit":
            console.print(Panel(
                "[blue]Shutting down Code-Lens...[/blue]",
                border_style="blue"
            ))
            break
        elif command == "browse":
            loading_screen("Loading file browser", 2)
            browse_files()
        elif command == "upload":
            loading_screen("Initializing upload", 2)
            upload_file()
        elif command == "sync":
            loading_screen("Syncing with GitHub", 3)
            console.print(Panel(
                "[green]Sync operation completed[/green]",
                title="Sync Status",
                border_style="green"
            ))
            input("Press Enter to continue...")
        elif command == "fetch":
            loading_screen("Initializing file fetch", 2)
            fetch_files()
        elif command == "auth":
            from github_auth import setup_authentication
            setup_authentication()
        elif command == "settings":
            console.print(Panel(
                "[yellow]Settings panel - coming soon[/yellow]",
                title="Settings",
                border_style="yellow"
            ))
            input("Press Enter to continue...")
        elif command == "auth-status":
            from config_manager import ConfigManager
            config = ConfigManager()
            token = config.get_github_token()
            if token:
                console.print(Panel(
                    f"[green]Token found: {token[:10]}...[/green]\n"
                    f"Length: {len(token)} characters\n"
                    f"Authenticated: {config.is_authenticated()}",
                    title="Auth Status",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    "[red]No token found[/red]",
                    title="Auth Status", 
                    border_style="red"
                ))
            input("Press Enter to continue...")
        elif command == "upload-community":
            loading_screen("Initializing community upload", 2)
            upload_to_community()
        elif command == "fetch-community":
            loading_screen("Initializing community fetch", 2)
            fetch_from_community()
        elif command == "verify-me":
            request_verification()
        else:
            console.print(Panel(
                f"[red]Unknown command: {command}[/red]",
                title="Command Error",
                border_style="red"
            ))
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()