# GP Manager - Quick Navigation

## 📚 **Documentation Hub**

### **📋 Main Documentation**
- **[INDEX.md](INDEX.md)** - 🗂️ Complete project index and overview
- **[README.md](../README.md)** - 📖 Main project documentation and getting started
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - 🔧 Detailed installation instructions

### **🎯 Feature Documentation**
- **[SYNTAX_HIGHLIGHTING.md](SYNTAX_HIGHLIGHTING.md)** - 🎨 Syntax highlighting system
- **[EXTERNAL_EDITORS_AND_HEX.md](EXTERNAL_EDITORS_AND_HEX.md)** - 🔗 External editor integration
- **[FLEXIBLE_TOOLS_SYSTEM.md](FLEXIBLE_TOOLS_SYSTEM.md)** - 🧩 Modular tool architecture
- **[WINDOW_CONTROLS.md](WINDOW_CONTROLS.md)** - 🪟 Window management features

## 🚀 **Quick Start**

### **For Users**
1. **[Installation](INSTALLATION_GUIDE.md)** - Get GP Manager running
2. **[Basic Usage](../README.md#usage)** - Learn the fundamentals
3. **[Keyboard Shortcuts](../README.md#keyboard-shortcuts)** - Speed up your workflow
4. **[Configuration](../README.md#configuration)** - Customize your experience

### **For Developers**
1. **[Project Structure](INDEX.md#directory-structure)** - Understand the codebase
2. **[Technical Architecture](INDEX.md#technical-architecture)** - Learn the design patterns
3. **[API & Extensions](INDEX.md#api--extension-points)** - Add new features
4. **[Development Workflow](INDEX.md#development-workflow)** - Contribute to the project

## 🧩 **Core Components**

### **File Management**
- **[Dual Pane System](../src/file_manager/dual_pane.py)** - Main file browser
- **[File Operations](../src/file_manager/file_operations.py)** - Copy, move, delete
- **[File Utilities](../src/utils/file_utils.py)** - Helper functions

### **APK Tools**
- **[APKTool Integration](../src/tools/apktool.py)** - Decompile/recompile APKs
- **[Archive Manager](../src/tools/archive_manager.py)** - ZIP/APK viewing

### **Text Editing**
- **[Text Editor](../src/editors/text_editor.py)** - Main editor component
- **[Syntax Highlighting](../src/editors/syntax_highlighter.py)** - Language support
- **[External Editors](../src/editors/external_editor.py)** - VSCode/vim integration

### **User Interface**
- **[Main Window](../src/main_window.py)** - Application entry point
- **[Themes](../src/ui/themes.py)** - Dark/light theme system
- **[Dialogs](../src/ui/dialogs.py)** - Custom dialog boxes

## 🔧 **Configuration & Setup**

### **System Requirements**
- **Python 3.6+** - Core runtime
- **PyQt5** - GUI framework
- **APKTool** - APK operations (optional)
- **Java** - APK signing (optional)

### **Installation Methods**
- **[GUI Installer](../setup.py)** - `python3 setup.py --gui`
- **[Command Line](../setup.py)** - `python3 setup.py --install`
- **[Manual Setup](../README.md#manual-installation)** - Step-by-step instructions

### **Configuration Files**
- **[User Config](~/.gpmanager/config.json)** - Personal settings
- **[Default Config](../src/utils/config.py)** - System defaults

## 🧪 **Testing & Debugging**

### **Test Scripts**
- **[APKTool Tests](../test/test_apktool_fixes.py)** - APK functionality
- **[Syntax Tests](../test/test_highlight.py)** - Highlighting system
- **[Editor Tests](../test/test_external_editors.py)** - External editor integration
- **[Theme Tests](../test/test_color_contrast.py)** - Color and contrast

### **Debug Tools**
- **[Debug Mode](../main.py)** - `python main.py --debug`
- **[Highlight Debug](../test/debug_highlight.py)** - Syntax highlighting debug
- **[Test App](../test/test_app.py)** - General application testing

## 🎨 **Customization**

### **Themes**
- **[Dark Theme](../src/ui/themes.py)** - Default dark theme
- **[Custom Themes](INDEX.md#adding-themes)** - Create your own

### **Syntax Highlighting**
- **[Language Files](../src/editors/highlight/)** - 15+ supported languages
- **[Adding Languages](INDEX.md#adding-syntax-highlighting)** - Extend support

### **Tools & Extensions**
- **[Tool System](FLEXIBLE_TOOLS_SYSTEM.md)** - Modular architecture
- **[Adding Tools](INDEX.md#adding-new-tools)** - Create new tools

## 🆘 **Support & Troubleshooting**

### **Common Issues**
- **[Troubleshooting](../README.md#troubleshooting)** - Common problems and solutions
- **[Dependencies](../README.md#requirements)** - Required packages
- **[Permissions](../README.md#troubleshooting)** - File access issues

### **Getting Help**
- **[GitHub Issues](https://github.com/your-repo/issues)** - Report bugs
- **[Discussions](https://github.com/your-repo/discussions)** - Ask questions
- **[Contributing](../README.md#contributing)** - Help improve the project

## 📈 **Recent Updates**

### **Latest Fixes (Current)**
- ✅ **APKTool decompile issues fixed**
- ✅ **Progress bar functionality improved**
- ✅ **Log window connection enhanced**
- ✅ **Error handling upgraded**
- ✅ **Dependency validation added**

### **Recent Features**
- ✅ **External editor integration**
- ✅ **Hex editor support**
- ✅ **Modular tool system**
- ✅ **Enhanced syntax highlighting**
- ✅ **Detachable windows**

## 🎯 **Project Goals**

### **Current Focus**
- 🔄 **Stability improvements**
- 🎨 **UI/UX enhancements**
- 🧩 **Plugin system development**
- 📱 **Mobile development tools**

### **Future Plans**
- 🌐 **Multi-language support**
- 🔌 **Plugin marketplace**
- 📊 **Performance optimization**
- 🤖 **AI-assisted features**

---

**💡 Tip**: Bookmark this navigation page for quick access to all GP Manager documentation and resources!

**🔗 Quick Links**: [Main App](../main.py) | [Setup](../setup.py) | [Tests](../test/test_app.py) | [Config](../src/utils/config.py)
