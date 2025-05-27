"""
Language selector widget for syntax highlighting
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QPushButton, QListWidget, QListWidgetItem,
                            QGroupBox, QTextEdit, QSplitter)
from PyQt5.QtGui import QFont
from src.editors.json_highlighter import highlighter_manager


class LanguageInfoWidget(QWidget):
    """Widget to display language information and supported extensions"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_languages()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Supported Programming Languages")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Splitter for languages and details
        splitter = QSplitter(Qt.Horizontal)
        
        # Languages list
        languages_group = QGroupBox("Languages")
        languages_layout = QVBoxLayout(languages_group)
        
        self.languages_list = QListWidget()
        self.languages_list.currentItemChanged.connect(self.on_language_selected)
        languages_layout.addWidget(self.languages_list)
        
        splitter.addWidget(languages_group)
        
        # Language details
        details_group = QGroupBox("Language Details")
        details_layout = QVBoxLayout(details_group)
        
        # Language name
        self.language_name_label = QLabel("Select a language")
        self.language_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        details_layout.addWidget(self.language_name_label)
        
        # Extensions
        self.extensions_label = QLabel("Extensions: ")
        details_layout.addWidget(self.extensions_label)
        
        # Color scheme preview
        colors_group = QGroupBox("Color Scheme")
        colors_layout = QVBoxLayout(colors_group)
        
        self.colors_text = QTextEdit()
        self.colors_text.setMaximumHeight(150)
        self.colors_text.setReadOnly(True)
        self.colors_text.setFont(QFont("monospace"))
        colors_layout.addWidget(self.colors_text)
        
        details_layout.addWidget(colors_group)
        
        # Sample code preview
        sample_group = QGroupBox("Sample Code")
        sample_layout = QVBoxLayout(sample_group)
        
        self.sample_text = QTextEdit()
        self.sample_text.setReadOnly(True)
        self.sample_text.setFont(QFont("monospace"))
        sample_layout.addWidget(self.sample_text)
        
        details_layout.addWidget(sample_group)
        
        splitter.addWidget(details_group)
        
        # Set splitter ratio
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
    
    def load_languages(self):
        """Load supported languages into the list"""
        languages = highlighter_manager.get_supported_languages()
        languages.sort()
        
        for language in languages:
            item = QListWidgetItem(language.title())
            item.setData(Qt.UserRole, language)
            self.languages_list.addItem(item)
        
        # Select first language
        if self.languages_list.count() > 0:
            self.languages_list.setCurrentRow(0)
    
    def on_language_selected(self, current, previous):
        """Handle language selection"""
        if not current:
            return
        
        language_name = current.data(Qt.UserRole)
        self.show_language_details(language_name)
    
    def show_language_details(self, language_name):
        """Show details for selected language"""
        language_info = highlighter_manager.get_language_info(language_name)
        
        if not language_info:
            self.language_name_label.setText("Language information not available")
            return
        
        # Update language name
        display_name = language_info.get('name', language_name.title())
        self.language_name_label.setText(display_name)
        
        # Update extensions
        extensions = language_info.get('extensions', [])
        extensions_text = "Extensions: " + ", ".join(extensions)
        self.extensions_label.setText(extensions_text)
        
        # Update color scheme
        self.show_color_scheme(language_info.get('colors', {}))
        
        # Update sample code
        self.show_sample_code(language_name, language_info)
    
    def show_color_scheme(self, colors):
        """Show color scheme information"""
        color_text = ""
        for color_name, color_value in colors.items():
            color_text += f"{color_name}: {color_value}\n"
        
        self.colors_text.setPlainText(color_text)
    
    def show_sample_code(self, language_name, language_info):
        """Show sample code with syntax highlighting"""
        samples = {
            'py': '''# Python sample code
def fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Usage
result = fibonacci(10)
print(f"Fibonacci(10) = {result}")''',
            
            'java': '''// Java sample code
public class HelloWorld {
    private static final String MESSAGE = "Hello, World!";
    
    public static void main(String[] args) {
        System.out.println(MESSAGE);
        
        // Create instance
        HelloWorld app = new HelloWorld();
        app.greet("Java");
    }
    
    public void greet(String name) {
        System.out.println("Hello, " + name + "!");
    }
}''',
            
            'cpp': '''// C++ sample code
#include <iostream>
#include <vector>
#include <string>

class Calculator {
private:
    std::vector<double> history;
    
public:
    double add(double a, double b) {
        double result = a + b;
        history.push_back(result);
        return result;
    }
    
    void printHistory() const {
        for (const auto& value : history) {
            std::cout << value << " ";
        }
        std::cout << std::endl;
    }
};''',
            
            'js': '''// JavaScript sample code
class TaskManager {
    constructor() {
        this.tasks = [];
    }
    
    addTask(task) {
        this.tasks.push({
            id: Date.now(),
            text: task,
            completed: false
        });
    }
    
    completeTask(id) {
        const task = this.tasks.find(t => t.id === id);
        if (task) {
            task.completed = true;
        }
    }
    
    getTasks() {
        return this.tasks.filter(t => !t.completed);
    }
}

// Usage
const manager = new TaskManager();
manager.addTask("Learn JavaScript");''',
            
            'html': '''<!-- HTML sample code -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample Page</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 800px; margin: 0 auto; }
        .highlight { background-color: yellow; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to My Page</h1>
        <p class="highlight">This is a sample HTML document.</p>
        <ul>
            <li><a href="#section1">Section 1</a></li>
            <li><a href="#section2">Section 2</a></li>
        </ul>
    </div>
</body>
</html>''',
            
            'smali': '''# Smali sample code
.class public Lcom/example/MainActivity;
.super Landroid/app/Activity;

.field private message:Ljava/lang/String;

.method public constructor <init>()V
    .locals 1
    
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V
    
    const-string v0, "Hello, Android!"
    iput-object v0, p0, Lcom/example/MainActivity;->message:Ljava/lang/String;
    
    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 2
    .param p1, "savedInstanceState"    # Landroid/os/Bundle;
    
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
    
    const v0, 0x7f030000
    invoke-virtual {p0, v0}, Lcom/example/MainActivity;->setContentView(I)V
    
    return-void
.end method'''
        }
        
        sample_code = samples.get(language_name, f"# {language_info.get('name', 'Sample')} code\n# No sample available")
        self.sample_text.setPlainText(sample_code)
        
        # Apply syntax highlighting to sample
        try:
            highlighter = highlighter_manager.get_highlighter_for_file(
                f"sample.{language_info.get('extensions', ['txt'])[0][1:]}",
                self.sample_text.document()
            )
        except:
            pass  # Highlighting failed, show plain text


class LanguageSelectorDialog(QWidget):
    """Dialog for selecting syntax highlighting language"""
    
    language_selected = pyqtSignal(str)
    
    def __init__(self, current_language=None, parent=None):
        super().__init__(parent)
        self.current_language = current_language
        self.setWindowTitle("Select Syntax Highlighting Language")
        self.resize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Language selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Language:"))
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("Auto-detect", "auto")
        self.language_combo.addItem("Plain Text", "none")
        
        # Add supported languages
        languages = highlighter_manager.get_supported_languages()
        languages.sort()
        
        for language in languages:
            display_name = language.title()
            self.language_combo.addItem(display_name, language)
        
        selection_layout.addWidget(self.language_combo)
        layout.addLayout(selection_layout)
        
        # Set current language
        if self.current_language:
            index = self.language_combo.findData(self.current_language)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_language)
        button_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def apply_language(self):
        """Apply selected language"""
        language = self.language_combo.currentData()
        self.language_selected.emit(language)
        self.close()
