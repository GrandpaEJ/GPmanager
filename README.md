# GP Manager

A dual-pane file manager for Linux with APK tools integration, inspired by MT Manager for Android.

## Features

- **Dual-pane file manager** - Navigate with two side-by-side file browsers  ❌ `REMOVED`
- **File operations** - Copy, move, rename, delete with progress dialogs
- **APKTool integration** - Decompile and recompile APK files
- **Text editor** - Built-in editor with syntax highlighting for Smali, Java, XML
- **Archive support** - Browse and extract ZIP/APK archives
- **Dark theme** - Modern dark UI theme
- **Modular design** - Clean, class-based architecture

## Requirements

- Python 3.6+
- PyQt5
- APKTool (for APK operations)
- Java (for APK signing)

## Installation

### Quick Installation (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GrandpaEJ/GPmanager.git
   cd GPmanager
   ```

2. **Run the setup wizard:**
   ```bash
   # GUI installer (recommended)
   python3 setup.py --gui

   # Or command-line installer
   python3 setup.py --install
   ```

3. **Start the application:**
   ```bash
   ./run.sh
   ```

### Manual Installation

#### Ubuntu/Debian Systems
```bash
# Install required dependencies
sudo apt update
sudo apt install python3-pyqt5 python3-pyqt5.qsci python3-pygments python3-magic

# Install optional dependencies for APK operations
sudo apt install apktool default-jdk git

# Run the application
python3 main.py
```

#### Fedora/RHEL/CentOS
```bash
# Install required dependencies
sudo dnf install python3-qt5 qscintilla-python3 python3-pygments python3-magic

# Install optional dependencies
sudo dnf install apktool java-11-openjdk-devel git

# Run the application
python3 main.py
```

#### Arch Linux/Manjaro
```bash
# Install required dependencies
sudo pacman -S python-pyqt5 qscintilla-python python-pygments python-magic

# Install optional dependencies
sudo pacman -S apktool jdk-openjdk git

# Run the application
python3 main.py
```

#### Other Systems (using pip)
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install PyQt5 QScintilla Pygments python-magic

# Install system tools separately
# APKTool: Download from https://ibotpeaches.github.io/Apktool/
# Java: Install OpenJDK from your system package manager

# Run the application
python3 main.py
```

### Setup Options

The setup script provides multiple installation methods:

```bash
# Check dependency status
python3 setup.py --check

# Install missing dependencies
python3 setup.py --install

# Install only required dependencies (skip APKTool, Java, Git)
python3 setup.py --install --skip-optional

# Generate installation script for manual execution
python3 setup.py --script

# Save installation script to file
python3 setup.py --script -o install.sh

# Create desktop entry
python3 setup.py --desktop

# Run GUI setup wizard
python3 setup.py --gui
```

## Usage

### Running the Application

```bash
python main.py
```

### Basic Operations

#### File Management
- **Navigate**: Double-click folders to enter, use ↑ button to go up
- **Copy**: Select files and click "Copy" or Ctrl+C, then paste in other pane
- **Move**: Select files and click "Move" or cut with Ctrl+X
- **Delete**: Select files and press Delete key or click "Delete" button
- **Rename**: Select file and press F2 or right-click → Rename
- **New Folder**: Ctrl+Shift+N or right-click → New Folder

#### Dual Pane Features
- **Swap Panes**: Ctrl+U to swap left and right pane contents
- **Sync Panes**: Ctrl+Shift+O to sync inactive pane to active pane's directory
- **Copy to Other Pane**: Select files and click "Copy" button in toolbar
- **Move to Other Pane**: Select files and click "Move" button in toolbar

#### APK Operations
1. Select an APK file in the file manager
2. Double-click to open APK tools, or click "APK" button in toolbar
3. **Decompile**: Click "Decompile APK" to extract and decompile
4. **Recompile**: Select decompiled directory and click "Recompile APK"
5. **Sign**: Click "Sign APK" to sign with debug key

#### Text Editing
- Double-click text files (.txt, .java, .smali, .xml) to open in editor
- **Syntax highlighting** for Smali, Java, and XML files
- **Find/Replace**: Ctrl+F to open find panel
- **Go to Line**: Ctrl+G to jump to specific line
- **Multiple tabs** for editing multiple files

#### Archive Viewing
- Double-click ZIP/APK files to open in archive viewer
- **Browse contents** with file details (size, compression, date)
- **Extract files**: Select files and click "Extract Selected" or "Extract All"
- **View files**: Double-click text files in archive to view content

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open file |
| Ctrl+S | Save file |
| Ctrl+Shift+N | New folder |
| Ctrl+C | Copy |
| Ctrl+X | Cut |
| Ctrl+V | Paste |
| Delete | Delete selected |
| F2 | Rename |
| F5 | Refresh |
| Ctrl+A | Select all |
| Ctrl+U | Swap panes |
| Ctrl+Shift+O | Sync panes |
| Ctrl+F | Find/Replace |
| Ctrl+G | Go to line |
| Ctrl+, | Preferences |
| Ctrl+Q | Quit |

## Configuration

Access preferences through **File → Preferences** or **Ctrl+,**:

### General Settings
- **Theme**: Dark/Light theme selection
- **Show hidden files**: Toggle visibility of hidden files

### Editor Settings
- **Font family**: Set editor font (default: Consolas)
- **Font size**: Set editor font size (default: 10)

### Tools Settings
- **APKTool path**: Path to apktool executable
- **Java path**: Path to java executable

Configuration is saved in `~/.gpmanager/config.json`

## Project Structure

```
gpmanager/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── main_window.py      # Main application window
│   ├── file_manager/       # File manager components
│   │   ├── file_pane.py    # Single file browser pane
│   │   ├── dual_pane.py    # Dual pane manager
│   │   └── file_operations.py  # File operations
│   ├── editors/            # Text editor components
│   │   ├── text_editor.py  # Text editor widget
│   │   └── syntax_highlighter.py  # Syntax highlighting
│   ├── tools/              # Tool integrations
│   │   ├── apktool.py      # APKTool integration
│   │   └── archive_manager.py  # Archive handling
│   ├── ui/                 # UI components
│   │   ├── themes.py       # Theme management
│   │   └── dialogs.py      # Custom dialogs
│   └── utils/              # Utility modules
│       ├── file_utils.py   # File utility functions
│       └── config.py       # Configuration management
└── README.md
```

## Development

### Adding New Features

The application is designed with a modular architecture:

- **File Manager**: Extend `file_pane.py` or `dual_pane.py` for new file operations
- **Editors**: Add new syntax highlighters in `syntax_highlighter.py`
- **Tools**: Create new tool integrations in the `tools/` directory
- **UI**: Add new dialogs or themes in the `ui/` directory

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Troubleshooting

### Common Issues

**PyQt5 import errors:**
```bash
pip install PyQt5
```

**APKTool not found:**
- Install apktool: `sudo apt install apktool`
- Or set custom path in Preferences

**Permission denied errors:**
- Ensure you have read/write permissions for the directories
- Run with appropriate user permissions

**Archive extraction fails:**
- Check if the archive file is corrupted
- Ensure sufficient disk space for extraction

### Debug Mode

Run with debug output:
```bash
python main.py --debug
```

## License

This project is open source. See LICENSE file for details.

## Acknowledgments

- Inspired by MT Manager for Android
- Built with PyQt5
- Uses APKTool for APK operations
- Syntax highlighting powered by Pygments concepts
