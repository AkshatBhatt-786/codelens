from .base_screen import BaseScreen
from rich.panel import Panel

class WelcomeScreen(BaseScreen):
    def display_content(self):
        self.ascii_banner("CodeLens", "slant", "bold cyan")
        self.console.print(Panel("Java Learning Platform - Type 'menu' for commands", style="blue"))

