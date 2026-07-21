# Contributing

Thanks for contributing to Galaxy Runner.

## Development Setup

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Quality Checks

```bash
ruff check .
pytest -q
```

## Pull Request Rules

- Keep changes scoped and atomic.
- Update docs for behavior changes.
- Add or update tests for logic changes.
- Keep commit messages clear and imperative.
