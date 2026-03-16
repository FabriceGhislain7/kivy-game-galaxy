# Galaxy Runner API Reference

## Architecture

The game is organized into small modules with explicit responsibilities:

- `main.py`: game state, render/update loop, collision and audio orchestration.
- `transforms.py`: coordinate transforms (2D + perspective projection).
- `user_actions.py`: keyboard/touch handlers used by `MainWidget`.
- `menu.py`: menu overlay widget behavior.
- `galaxy.kv` and `menu.kv`: Kivy UI declarations.

## Main Classes

### `MainWidget` (`main.py`)

Responsibilities:

- Initializes graphics primitives (grid lines, tiles, ship).
- Maintains run state (`started`, `game_over`, score, offsets).
- Runs frame updates at 60 FPS through `Clock.schedule_interval`.
- Generates procedural tile coordinates and keeps them in sync with render objects.
- Detects ship/tile collisions and transitions to game-over state.

Important properties:

- `perspective_point_x`, `perspective_point_y`: vanishing point.
- `menu_title`, `menu_button_title`, `score_txt`: UI-bound text.

### `MenuWidget` (`menu.py`)

- Overlay widget shown at boot and game over.
- Ignores touch when invisible (`opacity == 0`) so gameplay input passes through.

## Core Runtime Flow

1. App starts and `MainWidget` is instantiated.
2. Audio, geometry and path state are initialized.
3. Frame update runs at ~60 FPS.
4. If gameplay is active:
   - world scrolls forward,
   - horizontal offset follows input,
   - score increases with each loop.
5. On collision:
   - game state changes to over,
   - menu reappears,
   - gameplay music stops and game-over cues are played.

## Coordinate and Perspective System

`transform_perspective(x, y)` maps world coordinates to a pseudo-3D projection using:

- Y normalization against viewport height,
- vanishing point distances,
- an exponential depth factor (`factor^4`) to accentuate perspective.

Fallback behavior returns untransformed coordinates if viewport metrics are invalid.

## Input API

`user_actions.py` exposes methods imported directly in `MainWidget`:

- `on_keyboard_down`, `on_keyboard_up`
- `on_touch_down`, `on_touch_up`
- `keyboard_closed`

Control contract:

- Left input sets `current_speed_x` positive.
- Right input sets `current_speed_x` negative.
- Release sets `current_speed_x = 0`.

## Tunable Gameplay Constants

Defined in `MainWidget`:

- `SPEED`, `SPEED_X`
- `V_NB_LINES`, `V_LINES_SPACING`
- `H_NB_LINES`, `H_LINES_SPACING`
- `NB_TILES`
- `SHIP_WIDTH`, `SHIP_HEIGHT`, `SHIP_BASE_Y`

These values can be tuned without changing module interfaces.

## Assets

Expected asset paths:

- `audio/*.wav`
- `images/bg1.jpg`
- `fonts/*.ttf`

The audio loader is defensive and logs missing files instead of crashing immediately.
