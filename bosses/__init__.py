"""
Boss detection and loading with auto-discovery.
"""

import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict
from .base import Boss


def _discover_bosses() -> Dict[str, Boss]:
    """
    Automatically discover and register boss classes from the bosses/ directory.

    Scans only the main bosses/ directory (NOT bosses/archived/) for Python files,
    dynamically imports them, and finds all classes that inherit from Boss.

    Returns:
        Dictionary mapping class names to boss instances.

    Raises:
        ImportError: If no boss classes are found in the directory.
    """
    boss_registry = {}

    # Get the directory path where this __init__.py file is located
    bosses_dir = Path(__file__).parent

    # Scan for .py files in the bosses/ directory (excluding __init__.py and base.py)
    for file_path in bosses_dir.glob('*.py'):
        filename = file_path.name

        # Skip special files
        if filename in ['__init__.py', 'base.py']:
            continue

        # Get module name (filename without .py extension)
        module_name = filename[:-3]

        try:
            # Dynamically import the module
            full_module_name = f'bosses.{module_name}'
            module = importlib.import_module(full_module_name)

            # Inspect the module for Boss subclasses
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                # Check if it's a class
                if inspect.isclass(attr):
                    # Check if it inherits from Boss (but is not Boss itself)
                    if issubclass(attr, Boss) and attr is not Boss:
                        # Check if it has detection_patterns attribute
                        if not hasattr(attr, 'detection_patterns'):
                            print(f"Warning: {attr.__name__} has no detection_patterns attribute, skipping",
                                  file=sys.stderr)
                            continue

                        # Validate detection_patterns format
                        patterns = attr.detection_patterns
                        if not isinstance(patterns, (list, tuple)):
                            print(f"Warning: {attr.__name__}.detection_patterns must be a list or tuple, skipping",
                                  file=sys.stderr)
                            continue

                        if not all(isinstance(p, str) for p in patterns):
                            print(f"Warning: {attr.__name__}.detection_patterns must contain only strings, skipping",
                                  file=sys.stderr)
                            continue

                        # Valid boss class found - instantiate and register it
                        try:
                            instance = attr()
                            boss_registry[attr.__name__] = instance
                        except Exception as e:
                            print(f"Warning: Failed to instantiate {attr.__name__}: {e}",
                                  file=sys.stderr)
                            continue

        except Exception as e:
            print(f"Warning: Failed to import bosses/{filename}: {e}",
                  file=sys.stderr)
            continue

    # Ensure at least one boss was found
    if not boss_registry:
        raise ImportError("No boss classes found in bosses/ directory. Ensure at least one boss class exists.")

    return boss_registry


# Discover and register all bosses at module load time
_boss_registry = _discover_bosses()


def detect_boss_from_content(content: str) -> Boss:
    """
    Detect which boss the log file is for based on content matching.

    Iterates through all discovered bosses and checks if any of their
    detection_patterns appear in the file content (case-insensitive).

    Args:
        content: The full content of the log file as a string.

    Returns:
        Boss instance for the detected boss.

    Raises:
        ValueError: If no boss matches the content.
    """
    content_lower = content.lower()

    # Check each registered boss for pattern matches
    for boss_name, boss_instance in _boss_registry.items():
        for pattern in boss_instance.detection_patterns:
            if pattern.lower() in content_lower:
                return boss_instance

    # No boss matched
    raise ValueError("Could not detect boss from log file content. No matching boss patterns found.")
