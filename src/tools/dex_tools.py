"""
DEX (Dalvik Executable) manipulation tools
Provides tools for working with Android DEX files
"""
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple, List
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class DexToolsError(Exception):
    """Exception raised by DEX tools"""
    pass


class SmaliWorker(QThread):
    """Worker thread for Smali operations"""
    
    operation_finished = pyqtSignal(bool, str)  # success, message
    progress_updated = pyqtSignal(str)  # status message
    
    def __init__(self, operation: str, input_path: str, output_path: str):
        super().__init__()
        self.operation = operation  # 'dex2smali' or 'smali2dex'
        self.input_path = input_path
        self.output_path = output_path
    
    def run(self):
        """Run the Smali operation"""
        try:
            if self.operation == 'dex2smali':
                success, message = DexTools.dex_to_smali(
                    self.input_path, 
                    self.output_path,
                    progress_callback=self.progress_updated.emit
                )
            elif self.operation == 'smali2dex':
                success, message = DexTools.smali_to_dex(
                    self.input_path,
                    self.output_path,
                    progress_callback=self.progress_updated.emit
                )
            else:
                success, message = False, f"Unknown operation: {self.operation}"
                
            self.operation_finished.emit(success, message)
            
        except Exception as e:
            self.operation_finished.emit(False, str(e))


class DexTools:
    """Tools for DEX file manipulation"""
    
    @staticmethod
    def is_baksmali_available() -> bool:
        """Check if baksmali is available"""
        try:
            result = subprocess.run(['baksmali', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @staticmethod
    def is_smali_available() -> bool:
        """Check if smali is available"""
        try:
            result = subprocess.run(['smali', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @staticmethod
    def get_baksmali_version() -> Optional[str]:
        """Get baksmali version"""
        try:
            result = subprocess.run(['baksmali', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None
    
    @staticmethod
    def get_smali_version() -> Optional[str]:
        """Get smali version"""
        try:
            result = subprocess.run(['smali', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None
    
    @staticmethod
    def dex_to_smali(dex_path: str, output_dir: str, 
                     progress_callback=None) -> Tuple[bool, str]:
        """Convert DEX file to Smali format"""
        try:
            dex_file = Path(dex_path)
            output_path = Path(output_dir)
            
            if not dex_file.exists():
                return False, f"DEX file not found: {dex_path}"
            
            if not DexTools.is_baksmali_available():
                return False, "baksmali not found. Please install baksmali/smali tools."
            
            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)
            
            if progress_callback:
                progress_callback("Starting DEX to Smali conversion...")
            
            # Build baksmali command
            cmd = [
                'baksmali', 'disassemble',
                str(dex_file),
                '-o', str(output_path)
            ]
            
            if progress_callback:
                progress_callback("Running baksmali...")
            
            # Run baksmali
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                if progress_callback:
                    progress_callback("Conversion completed successfully")
                return True, f"Successfully converted DEX to Smali in {output_path}"
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, f"baksmali failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "baksmali operation timed out"
        except Exception as e:
            return False, f"Error during DEX to Smali conversion: {str(e)}"
    
    @staticmethod
    def smali_to_dex(smali_dir: str, output_dex: str,
                     progress_callback=None) -> Tuple[bool, str]:
        """Convert Smali directory to DEX file"""
        try:
            smali_path = Path(smali_dir)
            output_file = Path(output_dex)
            
            if not smali_path.exists():
                return False, f"Smali directory not found: {smali_dir}"
            
            if not DexTools.is_smali_available():
                return False, "smali not found. Please install baksmali/smali tools."
            
            # Create output directory
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if progress_callback:
                progress_callback("Starting Smali to DEX conversion...")
            
            # Build smali command
            cmd = [
                'smali', 'assemble',
                str(smali_path),
                '-o', str(output_file)
            ]
            
            if progress_callback:
                progress_callback("Running smali...")
            
            # Run smali
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                if progress_callback:
                    progress_callback("Conversion completed successfully")
                return True, f"Successfully converted Smali to DEX: {output_file}"
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, f"smali failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "smali operation timed out"
        except Exception as e:
            return False, f"Error during Smali to DEX conversion: {str(e)}"
    
    @staticmethod
    def validate_dex_file(dex_path: str) -> Tuple[bool, str]:
        """Validate DEX file format"""
        try:
            dex_file = Path(dex_path)
            
            if not dex_file.exists():
                return False, f"File not found: {dex_path}"
            
            # Check file size
            if dex_file.stat().st_size < 112:  # Minimum DEX header size
                return False, "File too small to be a valid DEX file"
            
            # Check magic number
            with open(dex_file, 'rb') as f:
                magic = f.read(4)
                if magic != b'dex\n':
                    return False, "Invalid DEX magic number"
                
                # Check version
                version = f.read(4)
                valid_versions = [b'035\x00', b'037\x00', b'038\x00', b'039\x00']
                if version not in valid_versions:
                    return False, f"Unsupported DEX version: {version}"
            
            return True, "Valid DEX file"
            
        except Exception as e:
            return False, f"Error validating DEX file: {str(e)}"
    
    @staticmethod
    def extract_dex_from_apk(apk_path: str, output_dir: str) -> Tuple[bool, str, List[str]]:
        """Extract DEX files from APK"""
        try:
            apk_file = Path(apk_path)
            output_path = Path(output_dir)
            
            if not apk_file.exists():
                return False, f"APK file not found: {apk_path}", []
            
            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Extract APK using unzip
            import zipfile
            dex_files = []
            
            with zipfile.ZipFile(apk_file, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith('.dex'):
                        # Extract DEX file
                        zip_ref.extract(file_info, output_path)
                        dex_files.append(str(output_path / file_info.filename))
            
            if dex_files:
                return True, f"Extracted {len(dex_files)} DEX files", dex_files
            else:
                return False, "No DEX files found in APK", []
                
        except Exception as e:
            return False, f"Error extracting DEX from APK: {str(e)}", []
    
    @staticmethod
    def get_dex_info(dex_path: str) -> dict:
        """Get basic information about DEX file"""
        try:
            from src.parsers.dex_parser import DexParser
            
            parser = DexParser(dex_path)
            if parser.parse():
                return parser.get_summary()
            else:
                return {'error': 'Failed to parse DEX file'}
                
        except ImportError:
            # Fallback to basic file info
            dex_file = Path(dex_path)
            return {
                'file_path': str(dex_file),
                'file_size': dex_file.stat().st_size,
                'error': 'DEX parser not available'
            }
        except Exception as e:
            return {'error': f'Error getting DEX info: {str(e)}'}
    
    @staticmethod
    def install_smali_tools() -> Tuple[bool, str]:
        """Install baksmali/smali tools"""
        try:
            # Check if tools are already available
            if DexTools.is_baksmali_available() and DexTools.is_smali_available():
                return True, "baksmali/smali tools are already installed"
            
            # Try to install via package manager
            install_commands = [
                ['apt', 'install', '-y', 'smali'],  # Debian/Ubuntu
                ['yum', 'install', '-y', 'smali'],  # RHEL/CentOS
                ['pacman', '-S', '--noconfirm', 'smali'],  # Arch
                ['brew', 'install', 'smali']  # macOS
            ]
            
            for cmd in install_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        # Verify installation
                        if DexTools.is_baksmali_available() and DexTools.is_smali_available():
                            return True, f"Successfully installed smali tools via {cmd[0]}"
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            return False, "Failed to install smali tools. Please install manually."
            
        except Exception as e:
            return False, f"Error installing smali tools: {str(e)}"


class DexOptimizer:
    """DEX file optimization tools"""
    
    @staticmethod
    def optimize_dex(dex_path: str, output_path: str) -> Tuple[bool, str]:
        """Optimize DEX file (placeholder for future implementation)"""
        # This would implement DEX optimization techniques
        # For now, just copy the file
        try:
            shutil.copy2(dex_path, output_path)
            return True, f"DEX file copied to {output_path} (optimization not yet implemented)"
        except Exception as e:
            return False, f"Error copying DEX file: {str(e)}"
    
    @staticmethod
    def analyze_dex_dependencies(dex_path: str) -> dict:
        """Analyze DEX file dependencies (placeholder)"""
        # This would analyze class dependencies, method calls, etc.
        return {
            'analysis': 'Dependency analysis not yet implemented',
            'file': dex_path
        }
