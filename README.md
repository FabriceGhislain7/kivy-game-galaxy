# Galaxy Runner

A production-minded Kivy game starter built as a clean, documented, and extensible codebase.

This repository is a full restart of the original prototype and is designed to be maintainable,
teachable, and ready for commercial product iteration.

## Product Direction

Galaxy Runner is an arcade reflex game with a pseudo-3D tunnel look, where the player avoids incoming obstacles, collects score over time, and progressively faces higher speed and challenge.

## Key Goals

- Clean architecture with separation of concerns
- Fast onboarding for developers new to Kivy
- Documentation from zero to advanced implementation
- Reliable baseline for scaling into a sellable game product

## Tech Stack

- Python 3.10+
- Kivy 2.3.1
- Pytest + Ruff for quality checks

## Repository Structure

```text
.
|-- docs/
|   |-- architecture.md
|   |-- roadmap.md
|   |-- technical-spec.md
|   |-- testing.md
|   `-- steps/
|       |-- 01-installation.md
|       |-- ...
|       `-- 11-quality-tooling.md
|-- src/
|   `-- galaxy_runner/
|       |-- __init__.py
|       |-- app.py
|       |-- config.py
|       |-- core.py
|       `-- game.py
|-- tests/
|   `-- test_core.py
|-- main.py
|-- requirements.txt
|-- pyproject.toml
|-- CONTRIBUTING.md
|-- CHANGELOG.md
`-- LICENSE
```

## Quick Start

1. Create and activate a virtual environment.

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Run the game.

```bash
python main.py
```

## Controls

- Left Arrow / A: move left
- Right Arrow / D: move right
- R: restart after game over

## Quality Commands

```bash
ruff check .
pytest -q
```

## Documentation Path

Read `docs/steps/` in order, from installation to quality and release practices.

## Visual Features`r`n`r`n- Pseudo-3D tunnel rendering with perspective grid`r`n- Animated starfield background`r`n- Depth-based obstacle scaling and motion`r`n- Neon sci-fi HUD style`r`n`r`n## Status`r`n`r`n- Working playable baseline
- Documented architecture and technical spec
- Testable core logic utilities
- Initial CI-ready local quality workflow

## License

MIT. See `LICENSE`.

