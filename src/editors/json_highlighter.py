"""
JSON-based syntax highlighter for MT Manager Linux
Loads highlighting rules from JSON configuration files
"""
import json
from pathlib import Path
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter that loads rules from JSON configuration files"""

    def __init__(self, language_file, parent=None):
        super().__init__(parent)
        self.language_config = None
        self.highlighting_rules = []
        self.multiline_rules = []
        self.load_language_config(language_file)
        self.setup_highlighting_rules()

    def load_language_config(self, language_file):
        """Load language configuration from JSON file"""
        try:
            config_path = Path(__file__).parent / 'highlight' / f'{language_file}.json'
            if not config_path.exists():
                print(f"Warning: Language config not found: {config_path}")
                return

            with open(config_path, 'r', encoding='utf-8') as f:
                self.language_config = json.load(f)

        except Exception as e:
            print(f"Error loading language config {language_file}: {e}")
            self.language_config = None

    def setup_highlighting_rules(self):
        """Setup highlighting rules from loaded configuration"""
        if not self.language_config:
            return

        colors = self.language_config.get('colors', {})
        rules = self.language_config.get('rules', [])
        multiline_rules = self.language_config.get('multiline_rules', [])

        # Sort rules by priority (higher priority first), then by order
        sorted_rules = sorted(rules, key=lambda r: (r.get('priority', 0), -rules.index(r)), reverse=True)

        # Process single-line rules
        for rule in sorted_rules:
            try:
                format_obj = self.create_text_format(rule, colors)
                pattern = rule.get('pattern', '')
                case_insensitive = rule.get('case_insensitive', False)
                group = rule.get('group', 0)

                # Create QRegExp with appropriate flags
                regex = QRegExp(pattern)
                if case_insensitive:
                    regex.setCaseSensitivity(0)  # Case insensitive
                else:
                    regex.setCaseSensitivity(1)  # Case sensitive

                self.highlighting_rules.append((regex, format_obj, group))

            except Exception as e:
                print(f"Error processing rule {rule.get('name', 'unknown')}: {e}")

        # Process multiline rules
        for rule in multiline_rules:
            try:
                format_obj = self.create_text_format(rule, colors)
                start_pattern = rule.get('start', '')
                end_pattern = rule.get('end', '')

                start_regex = QRegExp(start_pattern)
                end_regex = QRegExp(end_pattern)

                self.multiline_rules.append((start_regex, end_regex, format_obj))

            except Exception as e:
                print(f"Error processing multiline rule {rule.get('name', 'unknown')}: {e}")

    def create_text_format(self, rule, colors):
        """Create QTextCharFormat from rule configuration"""
        format_obj = QTextCharFormat()

        # Get color
        color_name = rule.get('color', 'text')
        color_value = colors.get(color_name, '#d4d4d4')  # Default to light gray

        try:
            color = QColor(color_value)
            format_obj.setForeground(color)
        except:
            # Fallback to default color
            format_obj.setForeground(QColor('#d4d4d4'))

        # Set font weight
        if rule.get('bold', False):
            format_obj.setFontWeight(QFont.Bold)

        # Set font style
        if rule.get('italic', False):
            format_obj.setFontItalic(True)

        # Set underline
        if rule.get('underline', False):
            format_obj.setFontUnderline(True)

        return format_obj

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        # Apply single-line rules
        for pattern, format_obj, group in self.highlighting_rules:
            index = pattern.indexIn(text)
            while index >= 0:
                if group > 0:
                    # Highlight specific capture group
                    length = len(pattern.cap(group))
                    start_pos = pattern.pos(group)
                    if start_pos >= 0 and length > 0:
                        self.setFormat(start_pos, length, format_obj)
                else:
                    # Highlight entire match
                    length = pattern.matchedLength()
                    if length > 0:
                        self.setFormat(index, length, format_obj)

                # Move to next match, ensure we advance at least 1 character
                next_index = index + max(1, length)
                index = pattern.indexIn(text, next_index)

        # Apply multiline rules
        self.apply_multiline_highlighting(text)

    def apply_multiline_highlighting(self, text):
        """Apply multiline highlighting rules"""
        for i, (start_regex, end_regex, format_obj) in enumerate(self.multiline_rules):
            # Use different block states for different multiline rules
            block_state = i + 1

            self.setCurrentBlockState(0)

            start_index = 0
            if self.previousBlockState() != block_state:
                start_index = start_regex.indexIn(text)

            while start_index >= 0:
                end_index = end_regex.indexIn(text, start_index)

                if end_index == -1:
                    self.setCurrentBlockState(block_state)
                    comment_length = len(text) - start_index
                else:
                    comment_length = end_index - start_index + end_regex.matchedLength()

                self.setFormat(start_index, comment_length, format_obj)
                start_index = start_regex.indexIn(text, start_index + comment_length)


class HighlighterManager:
    """Manages syntax highlighters for different file types"""

    def __init__(self):
        self.language_mappings = {}
        self.load_language_mappings()

    def load_language_mappings(self):
        """Load file extension to language mappings"""
        highlight_dir = Path(__file__).parent / 'highlight'

        for json_file in highlight_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                language_name = json_file.stem
                extensions = config.get('extensions', [])

                for ext in extensions:
                    self.language_mappings[ext.lower()] = language_name

            except Exception as e:
                print(f"Error loading language mapping from {json_file}: {e}")

    def get_highlighter_for_file(self, file_path, parent=None):
        """Get appropriate syntax highlighter for a file"""
        if not file_path:
            return None

        # Get file extension
        ext = Path(file_path).suffix.lower()

        # Find language for extension
        language = self.language_mappings.get(ext)

        if language:
            try:
                return JsonSyntaxHighlighter(language, parent)
            except Exception as e:
                print(f"Error creating highlighter for {language}: {e}")

        return None

    def get_supported_extensions(self):
        """Get list of all supported file extensions"""
        return list(self.language_mappings.keys())

    def get_supported_languages(self):
        """Get list of all supported languages"""
        return list(set(self.language_mappings.values()))

    def get_language_info(self, language_name):
        """Get detailed information about a language"""
        try:
            config_path = Path(__file__).parent / 'highlight' / f'{language_name}.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading language info for {language_name}: {e}")
            return None


# Global highlighter manager instance
highlighter_manager = HighlighterManager()
