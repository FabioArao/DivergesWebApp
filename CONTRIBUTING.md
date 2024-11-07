# Contributing to DivergesApp

## Welcome Contributors!

We're excited that you're interested in contributing to DivergesApp. This document provides guidelines for contributing to the project.

## Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing. We are committed to providing a welcoming and inspiring community for all.

## How to Contribute

### Reporting Bugs

1. Check existing issues to ensure the bug hasn't been reported
2. Use the bug report template when creating a new issue
3. Provide detailed information:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details (OS, Python/Node.js version, etc.)

### Feature Requests

1. Check existing issues for similar requests
2. Use the feature request template
3. Clearly describe:
   - The problem you're solving
   - Proposed solution
   - Potential implementation approach

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Node.js 18+
- Firebase Account

### Local Development

1. Fork the repository
2. Clone your fork
3. Create environment files
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

4. Set up Firebase configuration in both .env files

5. Use the management script for setup
```bash
# Initialize project
python manage.py --init

# Run tests
python manage.py --test all

# Run linters
python manage.py --lint all
```

### Docker Development
```bash
# Build and start containers
python manage.py --docker up
```

## Coding Standards

### Backend (Python)
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- Use Black for formatting
- Use Mypy for type checking

### Frontend (TypeScript/React)
- Follow React best practices
- Use TypeScript with strict mode
- Write clear, concise components
- Use ESLint and Prettier
- Write unit tests for components

### Commit Guidelines
- Use conventional commits
- Prefix commits:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `style:` for formatting changes
  - `refactor:` for code restructuring
  - `test:` for test-related changes
  - `chore:` for maintenance tasks

## Pull Request Process

1. Create a feature branch
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
   - Follow coding standards
   - Add/update tests
   - Ensure all tests pass

3. Commit your changes
```bash
git add .
git commit -m "feat: describe your feature"
```

4. Push to your fork
```bash
git push origin feature/your-feature-name
```

5. Open a Pull Request
   - Use the PR template
   - Describe changes clearly
   - Link related issues

## Code Review Process

- All contributions require review
- Maintainers will provide constructive feedback
- Be open to suggestions and collaborative improvement

## Testing

### Backend Testing
```bash
# Run all backend tests
python manage.py --test backend

# Run specific test
pytest backend/tests/specific_test.py
```

### Frontend Testing
```bash
# Run all frontend tests
python manage.py --test frontend

# Run specific test
npm test -- -t "specific test name"
```

## Security

- Do not commit sensitive information
- Report security issues privately
- Use environment variables for secrets

## Documentation

- Update README if your changes affect setup/usage
- Add/update docstrings and comments
- Keep documentation clear and concise

## Financial Contributions

Support the project:
- GitHub Sponsors
- Open Collective
- Individual donations

## Questions?

- Open an issue
- Join our community discussions

## Thank You!

Your contributions make open source amazing. Thank you for your help!
