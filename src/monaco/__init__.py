"""Minimal Project Task Forecasting."""

# Import order matters: task must come before project to avoid circular imports
from monaco.task import *  # noqa: E402, F401
from monaco.project import *  # noqa: E402, F401

__version__ = "0.1.2"
