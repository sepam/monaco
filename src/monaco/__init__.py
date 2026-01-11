"""Minimal Project Task Forecasting."""

# Import order matters: distributions -> task -> project to avoid circular imports
from monaco.distributions import (
    BetaDistribution,
    Distribution,
    LogNormalDistribution,
    NormalDistribution,
    PERTDistribution,
    TriangularDistribution,
    UniformDistribution,
)
from monaco.task import Task
from monaco.project import Project

__version__ = "0.1.2"

__all__ = [
    # Core classes
    "Project",
    "Task",
    # Distribution base
    "Distribution",
    # Distribution types
    "BetaDistribution",
    "LogNormalDistribution",
    "NormalDistribution",
    "PERTDistribution",
    "TriangularDistribution",
    "UniformDistribution",
    # Version
    "__version__",
]
