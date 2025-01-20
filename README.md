# 🌊 Windsurf Trial Reset Tool

![Command Line Interface](https://iili.io/2i2i8gI.png)

A Python utility script that resets device IDs in Windsurf's configuration file by generating new random identifiers. This tool is useful for managing Windsurf installations and resetting trial periods.

## ✨ Features

- Modern and beautiful terminal UI with progress indicators
- Color-coded output for better readability
- Real-time progress tracking with spinners
- Automatically detects and supports multiple operating systems (Windows, macOS, Linux)
- Creates timestamped backups of existing configuration files
- Generates secure random device IDs
- Provides detailed logging for troubleshooting
- Handles errors gracefully with informative messages

## 📋 Requirements

- Python 3.6 or higher
  - Download Python:
    - Windows 64-bit: [Python 3.13.1 (64-bit)](https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe)
    - Windows 32-bit: [Python 3.13.1 (32-bit)](https://www.python.org/ftp/python/3.13.1/python-3.13.1.exe)
    - macOS: [Python 3.13.1](https://www.python.org/ftp/python/3.13.1/python-3.13.1-macos11.pkg)
- Required packages (installed automatically via requirements.txt):
  - rich (13.6.0 or higher) - Beautiful terminal output and progress indicators
  - typing-extensions (4.8.0 or higher) - Enhanced type hints support

## 🚀 Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd reset-windsurf-id
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable (Unix-based systems only):
```bash
chmod +x reset.py
```

## 🛠️ Usage

Run the script directly from the command line:

```bash
# Windows
python reset.py

# macOS/Linux
./reset.py
```

The script will:
1. Display a welcome message with instructions
2. Detect your operating system and locate the appropriate storage file
3. Offer to create a backup of your existing configuration
4. Show real-time progress with spinners for each operation:
   - Locating storage file
   - Creating necessary directories
   - Creating backup (if requested)
   - Loading existing configuration
   - Generating new device IDs
   - Saving updated configuration
5. Display the newly generated device IDs upon completion

### ⚠️ Error Handling

The script includes comprehensive error handling for common scenarios:
- Unsupported operating systems
- Missing directories
- Insufficient permissions
- Invalid JSON configuration
- Backup failures

If any error occurs, the script will:
1. Display a detailed error message
2. Create a backup if possible
3. Exit with a non-zero status code

## 📂 Configuration File Locations

The script automatically manages configuration files in the following locations:

- Windows: `%APPDATA%\Windsurf\User\globalStorage\storage.json`
- macOS: `~/Library/Application Support/Windsurf/User/globalStorage/storage.json`
- Linux: `~/.config/Windsurf/User/globalStorage/storage.json`

## 💾 Backup System

Before making any changes, the script automatically creates a backup of your existing configuration file with a timestamp:
```
storage.json.backup_YYYYMMDD_HHMMSS
```

## 🔒 Security

- Uses cryptographically secure random number generation (`os.urandom`)
- Generates UUIDs for device identification
- Maintains existing file permissions

## 👥 Contributing

Feel free to submit issues and enhancement requests through the repository's issue tracker.

## 👨‍💻 Author

@devchristian1337

## 📅 Created

January 20, 2025