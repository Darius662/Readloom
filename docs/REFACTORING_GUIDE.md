# MangaArr Refactoring Guide

This document provides guidelines and best practices for refactoring code in the MangaArr project, based on the recent modularization effort.

## Why Refactor?

Refactoring is the process of restructuring existing code without changing its external behavior. The main goals are:

1. **Improved maintainability**: Smaller, focused modules are easier to understand and modify
2. **Better organization**: Related functionality is grouped together
3. **Reduced complexity**: Breaking down large files into smaller components
4. **Enhanced testability**: Isolated components are easier to test
5. **Better separation of concerns**: Each module has a clear responsibility

## Refactoring Patterns

### Package-Based Modularization

The primary pattern used in MangaArr is package-based modularization:

1. **Identify a large module** that needs refactoring
2. **Create a package** with the same name as the module
3. **Split functionality** into smaller, focused files within the package
4. **Create an `__init__.py`** that re-exports the public API
5. **Create a compatibility shim** with the original filename that imports from the package

Example:
```
# Before
notifications.py (600+ lines)

# After
notifications/
  __init__.py         # Re-exports public API
  schema.py           # Database schema
  notifications.py    # Core notification logic
  subscriptions.py    # Subscription management
  settings.py         # Settings management
  channels.py         # Notification channels
  releases.py         # Release notifications
notifications.py      # Compatibility shim
```

### Compatibility Shims

To maintain backward compatibility, create a shim file with the original module name that re-exports from the new package:

```python
# notifications.py (compatibility shim)
from backend.features.notifications import (
    setup_notifications_tables,
    create_notification,
    get_notifications,
    # ... other exports
)

__all__ = [
    "setup_notifications_tables",
    "create_notification",
    "get_notifications",
    # ... other exports
]
```

This ensures that existing code can continue to import from the original module path.

## Step-by-Step Refactoring Process

1. **Analyze the module**:
   - Identify logical groupings of functions
   - Look for natural separation points
   - Identify the public API

2. **Plan the package structure**:
   - Decide on file names based on responsibilities
   - Plan what goes in each file
   - Define the public API to be exported

3. **Create the package directory and files**:
   - Create the package directory
   - Create empty files for each module
   - Create an `__init__.py` file

4. **Move code to appropriate files**:
   - Move related functions to their respective files
   - Update imports within the package
   - Fix any circular dependencies

5. **Create the `__init__.py` file**:
   - Import all public functions, classes, and constants
   - Re-export them using `__all__`

6. **Create the compatibility shim**:
   - Create a file with the original module name
   - Import all public items from the package
   - Re-export them using `__all__`

7. **Test thoroughly**:
   - Verify that all functionality works as before
   - Check that imports from both the original module and the new package work

## Best Practices

1. **Single Responsibility Principle**: Each module should have one clear responsibility
2. **Consistent Naming**: Use consistent naming conventions for files and modules
3. **Minimize Dependencies**: Reduce dependencies between modules
4. **Clear Public API**: Clearly define what is part of the public API
5. **Comprehensive Documentation**: Document the purpose of each module
6. **Backward Compatibility**: Maintain backward compatibility through shims
7. **Test Coverage**: Ensure good test coverage for refactored code

## Example: Refactoring a Provider

Here's an example of refactoring a metadata provider:

1. **Identify components**:
   - API client functionality
   - Constants and URLs
   - Data mapping/transformation
   - Provider implementation

2. **Create package structure**:
   ```
   provider_name/
     __init__.py       # Re-exports Provider class
     client.py         # API client functionality
     constants.py      # Constants and URLs
     mapper.py         # Data mapping functions
     provider.py       # Provider implementation
   provider_name.py    # Compatibility shim
   ```

3. **Move code to appropriate files**:
   - Move API client code to `client.py`
   - Move constants to `constants.py`
   - Move data mapping to `mapper.py`
   - Move provider implementation to `provider.py`

4. **Create `__init__.py`**:
   ```python
   from .provider import ProviderName

   __all__ = ["ProviderName"]
   ```

5. **Create compatibility shim**:
   ```python
   from .provider_name.provider import ProviderName

   __all__ = ["ProviderName"]
   ```

## Conclusion

Refactoring is an ongoing process that improves code quality over time. By following these guidelines, you can contribute to making MangaArr's codebase more maintainable, extensible, and easier to understand.
