from rich.console import Console
from rich.text import Text
import os
import getpass
import pyfiglet

class BaseScreen:
    def __init__(self):
        self.console = Console()
        self.username = getpass.getuser()
    
    def clear_screen(self):
        os.system('clear')
    
    def show(self):
        self.clear_screen()
        self.display_prompt()
        self.display_content()
    
    def display_prompt(self):
        prompt = Text()
        prompt.append(f"{self.username}@codelens", style="bold green")
        prompt.append(":~$ ", style="bold white")
        self.console.print(prompt)
    
    def ascii_banner(self, text, font="slant", color="cyan"):
        ascii_art = pyfiglet.figlet_format(text, font=font)
        self.console.print(Text(ascii_art, style=color))