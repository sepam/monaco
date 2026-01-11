# Documentation Improvement Execution Plan

This document outlines the execution strategy and evaluation framework for addressing documentation gaps in the Monaco codebase.

---

## Table of Contents

1. [Evaluation Framework](#evaluation-framework)
2. [Baseline Metrics](#baseline-metrics)
3. [Execution Phases](#execution-phases)
4. [Module-Specific Plans](#module-specific-plans)
5. [Verification Checklists](#verification-checklists)
6. [Success Criteria](#success-criteria)

---

## Evaluation Framework

### Documentation Quality Dimensions

We will evaluate documentation across 5 dimensions:

| Dimension | Description | Weight |
|-----------|-------------|--------|
| **Completeness** | All public APIs have docstrings | 30% |
| **Clarity** | Documentation is understandable without reading source | 25% |
| **Examples** | Code examples provided for complex functionality | 20% |
| **Consistency** | Uniform style across all modules | 15% |
| **Accuracy** | Documentation matches actual behavior | 10% |

### Scoring Rubric (1-5 scale)

| Score | Meaning |
|-------|---------|
| 1 | Missing - No documentation |
| 2 | Minimal - One-line description only |
| 3 | Basic - Parameters documented, no examples |
| 4 | Good - Full docstring with examples |
| 5 | Excellent - Comprehensive with edge cases, links, and examples |

---

## Baseline Metrics

### Current State Assessment

| Module | Completeness | Clarity | Examples | Consistency | Accuracy | **Weighted Score** |
|--------|--------------|---------|----------|-------------|----------|-------------------|
| `distributions.py` | 5 | 5 | 4 | 5 | 5 | **4.8** |
| `task.py` | 3 | 3 | 3 | 4 | 5 | **3.4** |
| `project.py` | 2 | 3 | 3 | 3 | 5 | **2.9** |
| `config.py` | 3 | 3 | 2 | 4 | 5 | **3.2** |
| `cli.py` | 4 | 4 | 3 | 4 | 5 | **3.9** |
| `__init__.py` | 1 | 2 | 1 | 3 | 5 | **1.9** |
| Tests | 2 | 3 | N/A | 2 | 5 | **2.6** |

**Overall Baseline Score: 3.2 / 5.0**

### Target State

| Module | Target Score | Improvement Needed |
|--------|-------------|-------------------|
| `distributions.py` | 4.8 (maintain) | None |
| `task.py` | 4.5 | +1.1 |
| `project.py` | 4.5 | +1.6 |
| `config.py` | 4.2 | +1.0 |
| `cli.py` | 4.2 | +0.3 |
| `__init__.py` | 4.5 | +2.6 |
| Tests | 3.5 | +0.9 |

**Target Overall Score: 4.3 / 5.0 (+1.1 improvement)**

---

## Execution Phases

### Phase 1: High Priority (Core Modules)

**Scope:** `project.py`, `__init__.py`

#### 1.1 `project.py` Documentation

**Tasks:**
1. Add module-level docstring
2. Expand `Project.__init__` docstring
3. Document graph algorithms with inline comments
4. Add docstrings to undocumented private methods

**Execution Steps:**

```
Step 1.1.1: Module Docstring
- Location: Line 1
- Content: Purpose, relationship to Task, key features
- Estimated lines: 15-20

Step 1.1.2: Project.__init__ Expansion
- Location: Lines 16-35
- Add: Conceptual explanation, inheritance note, usage patterns
- Estimated addition: 10-15 lines

Step 1.1.3: Algorithm Documentation
- _validate_dag(): Add DFS cycle detection explanation
- _topological_sort(): Document Kahn's algorithm
- _calculate_critical_path(): Explain forward/backward pass
- Estimated comments: 20-30 lines total

Step 1.1.4: Private Method Docstrings
- _has_dependencies()
- tasks property
- Estimated addition: 5-10 lines
```

**Testing:**
- Run `python -c "from monaco import Project; help(Project)"`
- Verify all methods appear in help output
- Check docstring renders correctly in IDE tooltips

#### 1.2 `__init__.py` Documentation

**Tasks:**
1. Add comprehensive module docstring
2. Document public API
3. Add quick-start examples

**Execution Steps:**

```
Step 1.2.1: Package Docstring
- Purpose and overview
- Main classes (Distribution, Task, Project)
- Quick usage example
- Version info
- Estimated lines: 40-50

Step 1.2.2: Public API Documentation
- List all exported symbols
- Brief description of each
- Estimated lines: 10-15
```

**Testing:**
- Run `python -c "import monaco; help(monaco)"`
- Verify package docstring displays correctly
- Check `monaco.__doc__` is not None

---

### Phase 2: Medium Priority

**Scope:** `task.py`, `config.py`, Tests

#### 2.1 `task.py` Documentation

**Tasks:**
1. Expand module docstring
2. Add inline comments for initialization logic
3. Document relationship with Distribution

**Execution Steps:**

```
Step 2.1.1: Module Docstring Expansion
- Explain Task concept in project planning
- Document legacy vs modern initialization
- Estimated addition: 15-20 lines

Step 2.1.2: Inline Comments
- Distribution initialization branching logic
- Estimator selection logic
- Estimated addition: 10 lines
```

**Testing:**
- Run `python -c "from monaco import Task; help(Task)"`
- Verify examples in docstrings are executable

#### 2.2 `config.py` Documentation

**Tasks:**
1. Document `_validate_config()` validation rules
2. Add inline comments for recursive dependency resolution
3. Expand `ConfigError` with examples

**Execution Steps:**

```
Step 2.2.1: Validation Rules Documentation
- List all validation checks performed
- Document error messages
- Estimated addition: 20-25 lines

Step 2.2.2: Inline Comments
- build_project_from_config() recursion
- add_task_with_deps() inner function
- Estimated addition: 10-15 lines
```

**Testing:**
- Trigger each validation error and verify messages are helpful
- Run `python -c "from monaco.config import load_config; help(load_config)"`

#### 2.3 Test Documentation

**Tasks:**
1. Add docstrings to all test functions
2. Follow consistent format

**Execution Steps:**

```
Step 2.3.1: test_project.py
- 6 tests missing docstrings
- Format: "Test that [condition] results in [expected behavior]"

Step 2.3.2: test_task.py
- Add docstrings to all test functions

Step 2.3.3: test_distributions.py
- Add docstrings to all test functions

Step 2.3.4: test_config.py
- Add docstrings to all test functions

Step 2.3.5: test_cli.py
- Add docstrings to all test functions
```

**Testing:**
- Run `pytest --collect-only` and verify test descriptions
- Run `pytest -v` to see test names are descriptive

---

### Phase 3: Low Priority & New Files

**Scope:** `cli.py` minor improvements, new documentation files

#### 3.1 `cli.py` Minor Improvements

**Tasks:**
1. Expand `_print_stats()` docstring

#### 3.2 New Documentation Files

**Tasks:**
1. Create `CHANGELOG.md`
2. Create `CONTRIBUTING.md` (optional)

---

## Module-Specific Plans

### `project.py` Detailed Plan

```python
# BEFORE (Line 1)
from collections import Counter
from typing import Any, Dict, List, Optional, Set, Tuple
...

# AFTER (Line 1)
"""
Project module for managing task collections with dependencies.

This module provides the Project class, which extends Task to represent
a collection of tasks that can have dependencies between them. Projects
support Monte Carlo simulation for estimating completion times while
accounting for uncertainty in task durations.

Key Features:
    - Task dependency management (DAG-based)
    - Critical path analysis
    - Monte Carlo simulation with configurable iterations
    - Statistical analysis (mean, median, percentiles, confidence intervals)
    - Visualization (histograms, cumulative distributions, dependency graphs)

The Project class uses a Directed Acyclic Graph (DAG) to model task
dependencies. When dependencies are specified, the critical path method
is used to calculate project duration. Without dependencies, tasks are
assumed to be sequential (backward compatibility).

Example:
    >>> from monaco import Project, Task
    >>> backend = Task(name="Backend", min_duration=10, mode_duration=15, max_duration=20)
    >>> frontend = Task(name="Frontend", min_duration=8, mode_duration=12, max_duration=15)
    >>> integration = Task(name="Integration", min_duration=2, mode_duration=3, max_duration=5)
    >>>
    >>> project = Project(name="Web App")
    >>> project.add_task(backend)
    >>> project.add_task(frontend)
    >>> project.add_task(integration, depends_on=[backend, frontend])
    >>>
    >>> stats = project.statistics(n=10000)
    >>> print(f"Expected duration: {stats['mean']:.1f} days")

See Also:
    Task: Individual task with probabilistic duration
    Distribution: Probability distributions for modeling uncertainty
"""
from collections import Counter
...
```

### `__init__.py` Detailed Plan

```python
# BEFORE
"""Minimal Project Task Forecasting."""

# AFTER
"""
Monaco: Probabilistic Project Planning with Monte Carlo Simulation.

Monaco is a Python library for estimating project completion times using
Monte Carlo simulation. It models task durations as probability distributions
and calculates project timelines while accounting for uncertainty and
task dependencies.

Main Components:
    Distribution classes:
        - TriangularDistribution: Three-point estimate (min, mode, max)
        - UniformDistribution: Equal probability between bounds
        - NormalDistribution: Gaussian with optional truncation
        - PERTDistribution: Smooth triangular (Program Evaluation Review Technique)
        - LogNormalDistribution: Right-skewed for modeling delays
        - BetaDistribution: Flexible shape with alpha/beta parameters

    Task:
        Represents a single task with probabilistic duration.

    Project:
        Collection of tasks with optional dependencies. Supports Monte Carlo
        simulation and critical path analysis.

Quick Start:
    >>> from monaco import Project, Task, TriangularDistribution
    >>>
    >>> # Create tasks with uncertainty
    >>> task1 = Task(name="Design", min_duration=5, mode_duration=7, max_duration=14)
    >>> task2 = Task(name="Build", min_duration=10, mode_duration=15, max_duration=25)
    >>>
    >>> # Create project and add tasks
    >>> project = Project(name="My Project")
    >>> project.add_task(task1)
    >>> project.add_task(task2, depends_on=[task1])
    >>>
    >>> # Run simulation and get statistics
    >>> stats = project.statistics(n=10000)
    >>> print(f"P85 estimate: {stats['percentiles']['p85']:.1f} days")

Configuration:
    Projects can also be defined via YAML configuration files.
    See monaco.config for loading configurations.

Command Line:
    Monaco provides a CLI tool for running simulations:

    $ monaco init          # Create template config
    $ monaco run config.yaml   # Run simulation
    $ monaco stats config.yaml # Show statistics
    $ monaco plot config.yaml  # Generate visualization

Version: 0.1.2
License: MIT
"""
```

---

## Verification Checklists

### Pre-Implementation Checklist

- [ ] Read current documentation for the module
- [ ] Identify all public APIs (classes, functions, methods)
- [ ] Note existing docstring style for consistency
- [ ] Review related modules for cross-references

### Post-Implementation Checklist

#### For Each Module:

- [ ] **Completeness**
  - [ ] Module has docstring
  - [ ] All public classes have docstrings
  - [ ] All public methods have docstrings
  - [ ] All public functions have docstrings
  - [ ] Complex private methods have docstrings

- [ ] **Clarity**
  - [ ] Purpose is clear without reading implementation
  - [ ] Parameters are documented with types
  - [ ] Return values are documented
  - [ ] Exceptions/raises are documented

- [ ] **Examples**
  - [ ] At least one usage example per class
  - [ ] Examples are executable (copy-paste works)
  - [ ] Edge cases mentioned where relevant

- [ ] **Consistency**
  - [ ] Follows Google/NumPy docstring style
  - [ ] Consistent formatting with other modules
  - [ ] Cross-references use consistent format

- [ ] **Accuracy**
  - [ ] Docstrings match actual behavior
  - [ ] Examples produce documented output
  - [ ] No outdated information

### Automated Verification

```bash
# 1. Check all modules have docstrings
python -c "
import monaco
from monaco import distributions, task, project, config, cli

modules = [monaco, distributions, task, project, config, cli]
for m in modules:
    assert m.__doc__, f'{m.__name__} missing docstring'
    print(f'✓ {m.__name__} has docstring')
"

# 2. Check all public classes have docstrings
python -c "
from monaco import (
    Distribution, TriangularDistribution, UniformDistribution,
    NormalDistribution, PERTDistribution, LogNormalDistribution,
    BetaDistribution, Task, Project
)

classes = [
    Distribution, TriangularDistribution, UniformDistribution,
    NormalDistribution, PERTDistribution, LogNormalDistribution,
    BetaDistribution, Task, Project
]

for cls in classes:
    assert cls.__doc__, f'{cls.__name__} missing docstring'
    assert len(cls.__doc__) > 50, f'{cls.__name__} docstring too short'
    print(f'✓ {cls.__name__} has adequate docstring ({len(cls.__doc__)} chars)')
"

# 3. Check key methods have docstrings
python -c "
from monaco import Project

methods = [
    'add_task', 'estimate', 'statistics',
    'get_critical_path_analysis', 'export_results', 'plot'
]

for method_name in methods:
    method = getattr(Project, method_name)
    assert method.__doc__, f'Project.{method_name} missing docstring'
    print(f'✓ Project.{method_name} has docstring')
"

# 4. Verify examples are executable
python -c "
# Test example from __init__.py docstring
from monaco import Project, Task

task1 = Task(name='Design', min_duration=5, mode_duration=7, max_duration=14)
task2 = Task(name='Build', min_duration=10, mode_duration=15, max_duration=25)

project = Project(name='My Project')
project.add_task(task1)
project.add_task(task2, depends_on=[task1])

stats = project.statistics(n=1000)
assert 'percentiles' in stats
assert 'p85' in stats['percentiles']
print('✓ Package docstring example executes correctly')
"

# 5. Run doctest on modules (if doctests added)
python -m doctest -v src/monaco/project.py
python -m doctest -v src/monaco/task.py
```

### Manual Verification

1. **IDE Tooltip Test**
   - Open each module in VS Code/PyCharm
   - Hover over classes and methods
   - Verify tooltips show useful documentation

2. **Help Function Test**
   - Run `help(monaco)` in Python REPL
   - Run `help(Project)`, `help(Task)`, etc.
   - Verify output is comprehensive and readable

3. **New User Test**
   - Can someone understand the module's purpose from docstring alone?
   - Are examples clear enough to get started?

---

## Success Criteria

### Quantitative Metrics

| Metric | Current | Target | How to Measure |
|--------|---------|--------|----------------|
| Modules with docstrings | 5/7 (71%) | 7/7 (100%) | `module.__doc__ is not None` |
| Public classes with docstrings | 9/9 (100%) | 9/9 (100%) | Maintain |
| Public methods with docstrings | ~85% | 100% | Manual audit |
| Docstring avg length | ~150 chars | >250 chars | Script measurement |
| Modules with examples | 3/7 (43%) | 7/7 (100%) | Check for `>>>` in docstring |
| Test functions with docstrings | ~40% | 100% | `pytest --collect-only` |
| Weighted quality score | 3.2/5.0 | 4.3/5.0 | Rubric assessment |

### Qualitative Criteria

1. **Self-Sufficiency**: A developer can understand and use any public API by reading only its docstring
2. **Discoverability**: `help(monaco)` provides a complete overview of the package
3. **Executable Examples**: All code examples in docstrings run without modification
4. **Algorithm Clarity**: Graph algorithms have inline comments explaining the approach

### Definition of Done

A module's documentation is considered complete when:

1. ✅ Module docstring explains purpose and key features
2. ✅ All public classes have docstrings with Parameters section
3. ✅ All public methods have docstrings with Parameters, Returns, Raises
4. ✅ At least one executable example per class
5. ✅ Complex algorithms have inline comments
6. ✅ Automated verification script passes
7. ✅ Manual IDE tooltip check passes
8. ✅ Weighted quality score ≥ 4.0

---

## Execution Order

```
Week 1: Phase 1 (High Priority)
├── Day 1-2: project.py documentation
│   ├── Module docstring
│   ├── Project.__init__ expansion
│   └── Algorithm comments
├── Day 3: __init__.py documentation
│   ├── Package docstring
│   └── Public API documentation
└── Day 4-5: Verification & refinement

Week 2: Phase 2 (Medium Priority)
├── Day 1: task.py documentation
├── Day 2: config.py documentation
├── Day 3-4: Test documentation
└── Day 5: Verification & refinement

Week 3: Phase 3 (Low Priority) + Final
├── Day 1: cli.py minor improvements
├── Day 2: CHANGELOG.md creation
├── Day 3-4: Final verification
└── Day 5: Documentation review & sign-off
```

---

## Rollback Plan

If documentation changes introduce issues:

1. Each phase will be committed separately
2. Commits will be atomic (one module per commit)
3. All changes are additive (no code logic changes)
4. Easy to revert individual modules if needed

---

## Appendix: Documentation Style Guide

### Docstring Format (Google Style)

```python
def function_name(param1: str, param2: int = 10) -> bool:
    """Short one-line description.

    Longer description if needed. Can span multiple lines and include
    details about the function's behavior.

    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 10.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is empty.
        TypeError: When param2 is not an integer.

    Example:
        >>> result = function_name("test", 5)
        >>> print(result)
        True

    Note:
        Additional notes about usage or implementation details.

    See Also:
        related_function: Description of relationship.
    """
```

### Class Docstring Format

```python
class ClassName:
    """Short one-line description.

    Longer description of the class purpose and behavior.

    Attributes:
        attr1: Description of attr1.
        attr2: Description of attr2.

    Example:
        >>> obj = ClassName(param1="value")
        >>> obj.method()
        'result'
    """
```

---

*Plan created: 2026-01-11*
*Target completion: After Phase 3*
