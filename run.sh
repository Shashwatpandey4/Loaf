#!/bin/bash

# Food KB Answerer - Run Script
# Starts the interactive recipe chat bot

set -e  # Exit on any error

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

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d ".venv" ]; then
        print_error "Virtual environment not found!"
        print_status "Creating virtual environment..."
        python3 -m venv .venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment found"
    fi
}

# Function to activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source .venv/bin/activate
    print_success "Virtual environment activated"
}

# Function to check and install dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    # Install dependencies if needed
    print_status "Installing/updating dependencies..."
    pip install -r requirements.txt --quiet --disable-pip-version-check 2>/dev/null || pip install -r requirements.txt --quiet
    print_success "Dependencies installed"
}

# Function to check if chat.py exists
check_chat_script() {
    if [ ! -f "chat.py" ]; then
        print_error "chat.py not found!"
        exit 1
    fi
    
    if [ ! -x "chat.py" ]; then
        print_status "Making chat.py executable..."
        chmod +x chat.py
    fi
    
    print_success "Chat script found and ready"
}

# Function to start the chat bot
start_chat() {
    print_status "Starting Recipe Chat Bot..."
    echo ""
    echo "🍜 Food KB Answerer - Recipe Chat Bot"
    echo "======================================"
    echo ""
    
    python chat.py
}

# Function to show help
show_help() {
    echo "Food KB Answerer - Run Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -s, --setup    Setup environment and exit"
    echo "  -c, --check    Check environment and exit"
    echo ""
    echo "Examples:"
    echo "  $0              # Start the chat bot"
    echo "  $0 --setup      # Setup environment only"
    echo "  $0 --check      # Check environment only"
    echo ""
}

# Function to setup environment
setup_environment() {
    print_status "Setting up Food KB Answerer environment..."
    check_venv
    activate_venv
    check_dependencies
    check_chat_script
    print_success "Environment setup complete!"
}

# Function to check environment
check_environment() {
    print_status "Checking Food KB Answerer environment..."
    
    # Check virtual environment
    if [ -d ".venv" ]; then
        print_success "✓ Virtual environment exists"
    else
        print_error "✗ Virtual environment missing"
        return 1
    fi
    
    # Check dependencies
    if [ -f "requirements.txt" ]; then
        print_success "✓ requirements.txt exists"
    else
        print_error "✗ requirements.txt missing"
        return 1
    fi
    
    # Check chat script
    if [ -f "chat.py" ]; then
        print_success "✓ chat.py exists"
    else
        print_error "✗ chat.py missing"
        return 1
    fi
    
    # Check src directory
    if [ -d "src" ]; then
        print_success "✓ src directory exists"
    else
        print_error "✗ src directory missing"
        return 1
    fi
    
    print_success "Environment check complete!"
    return 0
}

# Main function
main() {
    # Parse command line arguments
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -s|--setup)
            setup_environment
            exit 0
            ;;
        -c|--check)
            check_environment
            exit $?
            ;;
        "")
            # No arguments - start the chat bot
            setup_environment
            start_chat
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
