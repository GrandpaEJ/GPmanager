"""
Syntax highlighter for MT Manager Linux
"""
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


class SmaliSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Smali files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Define colors
        keyword_color = QColor(86, 156, 214)      # Blue
        string_color = QColor(206, 145, 120)      # Orange
        comment_color = QColor(106, 153, 85)      # Green
        number_color = QColor(181, 206, 168)      # Light green
        register_color = QColor(220, 220, 170)    # Yellow
        directive_color = QColor(197, 134, 192)   # Purple
        
        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setColor(keyword_color)
        keyword_format.setFontWeight(QFont.Bold)
        
        # Smali keywords
        keywords = [
            'class', 'super', 'implements', 'source', 'field', 'method',
            'end', 'local', 'line', 'parameter', 'annotation', 'enum',
            'interface', 'abstract', 'final', 'static', 'public', 'private',
            'protected', 'synchronized', 'volatile', 'transient', 'native',
            'strictfp', 'synthetic', 'bridge', 'varargs'
        ]
        
        for keyword in keywords:
            pattern = QRegExp(f'\\b{keyword}\\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Directive format
        directive_format = QTextCharFormat()
        directive_format.setColor(directive_color)
        directive_format.setFontWeight(QFont.Bold)
        
        # Smali directives
        directives = [
            '\\.class', '\\.super', '\\.implements', '\\.source', '\\.field',
            '\\.method', '\\.end', '\\.local', '\\.line', '\\.parameter',
            '\\.annotation', '\\.prologue', '\\.epilogue', '\\.catch',
            '\\.catchall', '\\.packed-switch', '\\.sparse-switch', '\\.array-data'
        ]
        
        for directive in directives:
            pattern = QRegExp(directive)
            self.highlighting_rules.append((pattern, directive_format))
        
        # Register format
        register_format = QTextCharFormat()
        register_format.setColor(register_color)
        
        # Registers (v0, v1, p0, p1, etc.)
        register_pattern = QRegExp('[vp]\\d+')
        self.highlighting_rules.append((register_pattern, register_format))
        
        # String format
        string_format = QTextCharFormat()
        string_format.setColor(string_color)
        
        # Strings
        string_pattern = QRegExp('".*"')
        self.highlighting_rules.append((string_pattern, string_format))
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setColor(number_color)
        
        # Numbers
        number_pattern = QRegExp('\\b\\d+\\b')
        self.highlighting_rules.append((number_pattern, number_format))
        
        # Hex numbers
        hex_pattern = QRegExp('0x[0-9a-fA-F]+')
        self.highlighting_rules.append((hex_pattern, number_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setColor(comment_color)
        comment_format.setFontItalic(True)
        
        # Comments
        comment_pattern = QRegExp('#.*')
        self.highlighting_rules.append((comment_pattern, comment_format))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


class JavaSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Java files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Define colors
        keyword_color = QColor(86, 156, 214)      # Blue
        string_color = QColor(206, 145, 120)      # Orange
        comment_color = QColor(106, 153, 85)      # Green
        number_color = QColor(181, 206, 168)      # Light green
        class_color = QColor(78, 201, 176)        # Cyan
        
        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setColor(keyword_color)
        keyword_format.setFontWeight(QFont.Bold)
        
        # Java keywords
        keywords = [
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch',
            'char', 'class', 'const', 'continue', 'default', 'do', 'double',
            'else', 'enum', 'extends', 'final', 'finally', 'float', 'for',
            'goto', 'if', 'implements', 'import', 'instanceof', 'int',
            'interface', 'long', 'native', 'new', 'package', 'private',
            'protected', 'public', 'return', 'short', 'static', 'strictfp',
            'super', 'switch', 'synchronized', 'this', 'throw', 'throws',
            'transient', 'try', 'void', 'volatile', 'while'
        ]
        
        for keyword in keywords:
            pattern = QRegExp(f'\\b{keyword}\\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Class format
        class_format = QTextCharFormat()
        class_format.setColor(class_color)
        class_format.setFontWeight(QFont.Bold)
        
        # Class names (capitalized words)
        class_pattern = QRegExp('\\b[A-Z][a-zA-Z0-9_]*\\b')
        self.highlighting_rules.append((class_pattern, class_format))
        
        # String format
        string_format = QTextCharFormat()
        string_format.setColor(string_color)
        
        # Strings
        string_pattern = QRegExp('".*"')
        self.highlighting_rules.append((string_pattern, string_format))
        
        # Character literals
        char_pattern = QRegExp("'.*'")
        self.highlighting_rules.append((char_pattern, string_format))
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setColor(number_color)
        
        # Numbers
        number_pattern = QRegExp('\\b\\d+(\\.\\d+)?[fFdDlL]?\\b')
        self.highlighting_rules.append((number_pattern, number_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setColor(comment_color)
        comment_format.setFontItalic(True)
        
        # Single line comments
        single_comment_pattern = QRegExp('//.*')
        self.highlighting_rules.append((single_comment_pattern, comment_format))
        
        # Multi-line comments
        self.comment_start_expression = QRegExp('/\\*')
        self.comment_end_expression = QRegExp('\\*/')
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        # Apply single-line rules
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        
        # Handle multi-line comments
        self.setCurrentBlockState(0)
        
        comment_format = QTextCharFormat()
        comment_format.setColor(QColor(106, 153, 85))
        comment_format.setFontItalic(True)
        
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)
        
        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()
            
            self.setFormat(start_index, comment_length, comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)


class XmlSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for XML files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define colors
        self.xml_keyword_color = QColor(86, 156, 214)     # Blue
        self.xml_element_color = QColor(78, 201, 176)     # Cyan
        self.xml_comment_color = QColor(106, 153, 85)     # Green
        self.xml_string_color = QColor(206, 145, 120)     # Orange
        self.xml_attribute_color = QColor(156, 220, 254)  # Light blue
    
    def highlightBlock(self, text):
        """Apply XML syntax highlighting"""
        # XML comments
        comment_format = QTextCharFormat()
        comment_format.setColor(self.xml_comment_color)
        comment_format.setFontItalic(True)
        
        comment_start = QRegExp('<!--')
        comment_end = QRegExp('-->')
        
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = comment_start.indexIn(text)
        
        while start_index >= 0:
            end_index = comment_end.indexIn(text, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + comment_end.matchedLength()
            
            self.setFormat(start_index, comment_length, comment_format)
            start_index = comment_start.indexIn(text, start_index + comment_length)
        
        # XML elements
        element_format = QTextCharFormat()
        element_format.setColor(self.xml_element_color)
        element_format.setFontWeight(QFont.Bold)
        
        element_pattern = QRegExp('<[!?/]?\\b[A-Za-z0-9_-]+(?=\\s|>|/>)')
        index = element_pattern.indexIn(text)
        while index >= 0:
            length = element_pattern.matchedLength()
            self.setFormat(index, length, element_format)
            index = element_pattern.indexIn(text, index + length)
        
        # XML attributes
        attribute_format = QTextCharFormat()
        attribute_format.setColor(self.xml_attribute_color)
        
        attribute_pattern = QRegExp('\\b[A-Za-z0-9_-]+(?=\\s*=)')
        index = attribute_pattern.indexIn(text)
        while index >= 0:
            length = attribute_pattern.matchedLength()
            self.setFormat(index, length, attribute_format)
            index = attribute_pattern.indexIn(text, index + length)
        
        # XML strings
        string_format = QTextCharFormat()
        string_format.setColor(self.xml_string_color)
        
        string_pattern = QRegExp('"[^"]*"')
        index = string_pattern.indexIn(text)
        while index >= 0:
            length = string_pattern.matchedLength()
            self.setFormat(index, length, string_format)
            index = string_pattern.indexIn(text, index + length)
