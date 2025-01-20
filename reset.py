#!/usr/bin/env python3
'''
Windsurf Trial Reset Tool

This script resets the device IDs in Windsurf's configuration file to generate a new random device ID.

Repository: ...
Author: @devchristian1337
Created: 20/Jan/2025
'''

import json
import os
import shutil
import uuid
import logging
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.theme import Theme
from rich import print as rprint

# Import platform-specific modules
if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios

# Configure rich console
console = Console(theme=Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "success": "green"
}))

# Configure logging with rich handler
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class WindsurfResetError(Exception):
    """Custom exception for Windsurf reset-related errors."""
    pass

def get_single_keypress() -> str:
    """
    Get a single keypress from the user without requiring Enter.
    Cross-platform implementation for Windows, macOS, and Linux.
    
    Returns:
        str: The character pressed by the user
    """
    if platform.system() == "Windows":
        import msvcrt
        return msvcrt.getch().decode('utf-8').lower()
    else:
        # Only import Unix-specific modules when needed
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def backup_file(file_path: Path) -> Optional[Path]:
    """
    Create a timestamped backup of the given file.
    
    Args:
        file_path: Path to the file to backup
        
    Returns:
        Path to the backup file if successful, None if source doesn't exist
        
    Raises:
        WindsurfResetError: If backup operation fails
    """
    try:
        if file_path.exists():
            backup_path = file_path.with_name(
                f"{file_path.name}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            shutil.copy2(file_path, backup_path)
            console.print(f"[info]✓ Created backup at:[/info] {backup_path}")
            return backup_path
        return None
    except Exception as e:
        raise WindsurfResetError(f"Failed to create backup: {str(e)}") from e

def get_storage_file() -> Path:
    """
    Determine the storage file location based on the operating system.
    
    Returns:
        Path object pointing to the storage file location
        
    Raises:
        WindsurfResetError: If the operating system is not supported
    """
    try:
        system = platform.system()
        
        # Common paths for different operating systems
        paths = {
            "Windows": Path(os.getenv("APPDATA", "")),
            "Darwin": Path.home() / "Library" / "Application Support",
            "Linux": Path.home() / ".config"
        }
        
        base_path = paths.get(system)
        if not base_path:
            supported_os = ", ".join(paths.keys())
            raise WindsurfResetError(
                f"Unsupported operating system: {system}. "
                f"Supported systems are: {supported_os}"
            )
        
        storage_path = base_path / "Windsurf" / "User" / "globalStorage" / "storage.json"
        
        # Verify path is valid and accessible
        if not base_path.exists():
            raise WindsurfResetError(f"Base directory does not exist: {base_path}")
        if not os.access(str(base_path), os.W_OK):
            raise WindsurfResetError(f"No write permission for directory: {base_path}")
            
        return storage_path
    except Exception as e:
        if isinstance(e, WindsurfResetError):
            raise
        raise WindsurfResetError(f"Failed to determine storage file location: {str(e)}") from e

def generate_device_ids() -> Dict[str, str]:
    """
    Generate new device IDs for Windsurf.
    
    Returns:
        Dictionary containing the new device IDs
    """
    return {
        "telemetry.machineId": os.urandom(32).hex(),
        "telemetry.macMachineId": os.urandom(32).hex(),
        "telemetry.devDeviceId": str(uuid.uuid4())
    }

def reset_windsurf_id() -> bool:
    """
    Reset Windsurf device IDs by generating new random identifiers.
    
    Returns:
        bool: True if reset was successful, False otherwise
        
    Raises:
        WindsurfResetError: If any step in the reset process fails
    """
    try:
        # Get storage file location first
        storage_file = get_storage_file()
        
        # Ask for backup confirmation before starting progress
        should_backup = False
        if storage_file.exists():
            console.print("\n[warning]⚠️  Would you like to create a backup before proceeding? (y/n)[/warning]")
            while True:
                response = get_single_keypress()
                if response in ['y', 'n']:
                    should_backup = (response == 'y')
                    console.print(f"\n[info]Selected: {response}[/info]")
                    break
            
            if not should_backup:
                console.print("[warning]⚠️  Proceeding without backup[/warning]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Show storage file status
            task = progress.add_task("🔍 Locating storage file...", total=None)
            progress.update(task, description="✓ Storage file located")
            
            # Create directories if needed
            task = progress.add_task("📁 Creating directories...", total=None)
            storage_file.parent.mkdir(parents=True, exist_ok=True)
            progress.update(task, description="✓ Directories ready")
            
            # Create backup if requested
            if should_backup:
                task = progress.add_task("💾 Creating backup...", total=None)
                backup_file(storage_file)
                progress.update(task, description="✓ Backup created")
            
            # Load existing data
            task = progress.add_task("📖 Loading configuration...", total=None)
            data = {}
            if storage_file.exists():
                try:
                    with open(storage_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except json.JSONDecodeError as e:
                    console.print("[warning]⚠️  Invalid JSON in storage file, creating new configuration[/warning]")
            progress.update(task, description="✓ Configuration loaded")
            
            # Generate and update IDs
            task = progress.add_task("🔄 Generating new device IDs...", total=None)
            new_ids = generate_device_ids()
            data.update(new_ids)
            progress.update(task, description="✓ New device IDs generated")
            
            # Save configuration
            task = progress.add_task("💾 Saving configuration...", total=None)
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            progress.update(task, description="✓ Configuration saved")

        # Show success message
        console.print("\n[success]🎉 Device IDs have been successfully reset![/success]\n")
        console.print(Panel.fit(
            json.dumps(new_ids, indent=2),
            title="New Device IDs",
            border_style="green"
        ))
        
        return True
        
    except WindsurfResetError as e:
        console.print(f"\n[error]❌ Reset failed: {str(e)}[/error]")
        raise
    except Exception as e:
        console.print(f"\n[error]❌ Unexpected error: {str(e)}[/error]")
        raise WindsurfResetError(f"Failed to reset Windsurf IDs: {str(e)}") from e

if __name__ == "__main__":
    console.print(Panel.fit(
        "This tool will reset your Windsurf device IDs and create a backup of your existing configuration.",
        title="🔧 Windsurf Reset Tool",
        border_style="cyan"
    ))
    console.print()
    
    try:
        reset_windsurf_id()
    except WindsurfResetError as e:
        console.print(f"\n[error]❌ Error: {str(e)}[/error]")
        exit(1)
    except KeyboardInterrupt:
        console.print("\n[warning]⚠️  Operation cancelled by user[/warning]")
        exit(1)