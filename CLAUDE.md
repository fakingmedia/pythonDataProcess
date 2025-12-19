# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python data processing project using:
- **Python 3.14** (specified in .python-version)
- **UV package manager** for dependency management and virtual environments
- **Modern Python packaging** with pyproject.toml
- **Data science libraries**: NumPy, Pandas, and Statsmodels

## Development Commands

```bash
# Run the main script
uv run main.py

# Install/update dependencies
uv sync

# Add a new dependency
uv add <package-name>

# Build the package (creates wheel and tarball in dist/)
uv build

# Run Python interactively with project dependencies
uv run python
```

## Architecture

The project follows modern Python packaging standards:
- `pyproject.toml` - Project configuration and dependencies
- `src/` - Source code directory (currently empty)
- `main.py` - Entry point script
- `.venv/` - UV-managed virtual environment
- `uv.lock` - Lock file for reproducible builds

## Code Quality

The project uses Ruff for linting (cache directory `.ruff_cache/` present). No explicit configuration file found, so Ruff uses default settings.

## Current State

This is a minimal project template with:
- Basic package structure configured
- Data science dependencies (numpy, pandas, statsmodels)
- Simple entry point in main.py
- No source code in src/ directory yet
- No testing framework configured
- Empty README.md