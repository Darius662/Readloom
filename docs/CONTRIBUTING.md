# Contributing to MangaArr

Thank you for your interest in contributing to MangaArr! We welcome contributions from everyone, regardless of experience level.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Workflow](#workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/MangARR.git
   cd MangARR
   ```
3. **Set up the upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/MangARR.git
   ```
4. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Environment

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the development server:
   ```bash
   python run_dev.py
   ```

3. Access the application at http://localhost:7227

## Workflow

1. **Keep your fork updated**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a new branch** for each feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and commit them with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description of the feature"
   ```

4. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** from your fork to the main repository.

## Pull Request Process

1. **Update the README.md** if necessary with details of changes.
2. **Add tests** for new functionality.
3. **Ensure all tests pass**.
4. **Update documentation** if necessary.
5. **Submit your pull request** with a clear title and description.
6. **Respond to feedback** from maintainers.

## Coding Standards

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
- Use 4 spaces for indentation (not tabs).
- Maximum line length of 100 characters.
- Include docstrings for all functions, classes, and modules.
- Use descriptive variable names.

### JavaScript

- Follow [Standard JS](https://standardjs.com/) style.
- Use 2 spaces for indentation.
- Use semicolons.
- Use camelCase for variable and function names.

### HTML/CSS

- Use 2 spaces for indentation.
- Use lowercase for HTML element names, attributes, and values.
- Use kebab-case for CSS class names.

## Testing

- Write tests for all new functionality.
- Run tests before submitting a pull request:
  ```bash
  python -m pytest
  ```
- Aim for high test coverage.

## Documentation

- Update documentation when adding or changing features.
- Use clear, concise language.
- Include examples where appropriate.
- Follow Markdown best practices.

## Community

- Join our [Discord server](https://discord.gg/mangarr) for discussions.
- Check the [GitHub Issues](https://github.com/ORIGINAL-OWNER/MangARR/issues) for tasks to work on.
- Help answer questions in issues and discussions.

Thank you for contributing to MangaArr!
