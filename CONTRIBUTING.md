# Contributing to QuickCards

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

1. Fork the repository.
2. Clone your fork locally.
3. Create a new branch: `git checkout -b feat/my-feature`
4. Make your changes following the guidelines below.
5. Commit using [Conventional Commits](https://www.conventionalcommits.org/): `git commit -m "feat: add new feature"`
6. Push to your fork and submit a Pull Request.

## Development Setup

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
# No install required — just serve
python -m http.server 5500 -d frontend
```

## Code Style

- **Python:** Follow PEP 8. We use `ruff` for linting and formatting.
- **JavaScript:** ES6 modules. We use `biome` for linting and `prettier` for formatting.
- **CSS:** Follow existing design token patterns in `style.css`.

## Pre-commit Hooks

We use `pre-commit` to enforce code quality. Install hooks with:
```bash
pip install pre-commit
pre-commit install
```

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `style:` — Code style changes (formatting, no logic change)
- `refactor:` — Code restructuring
- `test:` — Adding or updating tests

## Reporting Issues

Use the GitHub/GitLab issue tracker. Include:
- Steps to reproduce
- Expected vs actual behavior
- Browser/OS information
- Console error output if applicable
