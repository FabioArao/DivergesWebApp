# Contributing to DivergesApp

## Welcome!

We're thrilled that you're interested in contributing to DivergesApp. This document provides guidelines for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others. Harassment and discrimination are not tolerated.

## How to Contribute

### Reporting Bugs

1. Check existing issues to ensure the bug hasn't been reported
2. Use the issue template
3. Provide detailed information:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details

### Feature Requests

1. Check existing issues for similar requests
2. Clearly describe the feature
3. Explain the use case and potential benefits

## Development Process

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker
- Firebase Account

### Setup

1. Fork the repository
2. Clone your fork
3. Create a virtual environment
4. Install dependencies
5. Set up environment variables

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Making Changes

1. Create a new branch
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
   - Follow existing code style
   - Add tests for new functionality
   - Ensure all tests pass

3. Commit your changes
```bash
git add .
git commit -m "Description of changes"
```

### Code Style

#### Backend (Python)
- Use Black for formatting
- Follow PEP 8 guidelines
- Type hints are required
- Docstrings for all functions and classes

```bash
# Format code
black .
# Type checking
mypy .
# Lint
flake8
```

#### Frontend (TypeScript/React)
- Use ESLint and Prettier
- Follow React best practices
- Use TypeScript with strict mode

```bash
# Format and lint
npm run lint
npm run format
```

### Testing

#### Backend
- Use pytest for testing
- Aim for high test coverage
```bash
pytest
```

#### Frontend
- Use Jest and React Testing Library
```bash
npm test
```

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Squash commits
4. Use descriptive PR title and description
5. Link to related issues

### Review Process

- PRs require review from maintainers
- Be open to feedback
- Discussions should be constructive

## Security

- Do not commit sensitive information
- Report security issues privately
- Use environment variables for secrets

## Communication

- Join our Discord/Slack channel
- Use GitHub issues for tracked discussions
- Be patient and respectful

## Financial Contributions

Support the project via:
- GitHub Sponsors
- Open Collective
- Individual donations

## Thank You!

Your contributions make open source amazing. Thank you for your help!
