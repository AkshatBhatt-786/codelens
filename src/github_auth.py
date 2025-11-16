from config_manager import ConfigManager
import questionary
from rich.console import Console
from rich.panel import Panel

console = Console()

def setup_authentication():
    """Setup GitHub authentication"""
    config = ConfigManager()
    
    console.print(Panel(
        "[bold]GitHub Token Setup[/bold]\n"
        "1. Go to: https://github.com/settings/tokens\n"
        "2. Click 'Generate new token (classic)'\n"
        "3. Set expiration (recommended: 90 days)\n"
        "4. Select scopes: 'repo' and 'read:org'\n"
        "5. Copy the token and paste below",
        title="Instructions",
        border_style="yellow"
    ))
    
    token = questionary.password(
        "Enter GitHub Personal Access Token:",
        instruction="(token will be saved locally)"
    ).ask()
    
    if token:
        console.print(f"DEBUG: Token length: {len(token)} characters")
        console.print(f"DEBUG: First 10 chars: {token[:10]}")
        
        # Test the token first
        from github import Github
        try:
            g = Github(token)
            user = g.get_user()
            console.print(Panel(
                f"[green]✓ Authentication successful![/green]\n"
                f"Logged in as: {user.login}\n"
                f"Token length: {len(token)} characters",
                title="Success",
                border_style="green"
            ))
            
            # Save the valid token
            config.save_github_token(token)
            
            # Verify it was saved correctly
            saved_token = config.get_github_token()
            console.print(f"DEBUG: Saved token length: {len(saved_token) if saved_token else 'None'}")
            
            return True
            
        except Exception as e:
            console.print(Panel(
                f"[red]✗ Authentication failed![/red]\n"
                f"Error: {e}",
                title="Authentication Failed",
                border_style="red"
            ))
            return False
    return False

def get_github_client():
    """Get authenticated GitHub client"""
    config = ConfigManager()
    token = config.get_github_token()
    
    if token:
        console.print(f"DEBUG: Retrieved token length: {len(token)}")
        from github import Github
        try:
            return Github(token)
        except Exception as e:
            console.print(f"DEBUG: Failed to create client: {e}")
            return None
    else:
        console.print("DEBUG: No token found in config")
        return None