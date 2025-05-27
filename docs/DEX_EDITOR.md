# DEX Editor Documentation

## Overview

The DEX Editor is a powerful tool for viewing, analyzing, and editing Android DEX (Dalvik Executable) files. It provides comprehensive functionality similar to MT Manager's DEX editing capabilities.

## Features

### 🔍 **DEX File Analysis**
- **File Structure Viewer**: Browse DEX headers, string pools, type definitions, method signatures, and class hierarchies
- **Header Information**: Display detailed DEX file metadata including version, checksums, and section sizes
- **Validation**: Verify DEX file integrity and format compliance
- **Cross-references**: Navigate between related elements in the DEX structure

### ⚙️ **Bytecode Operations**
- **Disassembly**: View Dalvik bytecode instructions in human-readable format
- **Assembly**: Edit and reassemble bytecode back to DEX format
- **Instruction Analysis**: Detailed breakdown of Dalvik opcodes and operands
- **Method Navigation**: Browse and edit individual method implementations

### 📝 **Smali Integration**
- **DEX ↔ Smali Conversion**: Convert between DEX and Smali formats using baksmali/smali tools
- **Smali Editor**: Edit Smali code with syntax highlighting and validation
- **File Browser**: Navigate Smali directory structures
- **Compilation**: Compile modified Smali back to DEX format

### 🎨 **Syntax Highlighting**
- **DEX Bytecode**: Comprehensive highlighting for Dalvik opcodes, registers, and types
- **Smali Code**: Enhanced syntax highlighting for Smali assembly language
- **Error Detection**: Visual indicators for syntax errors and invalid constructs

## Getting Started

### Prerequisites

1. **Python Dependencies**: Ensure PyQt5 is installed
2. **Smali Tools** (optional but recommended):
   - `baksmali` - For DEX to Smali conversion
   - `smali` - For Smali to DEX compilation

### Installation

The DEX editor is automatically available when you install GP Manager. To enable it:

1. Open GP Manager
2. Navigate to a `.dex` file
3. Double-click the file or right-click and select "DEX Editor"
4. The DEX editor will be automatically enabled and loaded

### Manual Installation of Smali Tools

```bash
# Ubuntu/Debian
sudo apt install smali

# Arch Linux
sudo pacman -S smali

# Manual installation
wget https://github.com/JesusFreke/smali/releases/download/v2.5.2/smali-2.5.2.jar
wget https://github.com/JesusFreke/smali/releases/download/v2.5.2/baksmali-2.5.2.jar
```

## Usage Guide

### Opening DEX Files

1. **File Manager**: Double-click any `.dex` file
2. **Context Menu**: Right-click → "Open with" → "DEX Editor"
3. **Drag & Drop**: Drag DEX files onto the application window
4. **Menu**: File → Open → Select DEX file

### Structure Viewer

The Structure Viewer displays the internal organization of the DEX file:

- **String Pool**: All string constants used in the DEX file
- **Type Definitions**: Class and primitive type references
- **Method Definitions**: Method signatures and prototypes
- **Class Definitions**: Class hierarchy and metadata

Click on any item to view detailed information and navigate to related elements.

### Bytecode Viewer

View and edit Dalvik bytecode instructions:

1. Select a method from the Structure Viewer
2. Switch to the "Bytecode" tab
3. View disassembled instructions
4. Edit bytecode (advanced users)
5. Reassemble to update the DEX file

### Smali Operations

#### DEX to Smali Conversion

1. Load a DEX file in the editor
2. Switch to the "Smali" tab
3. Click "DEX → Smali"
4. Choose output directory
5. Wait for conversion to complete

#### Smali to DEX Compilation

1. Click "Open Smali Dir" to load a Smali project
2. Browse and edit Smali files
3. Click "Smali → DEX"
4. Choose output DEX file location
5. Wait for compilation to complete

### File Validation

Validate DEX file integrity:

1. Load a DEX file
2. Click "Validate" in the toolbar
3. Review validation results
4. Fix any reported issues

## Advanced Features

### External Tool Integration

The DEX editor integrates with external tools:

- **Android Studio**: Open DEX/Smali files in Android Studio
- **Jadx GUI**: Decompile DEX files to Java source
- **Baksmali CLI**: Command-line DEX disassembly
- **Custom Editors**: Configure additional external tools

### Keyboard Shortcuts

- `Ctrl+O`: Open DEX file
- `Ctrl+S`: Save current file
- `Ctrl+F`: Search in current view
- `F5`: Refresh/Reload file
- `Ctrl+G`: Go to line/address

### Search and Navigation

- **String Search**: Find strings in the string pool
- **Class Search**: Locate specific classes
- **Method Search**: Find methods by name or signature
- **Cross-references**: Jump to method/field definitions

## File Format Support

### Supported DEX Versions
- DEX version 035 (Android 7.0+)
- DEX version 037 (Android 8.0+)
- DEX version 038 (Android 9.0+)
- DEX version 039 (Android 10.0+)

### Related Formats
- **APK files**: Extract and edit DEX files from APK packages
- **JAR files**: Handle Java archives containing DEX files
- **Smali files**: Full support for Smali assembly language

## Troubleshooting

### Common Issues

**DEX file won't open**
- Verify file is a valid DEX file
- Check file permissions
- Ensure file is not corrupted

**Smali conversion fails**
- Install baksmali/smali tools
- Check tool versions compatibility
- Verify DEX file integrity

**Syntax highlighting not working**
- Check highlight configuration files
- Restart the application
- Verify file extension associations

### Error Messages

- **"Invalid DEX magic number"**: File is not a valid DEX file
- **"Unsupported DEX version"**: DEX version not supported
- **"baksmali not found"**: Install Smali tools
- **"Failed to parse DEX file"**: File may be corrupted

## Configuration

### Settings

Access DEX editor settings through:
- File → Preferences → DEX Editor
- Right-click in editor → Settings

### Customization Options

- **Font size**: Adjust editor font size
- **Color scheme**: Choose syntax highlighting colors
- **Tool paths**: Configure external tool locations
- **Auto-save**: Enable automatic file saving

## API Reference

### DexParser Class

```python
from src.parsers.dex_parser import DexParser

parser = DexParser('classes.dex')
if parser.parse():
    summary = parser.get_summary()
    classes = parser.get_class_names()
    methods = parser.get_method_names()
```

### DexTools Class

```python
from src.tools.dex_tools import DexTools

# Validate DEX file
is_valid, message = DexTools.validate_dex_file('classes.dex')

# Convert DEX to Smali
success, message = DexTools.dex_to_smali('classes.dex', 'output_dir')

# Convert Smali to DEX
success, message = DexTools.smali_to_dex('smali_dir', 'output.dex')
```

## Contributing

To contribute to the DEX editor:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-repo/gp-manager.git
cd gp-manager

# Install dependencies
pip install -r requirements.txt

# Run tests
python test/test_dex_editor.py

# Start development server
python main.py
```

## License

The DEX editor is part of GP Manager and is licensed under the same terms as the main project.

## Support

For support and bug reports:
- GitHub Issues: [Project Issues](https://github.com/your-repo/gp-manager/issues)
- Documentation: [Project Wiki](https://github.com/your-repo/gp-manager/wiki)
- Community: [Discussions](https://github.com/your-repo/gp-manager/discussions)
