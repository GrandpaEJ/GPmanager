"""
Configuration management for GP Manager
"""
import os
import json
from pathlib import Path


class Config:
    """Application configuration manager"""

    def __init__(self):
        self.config_dir = Path.home() / '.gpmanager'
        self.config_file = self.config_dir / 'config.json'
        self.default_config = {
            'theme': 'dark',
            'font_size': 10,
            'font_family': 'Consolas',
            'show_hidden_files': False,
            'apktool_path': 'apktool',
            'java_path': 'java',
            'window_geometry': {
                'width': 1200,
                'height': 800,
                'x': 100,
                'y': 100
            },
            'pane_splitter_ratio': 0.5,
            'recent_paths': []
        }
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file"""
        if not self.config_file.exists():
            return self.default_config.copy()

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_config = self.default_config.copy()
                merged_config.update(config)
                return merged_config
        except (json.JSONDecodeError, IOError):
            return self.default_config.copy()

    def save_config(self):
        """Save configuration to file"""
        self.config_dir.mkdir(exist_ok=True)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError:
            pass  # Fail silently

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value

    def add_recent_path(self, path):
        """Add path to recent paths list"""
        recent = self.config.get('recent_paths', [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self.config['recent_paths'] = recent[:10]  # Keep only last 10


# Global config instance
config = Config()
