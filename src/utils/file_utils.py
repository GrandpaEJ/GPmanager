"""
File utility functions for MT Manager Linux
"""
import os
import shutil
import stat
import mimetypes
from pathlib import Path
from datetime import datetime


class FileUtils:
    """Utility class for file operations"""

    @staticmethod
    def get_file_size_str(size):
        """Convert file size to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    @staticmethod
    def get_file_icon_type(file_path):
        """Get file type for icon selection"""
        if os.path.isdir(file_path):
            return 'folder'

        ext = Path(file_path).suffix.lower()

        # APK files
        if ext == '.apk':
            return 'apk'

        # Archive files
        if ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
            return 'archive'

        # Image files
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
            return 'image'

        # Text files
        if ext in ['.txt', '.log', '.md', '.xml', '.json', '.smali', '.java']:
            return 'text'

        # DEX files (Android Dalvik Executable)
        if ext == '.dex':
            return 'dex'

        # Executable files
        if ext in ['.exe', '.so']:
            return 'executable'

        return 'file'

    @staticmethod
    def is_hidden_file(file_path):
        """Check if file is hidden"""
        return Path(file_path).name.startswith('.')

    @staticmethod
    def get_file_permissions_str(file_path):
        """Get file permissions as string"""
        try:
            mode = os.stat(file_path).st_mode
            permissions = stat.filemode(mode)
            return permissions
        except OSError:
            return '----------'

    @staticmethod
    def get_file_modified_time(file_path):
        """Get file modification time as string"""
        try:
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        except OSError:
            return 'Unknown'

    @staticmethod
    def copy_file(src, dst, progress_callback=None):
        """Copy file with optional progress callback"""
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            return True
        except Exception as e:
            print(f"Copy error: {e}")
            return False

    @staticmethod
    def move_file(src, dst):
        """Move file or directory"""
        try:
            shutil.move(src, dst)
            return True
        except Exception as e:
            print(f"Move error: {e}")
            return False

    @staticmethod
    def delete_file(file_path):
        """Delete file or directory"""
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    @staticmethod
    def create_directory(dir_path):
        """Create directory"""
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Create directory error: {e}")
            return False

    @staticmethod
    def is_apk_file(file_path):
        """Check if file is an APK"""
        return Path(file_path).suffix.lower() == '.apk'

    @staticmethod
    def is_archive_file(file_path):
        """Check if file is an archive"""
        ext = Path(file_path).suffix.lower()
        return ext in ['.zip', '.apk', '.jar', '.rar', '.7z', '.tar', '.gz']

    @staticmethod
    def is_text_file(file_path):
        """Check if file is a text file"""
        ext = Path(file_path).suffix.lower()
        text_extensions = ['.txt', '.log', '.md', '.xml', '.json', '.smali',
                          '.java', '.py', '.js', '.html', '.css', '.yml', '.yaml',
                          '.c', '.cpp', '.h', '.hpp', '.cs', '.php', '.rb', '.go',
                          '.rs', '.kt', '.swift', '.sh', '.bat', '.ps1', '.sql',
                          '.ini', '.cfg', '.conf', '.properties', '.gitignore']
        return ext in text_extensions

    @staticmethod
    def is_image_file(file_path):
        """Check if file is an image"""
        ext = Path(file_path).suffix.lower()
        return ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff', '.ico']

    @staticmethod
    def is_video_file(file_path):
        """Check if file is a video"""
        ext = Path(file_path).suffix.lower()
        return ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp']

    @staticmethod
    def is_audio_file(file_path):
        """Check if file is audio"""
        ext = Path(file_path).suffix.lower()
        return ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus']

    @staticmethod
    def is_dex_file(file_path):
        """Check if file is a DEX file"""
        ext = Path(file_path).suffix.lower()
        return ext == '.dex'

    @staticmethod
    def is_executable_file(file_path):
        """Check if file is executable"""
        ext = Path(file_path).suffix.lower()
        return ext in ['.exe', '.so', '.dll', '.app', '.dmg', '.deb', '.rpm']

    @staticmethod
    def is_document_file(file_path):
        """Check if file is a document"""
        ext = Path(file_path).suffix.lower()
        return ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp']
