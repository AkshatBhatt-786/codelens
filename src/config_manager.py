import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".codelens"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
        print(f"DEBUG: Config path: {self.config_file}")  # Debug
    
    def ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(exist_ok=True)
    
    def is_authenticated(self) -> bool:
        """Check if user has GitHub token"""
        token = self.get_github_token()
        print(f"DEBUG: Checking auth - token exists: {token is not None}")  # Debug
        return token is not None
    
    def get_github_token(self) -> Optional[str]:
        """Get GitHub token from config"""
        print(f"DEBUG: Looking for config at: {self.config_file}")  # Debug
        print(f"DEBUG: Config exists: {self.config_file.exists()}")  # Debug
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    token = config.get('github_token')
                    print(f"DEBUG: Token from file: {token}")  # Debug
                    return token
            except Exception as e:
                print(f"DEBUG: Error reading config: {e}")  # Debug
                return None
        return None
    
    def save_github_token(self, token: str):
        """Save GitHub token to config"""
        config = {}
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"DEBUG: Error reading existing config: {e}")  # Debug
                config = {}
        
        config['github_token'] = token
        print(f"DEBUG: Saving token to config: {token}")  # Debug
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"DEBUG: Config saved successfully")  # Debug
        except Exception as e:
            print(f"DEBUG: Error saving config: {e}")  # Debug
    
    def get_config(self) -> Dict[str, Any]:
        """Get all configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}