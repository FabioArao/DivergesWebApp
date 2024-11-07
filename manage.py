#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import shutil

# Color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

def run_command(command, cwd=None, env=None, capture_output=False):
    """Run a shell command with optional working directory and environment"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            cwd=cwd, 
            env=env or os.environ.copy(),
            capture_output=capture_output,
            text=True
        )
        print(f"{GREEN}Command executed successfully: {command}{NC}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"{RED}Command failed: {command}{NC}")
        print(f"{RED}Error output: {e.stderr}{NC}")
        sys.exit(1)

def setup_backend_env():
    """Set up backend virtual environment and install dependencies"""
    os.chdir('backend')
    
    # Create virtual environment if not exists
    if not os.path.exists('venv'):
        run_command('python3 -m venv venv')
    
    # Activate virtual environment and install dependencies
    run_command('. venv/bin/activate && pip install -r requirements.txt')
    
    os.chdir('..')

def run_migrations(action='upgrade'):
    """Manage database migrations"""
    setup_backend_env()
    os.chdir('backend')
    
    migration_commands = {
        'upgrade': 'alembic upgrade head',
        'downgrade': 'alembic downgrade -1',
        'generate': 'alembic revision --autogenerate -m "Auto-generated migration"',
        'history': 'alembic history'
    }
    
    if action not in migration_commands:
        print(f"{RED}Invalid migration action: {action}{NC}")
        sys.exit(1)
    
    run_command(f'. venv/bin/activate && {migration_commands[action]}')
    os.chdir('..')

def run_tests(component=None):
    """Run tests for backend or frontend"""
    if component == 'backend':
        os.chdir('backend')
        run_command('. venv/bin/activate && pytest')
        os.chdir('..')
    elif component == 'frontend':
        os.chdir('frontend')
        run_command('npm test')
        os.chdir('..')
    else:
        # Run all tests
        run_tests('backend')
        run_tests('frontend')

def lint_code(component=None):
    """Run linters for backend or frontend"""
    if component == 'backend':
        os.chdir('backend')
        run_command('. venv/bin/activate && black . && flake8 . && mypy .')
        os.chdir('..')
    elif component == 'frontend':
        os.chdir('frontend')
        run_command('npm run lint')
        os.chdir('..')
    else:
        # Lint all
        lint_code('backend')
        lint_code('frontend')

def docker_build():
    """Build Docker containers"""
    run_command('docker-compose build')

def docker_up(detached=False):
    """Start Docker containers"""
    command = 'docker-compose up' + (' -d' if detached else '')
    run_command(command)

def docker_down():
    """Stop and remove Docker containers"""
    run_command('docker-compose down')

def generate_env_files():
    """Generate .env files from .env.example if they don't exist"""
    for directory in ['frontend', 'backend']:
        env_example = os.path.join(directory, '.env.example')
        env_file = os.path.join(directory, '.env')
        
        if os.path.exists(env_example) and not os.path.exists(env_file):
            shutil.copy(env_example, env_file)
            print(f"{GREEN}Created {env_file} from {env_example}{NC}")

def security_scan():
    """Run security scans on dependencies"""
    print(f"{YELLOW}Running security scans...{NC}")
    
    # Backend dependency scan
    os.chdir('backend')
    run_command('. venv/bin/activate && safety check')
    os.chdir('..')
    
    # Frontend dependency scan
    os.chdir('frontend')
    run_command('npm audit')
    os.chdir('..')

def main():
    parser = argparse.ArgumentParser(description='DivergesApp Management Script')
    
    # Migration commands
    parser.add_argument('--migrate', choices=['upgrade', 'downgrade', 'generate', 'history'], 
                        help='Run database migrations')
    
    # Test commands
    parser.add_argument('--test', choices=['backend', 'frontend', 'all'], 
                        help='Run tests')
    
    # Lint commands
    parser.add_argument('--lint', choices=['backend', 'frontend', 'all'], 
                        help='Run code linters')
    
    # Docker commands
    parser.add_argument('--docker', choices=['build', 'up', 'down', 'up-detached'], 
                        help='Docker management commands')
    
    # Environment setup
    parser.add_argument('--init', action='store_true', 
                        help='Initialize project environment')
    
    # Security scan
    parser.add_argument('--security-scan', action='store_true', 
                        help='Run security dependency scans')
    
    args = parser.parse_args()
    
    if args.init:
        generate_env_files()
        setup_backend_env()
    
    if args.migrate:
        run_migrations(args.migrate)
    
    if args.test:
        run_tests(args.test)
    
    if args.lint:
        lint_code(args.lint)
    
    if args.docker:
        if args.docker == 'build':
            docker_build()
        elif args.docker == 'up':
            docker_up()
        elif args.docker == 'up-detached':
            docker_up(detached=True)
        elif args.docker == 'down':
            docker_down()
    
    if args.security_scan:
        security_scan()

if __name__ == '__main__':
    main()
