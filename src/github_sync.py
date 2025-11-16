import json
from datetime import datetime
from github_auth import get_github_client
import os
from rich.panel import Panel
from pathlib import Path
from github import GithubException
from rich.console import Console
import questionary

console = Console()

class GitHubSync:
    def __init__(self):
        self.client = get_github_client()
        self.personal_repo = "codelens-java-codes"
        self.community_repo = None  # Will be set dynamically
        self.contributors_file = "contributors/verified_contributors.json"
        self.requests_dir = "verification_requests"
    
    def get_community_repo_input(self):
        """Get community repository name from user"""
        console.print(Panel(
            "[bold]Community Repository Setup[/bold]\n\n"
            "Enter the community repository in format:\n"
            "[green]username/repository-name[/green] or [green]organization/repository-name[/green]\n\n"
            "Examples:\n"
            "• [cyan]code-lens-community/java-codes[/cyan] (organization)\n"
            "• [cyan]AkshatBhatt-786/java-community[/cyan] (personal)",
            title="Community Setup",
            border_style="yellow"
        ))
        
        repo_input = questionary.text(
            "Enter community repository:",
            default="code-lens-community/java-codes",
            instruction="format: owner/repo-name"
        ).ask()
        
        if repo_input and "/" in repo_input:
            self.community_repo = repo_input
            return True
        else:
            console.print("[red]Invalid format. Use: owner/repository-name[/red]")
            return False
    
    def setup_community_repo(self):
        """Setup community repository - create if doesn't exist"""
        if not self.client:
            return None
        
        # If community repo not set, ask user
        if not self.community_repo:
            if not self.get_community_repo_input():
                return None

        try:
            repo = self.client.get_repo(self.community_repo)
            console.print(f"[green]Found community repository: {repo.full_name}[/green]")
            return repo
        except GithubException as e:
            if e.status == 404:
                # Repo doesn't exist, ask to create it
                console.print(Panel(
                    f"[yellow]Repository '{self.community_repo}' not found[/yellow]\n\n"
                    "Options:\n"
                    "1. Create this repository automatically\n"
                    "2. Enter a different repository name\n"
                    "3. Cancel and create manually",
                    title="Repository Not Found",
                    border_style="yellow"
                ))
                
                choice = questionary.select(
                    "What would you like to do?",
                    choices=[
                        f"Create '{self.community_repo}' automatically",
                        "Enter different repository name", 
                        "Cancel and create manually on GitHub"
                    ]
                ).ask()
                
                if choice == f"Create '{self.community_repo}' automatically":
                    return self.create_community_repo()
                elif choice == "Enter different repository name":
                    self.community_repo = None  # Reset to ask again
                    return self.setup_community_repo()
                else:
                    console.print(f"[yellow]Please create repository manually: https://github.com/new[/yellow]")
                    return None
            else:
                console.print(f"[red]GitHub error: {e}[/red]")
                return None
    
    def create_community_repo(self):
        """Create the community repository"""
        try:
            # Extract owner and repo name
            owner, repo_name = self.community_repo.split("/")
            current_user = self.client.get_user().login
            
            # Check if user can create in this owner
            if owner != current_user:
                console.print(Panel(
                    f"[red]Cannot create repository in '{owner}'[/red]\n\n"
                    f"You can only create repositories in your own account ('{current_user}')\n"
                    f"or organizations where you have admin rights.",
                    title="Permission Denied",
                    border_style="red"
                ))
                
                # Offer to create in user's account instead
                use_personal = questionary.confirm(
                    f"Create '{repo_name}' in your personal account ({current_user}) instead?"
                ).ask()
                
                if use_personal:
                    self.community_repo = f"{current_user}/{repo_name}"
                    console.print(f"[green]Using repository: {self.community_repo}[/green]")
                else:
                    return None
            
            # Create the repository
            repo = self.client.get_user().create_repo(
                repo_name,
                description="Community Java code examples for CodeLens",
                private=False,
                auto_init=True  # Initialize with README
            )
            
            # Wait for GitHub to initialize
            import time
            time.sleep(2)
            
            # Create contributors directory and file
            initial_contributors = [self.client.get_user().login]
            repo.create_file(
                self.contributors_file,
                "Initialize verified contributors",
                json.dumps(initial_contributors, indent=2)
            )
            
            console.print(Panel(
                f"[green]Community repository created successfully![/green]\n"
                f"Name: {repo.full_name}\n"
                f"URL: {repo.html_url}",
                title="Community Setup Complete",
                border_style="green"
            ))
            return repo
            
        except Exception as create_error:
            console.print(f"[red]Failed to create community repo: {create_error}[/red]")
            return None
    
    def get_verified_contributors(self):
        """Get dynamic contributors list from community repo"""
        repo = self.setup_community_repo()
        if not repo:
            return ["AkshatBhatt-786"]  # Default admin
            
        try:
            contributors_file = repo.get_contents(self.contributors_file)
            contributors_json = contributors_file.decoded_content.decode()
            return json.loads(contributors_json)
        except:
            return ["AkshatBhatt-786"]  # Default if file doesn't exist
    
    def is_verified_contributor(self):
        """Check if current user is verified contributor"""
        if not self.client:
            return False
        user = self.client.get_user()
        contributors = self.get_verified_contributors()
        return user.login in contributors
    
    def request_verification(self):
        """Submit verification request"""
        if not self.client:
            return False
            
        user = self.client.get_user()
        repo = self.setup_community_repo()
        if not repo:
            return False
        
        request_data = {
            "username": user.login,
            "request_date": datetime.now().isoformat(),
            "status": "pending"
        }
        
        try:
            repo.create_file(
                f"{self.requests_dir}/{user.login}.json",
                f"Verification request from {user.login}",
                json.dumps(request_data, indent=2)
            )
            return True
        except Exception as e:
            console.print(f"[red]Request failed: {e}[/red]")
            return False
    
    def upload_to_community(self, file_path, category):
        """Upload file to community repo (verified users only)"""
        if not self.is_verified_contributor():
            return False
            
        repo = self.setup_community_repo()
        if not repo:
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            user = self.client.get_user()
            file_name = os.path.basename(file_path)
            
            # Add attribution
            attribution = f"// Contributor: {user.login}\n// Uploaded: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            content_with_attribution = attribution + content
            
            repo_path = f"{category}/{file_name}"
            
            repo.create_file(
                repo_path,
                f"Add {file_name} by {user.login}",
                content_with_attribution,
                branch="main"
            )
            return True
        except Exception as e:
            console.print(f"[red]Community upload failed: {e}[/red]")
            return False
    
    def fetch_from_community(self, category=None):
        """Fetch files from community repo (no auth required for read)"""
        repo = self.setup_community_repo()
        if not repo:
            return []
            
        try:
            contents = repo.get_contents(category) if category else repo.get_contents("")
            files = []
            for content in contents:
                # Skip contributor files
                if "contributors" not in content.path and "verification_requests" not in content.path:
                    files.append({
                        "name": content.name,
                        "path": content.path,
                        "type": "file" if content.type == "file" else "dir"
                    })
            return files
        except Exception as e:
            console.print(f"[red]Failed to fetch community files: {e}[/red]")
            return []
    
    def setup_repo(self):
        """Setup personal repository"""
        if not self.client:
            return None
            
        try:
            repo = self.client.get_user().get_repo(self.personal_repo)
            return repo
        except GithubException as e:
            if e.status == 404:
                try:
                    repo = self.client.get_user().create_repo(
                        self.personal_repo,
                        description="CodeLens Java Learning Codes",
                        private=False
                    )
                    return repo
                except GithubException:
                    return None
            return None
    
    def upload_file(self, file_path, category):
        """Upload file to personal repository"""
        repo = self.setup_repo()
        if not repo:
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_name = os.path.basename(file_path)
            repo_path = f"{category}/{file_name}"
            
            repo.create_file(
                repo_path,
                f"Add {file_name} via CodeLens",
                content,
                branch="main"
            )
            return True
        except Exception as e:
            print(f"Upload error: {e}")
            return False
    
    def list_remote_files(self, category=None):
        """List files from personal repository"""
        repo = self.setup_repo()
        if not repo:
            return []
            
        try:
            contents = repo.get_contents(category) if category else repo.get_contents("")
            files = []
            for content in contents:
                files.append({
                    "name": content.name,
                    "path": content.path,
                    "type": "file" if content.type == "file" else "dir"
                })
            return files
        except:
            return []
    
    def download_file(self, remote_path, local_path):
        """Download a file from GitHub to local storage"""
        repo = self.setup_repo()
        if not repo:
            return False
            
        try:
            file_content = repo.get_contents(remote_path)
            local_path = Path(local_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(file_content.decoded_content.decode())
            
            console.print(f"[green]Downloaded: {remote_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Download failed: {e}[/red]")
            return False