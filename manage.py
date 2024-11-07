#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

# Color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

def print_success(message):
    print(f"{GREEN}{message}{NC}")

def print_warning(message):
    print(f"{YELLOW}{message}{NC}")

def print_error(message):
    print(f"{RED}{message}{NC}")

def run_command(command, cwd=None, env=None):
    """Run a shell command with optional working directory and environment"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            cwd=cwd, 
            env=env or os.environ.copy(),
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        print_success(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        print_error(f"STDOUT: {e.stdout}")
        print_error(f"STDERR: {e.stderr}")
        sys.exit(1)

def setup_backend_env():
    """Set up backend virtual environment"""
    os.chdir('backend')
    
    # Create virtual environment if not exists
    if not os.path.exists('venv'):
        run_command('python3 -m venv venv')
    
    # Activate virtual environment and install dependencies
    run_command('. venv/bin/activate && pip install -r requirements.txt')
    
    os.chdir('..')

def run_migrations(action='upgrade'):
    """Run database migrations"""
    setup_backend_env()
    os.chdir('backend')
    
    migration_commands = {
        'upgrade': 'alembic upgrade head',
        'downgrade': 'alembic downgrade -1',
        'generate': 'alembic revision --autogenerate -m "Auto-generated migration"',
        'history': 'alembic history'
    }
    
    if action not in migration_commands:
        print_error(f"Invalid migration action: {action}")
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
    
    args = parser.parse_args()
    
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

if __name__ == '__main__':
    main()
