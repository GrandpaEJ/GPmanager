# GP Manager - Syntax Highlighting System

## Overview

GP Manager features a comprehensive JSON-based syntax highlighting system that supports 15+ programming languages with customizable color schemes and extensible configuration.

## Supported Languages

### Core Programming Languages
| Language | Extensions | Features |
|----------|------------|----------|
| **Python** | `.py`, `.pyw`, `.pyi` | Keywords, functions, classes, decorators, strings, comments |
| **Java** | `.java` | Keywords, annotations, classes, methods, primitives, strings |
| **C++** | `.cpp`, `.cxx`, `.cc`, `.h`, `.hpp` | Keywords, preprocessor, classes, STL types, strings |
| **C#** | `.cs` | Keywords, attributes, classes, methods, built-in types |
| **JavaScript** | `.js`, `.jsx`, `.mjs`, `.es6` | ES6+ keywords, functions, classes, template literals |

### Web Technologies
| Language | Extensions | Features |
|----------|------------|----------|
| **HTML** | `.html`, `.htm`, `.xhtml` | Tags, attributes, entities, nested JS/CSS |
| **XML** | `.xml`, `.xsd`, `.xsl`, `.svg` | Tags, attributes, namespaces, CDATA |
| **CSS** | `.css`, `.scss`, `.sass`, `.less` | Selectors, properties, values, at-rules |
| **JSON** | `.json`, `.jsonc` | Keys, values, types, comments (JSONC) |

### Mobile Development
| Language | Extensions | Features |
|----------|------------|----------|
| **Smali** | `.smali` | Directives, instructions, registers, types, labels |

### Database & Scripting
| Language | Extensions | Features |
|----------|------------|----------|
| **SQL** | `.sql`, `.mysql`, `.pgsql` | Keywords, functions, data types, operators |
| **PHP** | `.php`, `.phtml` | Keywords, variables, functions, classes |
| **Bash** | `.sh`, `.bash`, `.zsh` | Keywords, variables, functions, operators |

### Configuration & Documentation
| Language | Extensions | Features |
|----------|------------|----------|
| **YAML** | `.yaml`, `.yml` | Keys, values, anchors, tags, booleans |
| **Markdown** | `.md`, `.markdown` | Headings, formatting, links, code blocks |

## JSON Configuration System

### Configuration Structure
Each language is defined by a JSON file in `src/editors/highlight/`:

```json
{
  "name": "Language Name",
  "extensions": [".ext1", ".ext2"],
  "colors": {
    "keyword": "#569cd6",
    "string": "#ce9178",
    "comment": "#6a9955"
  },
  "rules": [
    {
      "name": "rule_name",
      "pattern": "regex_pattern",
      "color": "color_name",
      "bold": true,
      "italic": false
    }
  ],
  "multiline_rules": [
    {
      "name": "multiline_rule",
      "start": "start_pattern",
      "end": "end_pattern",
      "color": "color_name"
    }
  ]
}
```

### Color Scheme
Standard color palette used across languages:

| Color Name | Hex Value | Usage |
|------------|-----------|-------|
| `keyword` | `#569cd6` | Language keywords |
| `string` | `#ce9178` | String literals |
| `comment` | `#6a9955` | Comments |
| `number` | `#b5cea8` | Numeric values |
| `function` | `#dcdcaa` | Function names |
| `class` | `#4ec9b0` | Class names |
| `operator` | `#d4d4d4` | Operators |

### Rule Types

#### Single-line Rules
```json
{
  "name": "keywords",
  "pattern": "\\b(if|else|while|for)\\b",
  "color": "keyword",
  "bold": true,
  "case_insensitive": false,
  "group": 0
}
```

#### Multiline Rules
```json
{
  "name": "multiline_comments",
  "start": "/\\*",
  "end": "\\*/",
  "color": "comment",
  "italic": true
}
```

#### Capture Groups
```json
{
  "name": "function_definition",
  "pattern": "\\bdef\\s+(\\w+)",
  "color": "function",
  "group": 1
}
```

## Features

### Automatic Detection
- **File extension mapping** - Automatically applies highlighting based on file extension
- **Fallback handling** - Graceful degradation when language not supported
- **Real-time switching** - Change highlighting language on-the-fly

### Advanced Highlighting
- **Nested languages** - HTML with embedded CSS/JavaScript
- **Capture groups** - Highlight specific parts of regex matches
- **Case sensitivity** - Configurable case-sensitive/insensitive matching
- **Multiline support** - Comments, strings, code blocks

### Customization
- **JSON configuration** - Easy to modify and extend
- **Color themes** - Consistent color scheme across languages
- **Rule priority** - Ordered rule application
- **Font styling** - Bold, italic, underline support

## Usage

### In Text Editor
1. **Open file** - Highlighting applied automatically based on extension
2. **Manual selection** - Use View → Language menu (future feature)
3. **Live preview** - See highlighting as you type

### In Preferences
1. Go to **File → Preferences**
2. Navigate to **Languages** tab
3. Browse supported languages and their features
4. View color schemes and sample code

### For Developers
```python
from src.editors.json_highlighter import highlighter_manager

# Get highlighter for file
highlighter = highlighter_manager.get_highlighter_for_file("example.py")

# Get supported languages
languages = highlighter_manager.get_supported_languages()

# Get language info
info = highlighter_manager.get_language_info("python")
```

## Adding New Languages

### 1. Create JSON Configuration
Create `src/editors/highlight/newlang.json`:

```json
{
  "name": "New Language",
  "extensions": [".newlang"],
  "colors": {
    "keyword": "#569cd6",
    "string": "#ce9178",
    "comment": "#6a9955"
  },
  "rules": [
    {
      "name": "keywords",
      "pattern": "\\b(keyword1|keyword2)\\b",
      "color": "keyword",
      "bold": true
    }
  ]
}
```

### 2. Test Configuration
```python
# Test the new language
highlighter = highlighter_manager.get_highlighter_for_file("test.newlang")
```

### 3. Add Sample Code
Update `src/ui/language_selector.py` to include sample code for the new language.

## Language-Specific Features

### Python
- **Decorators** - `@property`, `@staticmethod`
- **F-strings** - `f"Hello {name}"`
- **Triple quotes** - Multiline strings
- **Built-in functions** - `len()`, `range()`, `print()`

### Java
- **Annotations** - `@Override`, `@Deprecated`
- **Generics** - `List<String>`
- **Lambda expressions** - `x -> x * 2`
- **Method references** - `String::length`

### Smali
- **Directives** - `.class`, `.method`, `.field`
- **Instructions** - `invoke-virtual`, `move-result`
- **Registers** - `v0`, `p1`
- **Type descriptors** - `Ljava/lang/String;`

### HTML/XML
- **Nested languages** - JavaScript in `<script>`, CSS in `<style>`
- **Attributes** - Proper attribute name/value highlighting
- **Entities** - `&amp;`, `&#39;`
- **CDATA sections** - `<![CDATA[...]]>`

### CSS
- **Selectors** - Class, ID, element, pseudo
- **Properties** - All CSS properties
- **Values** - Colors, units, functions
- **At-rules** - `@media`, `@import`

## Performance

### Optimizations
- **Compiled regex** - Pre-compiled patterns for speed
- **Incremental highlighting** - Only highlight visible text
- **Caching** - Language configurations cached in memory
- **Lazy loading** - Languages loaded on demand

### Benchmarks
- **Small files** (<1KB): Instant highlighting
- **Medium files** (1-100KB): <100ms highlighting
- **Large files** (>100KB): Progressive highlighting

## Troubleshooting

### Common Issues

#### Highlighting Not Working
1. Check file extension is supported
2. Verify JSON configuration syntax
3. Check console for error messages
4. Restart application if needed

#### Colors Not Showing
1. Verify color hex values in JSON
2. Check theme compatibility
3. Ensure proper rule ordering

#### Performance Issues
1. Simplify complex regex patterns
2. Reduce number of rules
3. Use more specific patterns

### Debug Mode
Enable debug output:
```bash
export MTLINUX_DEBUG=1
python3 main.py
```

## Future Enhancements

### Planned Features
- **Theme editor** - Visual color scheme customization
- **Language detection** - Auto-detect language from content
- **Plugin system** - Third-party language support
- **Semantic highlighting** - Context-aware highlighting
- **Code folding** - Collapsible code blocks

### Community Contributions
- **Language requests** - Submit issues for new languages
- **JSON contributions** - Share language configurations
- **Color themes** - Alternative color schemes
- **Performance improvements** - Optimize regex patterns

## Conclusion

The JSON-based syntax highlighting system provides comprehensive language support with easy extensibility and customization. The modular design allows for rapid addition of new languages while maintaining consistent performance and user experience across all supported file types.
