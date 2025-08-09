# Galaxy Runner API Reference

This document provides a comprehensive technical reference for the Galaxy Runner game architecture, classes, methods, and systems.

## Table of Contents

- [Core Architecture](#core-architecture)
- [MainWidget Class](#mainwidget-class)
- [Transformation System](#transformation-system)
- [Input System](#input-system)
- [Menu System](#menu-system)
- [Game Constants](#game-constants)
- [Audio System](#audio-system)
- [Coordinate Systems](#coordinate-systems)
- [Event Flow](#event-flow)

## Core Architecture

Galaxy Runner follows a modular architecture with clear separation of concerns:

```
main.py (Core Engine)
├── transforms.py (3D Math)
├── user_actions.py (Input Handling)
├── menu.py (Menu Logic)
├── galaxy.kv (Main UI Layout)
└── menu.kv (Menu UI Layout)
```

## MainWidget Class

### Class Definition

```python
class MainWidget(RelativeLayout)
```

Main game widget that orchestrates all game systems including rendering, physics, input, and audio.

### Properties

#### Kivy Properties
- `menu_widget: ObjectProperty` - Reference to MenuWidget instance
- `perspective_point_x: NumericProperty` - X coordinate of vanishing point
- `perspective_point_y: NumericProperty` - Y coordinate of vanishing point
- `menu_title: StringProperty` - Dynamic menu title text
- `menu_button_title: StringProperty` - Dynamic menu button text
- `score_txt: StringProperty` - Score display text

#### Grid Configuration
- `V_NB_LINES: int = 8` - Number of vertical grid lines
- `V_LINES_SPACING: float = 0.4` - Vertical line spacing (% of width)
- `H_NB_LINES: int = 8` - Number of horizontal grid lines
- `H_LINES_SPACING: float = 0.15` - Horizontal line spacing (% of height)

#### Movement Constants
- `SPEED: float = 0.8` - Forward movement speed
- `SPEED_X: float = 3.5` - Horizontal movement sensitivity

#### Ship Configuration
- `SHIP_WIDTH: float = 0.1` - Ship width (% of screen width)
- `SHIP_HEIGHT: float = 0.035` - Ship height (% of screen height)
- `SHIP_BASE_Y: float = 0.04` - Ship Y position (% of screen height)

#### Tile System
- `NB_TILES: int = 16` - Maximum rendered tiles

### Core Methods

#### Initialization

```python
def __init__(self, **kwargs) -> None
```
Initialize all game systems and start the main loop.

**Systems initialized:**
- Audio system
- Grid lines (vertical/horizontal)
- Tiles (obstacles)
- Player ship
- Input handlers
- 60 FPS game loop

#### Game State Management

```python
def reset_game(self) -> None
```
Reset all game variables to initial state.

**Reset operations:**
- Movement offsets and speeds
- Tile coordinates
- Score counter
- Game state flags
- Path generation

```python
def is_desktop(self) -> bool
```
Platform detection for input method selection.

**Returns:**
- `True` for Linux, Windows, macOS
- `False` for mobile platforms

#### Audio System

```python
def init_audio(self) -> None
```
Initialize complete audio system with volume configuration.

**Audio files loaded:**
- `begin.wav` - Game start sound
- `galaxy.wav` - Title ambient sound
- `gameover_impact.wav` - Collision sound
- `gameover_voice.wav` - Game over announcement
- `music1.wav` - Background music
- `restart.wav` - Restart confirmation

**Volume levels:**
- Music: 1.0 (full volume)
- Voice/UI: 0.25 (subtle)
- Impact: 0.6 (prominent)

#### Ship System

```python
def init_ship(self) -> None
```
Create ship graphics object (black triangle).

```python
def update_ship(self) -> None
```
Update ship position and apply perspective transformation.

**Ship geometry:**
```
    2 (top vertex)
 1     3 (base vertices)
```

#### Collision Detection

```python
def check_ship_collisions(self) -> bool
```
Check collision between ship and all tiles.

**Returns:**
- `True` if collision detected
- `False` if no collision

**Algorithm:**
1. Iterate through all tile coordinates
2. Skip distant tiles (optimization)
3. Check collision with each relevant tile
4. Return on first collision found

```python
def check_ship_collision_with_tile(self, ti_x: int, ti_y: int) -> bool
```
Check collision between ship and specific tile using AABB detection.

**Parameters:**
- `ti_x` - Tile X coordinate in grid space
- `ti_y` - Tile Y coordinate in grid space

**Returns:**
- `True` if any ship vertex intersects tile boundaries

#### Tile System

```python
def init_tiles(self) -> None
```
Create tile graphics objects (white quads).

```python
def pre_fill_tiles_coordinates(self) -> None
```
Generate initial straight path for safe starting area.

```python
def generate_tiles_coordinates(self) -> None
```
Procedural path generation with intelligent boundary handling.

**Generation algorithm:**
1. Remove off-screen tiles
2. Get last tile position
3. Random direction selection (0=straight, 1=right, 2=left)
4. Boundary collision prevention
5. Generate turn sequences

```python
def get_tile_coordinates(self, ti_x: int, ti_y: int) -> Tuple[float, float]
```
Convert grid coordinates to world coordinates.

```python
def update_tiles(self) -> None
```
Update all tile positions with perspective transformation.

#### Grid System

```python
def init_vertical_lines(self) -> None
def init_horizontal_lines(self) -> None
```
Initialize grid line graphics objects.

```python
def get_line_x_from_index(self, index: int) -> float
def get_line_y_from_index(self, index: int) -> float
```
Calculate world coordinates for grid lines.

```python
def update_vertical_lines(self) -> None
def update_horizontal_lines(self) -> None
```
Update grid line positions with perspective transformation.

#### Main Game Loop

```python
def update(self, dt: float) -> None
```
Main game loop executed at 60 FPS.

**Operations per frame:**
1. Update visual elements (grid, tiles, ship)
2. Process game physics (movement, scrolling)
3. Handle score updates
4. Check collision detection
5. Manage game over logic

**Parameters:**
- `dt` - Delta time since last frame

#### Menu Integration

```python
def on_menu_button_pressed(self) -> None
```
Handle menu button press for start/restart functionality.

```python
def play_voice_game_over(self, dt: float) -> None
```
Delayed game over voice announcement.

## Transformation System

Located in `transforms.py`

### Core Functions

```python
def transform(self, x: float, y: float) -> Tuple[int, int]
```
Main transformation dispatcher.

```python
def transform_2D(self, x: float, y: float) -> Tuple[int, int]
```
Identity transformation for debugging.

```python
def transform_perspective(self, x: float, y: float) -> Tuple[int, int]
```
3D perspective transformation using vanishing point mathematics.

### Perspective Algorithm

```python
# Step 1: Y normalization
lin_y = y * perspective_point_y / height

# Step 2: Boundary clamping
if lin_y > perspective_point_y:
    lin_y = perspective_point_y

# Step 3: Distance calculation
diff_x = x - perspective_point_x
diff_y = perspective_point_y - lin_y

# Step 4: Perspective factor
factor_y = diff_y / perspective_point_y
factor_y = pow(factor_y, 4)  # Exponential curve

# Step 5: Coordinate transformation
tr_x = perspective_point_x + (diff_x * factor_y)
tr_y = perspective_point_y - (factor_y * perspective_point_y)
```

## Input System

Located in `user_actions.py`

### Keyboard Events

```python
def keyboard_closed(self) -> None
```
Cleanup keyboard bindings on shutdown.

```python
def on_keyboard_down(self, keyboard, keycode: Tuple[int, str], text: str, modifiers: List[str]) -> bool
```
Handle key press events.

**Key mappings:**
- Left Arrow: `current_speed_x = SPEED_X`
- Right Arrow: `current_speed_x = -SPEED_X`

```python
def on_keyboard_up(self, keyboard, keycode: Tuple[int, str]) -> None
```
Handle key release events (stops movement).

### Touch Events

```python
def on_touch_down(self, touch) -> bool
```
Handle touch/mouse press with screen-split controls.

**Touch mapping:**
- Left half: `current_speed_x = SPEED_X`
- Right half: `current_speed_x = -SPEED_X`

```python
def on_touch_up(self, touch) -> None
```
Handle touch/mouse release (stops movement).

## Menu System

Located in `menu.py`

### MenuWidget Class

```python
class MenuWidget(RelativeLayout)
```

Overlay menu with opacity-based interaction control.

```python
def on_touch_down(self, touch) -> Union[bool, None]
```
Smart touch filtering based on widget opacity.

**Behavior:**
- `opacity == 0`: Return `False` (pass-through)
- `opacity > 0`: Process normally

## Game Constants

### Configuration Values

| Constant | Value | Description |
|----------|-------|-------------|
| `V_NB_LINES` | 8 | Vertical grid lines |
| `V_LINES_SPACING` | 0.4 | Vertical spacing (% width) |
| `H_NB_LINES` | 8 | Horizontal grid lines |
| `H_LINES_SPACING` | 0.15 | Horizontal spacing (% height) |
| `SPEED` | 0.8 | Forward movement speed |
| `SPEED_X` | 3.5 | Horizontal sensitivity |
| `NB_TILES` | 16 | Maximum rendered tiles |
| `SHIP_WIDTH` | 0.1 | Ship width (% screen) |
| `SHIP_HEIGHT` | 0.035 | Ship height (% screen) |
| `SHIP_BASE_Y` | 0.04 | Ship Y position (% screen) |

### Perspective Configuration

| Property | Value | Description |
|----------|-------|-------------|
| `perspective_point_x` | `width / 2` | Horizontal vanishing point |
| `perspective_point_y` | `height * 0.75` | Vertical vanishing point |

## Audio System

### Sound Files

| File | Purpose | Volume |
|------|---------|--------|
| `begin.wav` | Game start | 0.25 |
| `galaxy.wav` | Title ambient | 0.25 |
| `gameover_impact.wav` | Collision | 0.6 |
| `gameover_voice.wav` | Game over | 0.25 |
| `music1.wav` | Background music | 1.0 |
| `restart.wav` | Restart confirm | 0.25 |

### Audio State Management

- Title screen: `galaxy.wav` playing
- Game start: `begin.wav` + `music1.wav`
- Game over: Stop `music1.wav`, play `gameover_impact.wav`
- Game over +3s: `gameover_voice.wav`
- Restart: `restart.wav` + `music1.wav`

## Coordinate Systems

### World Coordinates
- Origin: Bottom-left of screen
- X-axis: Left to right
- Y-axis: Bottom to top
- Units: Pixels

### Grid Coordinates
- Origin: Center of grid
- X-axis: Grid column index (can be negative)
- Y-axis: Grid row index (relative to current_y_loop)
- Units: Grid cells

### Screen Coordinates
- Origin: Bottom-left of screen (Kivy standard)
- X-axis: 0 to window width
- Y-axis: 0 to window height
- Units: Pixels

### Perspective Coordinates
- Transformed world coordinates
- Applied by `transform_perspective()`
- Creates 3D tunnel illusion
- Units: Screen pixels

## Event Flow

### Game Initialization
1. `MainWidget.__init__()`
2. `init_audio()`
3. `init_vertical_lines()`
4. `init_horizontal_lines()`
5. `init_tiles()`
6. `init_ship()`
7. `reset_game()`
8. Setup keyboard (desktop only)
9. Start 60 FPS loop
10. Play `galaxy.wav`

### Game Loop (60 FPS)
1. `update(dt)` called
2. Update visual elements:
   - `update_vertical_lines()`
   - `update_horizontal_lines()`
   - `update_tiles()`
   - `update_ship()`
3. Process physics (if game active):
   - Forward movement
   - Score updates
   - Horizontal movement
4. Collision detection
5. Game over handling

### Input Processing

#### Keyboard (Desktop)
1. Key press → `on_keyboard_down()`
2. Set `current_speed_x`
3. Key release → `on_keyboard_up()`
4. Reset `current_speed_x = 0`

#### Touch (Mobile)
1. Touch down → `on_touch_down()`
2. Check game state
3. Determine screen half
4. Set `current_speed_x`
5. Touch up → `on_touch_up()`
6. Reset `current_speed_x = 0`

### Game State Transitions

```
[Title Screen] 
    ↓ (button press)
[Game Active]
    ↓ (collision)
[Game Over]
    ↓ (button press)
[Game Active]
```

## Performance Considerations

### Optimization Techniques
- Early exit collision detection
- Tile culling (off-screen removal)
- 60 FPS frame rate limiting
- Efficient coordinate transformations
- Minimal memory allocations

### Memory Management
- Reuse graphics objects
- Automatic tile cleanup
- Proper keyboard unbinding
- Sound object persistence

## Error Handling

### Common Edge Cases
- Division by zero prevention in perspective math
- Boundary checking in path generation
- Audio file loading failures
- Keyboard cleanup on app exit

### Debug Features
- 2D transformation mode available
- Console debug output
- Visual coordinate debugging possible