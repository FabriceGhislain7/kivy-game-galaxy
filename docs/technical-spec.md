# Technical Specification

## Minimum Requirements

- Python 3.10+
- Kivy 2.3.1
- Windows/macOS/Linux desktop runtime

## Gameplay Rules

- Player moves horizontally on bottom lane
- Obstacles spawn at top with random X
- Collision triggers game over
- Score increases over time while alive
- Difficulty ramps via obstacle speed growth

## Configurable Constants

See `src/galaxy_runner/config.py`:

- window size and FPS
- player geometry and speed
- obstacle geometry, speed, spawn interval
- score rate

## Input Map

- Left Arrow / A => move left
- Right Arrow / D => move right
- R => restart after game over
