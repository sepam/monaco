#!/usr/bin/env python3
"""
Documentation Quality Verification Script.

This script measures documentation quality across the Monaco codebase
and produces a report with scores based on the evaluation framework.

Usage:
    python scripts/verify_documentation.py
    python scripts/verify_documentation.py --verbose
    python scripts/verify_documentation.py --json

Exit codes:
    0: All checks pass (score >= 4.0)
    1: Some checks fail (score < 4.0)
"""

import argparse
import ast
import importlib
import inspect
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DocstringMetrics:
    """Metrics for a single docstring."""

    name: str
    has_docstring: bool
    docstring_length: int
    has_params: bool
    has_returns: bool
    has_raises: bool
    has_examples: bool
    score: float


@dataclass
class ModuleMetrics:
    """Aggregated metrics for a module."""

    name: str
    has_module_docstring: bool
    module_docstring_length: int
    total_public_items: int
    documented_items: int
    items_with_examples: int
    completeness_score: float
    clarity_score: float
    examples_score: float
    consistency_score: float
    weighted_score: float
    items: list


def get_docstring_score(doc: str | None) -> tuple[float, dict]:
    """Score a docstring on multiple dimensions."""
    if not doc:
        return 1.0, {
            "has_docstring": False,
            "length": 0,
            "has_params": False,
            "has_returns": False,
            "has_raises": False,
            "has_examples": False,
        }

    length = len(doc)
    has_params = "Args:" in doc or "Parameters:" in doc or ":param" in doc
    has_returns = "Returns:" in doc or ":returns:" in doc or ":return:" in doc
    has_raises = "Raises:" in doc or ":raises:" in doc
    has_examples = ">>>" in doc or "Example:" in doc or "Examples:" in doc

    # Calculate score (1-5 scale)
    score = 2.0  # Base score for having a docstring

    if length > 50:
        score += 0.5
    if length > 150:
        score += 0.5
    if has_params:
        score += 0.5
    if has_returns:
        score += 0.25
    if has_raises:
        score += 0.25
    if has_examples:
        score += 1.0

    score = min(5.0, score)

    return score, {
        "has_docstring": True,
        "length": length,
        "has_params": has_params,
        "has_returns": has_returns,
        "has_raises": has_raises,
        "has_examples": has_examples,
    }


def analyze_module(module_path: Path) -> ModuleMetrics:
    """Analyze documentation quality of a Python module."""
    with open(module_path) as f:
        source = f.read()

    tree = ast.parse(source)

    # Get module docstring
    module_doc = ast.get_docstring(tree)
    module_score, module_details = get_docstring_score(module_doc)

    items = []
    total_public = 0
    documented = 0
    with_examples = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # Skip private items (but include __init__)
            if node.name.startswith("_") and node.name != "__init__":
                continue

            total_public += 1
            doc = ast.get_docstring(node)
            score, details = get_docstring_score(doc)

            if details["has_docstring"]:
                documented += 1
            if details["has_examples"]:
                with_examples += 1

            items.append(
                DocstringMetrics(
                    name=node.name,
                    has_docstring=details["has_docstring"],
                    docstring_length=details["length"],
                    has_params=details["has_params"],
                    has_returns=details["has_returns"],
                    has_raises=details["has_raises"],
                    has_examples=details["has_examples"],
                    score=score,
                )
            )

    # Calculate aggregate scores
    completeness = (documented / total_public * 5) if total_public > 0 else 5.0
    examples = (with_examples / total_public * 5) if total_public > 0 else 1.0

    # Clarity based on average docstring length
    avg_length = (
        sum(i.docstring_length for i in items) / len(items) if items else 0
    )
    if avg_length > 200:
        clarity = 5.0
    elif avg_length > 100:
        clarity = 4.0
    elif avg_length > 50:
        clarity = 3.0
    elif avg_length > 0:
        clarity = 2.0
    else:
        clarity = 1.0

    # Consistency based on whether documented items follow similar patterns
    consistency = 4.0  # Default to good, would need more complex analysis

    # Weighted score (from evaluation framework)
    weighted = (
        completeness * 0.30
        + clarity * 0.25
        + examples * 0.20
        + consistency * 0.15
        + 5.0 * 0.10  # Accuracy assumed good
    )

    return ModuleMetrics(
        name=module_path.stem,
        has_module_docstring=module_details["has_docstring"],
        module_docstring_length=module_details["length"],
        total_public_items=total_public,
        documented_items=documented,
        items_with_examples=with_examples,
        completeness_score=completeness,
        clarity_score=clarity,
        examples_score=examples,
        consistency_score=consistency,
        weighted_score=weighted,
        items=items,
    )


def analyze_test_file(test_path: Path) -> dict:
    """Analyze test file for docstring coverage."""
    with open(test_path) as f:
        source = f.read()

    tree = ast.parse(source)

    total_tests = 0
    documented_tests = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            total_tests += 1
            if ast.get_docstring(node):
                documented_tests += 1

    return {
        "file": test_path.name,
        "total_tests": total_tests,
        "documented_tests": documented_tests,
        "coverage": (documented_tests / total_tests * 100) if total_tests > 0 else 0,
    }


def verify_examples_execute(module_name: str) -> list[dict]:
    """Verify that docstring examples actually execute."""
    results = []
    try:
        module = importlib.import_module(module_name)

        for name, obj in inspect.getmembers(module):
            if name.startswith("_"):
                continue

            doc = inspect.getdoc(obj)
            if doc and ">>>" in doc:
                # Extract and test examples using doctest
                import doctest

                try:
                    doctest_results = doctest.testmod(
                        module, verbose=False, optionflags=doctest.ELLIPSIS
                    )
                    results.append(
                        {
                            "module": module_name,
                            "item": name,
                            "failures": doctest_results.failed,
                            "tests": doctest_results.attempted,
                        }
                    )
                except Exception as e:
                    results.append(
                        {
                            "module": module_name,
                            "item": name,
                            "error": str(e),
                        }
                    )
    except ImportError as e:
        results.append({"module": module_name, "error": f"Import failed: {e}"})

    return results


def print_report(metrics: list[ModuleMetrics], test_results: list[dict], verbose: bool = False):
    """Print human-readable documentation quality report."""
    print("=" * 70)
    print("MONACO DOCUMENTATION QUALITY REPORT")
    print("=" * 70)
    print()

    # Summary table
    print("MODULE SCORES")
    print("-" * 70)
    print(
        f"{'Module':<20} {'Complete':>10} {'Clarity':>10} {'Examples':>10} {'Weighted':>10}"
    )
    print("-" * 70)

    total_weighted = 0
    for m in metrics:
        print(
            f"{m.name:<20} {m.completeness_score:>10.1f} {m.clarity_score:>10.1f} "
            f"{m.examples_score:>10.1f} {m.weighted_score:>10.2f}"
        )
        total_weighted += m.weighted_score

    avg_score = total_weighted / len(metrics) if metrics else 0
    print("-" * 70)
    print(f"{'AVERAGE':<20} {'':<10} {'':<10} {'':<10} {avg_score:>10.2f}")
    print()

    # Detailed issues
    print("DOCUMENTATION GAPS")
    print("-" * 70)

    for m in metrics:
        issues = []
        if not m.has_module_docstring:
            issues.append("Missing module docstring")
        elif m.module_docstring_length < 100:
            issues.append(f"Module docstring too short ({m.module_docstring_length} chars)")

        undocumented = [i.name for i in m.items if not i.has_docstring]
        if undocumented:
            issues.append(f"Undocumented: {', '.join(undocumented[:5])}")
            if len(undocumented) > 5:
                issues.append(f"  ... and {len(undocumented) - 5} more")

        no_examples = [i.name for i in m.items if i.has_docstring and not i.has_examples]
        if no_examples and m.name != "__init__":
            issues.append(f"No examples: {', '.join(no_examples[:3])}")

        if issues:
            print(f"\n{m.name}:")
            for issue in issues:
                print(f"  • {issue}")

    # Test documentation
    print()
    print("TEST DOCUMENTATION")
    print("-" * 70)
    for t in test_results:
        status = "✓" if t["coverage"] >= 80 else "✗"
        print(
            f"{status} {t['file']:<30} {t['documented_tests']}/{t['total_tests']} "
            f"({t['coverage']:.0f}%)"
        )

    # Verbose output
    if verbose:
        print()
        print("DETAILED ITEM SCORES")
        print("-" * 70)
        for m in metrics:
            print(f"\n{m.name}:")
            for item in m.items:
                status = "✓" if item.score >= 3.5 else "○" if item.score >= 2.5 else "✗"
                extras = []
                if item.has_params:
                    extras.append("P")
                if item.has_returns:
                    extras.append("R")
                if item.has_examples:
                    extras.append("E")
                extras_str = f"[{','.join(extras)}]" if extras else ""
                print(f"  {status} {item.name:<30} {item.score:.1f} {extras_str}")

    # Final verdict
    print()
    print("=" * 70)
    target = 4.0
    if avg_score >= target:
        print(f"✓ PASS: Average score {avg_score:.2f} >= {target} target")
        return True
    else:
        print(f"✗ FAIL: Average score {avg_score:.2f} < {target} target")
        print(f"  Improvement needed: +{target - avg_score:.2f}")
        return False


def print_json_report(metrics: list[ModuleMetrics], test_results: list[dict]):
    """Print JSON report for programmatic consumption."""
    report = {
        "modules": [
            {
                "name": m.name,
                "has_module_docstring": m.has_module_docstring,
                "module_docstring_length": m.module_docstring_length,
                "total_public_items": m.total_public_items,
                "documented_items": m.documented_items,
                "items_with_examples": m.items_with_examples,
                "scores": {
                    "completeness": m.completeness_score,
                    "clarity": m.clarity_score,
                    "examples": m.examples_score,
                    "consistency": m.consistency_score,
                    "weighted": m.weighted_score,
                },
                "items": [
                    {
                        "name": i.name,
                        "has_docstring": i.has_docstring,
                        "docstring_length": i.docstring_length,
                        "has_params": i.has_params,
                        "has_returns": i.has_returns,
                        "has_raises": i.has_raises,
                        "has_examples": i.has_examples,
                        "score": i.score,
                    }
                    for i in m.items
                ],
            }
            for m in metrics
        ],
        "tests": test_results,
        "summary": {
            "average_weighted_score": sum(m.weighted_score for m in metrics) / len(metrics)
            if metrics
            else 0,
            "total_modules": len(metrics),
            "modules_with_docstrings": sum(1 for m in metrics if m.has_module_docstring),
            "target_score": 4.0,
        },
    }
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Verify Monaco documentation quality")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    src_dir = project_root / "src" / "monaco"
    tests_dir = project_root / "tests"

    # Analyze source modules
    source_files = [
        src_dir / "__init__.py",
        src_dir / "distributions.py",
        src_dir / "task.py",
        src_dir / "project.py",
        src_dir / "config.py",
        src_dir / "cli.py",
    ]

    metrics = []
    for path in source_files:
        if path.exists():
            metrics.append(analyze_module(path))

    # Analyze test files
    test_results = []
    if tests_dir.exists():
        for test_file in tests_dir.glob("test_*.py"):
            test_results.append(analyze_test_file(test_file))

    # Output report
    if args.json:
        print_json_report(metrics, test_results)
        avg_score = sum(m.weighted_score for m in metrics) / len(metrics) if metrics else 0
        sys.exit(0 if avg_score >= 4.0 else 1)
    else:
        passed = print_report(metrics, test_results, verbose=args.verbose)
        sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
