# Contributing to MangaArr

Thank you for your interest in contributing to MangaArr! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

- Check the issue tracker to see if the bug has already been reported
- If not, create a new issue with a clear title and description
- Include steps to reproduce the bug
- Include screenshots if applicable
- Include your environment information (OS, browser, etc.)

### Suggesting Features

- Check the issue tracker to see if the feature has already been suggested
- If not, create a new issue with a clear title and description
- Explain why this feature would be useful to most MangaArr users

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Submit a pull request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/MangaArr.git
   cd MangaArr
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   python run_dev.py
   ```

## Project Structure

- `MangaArr.py`: Main application entry point
- `backend/`: Backend code
  - `base/`: Base definitions and helpers
  - `features/`: Feature implementations
  - `internals/`: Internal components (database, server, settings)
- `frontend/`: Frontend code
  - `api.py`: API endpoints
  - `ui.py`: UI routes
  - `templates/`: HTML templates
  - `static/`: Static files (CSS, JS, images)
- `tests/`: Test code

## Coding Style

- Follow PEP 8 for Python code
- Use 4 spaces for indentation
- Use descriptive variable names
- Write docstrings for all functions, classes, and modules
- Keep lines under 100 characters

## Testing

- Run tests before submitting a pull request
- Add tests for new features
- Ensure all tests pass

## Documentation

- Update documentation when changing or adding features
- Write clear and concise documentation
- Include examples when appropriate

## License

By contributing to MangaArr, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
