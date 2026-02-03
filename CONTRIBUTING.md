# Contributing to GalacticNeighborsFinder

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Be respectful and inclusive in all interactions. We welcome contributions from researchers of all backgrounds and experience levels.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. **Check existing issues** to avoid duplicates
2. **Create a detailed report** including:
   - Clear description of the problem
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Python version, OS, and package versions
   - Minimal code example if applicable

### Submitting Changes

1. **Fork the repository** and create a feature branch:
   ```bash
   git clone https://github.com/YOUR_USERNAME/GalacticNeighborsFinder.git
   cd GalacticNeighborsFinder
   git checkout -b feature/your-feature-name
   ```

2. **Set up development environment:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Make your changes:**
   - Follow PEP 8 style guidelines
   - Add docstrings to new functions and classes
   - Include type hints for all new code
   - Write tests for new functionality

4. **Run tests and linting:**
   ```bash
   # Run tests
   pytest
   
   # Check code style
   black --check gnf/
   flake8 gnf/
   isort --check gnf/
   ```

5. **Format code:**
   ```bash
   black gnf/
   isort gnf/
   ```

6. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Clear description of changes"
   ```

7. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub with:
   - Clear title describing the changes
   - Description of what was changed and why
   - Reference to any related issues

## Development Guidelines

### Code Style

- Use Python 3.8+ features
- Follow PEP 8 guidelines
- Use type hints consistently
- Write clear, descriptive variable and function names
- Maximum line length: 100 characters

### Testing

- Write tests for all new functionality
- Aim for >80% code coverage
- Use pytest for testing framework
- Place tests in `tests/` directory with `test_*.py` naming

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include parameter descriptions, return types, and examples
- Update README if adding new features

### Commit Messages

- Use clear, descriptive messages
- Start with a verb (Add, Fix, Improve, etc.)
- Keep first line under 50 characters
- Reference issues when relevant: "Fixes #123"

## Project Structure

```
gnf/
├── core/              # Core functionality
├── config/            # Configuration management
├── utils/             # Utilities and validators
├── cli.py             # Command-line interface
├── constants.py       # Global constants
└── __init__.py        # Package init

tests/                 # Unit tests
examples/              # Example scripts and configs
docs/                  # Documentation (if added)
```

## Testing Commands

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=gnf --cov-report=html

# Run specific test file
pytest tests/test_validators.py

# Run with verbose output
pytest -v

# Run tests in parallel (faster)
pytest -n auto
```

## Questions?

- Check existing GitHub issues and discussions
- Review the README and example scripts
- Look at existing code for patterns and conventions

## Recognition

Contributors will be acknowledged in:
- Project README
- Release notes
- Contributors file (if added)

Thank you for making GalacticNeighborsFinder better!
