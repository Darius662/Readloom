# Changelog

All notable changes to MangaArr will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Improved documentation structure
- API documentation with endpoint descriptions and examples
- Installation guide with Docker and manual options
- Contributor guidelines and code of conduct

### Changed
- Updated development workflow for better compatibility
- Simplified package requirements for easier installation

## [0.0.1] - 2025-09-18

### Added
- Initial project structure and architecture
- Database schema for manga/comic tracking
- Basic API endpoints structure
- Simple web interface with "Coming Soon" page
- Test data generator for development
- Development environment setup script
- Docker configuration for containerization
- Basic documentation framework
- Home Assistant and Homarr integration templates

### Changed
- N/A (Initial release)

### Deprecated
- N/A (Initial release)

### Removed
- N/A (Initial release)

### Fixed
- N/A (Initial release)

### Security
- N/A (Initial release)

## How to Use This Changelog

Each version should:

- List its release date in YYYY-MM-DD format.
- Group changes to describe their impact on the project, as follows:
  - **Added** for new features.
  - **Changed** for changes in existing functionality.
  - **Deprecated** for soon-to-be removed features.
  - **Removed** for now removed features.
  - **Fixed** for any bug fixes.
  - **Security** in case of vulnerabilities.

## Release Process

1. Update the changelog with all relevant changes under the "Unreleased" section.
2. When ready to release, move the "Unreleased" changes to a new version section.
3. Tag the release in Git:
   ```bash
   git tag -a v1.2.3 -m "Release v1.2.3"
   git push origin v1.2.3
   ```
4. Create a new GitHub release with the same version number.
5. Include the changelog entries in the release notes.

## Contact

If you have questions about the changelog or release process, please contact the project maintainers.
