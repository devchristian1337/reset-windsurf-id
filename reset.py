#!/usr/bin/env python3
"""
Windsurf Trial Reset Tool

A utility script to manage device IDs in Windsurf's configuration system. Features:
- Reset device IDs to new random values
- View current device ID configuration 
- Interactive CLI with progress indicators
- Cross-platform support (Windows/Unix)

Repository: https://github.com/devchristian1337/reset-windsurf-id
Author: @devchristian1337
Created: 20/Jan/2025
"""

import json
import os
import shutil
import uuid
import logging
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.prompt import Confirm, Prompt
from rich.theme import Theme
from rich.layout import Layout
from rich.table import Table
from rich import print as rprint
from rich.style import Style
from rich.text import Text

# Import platform-specific modules
if platform.system() == "Windows":
    import msvcrt
    import os as win_os
else:
    import tty
    import termios
    import os as unix_os


def set_terminal_title(title: str):
    """Set the terminal title in a cross-platform way."""
    if platform.system() == "Windows":
        os.system(f"title {title}")
    else:
        # For Unix-like systems (Linux, macOS)
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()


def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    if platform.system() == "Windows":
        win_os.system("cls")
    else:
        unix_os.system("clear")


def hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB format."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"{r},{g},{b}"


# Enhanced theme configuration with custom colors
custom_theme = Theme(
    {
        "info": f"bold rgb({hex_to_rgb('#0A4A43')})",  # Darkest shade for maximum contrast
        "warning": f"bold rgb({hex_to_rgb('#158F82')})",  # Deep teal
        "error": "bold red",  # Keep red for errors (better accessibility)
        "success": f"bold rgb({hex_to_rgb('#21c0ae')})",  # Primary turquoise
        "header": f"bold rgb({hex_to_rgb('#0A4A43')})",  # Darkest shade
        "prompt": f"bold rgb({hex_to_rgb('#158F82')})",  # Deep teal
        "progress.bar": f"rgb({hex_to_rgb('#21c0ae')})",  # Primary turquoise
        "progress.percentage": f"rgb({hex_to_rgb('#0A4A43')})",  # Darkest shade
        "menu.border": f"rgb({hex_to_rgb('#158F82')})",  # Deep teal
        "menu.title": f"bold rgb({hex_to_rgb('#0A4A43')})",  # Darkest shade
        "dialog.border": f"rgb({hex_to_rgb('#21c0ae')})",  # Primary turquoise
        "dialog.title": f"bold rgb({hex_to_rgb('#0A4A43')})",  # Darkest shade
    }
)

# Configure rich console with enhanced theme
console = Console(theme=custom_theme)

# Configure logging with rich handler
logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class WindsurfResetError(Exception):
    """Custom exception for Windsurf reset-related errors."""

    pass


def display_header():
    """Display an enhanced header with version and system information."""
    message = Text(
        "This tool will reset your Windsurf device IDs and create a backup of your existing configuration.",
        justify="center",
    )
    console.print(
        Panel(
            message,
            title="🔧 Windsurf Reset Tool v1.0",
            border_style="menu.border",
            title_align="center",
            padding=(1, 2),
        )
    )


def display_menu() -> str:
    """
    Display an interactive menu with available options.

    Returns:
        str: Selected menu option
    """
    menu_items = {
        "1": "Reset Device IDs",
        "2": "View Current Configuration",
        "3": "Exit",
    }

    menu = Table.grid(padding=2)
    menu.add_column(style="prompt")
    menu.add_column(style="info")

    for key, value in menu_items.items():
        menu.add_row(f"[{key}]", value)

    console.print(
        Panel(menu, title="Main Menu", border_style="menu.border", padding=(1, 2))
    )

    console.print("[prompt]Press a key to select an option[/prompt]")
    while True:
        choice = get_single_keypress()
        if choice in menu_items:
            return choice


def confirm_action(message: str) -> bool:
    """
    Display an enhanced confirmation dialog.

    Args:
        message: Confirmation message to display

    Returns:
        bool: True if confirmed, False otherwise
    """
    console.print(f"\n[dialog.title]{message} (y/n)[/dialog.title]")
    while True:
        choice = get_single_keypress()
        if choice == "y":
            return True
        elif choice == "n":
            return False


def get_single_keypress() -> str:
    """
    Get a single keypress from the user without requiring Enter.
    Cross-platform implementation for Windows, macOS, and Linux.

    Returns:
        str: The character pressed by the user
    """
    if platform.system() == "Windows":
        return msvcrt.getch().decode("utf-8").lower()
    else:
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
    Create a timestamped backup of the given file with enhanced progress feedback.

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
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Creating backup...", total=100)
                shutil.copy2(file_path, backup_path)
                progress.update(task, advance=100)

            message = Text(f"Backup created at:\n{backup_path}", justify="center")
            console.print(
                Panel(
                    message,
                    title="[+] Backup Complete",
                    border_style="success",
                    padding=(1, 2),
                )
            )
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

        paths = {
            "Windows": Path(os.getenv("APPDATA", "")),
            "Darwin": Path.home() / "Library" / "Application Support",
            "Linux": Path.home() / ".config",
        }

        base_path = paths.get(system)
        if not base_path:
            supported_os = ", ".join(paths.keys())
            raise WindsurfResetError(
                f"Unsupported operating system: {system}. "
                f"Supported systems are: {supported_os}"
            )

        storage_path = (
            base_path / "Windsurf" / "User" / "globalStorage" / "storage.json"
        )

        if not base_path.exists():
            raise WindsurfResetError(f"Base directory does not exist: {base_path}")
        if not os.access(str(base_path), os.W_OK):
            raise WindsurfResetError(f"No write permission for directory: {base_path}")

        return storage_path
    except Exception as e:
        if isinstance(e, WindsurfResetError):
            raise
        raise WindsurfResetError(
            f"Failed to determine storage file location: {str(e)}"
        ) from e


def generate_device_ids() -> Dict[str, str]:
    """
    Generate new device IDs for Windsurf.

    Returns:
        Dictionary containing the new device IDs
    """
    return {
        "telemetry.machineId": os.urandom(32).hex(),
        "telemetry.macMachineId": os.urandom(32).hex(),
        "telemetry.devDeviceId": str(uuid.uuid4()),
    }


def display_device_ids(ids: Dict[str, str], title: str = "Device IDs"):
    """
    Display device IDs in a formatted panel.

    Args:
        ids: Dictionary of device IDs to display
        title: Title for the panel
    """
    table = Table.grid(padding=2)
    table.add_column(style=f"rgb({hex_to_rgb('#0A4A43')})")  # Darkest shade for labels
    table.add_column(style=f"rgb({hex_to_rgb('#158F82')})")  # Deep teal for values

    # Filter out telemetry.sqmId
    filtered_ids = {k: v for k, v in ids.items() if k != "telemetry.sqmId"}

    for key, value in filtered_ids.items():
        table.add_row(f"{key}:", value)

    console.print(Panel(table, title=title, border_style="info", padding=(1, 2)))


def reset_windsurf_id() -> bool:
    """
    Reset Windsurf device IDs by generating new random identifiers.

    Returns:
        bool: True if reset was successful, False otherwise

    Raises:
        WindsurfResetError: If any step in the reset process fails
    """
    try:
        storage_file = get_storage_file()

        if storage_file.exists():
            if confirm_action("Would you like to create a backup before proceeding?"):
                backup_file(storage_file)
            else:
                warning_message = Text("Proceeding without backup", justify="center")
                console.print(
                    Panel(
                        warning_message,
                        title="[!] Warning",
                        border_style="warning",
                        padding=(1, 2),
                    )
                )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            # Initialize total steps
            total_steps = 5
            current_step = 0

            # Show storage file status
            task = progress.add_task("🔍 Locating storage file...", total=total_steps)
            current_step += 1
            progress.update(task, completed=current_step)

            # Create directories if needed
            progress.update(task, description="📁 Creating directories...")
            storage_file.parent.mkdir(parents=True, exist_ok=True)
            current_step += 1
            progress.update(task, completed=current_step)

            # Load existing data
            progress.update(task, description="📖 Loading configuration...")
            data = {}
            if storage_file.exists():
                try:
                    with open(storage_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    warning_message = Text(
                        "Invalid JSON in storage file, creating new configuration",
                        justify="center",
                    )
                    console.print(
                        Panel(
                            warning_message,
                            title="[!] Warning",
                            border_style="warning",
                            padding=(1, 2),
                        )
                    )
            current_step += 1
            progress.update(task, completed=current_step)

            # Generate and update IDs
            progress.update(task, description="🔄 Generating new device IDs...")
            new_ids = generate_device_ids()
            data.update(new_ids)
            current_step += 1
            progress.update(task, completed=current_step)

            # Save configuration
            progress.update(task, description="💾 Saving configuration...")
            with open(storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            current_step += 1
            progress.update(task, completed=current_step)

        # Show success message
        success_message = Text(
            "Device IDs have been successfully reset!", justify="center"
        )
        console.print(
            Panel(
                success_message, title="Success", border_style="success", padding=(1, 2)
            )
        )

        display_device_ids(new_ids, "New Device IDs")
        return True

    except WindsurfResetError as e:
        error_message = Text(f"Reset failed: {str(e)}", justify="center")
        console.print(
            Panel(
                error_message, title="[x] Error", border_style="error", padding=(1, 2)
            )
        )
        raise
    except Exception as e:
        error_message = Text(f"Unexpected error: {str(e)}", justify="center")
        console.print(
            Panel(
                error_message, title="[x] Error", border_style="error", padding=(1, 2)
            )
        )
        raise WindsurfResetError(f"Failed to reset Windsurf IDs: {str(e)}") from e


def view_current_config():
    """Display the current configuration if it exists."""
    try:
        storage_file = get_storage_file()
        if storage_file.exists():
            with open(storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                display_device_ids(
                    {k: v for k, v in data.items() if k.startswith("telemetry")},
                    "Current Device IDs",
                )
        else:
            info_message = Text("No configuration file found", justify="center")
            console.print(
                Panel(
                    info_message,
                    title="[i] Information",
                    border_style="info",
                    padding=(1, 2),
                )
            )
    except Exception as e:
        error_message = Text(
            f"Failed to read configuration: {str(e)}", justify="center"
        )
        console.print(
            Panel(
                error_message, title="[x] Error", border_style="error", padding=(1, 2)
            )
        )


if __name__ == "__main__":
    try:
        set_terminal_title("Windsurf Reset Tool v1.0")
        clear_screen()  # Clear screen before starting
        while True:
            display_header()
            choice = display_menu()

            if choice == "1":
                if confirm_action("Are you sure you want to reset your device IDs?"):
                    reset_windsurf_id()
            elif choice == "2":
                view_current_config()
            else:
                goodbye_message = Text(
                    "Thank you for using Windsurf Reset Tool!", justify="center"
                )
                console.print(
                    Panel(
                        goodbye_message,
                        title="[-] Goodbye",
                        border_style="info",
                        padding=(1, 2),
                    )
                )
                break

            if choice != "3":
                if not confirm_action("Would you like to perform another operation?"):
                    goodbye_message = Text(
                        "Thank you for using Windsurf Reset Tool!", justify="center"
                    )
                    console.print(
                        Panel(
                            goodbye_message,
                            title="[-] Goodbye",
                            border_style="info",
                            padding=(1, 2),
                        )
                    )
                    break

    except WindsurfResetError as e:
        error_message = Text(f"Error: {str(e)}", justify="center")
        console.print(
            Panel(
                error_message, title="[x] Error", border_style="error", padding=(1, 2)
            )
        )
        exit(1)
    except KeyboardInterrupt:
        warning_message = Text("Operation cancelled by user", justify="center")
        console.print(
            Panel(
                warning_message,
                title="[!] Warning",
                border_style="warning",
                padding=(1, 2),
            )
        )
        exit(1)