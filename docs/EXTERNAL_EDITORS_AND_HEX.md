# GP Manager - External Editors & Hex Editor

## Overview

GP Manager now features comprehensive external editor integration and a powerful built-in hex editor, providing professional-grade file editing capabilities for developers and power users.

## 🚀 External Editor Integration

### **Supported External Editors**

#### **Text Editors & IDEs**
| Editor | Command | Auto-Detected | File Types |
|--------|---------|---------------|------------|
| **Visual Studio Code** | `code` | ✓ | All text files, code files |
| **VSCode Insiders** | `code-insiders` | ✓ | All text files, code files |
| **Vim** | `vim` | ✓ | All files |
| **Neovim** | `nvim` | ✓ | All files |
| **Emacs** | `emacs` | ✓ | All files |
| **Nano** | `nano` | ✓ | All files |
| **Gedit** | `gedit` | ✓ | Text files |
| **Kate** | `kate` | ✓ | All files |
| **Sublime Text** | `subl` | ✓ | All files |
| **Atom** | `atom` | ✓ | All files |

#### **Specialized IDEs**
| Editor | Command | File Types | Description |
|--------|---------|------------|-------------|
| **IntelliJ IDEA** | `idea` | `.java`, `.kt`, `.scala` | JetBrains IDE |
| **PyCharm** | `pycharm` | `.py`, `.pyw` | Python IDE |
| **Android Studio** | `studio` | `.java`, `.kt`, `.xml` | Android development |

#### **Hex Editors**
| Editor | Command | Description |
|--------|---------|-------------|
| **GHex** | `ghex` | GNOME Hex Editor |
| **Bless** | `bless` | Advanced hex editor |

#### **Specialized Applications**
| Application | Command | File Types | Description |
|-------------|---------|------------|-------------|
| **GIMP** | `gimp` | Images | GNU Image Manipulation Program |
| **Blender** | `blender` | 3D files | 3D Creation Suite |

### **Right-Click Context Menu**

#### **"Open with" Submenu**
- **🔧 Built-in Hex Editor** - Always available for all files
- **📝 External Editors** - Suitable editors for the file type
- **📋 Choose application...** - Full list of available editors
- **⚙️ Configure editors...** - Editor management dialog

#### **Smart File Type Detection**
```python
# Example: Python file (.py)
Right-click → Open with →
├── 🔧 Built-in Hex Editor
├── 📝 Visual Studio Code
├── 📝 PyCharm
├── 📝 Vim
├── 📝 Gedit
└── ⚙️ Configure editors...
```

### **External Editor Configuration**

#### **Adding Custom Editors**
1. **Tools** → **Configure External Editors**
2. Click **"Add Editor"**
3. Configure editor settings:
   - **Name**: Display name
   - **Command**: Executable command
   - **Arguments**: Command arguments (use `{file}` for file path)
   - **Extensions**: Supported file extensions
   - **Description**: Editor description

#### **Example Custom Editor Configuration**
```json
{
  "name": "Custom Editor",
  "command": "myeditor",
  "args": ["{file}", "--new-window"],
  "extensions": [".txt", ".md"],
  "description": "My custom text editor"
}
```

#### **Built-in Editor Detection**
- Automatically detects installed editors on system startup
- Only shows available editors in context menus
- Supports multiple installation paths and variants

### **Usage Examples**

#### **Opening Files**
1. **Right-click** on any file in file manager
2. Select **"Open with"** → Choose editor
3. File opens in selected external editor

#### **Quick Access**
- **Double-click** opens with default application
- **Right-click** provides editor options
- **Drag & drop** to external applications (future feature)

## 🔧 Built-in Hex Editor

### **Core Features**

#### **Hex/ASCII View**
- **Dual-pane display**: Hex values and ASCII representation
- **Configurable bytes per line**: 8, 16, or 32 bytes
- **Address display**: 8-digit hexadecimal addresses
- **Color-coded highlighting**: Selection, cursor, bookmarks

#### **Navigation & Selection**
- **Keyboard navigation**: Arrow keys, Home, End, Page Up/Down
- **Mouse selection**: Click and drag to select bytes
- **Go to address**: Jump to specific memory location
- **Search functionality**: Find hex patterns or text

#### **Data Editing**
- **Hex editing**: Direct hex value modification
- **ASCII editing**: Text-based editing
- **Insert/Delete**: Add or remove bytes
- **Undo/Redo**: Full edit history (future feature)

### **Advanced Features**

#### **Data Inspector**
Real-time interpretation of selected bytes:

| Data Type | Description | Example |
|-----------|-------------|---------|
| **Byte (unsigned)** | 0-255 | `72` |
| **Byte (signed)** | -128 to 127 | `72` |
| **Hex** | Hexadecimal | `0x48` |
| **Binary** | Binary representation | `0b01001000` |
| **ASCII** | Character | `H` |
| **UInt16 (LE/BE)** | 16-bit unsigned | `18504` / `29256` |
| **UInt32 (LE/BE)** | 32-bit unsigned | `1819043144` |
| **UInt64 (LE)** | 64-bit unsigned | `8031924123371070792` |
| **Float (LE)** | 32-bit float | `1.234567` |
| **Double (LE)** | 64-bit double | `1.234567890123` |

#### **Bookmarks System**
- **Add bookmarks**: Mark important locations
- **Named bookmarks**: Custom bookmark names
- **Visual indicators**: Highlighted bookmark positions
- **Bookmark navigation**: Quick jump to bookmarks

#### **Search & Replace**
- **Text search**: Find ASCII strings
- **Hex search**: Find hex patterns
- **Case sensitivity**: Optional case-sensitive search
- **Replace functionality**: Replace found patterns
- **Replace all**: Batch replacement operations

#### **File Operations**
- **Open files**: Load any file type
- **Save changes**: Write modifications to disk
- **Save as**: Export to new file
- **Large file support**: Efficient handling of large files

### **User Interface**

#### **Toolbar Actions**
| Action | Shortcut | Description |
|--------|----------|-------------|
| **Open** | `Ctrl+O` | Open file |
| **Save** | `Ctrl+S` | Save current file |
| **Save As** | `Ctrl+Shift+S` | Save as new file |
| **Copy** | `Ctrl+C` | Copy selection |
| **Paste** | `Ctrl+V` | Paste data |

#### **View Options**
- **Bytes per line**: 8, 16, 32 bytes
- **Address format**: Hexadecimal addresses
- **Font settings**: Monospace font for alignment
- **Color scheme**: Consistent with application theme

#### **Status Bar Information**
- **Current position**: Hex address and decimal offset
- **Selection info**: Number of selected bytes
- **File size**: Total file size and modification status
- **Encoding info**: Character encoding detection

### **Right Panel Tabs**

#### **1. Data Inspector**
- Real-time data interpretation
- Multiple data type views
- Endianness support
- Automatic updates on cursor movement

#### **2. Bookmarks**
- Bookmark list and management
- Named bookmark creation
- Quick navigation to bookmarks
- Bookmark import/export (future feature)

#### **3. Search**
- Text and hex search
- Case sensitivity options
- Replace functionality
- Search history (future feature)

### **Performance Features**

#### **Optimizations**
- **Lazy loading**: Only load visible data
- **Efficient rendering**: Optimized paint operations
- **Memory management**: Minimal memory footprint
- **Large file support**: Handle files up to several GB

#### **Responsive UI**
- **Smooth scrolling**: Fluid navigation experience
- **Real-time updates**: Instant visual feedback
- **Background operations**: Non-blocking file operations
- **Progress indicators**: Loading progress for large files

## 🎯 Integration Features

### **File Manager Integration**
- **Context menu integration**: Right-click to open with editors
- **File type detection**: Smart editor suggestions
- **Recent files**: Track recently opened files
- **File associations**: Remember preferred editors

### **Application Integration**
- **Tab system**: Hex editor as dedicated tab
- **Toolbar access**: Quick access button
- **Menu integration**: Tools menu configuration
- **Status updates**: File operation status in main status bar

### **Configuration Management**
- **Persistent settings**: Editor preferences saved
- **Custom editor support**: Add unlimited custom editors
- **File associations**: Remember file type preferences
- **Theme integration**: Consistent with application theme

## 🔧 Technical Implementation

### **External Editor System**
```python
# Editor detection and management
external_editor_manager.get_available_editors()
external_editor_manager.get_editors_for_file(file_path)
external_editor_manager.open_file(file_path, editor_name)
```

### **Hex Editor Architecture**
```python
# Core components
HexData          # Data management and operations
HexView          # Visual hex/ASCII display
DataInspector    # Multi-format data interpretation
HexEditor        # Main editor widget with toolbar
```

### **File Format Support**
- **Binary files**: Complete binary file support
- **Text files**: ASCII and UTF-8 text files
- **Executable files**: PE, ELF, Mach-O executables
- **Archive files**: ZIP, RAR, 7Z archives
- **Image files**: PNG, JPEG, GIF images
- **Any file type**: Universal file support

## 🚀 Usage Scenarios

### **Development Workflows**
1. **Code editing**: Open source files in preferred IDE
2. **Binary analysis**: Examine executable files in hex editor
3. **Data inspection**: Analyze file formats and structures
4. **Debugging**: Inspect memory dumps and core files

### **Reverse Engineering**
1. **APK analysis**: Examine Android application files
2. **Binary patching**: Modify executable files
3. **Protocol analysis**: Inspect network packet captures
4. **File format research**: Understand proprietary formats

### **System Administration**
1. **Configuration editing**: Modify system configuration files
2. **Log analysis**: Examine system and application logs
3. **Disk forensics**: Analyze disk images and file systems
4. **Security analysis**: Inspect suspicious files

## 🎉 Benefits

### **Productivity**
- **Seamless workflow**: Switch between editors without leaving GP Manager
- **Context awareness**: Smart editor suggestions based on file type
- **Quick access**: Right-click context menu for instant access
- **Professional tools**: Access to industry-standard editors

### **Flexibility**
- **Multiple editors**: Support for dozens of external editors
- **Custom configuration**: Add any editor with custom settings
- **File type associations**: Remember preferred editors per file type
- **Cross-platform**: Works with editors available on Linux

### **Power User Features**
- **Advanced hex editing**: Professional-grade binary file editing
- **Data analysis**: Multi-format data interpretation
- **Search capabilities**: Powerful search and replace functionality
- **Bookmark system**: Organize and navigate large files efficiently

The external editor and hex editor integration transforms GP Manager into a comprehensive development and analysis platform, providing the tools needed for professional software development, reverse engineering, and system administration tasks! 🎯
