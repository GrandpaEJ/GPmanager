# GP Manager - Test Suite

This directory contains test scripts and debugging tools for GP Manager.

## 🧪 **Test Files**

### **Functionality Tests**
- **`test_apktool_fixes.py`** - Tests APKTool integration and recent fixes
- **`test_app.py`** - General application functionality tests
- **`test_highlight.py`** - Syntax highlighting system tests
- **`test_external_editors.py`** - External editor integration tests
- **`test_color_contrast.py`** - Theme and color contrast tests

### **Debug Tools**
- **`debug_highlight.py`** - Interactive syntax highlighting debugger

## 🚀 **Running Tests**

### **Individual Tests**
```bash
# From project root
cd gpmanager

# Test APKTool functionality
python test/test_apktool_fixes.py

# Test syntax highlighting
python test/test_highlight.py

# Test external editors
python test/test_external_editors.py

# Test color themes
python test/test_color_contrast.py

# General application test
python test/test_app.py
```

### **Debug Tools**
```bash
# Debug syntax highlighting
python test/debug_highlight.py
```

## 📋 **Test Requirements**

All tests require the same dependencies as the main application:
- Python 3.6+
- PyQt5
- Pygments (for syntax highlighting tests)

Optional for APKTool tests:
- APKTool
- Java

## 🔧 **Test Structure**

Each test file follows this pattern:
1. **Setup** - Initialize test environment
2. **Import** - Import required modules with error handling
3. **Test UI** - Create test interface
4. **Execute** - Run specific functionality tests
5. **Cleanup** - Clean up resources

## 📊 **Test Coverage**

### **Core Components**
- ✅ APKTool integration
- ✅ Syntax highlighting
- ✅ External editor integration
- ✅ Theme system
- ✅ UI components

### **Recent Fixes Tested**
- ✅ APKTool decompile process
- ✅ Progress bar functionality
- ✅ Log window connection
- ✅ Error handling improvements

## 🐛 **Debugging**

### **Debug Mode**
Run any test with debug output:
```bash
python test/test_app.py --debug
```

### **Verbose Output**
Enable detailed logging in tests by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 **Adding New Tests**

1. Create new test file: `test_new_feature.py`
2. Follow existing test patterns
3. Add imports with error handling
4. Create test UI if needed
5. Document test purpose and usage
6. Update this README

## 🔗 **Related Documentation**

- **[Main Documentation](../docs/INDEX.md)** - Complete project overview
- **[Installation Guide](../docs/INSTALLATION_GUIDE.md)** - Setup instructions
- **[Development Guide](../docs/INDEX.md#support--development)** - Contributing guidelines

---

**💡 Tip**: Run tests after making changes to ensure functionality remains intact!
