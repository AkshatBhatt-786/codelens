import sys
from cx_Freeze import setup, Executable
import os

# Dependencies
build_exe_options = {
    "packages": [
        "rich", "questionary", "pygments", "github", 
        "git", "requests", "aiofiles", "watchdog",
        "json", "os", "sys", "pathlib", "getpass", "time",
        "datetime", "ssl", "urllib3", "charset_normalizer",
        "idna", "certifi", "http", "email", "base64"
    ],
    "include_files": [
        ("README.md", "README.md"),
        ("requirements.txt", "requirements.txt")
    ],
    "excludes": ["tkinter", "test", "unittest", "pytest"],
    "optimize": 2
}

# Base for Windows
base = "Console"

setup(
    name="CodeLens",
    version="1.0.0",
    description="Java Learning Platform with GitHub Sync",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "src/main.py",
            base=base,
            target_name="codelens.exe",
        )
    ]
)