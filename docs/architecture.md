# Architecture

## Overview

The project uses a compact architecture:

- `main.py`: executable bootstrap
- `src/galaxy_runner/app.py`: application wiring and HUD
- `src/galaxy_runner/game.py`: gameplay loop, input, collision, scoring
- `src/galaxy_runner/config.py`: tunable gameplay constants

## Design Principles

- Single responsibility per module
- Explicit game state (`running` vs `game over`)
- Data-oriented constants for balancing
- Safe keyboard lifecycle handling

## Runtime Flow

1. `main.py` calls `run()`
2. `GalaxyRunnerApp` builds UI + `RunnerWidget`
3. `RunnerWidget` schedules update loop at fixed FPS
4. Each frame:
   - process input
   - move player
   - spawn/move obstacles
   - detect collision
   - update score and status
