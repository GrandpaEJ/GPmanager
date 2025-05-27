#!/bin/bash
# GP Manager Launcher Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python module
check_python_module() {
    python3 -c "import $1" 2>/dev/null
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_status "GP Manager Launcher"
echo "=================================="

# Check if Python 3 is available
if ! command_exists python3; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3:"
    echo "  Ubuntu/Debian: sudo apt install python3"
    echo "  Fedora: sudo dnf install python3"
    echo "  Arch: sudo pacman -S python"
    exit 1
fi

print_success "Python 3 found: $(python3 --version)"

# Check dependencies
missing_deps=()

if ! check_python_module "PyQt5"; then
    missing_deps+=("python3-pyqt5")
fi

if ! check_python_module "PyQt5.Qsci"; then
    missing_deps+=("python3-pyqt5.qsci")
fi

if ! check_python_module "pygments"; then
    missing_deps+=("python3-pygments")
fi

# Check optional dependencies
optional_missing=()

if ! command_exists apktool; then
    optional_missing+=("apktool")
fi

if ! command_exists java; then
    optional_missing+=("java")
fi

# Handle missing dependencies
if [ ${#missing_deps[@]} -gt 0 ]; then
    print_error "Missing required dependencies: ${missing_deps[*]}"
    echo ""
    echo "Would you like to install them automatically? (y/n)"
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Running setup wizard..."
        python3 setup.py --install

        if [ $? -eq 0 ]; then
            print_success "Dependencies installed successfully!"
        else
            print_error "Installation failed. Please install manually:"
            echo "  sudo apt install ${missing_deps[*]}"
            exit 1
        fi
    else
        print_error "Cannot start without required dependencies"
        echo "Install them manually:"
        echo "  sudo apt install ${missing_deps[*]}"
        echo "Or run: python3 setup.py --install"
        exit 1
    fi
fi

# Show optional dependency status
if [ ${#optional_missing[@]} -gt 0 ]; then
    print_warning "Optional dependencies missing: ${optional_missing[*]}"
    echo "These are not required but enable additional features:"
    echo "  apktool: APK decompilation/recompilation"
    echo "  java: APK signing"
    echo ""
    echo "Install them with: python3 setup.py --install"
    echo ""
fi

# Check if all required dependencies are now available
all_good=true
for dep in "PyQt5" "pygments"; do
    if ! check_python_module "$dep"; then
        print_error "Dependency $dep still not available"
        all_good=false
    fi
done

if [ "$all_good" = false ]; then
    print_error "Some dependencies are still missing. Cannot start application."
    exit 1
fi

# Run the application
print_success "All required dependencies found!"
print_status "Starting GP Manager..."
echo ""

# Set environment variables for better Qt experience
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_ENABLE_HIGHDPI_SCALING=1

# Run the application
python3 main.py "$@"
