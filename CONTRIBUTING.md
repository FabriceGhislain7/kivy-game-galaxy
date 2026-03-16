# Contributing

Thank you for contributing to Galaxy Runner.

## Development Setup

1. Create a virtual environment.

```bash
python -m venv .venv
```

2. Activate it.

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Run the game.

```bash
python main.py
```

## Coding Guidelines

- Keep modules focused and responsibilities explicit.
- Prefer clear names over short names.
- Add type hints for new/changed Python functions when practical.
- Keep Kivy `.kv` files readable and aligned with Python widget logic.
- Avoid introducing unnecessary dependencies.

## Repository Rules

- Do not commit virtual environment artifacts.
- Do not commit generated cache files (`__pycache__`, `.pyc`).
- Keep docs (`README.md`, `API_REFERENCE.md`) aligned with behavioral changes.

## Validation Checklist

Before opening a PR:

- Ensure Python files compile:

```bash
python -m compileall main.py transforms.py user_actions.py menu.py
```

- Launch the app and verify:
  - Menu appears on startup.
  - Start/Restart flow works.
  - Keyboard and touch controls work.
  - Score increments during run.
  - Collision triggers game-over state.

## Commit Style

Use concise, imperative commit messages.

Examples:
- `docs: rewrite README and API reference`
- `fix: guard audio playback when assets are missing`
- `refactor: clean MainWidget lifecycle and input bindings`

## Pull Request Expectations

A good PR includes:

- A short problem statement.
- The implemented approach and tradeoffs.
- Any gameplay or UX impact.
- Screenshots/GIFs when UI behavior changes.
