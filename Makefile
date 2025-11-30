.PHONY: help install install-dev test test-cov type-check lint format check clean build

help:
	@echo "Monaco Development Commands"
	@echo "============================"
	@echo "install      Install package"
	@echo "install-dev  Install with dev dependencies"
	@echo "test         Run tests"
	@echo "test-cov     Run tests with coverage"
	@echo "type-check   Run mypy type checking"
	@echo "lint         Run ruff linter"
	@echo "format       Format code with black and ruff"
	@echo "check        Run all checks (lint, type-check, test)"
	@echo "clean        Remove build artifacts"
	@echo "build        Build distribution packages"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=monaco --cov-report=html --cov-report=term

type-check:
	mypy src/monaco/

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

check: lint type-check test

clean:
	rm -rf build/ dist/ *.egg-info/ src/*.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +

build: clean
	python -m build
