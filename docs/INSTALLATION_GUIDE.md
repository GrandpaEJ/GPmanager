# GP Manager - Complete Installation Guide

## Overview

GP Manager is a dual-pane file manager with APK tools integration. This guide provides comprehensive installation instructions with automatic dependency management.

## System Requirements

- **Operating System**: Linux (Ubuntu, Debian, Fedora, Arch, etc.)
- **Python**: 3.6 or higher
- **Memory**: 512 MB RAM minimum, 1 GB recommended
- **Storage**: 100 MB for application, additional space for APK operations

## Quick Start (Recommended)

### 1. Download and Setup
```bash
# Clone the repository
git clone <repository-url>
cd gpmanager

# Make scripts executable
chmod +x run.sh setup.py
```

### 2. Automatic Installation
```bash
# Option A: GUI Setup Wizard (Recommended)
python3 setup.py --gui

# Option B: Command Line Installation
python3 setup.py --install

# Option C: Smart Launcher (auto-detects and installs)
./run.sh
```

### 3. Run the Application
```bash
./run.sh
```

## Installation Methods

### Method 1: GUI Setup Wizard

The GUI setup wizard provides an interactive installation experience:

```bash
python3 setup.py --gui
```

Features:
- ✅ Visual dependency checking
- ✅ One-click installation
- ✅ Progress monitoring
- ✅ Installation logs
- ✅ Manual script generation

### Method 2: Command Line Setup

For automated or headless installations:

```bash
# Check what's missing
python3 setup.py --check

# Install everything
python3 setup.py --install

# Install only required dependencies
python3 setup.py --install --skip-optional

# Generate installation script
python3 setup.py --script -o install.sh
```

### Method 3: Smart Launcher

The enhanced run script automatically detects and offers to install missing dependencies:

```bash
./run.sh
```

If dependencies are missing, it will:
1. Show what's missing
2. Offer automatic installation
3. Provide manual installation commands
4. Start the application when ready

### Method 4: Manual Installation

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3-pyqt5 python3-pyqt5.qsci python3-pygments python3-magic
sudo apt install apktool default-jdk git  # Optional
```

#### Fedora/RHEL/CentOS
```bash
sudo dnf install python3-qt5 qscintilla-python3 python3-pygments python3-magic
sudo dnf install apktool java-11-openjdk-devel git  # Optional
```

#### Arch Linux/Manjaro
```bash
sudo pacman -S python-pyqt5 qscintilla-python python-pygments python-magic
sudo pacman -S apktool jdk-openjdk git  # Optional
```

#### openSUSE
```bash
sudo zypper install python3-qt5 python3-QScintilla python3-Pygments python3-python-magic
sudo zypper install apktool java-11-openjdk-devel git  # Optional
```

## Dependency Details

### Required Dependencies
| Package | Purpose | Check Command |
|---------|---------|---------------|
| python3-pyqt5 | GUI framework | `python3 -c "import PyQt5"` |
| python3-pyqt5.qsci | Text editor component | `python3 -c "import PyQt5.Qsci"` |
| python3-pygments | Syntax highlighting | `python3 -c "import pygments"` |
| python3-magic | File type detection | `python3 -c "import magic"` |

### Optional Dependencies
| Package | Purpose | Check Command |
|---------|---------|---------------|
| apktool | APK decompilation/recompilation | `apktool --version` |
| java | APK signing | `java -version` |
| git | Version control | `git --version` |

## Installation Verification

### Check Installation Status
```bash
python3 setup.py --check
```

### Test Application Launch
```bash
python3 main.py
```

### Verify Features
1. **File Manager**: Navigate directories in dual panes
2. **Text Editor**: Open .txt, .java, .smali files
3. **APK Tools**: Try decompiling an APK (requires apktool)
4. **Archive Viewer**: Open .zip files

## Troubleshooting

### Common Issues

#### 1. "PyQt5 not found"
```bash
# Ubuntu/Debian
sudo apt install python3-pyqt5 python3-pyqt5.qsci

# Or use setup script
python3 setup.py --install
```

#### 2. "Permission denied" during installation
```bash
# Ensure you have sudo privileges
sudo -v

# Or install to user directory
python3 setup.py --install --user
```

#### 3. "APKTool not found"
```bash
# Install via package manager
sudo apt install apktool

# Or manual installation
python3 setup.py --install
```

#### 4. Application won't start
```bash
# Check dependencies
python3 setup.py --check

# Run with debug output
python3 main.py --debug

# Check launcher output
./run.sh
```

#### 5. "externally-managed-environment" pip error
This is normal on newer systems. Use system packages instead:
```bash
# Use system package manager (recommended)
sudo apt install python3-pyqt5

# Or use setup script which handles this
python3 setup.py --install
```

### Debug Mode

Run with verbose output:
```bash
# Enable debug logging
export GPMANAGER_DEBUG=1
python3 main.py

# Or check system info
python3 setup.py --check --verbose
```

### Log Files

Application logs are stored in:
- `~/.gpmanager/logs/` - Application logs
- `~/.gpmanager/config.json` - Configuration file

## Advanced Installation

### Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv gpmanager-env
source gpmanager-env/bin/activate

# Install dependencies
pip install PyQt5 QScintilla Pygments python-magic

# Run application
python3 main.py
```

### System-wide Installation
```bash
# Install to /opt
sudo mkdir -p /opt/gpmanager
sudo cp -r . /opt/gpmanager/
sudo chown -R root:root /opt/gpmanager

# Create system launcher
sudo ln -s /opt/gpmanager/run.sh /usr/local/bin/gpmanager

# Create desktop entry
python3 setup.py --desktop
```

### Docker Installation
```bash
# Build Docker image
docker build -t gpmanager .

# Run with X11 forwarding
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $HOME:/host-home \
  gpmanager
```

## Post-Installation

### Create Desktop Entry
```bash
python3 setup.py --desktop
```

### Add to PATH
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Configure APKTool Path
If APKTool is installed in a custom location:
1. Open GP Manager
2. Go to File → Preferences
3. Set APKTool path in Tools tab

## Getting Help

### Documentation
- `README.md` - General usage guide
- `INSTALLATION_GUIDE.md` - This file
- In-app help: Help → About

### Support Commands
```bash
# Check system info
python3 setup.py --check

# Generate installation script
python3 setup.py --script

# Test basic functionality
python3 -c "import sys; sys.path.insert(0, 'src'); from src.main_window import MainWindow; print('Import successful')"
```

### Community Support
- Report issues with installation logs
- Include output of `python3 setup.py --check`
- Specify your Linux distribution and version

## Success Indicators

You'll know the installation is successful when:
- ✅ `./run.sh` starts without errors
- ✅ Dual-pane file manager appears
- ✅ You can navigate directories
- ✅ Text files open in the editor
- ✅ No dependency warnings in the launcher

Enjoy using GP Manager!
