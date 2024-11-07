#!/bin/bash

# DivergesApp Setup and Management Script

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed. Please install Docker and Docker Compose.${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Docker Compose is not installed. Please install Docker Compose.${NC}"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3.10+ is required but not installed.${NC}"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Node.js 18+ is required but not installed.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}All prerequisites are met!${NC}"
}

# Create environment files
create_env_files() {
    echo -e "${YELLOW}Creating environment files...${NC}"
    
    # Backend .env
    if [ ! -f backend/.env ]; then
        cp backend/.env.example backend/.env
        echo -e "${GREEN}Created backend/.env from example${NC}"
    fi
    
    # Frontend .env
    if [ ! -f frontend/.env ]; then
        cp frontend/.env.example frontend/.env
        echo -e "${GREEN}Created frontend/.env from example${NC}"
    fi
}

# Setup backend
setup_backend() {
    echo -e "${YELLOW}Setting up backend...${NC}"
    
    cd backend
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Run migrations
    alembic upgrade head
    
    deactivate
    cd ..
    
    echo -e "${GREEN}Backend setup complete!${NC}"
}

# Setup frontend
setup_frontend() {
    echo -e "${YELLOW}Setting up frontend...${NC}"
    
    cd frontend
    
    # Install dependencies
    npm install
    
    cd ..
    
    echo -e "${GREEN}Frontend setup complete!${NC}"
}

# Run development servers
run_dev_servers() {
    echo -e "${YELLOW}Starting development servers...${NC}"
    
    # Backend (Terminal 1)
    gnome-terminal --tab -- bash -c "cd backend && source venv/bin/activate && uvicorn app.main:app --reload; exec bash"
    
    # Frontend (Terminal 2)
    gnome-terminal --tab -- bash -c "cd frontend && npm run dev; exec bash"
    
    echo -e "${GREEN}Development servers started!${NC}"
}

# Docker development
run_docker_dev() {
    echo -e "${YELLOW}Starting Docker development environment...${NC}"
    
    # Ensure environment files exist
    create_env_files
    
    # Prune Docker system to free up space
    docker system prune -f
    
    # Build and start containers
    docker-compose up --build
}

# Main script
main() {
    echo -e "${GREEN}DivergesApp Setup Script${NC}"
    
    check_prerequisites
    
    # Prompt for setup type
    echo "Choose setup method:"
    echo "1. Local Development (Separate Terminals)"
    echo "2. Docker Development"
    read -p "Enter choice (1/2): " choice
    
    case $choice in
        1)
            create_env_files
            setup_backend
            setup_frontend
            run_dev_servers
            ;;
        2)
            run_docker_dev
            ;;
        *)
            echo -e "${RED}Invalid choice. Exiting.${NC}"
            exit 1
            ;;
    esac
}

# Run main script
main
