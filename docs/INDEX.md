# GP Manager - Project Index

## 📋 **Project Overview**

GP Manager is a dual-pane file manager with APK tools integration, inspired by MT Manager for Android. This index provides a comprehensive overview of the project structure, features, and components.

## 🗂️ **Directory Structure**

### **Root Directory**
```
gpmanager/
├── 📄 main.py                    # Application entry point
├── 📄 README.md                  # Main documentation
├── 📄 requirements.txt           # Python dependencies
├── 📄 setup.py                   # Installation script
├── 📄 run.sh                     # Launch script
├── 📄 gpmanager.desktop          # Desktop entry
├── 📁 mt_env/                    # Virtual environment
├── 📁 src/                       # Source code
├── 📁 test/                      # Test scripts
└── 📁 docs/                      # Documentation
```

### **Source Code Structure (`src/`)**
```
src/
├── 📄 __init__.py
├── 📄 main_window.py             # Main application window
├── 📁 file_manager/              # File management components
├── 📁 editors/                   # Text editing components
├── 📁 tools/                     # Tool integrations
├── 📁 ui/                        # User interface components
└── 📁 utils/                     # Utility modules
```

### **Test Structure (`test/`)**
```
test/
├── 📄 __init__.py
├── 📄 test_apktool_fixes.py      # APKTool functionality tests
├── 📄 test_app.py                # General application tests
├── 📄 test_highlight.py          # Syntax highlighting tests
├── 📄 test_external_editors.py   # External editor tests
├── 📄 test_color_contrast.py     # Theme color tests
└── 📄 debug_highlight.py         # Syntax highlighting debug tool
```

### **Documentation Structure (`docs/`)**
```
docs/
├── 📄 INDEX.md                   # This comprehensive index
├── 📄 README.md                  # Copy of main documentation
├── 📄 NAVIGATION.md              # Quick navigation hub
├── 📄 INSTALLATION_GUIDE.md      # Detailed installation guide
├── 📄 SYNTAX_HIGHLIGHTING.md     # Syntax highlighting system
├── 📄 EXTERNAL_EDITORS_AND_HEX.md # External editor integration
├── 📄 FLEXIBLE_TOOLS_SYSTEM.md   # Modular tool architecture
└── 📄 WINDOW_CONTROLS.md         # Window management features
```

## 🧩 **Core Components**

### **1. File Manager (`src/file_manager/`)**
- **`dual_pane.py`** - Dual-pane file browser manager
- **`single_pane.py`** - Single-pane file browser (alternative layout)
- **`file_pane.py`** - Individual file browser pane
- **`file_operations.py`** - File operations (copy, move, delete, etc.)

### **2. Editors (`src/editors/`)**
- **`text_editor.py`** - Main text editor widget
- **`syntax_highlighter.py`** - Syntax highlighting engine
- **`json_highlighter.py`** - JSON-based syntax highlighter
- **`external_editor.py`** - External editor integration
- **`hex_editor.py`** - Hex editor component
- **`highlight/`** - Syntax highlighting definitions

### **3. Tools (`src/tools/`)**
- **`apktool.py`** - APKTool integration (decompile/recompile APKs)
- **`archive_manager.py`** - Archive handling (ZIP, APK viewing)

### **4. UI Components (`src/ui/`)**
- **`themes.py`** - Theme management (dark/light themes)
- **`dialogs.py`** - Custom dialog boxes
- **`detachable_window.py`** - Detachable tool windows
- **`title_bar.py`** - Custom title bar
- **`tool_dock.py`** - Tool docking system
- **`install_wizard.py`** - Installation wizard
- **`language_selector.py`** - Language selection

### **5. Utilities (`src/utils/`)**
- **`config.py`** - Configuration management
- **`file_utils.py`** - File utility functions
- **`system_installer.py`** - System dependency installer

## 🎯 **Key Features**

### **File Management**
- ✅ Dual-pane file browser
- ✅ File operations (copy, move, delete, rename)
- ✅ Progress dialogs for long operations
- ✅ Hidden file toggle
- ✅ Keyboard shortcuts
- ✅ Context menus

### **APK Tools Integration**
- ✅ APK decompilation with APKTool
- ✅ APK recompilation
- ✅ APK signing with debug keys
- ✅ Progress tracking and logging
- ✅ Dependency checking and installation
- ✅ ZIP-style APK editing

### **Text Editing**
- ✅ Syntax highlighting for multiple languages
- ✅ External editor integration (VSCode, vim)
- ✅ Find/Replace functionality
- ✅ Multiple tabs
- ✅ Line numbers and folding

### **Archive Support**
- ✅ ZIP/APK archive browsing
- ✅ File extraction
- ✅ Archive content preview

### **UI/UX**
- ✅ Dark theme support
- ✅ Modular tool architecture
- ✅ Detachable windows
- ✅ Custom title bar option
- ✅ Responsive layout

## 📚 **Documentation Files**

### **Main Documentation**
- **`README.md`** - Main project documentation
- **`INSTALLATION_GUIDE.md`** - Detailed installation instructions
- **`INDEX.md`** - This comprehensive index

### **Feature Documentation**
- **`SYNTAX_HIGHLIGHTING.md`** - Syntax highlighting system
- **`EXTERNAL_EDITORS_AND_HEX.md`** - External editor integration
- **`FLEXIBLE_TOOLS_SYSTEM.md`** - Tool architecture
- **`WINDOW_CONTROLS.md`** - Window management features

## 🔧 **Syntax Highlighting Support**

### **Supported Languages (`src/editors/highlight/`)**
- **`py.json`** - Python
- **`java.json`** - Java
- **`cpp.json`** - C/C++
- **`cs.json`** - C#
- **`html.json`** - HTML
- **`xml.json`** - XML
- **`js.json`** - JavaScript
- **`css.json`** - CSS
- **`json.json`** - JSON
- **`smali.json`** - Smali (Android bytecode)
- **`bash.json`** - Bash/Shell
- **`sql.json`** - SQL
- **`php.json`** - PHP
- **`markdown.json`** - Markdown
- **`yaml.json`** - YAML

## 🧪 **Test Files (`test/`)**

- **`test_apktool_fixes.py`** - APKTool functionality tests
- **`test_app.py`** - General application tests
- **`test_highlight.py`** - Syntax highlighting tests
- **`test_external_editors.py`** - External editor tests
- **`test_color_contrast.py`** - Theme color tests
- **`debug_highlight.py`** - Syntax highlighting debug tool

## ⚙️ **Configuration**

### **Config Location**
- **User config**: `~/.gpmanager/config.json`
- **Default settings**: `src/utils/config.py`

### **Configurable Options**
- Theme (dark/light)
- Font family and size
- Show hidden files
- APKTool and Java paths
- Window geometry
- Recent paths
- Pane splitter ratio

## 🚀 **Getting Started**

### **Quick Start**
1. **Clone**: `git clone <repo-url> && cd gpmanager`
2. **Setup**: `python3 setup.py --gui`
3. **Run**: `./run.sh` or `python main.py`

### **Development Setup**
1. **Virtual Environment**: `python3 -m venv mt_env`
2. **Activate**: `source mt_env/bin/activate`
3. **Install**: `pip install -r requirements.txt`
4. **Run**: `python main.py`

## 🔍 **Recent Fixes & Improvements**

### **APKTool Integration (Latest)**
- ✅ **Fixed decompile process issues**
  - Improved subprocess output handling
  - Better process termination and cleanup
  - Enhanced error capture and reporting
- ✅ **Improved progress bar functionality**
  - Fixed premature hiding issues
  - Added proper 100% completion signaling
  - Better progress pattern matching
- ✅ **Enhanced log window connection**
  - Real-time log updates to detailed window
  - Improved log storage and retrieval
  - Better fallback handling for empty logs
- ✅ **Better error handling and reporting**
  - Detailed error messages with context
  - Last 10 lines of output for debugging
  - Clear guidance for missing dependencies
- ✅ **Dependency validation before operations**
  - Pre-operation dependency checking
  - Clear warning messages
  - Automatic installation options

### **Architecture Improvements**
- ✅ **Modular tool system**
  - Detachable tool windows
  - Independent tool scaling
  - Flexible tool arrangement
- ✅ **External editor integration**
  - VSCode integration
  - Vim support
  - Right-click context menu
- ✅ **Enhanced syntax highlighting**
  - 15+ language support
  - JSON-based configuration
  - Extensible highlighting system
- ✅ **Hex editor integration**
  - On-demand loading
  - External hex editor support
  - Built-in hex viewing

## 🏗️ **Technical Architecture**

### **Design Patterns**
- **MVC Architecture** - Model-View-Controller separation
- **Observer Pattern** - Signal/slot communication (PyQt5)
- **Factory Pattern** - Dynamic tool and editor creation
- **Strategy Pattern** - Pluggable syntax highlighters
- **Command Pattern** - File operations and undo/redo

### **Key Interfaces**
- **`QWidget`** - Base for all UI components
- **`QThread`** - Background operations (APKTool, file ops)
- **`pyqtSignal`** - Inter-component communication
- **`QAbstractItemModel`** - File system models

### **Threading Model**
- **Main Thread** - UI operations and event handling
- **Worker Threads** - File operations, APK processing
- **Background Tasks** - Dependency installation, system checks

## 🔌 **API & Extension Points**

### **Adding New Tools**
```python
# Create new tool in src/tools/
class MyTool(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Tool implementation

# Register in main_window.py
self.my_tool = MyTool()
self.add_tool("My Tool", self.my_tool)
```

### **Adding Syntax Highlighting**
```json
// Create new language file in src/editors/highlight/
{
    "name": "MyLanguage",
    "extensions": [".mylang"],
    "keywords": ["keyword1", "keyword2"],
    "operators": ["+", "-", "*"],
    "strings": ["\"", "'"],
    "comments": ["//", "/*", "*/"]
}
```

### **Adding Themes**
```python
# Extend ThemeManager in src/ui/themes.py
def apply_custom_theme(app):
    # Custom theme implementation
    pass
```

## 📞 **Support & Development**

### **Key Classes & Entry Points**
- **`MainWindow`** (`src/main_window.py`) - Main application window
- **`ApkToolWidget`** (`src/tools/apktool.py`) - APK operations
- **`DualPaneManager`** (`src/file_manager/dual_pane.py`) - File management
- **`TextEditor`** (`src/editors/text_editor.py`) - Text editing
- **`ThemeManager`** (`src/ui/themes.py`) - Theme system
- **`Config`** (`src/utils/config.py`) - Configuration management

### **Development Workflow**
1. **Fork** the repository
2. **Create** feature branch
3. **Implement** changes following existing patterns
4. **Test** thoroughly with test scripts
5. **Document** new features
6. **Submit** pull request

### **Testing**
- **Unit Tests** - Individual component testing
- **Integration Tests** - Cross-component functionality
- **UI Tests** - User interface validation
- **Performance Tests** - Large file handling

### **Debugging**
- **Debug Mode** - `python main.py --debug`
- **Test Scripts** - Use `test_*.py` files
- **Log Files** - Check `~/.gpmanager/logs/`
- **Verbose Output** - Enable in preferences

This index serves as a comprehensive roadmap for understanding, using, and contributing to GP Manager.
