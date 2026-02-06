#!/bin/bash

# CORE AI Chatbot - Development Environment Setup Script
# This script automates the setup of the development environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo -e "${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    print_info "Checking Python installation..."

    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION installed"

        # Check if version is 3.11 or higher
        MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
            print_success "Python version is compatible (3.11+)"
        else
            print_warning "Python 3.11+ recommended, found $PYTHON_VERSION"
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Check Node.js version
check_node() {
    print_info "Checking Node.js installation..."

    if command_exists node; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        print_success "Node.js $NODE_VERSION installed"

        # Check if version is 18 or higher
        MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)

        if [ "$MAJOR" -ge 18 ]; then
            print_success "Node.js version is compatible (18+)"
        else
            print_warning "Node.js 18+ recommended, found $NODE_VERSION"
        fi
    else
        print_error "Node.js is not installed"
        exit 1
    fi
}

# Setup backend
setup_backend() {
    print_header "Setting up Backend"

    cd backend

    # Create virtual environment
    print_info "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi

    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate

    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip --quiet
    print_success "Pip upgraded"

    # Install dependencies
    print_info "Installing Python dependencies..."
    pip install -r requirements-enterprise.txt --quiet
    print_success "Dependencies installed"

    # Setup environment file
    if [ ! -f ".env" ]; then
        print_info "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please update .env with your configuration (especially MISTRAL_API_KEY)"
    else
        print_success ".env file already exists"
    fi

    # Create logs directory
    if [ ! -d "logs" ]; then
        mkdir -p logs
        print_success "Logs directory created"
    fi

    cd ..
}

# Setup frontend
setup_frontend() {
    print_header "Setting up Frontend"

    cd frontend

    # Install dependencies
    print_info "Installing Node.js dependencies..."
    npm install --silent
    print_success "Dependencies installed"

    cd ..
}

# Setup database
setup_database() {
    print_header "Setting up Database"

    print_info "Initializing database..."
    cd backend
    source venv/bin/activate
    python3 ../scripts/init_db.py
    cd ..
}

# Check Docker
check_docker() {
    print_info "Checking Docker installation..."

    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker $DOCKER_VERSION installed"

        if command_exists docker-compose; then
            COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
            print_success "Docker Compose $COMPOSE_VERSION installed"
        else
            print_warning "Docker Compose not found (optional)"
        fi
    else
        print_warning "Docker not found (optional but recommended)"
    fi
}

# Main setup function
main() {
    print_header "CORE AI Chatbot - Development Setup"

    echo ""
    print_info "This script will set up your development environment"
    echo ""

    # Check prerequisites
    print_header "Checking Prerequisites"
    check_python
    check_node
    check_docker

    echo ""
    read -p "Continue with setup? (y/n) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Setup cancelled"
        exit 0
    fi

    # Setup components
    setup_backend
    setup_frontend

    # Ask about database initialization
    echo ""
    read -p "Initialize database now? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_database
    else
        print_info "Database initialization skipped"
        print_info "Run 'python scripts/init_db.py' when ready"
    fi

    # Final instructions
    print_header "Setup Complete!"

    echo ""
    print_success "Development environment is ready!"
    echo ""
    print_info "Next steps:"
    echo "  1. Update backend/.env with your MISTRAL_API_KEY"
    echo "  2. Start backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo "  3. Start frontend: cd frontend && npm run dev"
    echo ""
    print_info "Or use Docker:"
    echo "  docker-compose up -d"
    echo ""
    print_info "Access the application:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend:  http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
}

# Run main function
main
