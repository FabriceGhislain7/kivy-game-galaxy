"""
Galaxy Runner - Main Game Module

A 3D perspective space tunnel runner game built with Kivy.
Features dynamic procedural path generation, realistic perspective transformations,
and cross-platform input support.

Author: [Your Name]
Version: 1.0
License: MIT
"""

import random
from typing import Tuple, List, Optional

from kivy import platform
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

# ========================================
# WINDOW CONFIGURATION
# ========================================
# Set initial window size for desktop platforms
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.core.window import Window
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget

# Load menu UI layout
Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    """
    Main game widget that handles all game logic, rendering, and user interaction.
    
    This class manages:
    - 3D perspective grid rendering
    - Player ship movement and collision detection
    - Procedural path generation
    - Game state management
    - Audio system
    - User input handling
    """
    
    # ========================================
    # EXTERNAL MODULES IMPORT
    # ========================================
    # Import transformation and input handling methods from separate modules
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import on_keyboard_up, on_keyboard_down, keyboard_closed, on_touch_up, on_touch_down

    # ========================================
    # KIVY PROPERTIES
    # ========================================
    menu_widget = ObjectProperty()  # Reference to the menu widget
    perspective_point_x = NumericProperty(0)  # X coordinate of vanishing point
    perspective_point_y = NumericProperty(0)  # Y coordinate of vanishing point

    # ========================================
    # GRID CONFIGURATION CONSTANTS
    # ========================================
    V_NB_LINES = 8  # Number of vertical lines in the grid
    V_LINES_SPACING = .4  # Vertical lines spacing as percentage of screen width
    vertical_lines = []  # List to store vertical line objects

    H_NB_LINES = 8  # Number of horizontal lines in the grid
    H_LINES_SPACING = .15  # Horizontal lines spacing as percentage of screen height
    horizontal_lines = []  # List to store horizontal line objects

    # ========================================
    # MOVEMENT AND SPEED CONSTANTS
    # ========================================
    SPEED = .8  # Vertical movement speed (forward motion)
    current_offset_y = 0  # Current vertical offset for grid animation
    current_y_loop = 0  # Current Y position in the game world (used for scoring)

    SPEED_X = 3.5  # Horizontal movement sensitivity
    current_speed_x = 0  # Current horizontal movement speed (-SPEED_X, 0, or +SPEED_X)
    current_offset_x = 0  # Current horizontal offset for grid animation

    # ========================================
    # TILES (OBSTACLES) CONFIGURATION
    # ========================================
    NB_TILES = 16  # Maximum number of tiles to render simultaneously
    tiles = []  # List to store tile (Quad) objects
    tiles_coordinates = []  # List of (x, y) coordinates for each tile

    # ========================================
    # PLAYER SHIP CONFIGURATION
    # ========================================
    SHIP_WIDTH = .1  # Ship width as percentage of screen width
    SHIP_HEIGHT = 0.035  # Ship height as percentage of screen height
    SHIP_BASE_Y = 0.04  # Ship Y position as percentage of screen height
    ship = None  # Triangle object representing the player ship
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]  # Ship vertices coordinates

    # ========================================
    # GAME STATE VARIABLES
    # ========================================
    state_game_over = False  # True when game is over
    state_game_has_started = False  # True when game is actively running

    # ========================================
    # UI TEXT PROPERTIES
    # ========================================
    menu_title = StringProperty("G   A   L   A   X   Y")  # Dynamic menu title
    menu_button_title = StringProperty("START")  # Dynamic button text
    score_txt = StringProperty()  # Score display text

    # ========================================
    # AUDIO SYSTEM VARIABLES
    # ========================================
    sound_begin = None  # Game start sound
    sound_galaxy = None  # Title screen ambient sound
    sound_gameover_impact = None  # Collision impact sound
    sound_gameover_voice = None  # Game over voice announcement
    sound_music1 = None  # Background music during gameplay
    sound_restart = None  # Restart game sound

    def __init__(self, **kwargs) -> None:
        """
        Initialize the main game widget.
        
        Sets up all game systems:
        - Audio system
        - Grid lines (vertical and horizontal)
        - Tiles (obstacles)
        - Player ship
        - Input handling (keyboard for desktop)
        - Game loop (60 FPS)
        
        Args:
            **kwargs: Additional keyword arguments passed to parent class
        """
        super(MainWidget, self).__init__(**kwargs)
        
        # Initialize all game systems
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()

        # Reset game to initial state
        self.reset_game()

        # Setup keyboard input for desktop platforms
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)
        
        # Start main game loop at 60 FPS
        Clock.schedule_interval(self.update, 1.0 / 60.0)

        # Play title screen ambient sound
        self.sound_galaxy.play()

    def init_audio(self) -> None:
        """
        Initialize the audio system by loading all sound files and setting volumes.
        
        Loads:
        - Game state sounds (begin, restart, game over)
        - Ambient and music tracks
        - Sets appropriate volume levels for each sound
        """
        # Load all sound files
        self.sound_begin = SoundLoader.load('audio/begin.wav')
        self.sound_galaxy = SoundLoader.load('audio/galaxy.wav')
        self.sound_gameover_impact = SoundLoader.load('audio/gameover_impact.wav')
        self.sound_gameover_voice = SoundLoader.load('audio/gameover_voice.wav')
        self.sound_music1 = SoundLoader.load('audio/music1.wav')
        self.sound_restart = SoundLoader.load('audio/restart.wav')

        # Configure volume levels
        self.sound_music1.volume = 1  # Background music at full volume
        self.sound_begin.volume = .25  # Subtle game start sound
        self.sound_galaxy.volume = .25  # Quiet ambient title sound
        self.sound_gameover_voice.volume = .25  # Clear but not overpowering voice
        self.sound_restart.volume = .25  # Subtle restart confirmation
        self.sound_gameover_impact.volume = .6  # Prominent collision impact

    def reset_game(self) -> None:
        """
        Reset all game variables to initial state.
        
        Called at game start and when restarting after game over.
        Resets:
        - Movement offsets and speed
        - Tile coordinates
        - Score
        - Game state flags
        """
        # Reset movement and position
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        
        # Reset tiles and score
        self.tiles_coordinates = []
        self.score_txt = "SCORE: " + str(self.current_y_loop)
        
        # Generate initial path
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        
        # Reset game state
        self.state_game_over = False

    def is_desktop(self) -> bool:
        """
        Check if the current platform is a desktop platform.
        
        Used to determine whether to enable keyboard input.
        
        Returns:
            bool: True if running on Linux, Windows, or macOS
        """
        if platform in ('linux', 'windows', 'macosx'):
            return True
        return False

    # ========================================
    # PLAYER SHIP SYSTEM
    # ========================================

    def init_ship(self) -> None:
        """
        Initialize the player ship as a black triangle.
        
        Creates a Triangle graphics object that will be updated
        each frame with the ship's position and perspective transformation.
        """
        with self.canvas:
            Color(0, 0, 0)  # Black color for the ship
            self.ship = Triangle()

    def update_ship(self) -> None:
        """
        Update the player ship's position and apply perspective transformation.
        
        Calculates the ship's triangle vertices based on:
        - Screen center (ship doesn't move horizontally in world space)
        - Ship dimensions (SHIP_WIDTH, SHIP_HEIGHT)
        - Base Y position (SHIP_BASE_Y)
        
        Triangle structure:
        ```
            2 (top point)
         1     3 (base points)
        ```
        """
        # Calculate ship dimensions and position
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height

        # Define triangle vertices (world coordinates)
        self.ship_coordinates[0] = (center_x - half_width, base_y)  # Left base point
        self.ship_coordinates[1] = (center_x, base_y + ship_height)  # Top point
        self.ship_coordinates[2] = (center_x + half_width, base_y)  # Right base point

        # Apply perspective transformation and update graphics
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    # ========================================
    # COLLISION DETECTION SYSTEM
    # ========================================

    def check_ship_collisions(self) -> bool:
        """
        Check if the player ship collides with any tiles.
        
        Iterates through all tiles and checks collision with each one.
        Only checks tiles that are at or near the current Y position.
        
        Returns:
            bool: True if collision detected, False otherwise
        """
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            
            # Skip tiles that are too far ahead (optimization)
            if ti_y > self.current_y_loop + 1:
                return False
            
            # Check collision with current tile
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x: int, ti_y: int) -> bool:
        """
        Check collision between ship and a specific tile.
        
        Uses axis-aligned bounding box collision detection.
        Checks if any of the ship's three vertices are inside the tile boundaries.
        
        Args:
            ti_x (int): Tile X coordinate in grid space
            ti_y (int): Tile Y coordinate in grid space
            
        Returns:
            bool: True if collision detected, False otherwise
        """
        # Get tile boundaries in world coordinates
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        
        # Check if any ship vertex is inside the tile
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    # ========================================
    # TILES (OBSTACLES) SYSTEM
    # ========================================

    def init_tiles(self) -> None:
        """
        Initialize tile graphics objects.
        
        Creates white Quad objects that will represent obstacles/path tiles.
        The actual positioning is handled by update_tiles().
        """
        with self.canvas:
            Color(1, 1, 1)  # White color for tiles
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self) -> None:
        """
        Pre-fill the tiles coordinates list with initial straight path.
        
        Creates a straight path of 10 tiles at X position 0,
        providing a safe starting area for the player.
        """
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self) -> None:
        """
        Generate new tile coordinates using procedural generation.
        
        This method:
        1. Removes tiles that are no longer visible (behind the camera)
        2. Generates new tiles ahead of the player
        3. Uses random direction changes (straight, left turn, right turn)
        4. Prevents the path from going outside the grid boundaries
        
        Path generation logic:
        - 0: Continue straight
        - 1: Turn right (increase X)
        - 2: Turn left (decrease X)
        """
        last_x = 0
        last_y = 0

        # Remove tiles that are no longer visible (behind current position)
        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        # Get last tile position if any tiles exist
        if len(self.tiles_coordinates) > 0:
            last_coordinate = self.tiles_coordinates[-1]
            last_x = last_coordinate[0]
            last_y = last_coordinate[1] + 1

        # Generate new tiles to maintain NB_TILES count
        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            # Random direction choice
            r = random.randint(0, 2)
            # 0 -> straight ahead
            # 1 -> turn right
            # 2 -> turn left
            
            # Calculate grid boundaries
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            
            # Force direction if approaching boundaries
            if last_x <= start_index:
                r = 1  # Force right turn
            if last_x >= end_index:
                r = 2  # Force left turn

            # Place current tile
            self.tiles_coordinates.append((last_x, last_y))
            
            # Generate turn sequence based on random direction
            if r == 1:  # Right turn
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            elif r == 2:  # Left turn
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            
            # Advance to next row
            last_y += 1

    def get_tile_coordinates(self, ti_x: int, ti_y: int) -> Tuple[float, float]:
        """
        Convert tile grid coordinates to world coordinates.
        
        Args:
            ti_x (int): Tile X position in grid space
            ti_y (int): Tile Y position in grid space
            
        Returns:
            Tuple[float, float]: World coordinates (x, y)
        """
        # Adjust Y coordinate relative to current camera position
        ti_y = ti_y - self.current_y_loop
        
        # Convert grid coordinates to world coordinates
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        
        return x, y

    def update_tiles(self) -> None:
        """
        Update all tile positions and apply perspective transformation.
        
        For each tile:
        1. Gets world coordinates from grid coordinates
        2. Applies perspective transformation
        3. Updates the Quad points to form a rectangle
        
        Quad vertex structure:
        ```
        2 ---- 3
        |      |
        |      |
        1 ---- 4
        ```
        """
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            
            # Get tile boundaries in world coordinates
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0] + 1, tile_coordinates[1] + 1)

            # Apply perspective transformation to all four corners
            x1, y1 = self.transform(xmin, ymin)  # Bottom-left
            x2, y2 = self.transform(xmin, ymax)  # Top-left
            x3, y3 = self.transform(xmax, ymax)  # Top-right
            x4, y4 = self.transform(xmax, ymin)  # Bottom-right

            # Update quad points
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    # ========================================
    # GRID LINES SYSTEM
    # ========================================

    def init_vertical_lines(self) -> None:
        """
        Initialize vertical grid lines.
        
        Creates white Line objects that will form the vertical components
        of the 3D grid tunnel effect.
        """
        with self.canvas:
            Color(1, 1, 1)  # White color for grid lines
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index: int) -> float:
        """
        Calculate X coordinate for a vertical line at given grid index.
        
        Args:
            index (int): Grid line index (can be negative)
            
        Returns:
            float: X coordinate in world space
        """
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index: int) -> float:
        """
        Calculate Y coordinate for a horizontal line at given grid index.
        
        Args:
            index (int): Grid line index
            
        Returns:
            float: Y coordinate in world space
        """
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def update_vertical_lines(self) -> None:
        """
        Update all vertical grid lines with perspective transformation.
        
        Each vertical line extends from Y=0 to Y=screen_height and is
        transformed to create the tunnel perspective effect.
        """
        # Calculate line indices centered around 0
        start_index = -int(self.V_NB_LINES / 2) + 1
        
        for i in range(start_index, start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            
            # Transform line endpoints
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            
            # Update line points
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self) -> None:
        """
        Initialize horizontal grid lines.
        
        Creates white Line objects that will form the horizontal components
        of the 3D grid tunnel effect.
        """
        with self.canvas:
            Color(1, 1, 1)  # White color for grid lines
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self) -> None:
        """
        Update all horizontal grid lines with perspective transformation.
        
        Each horizontal line spans the width of the tunnel and is
        transformed to create the perspective effect.
        """
        # Calculate grid boundaries
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        # Get X boundaries for horizontal lines
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        
        # Update each horizontal line
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            
            # Transform line endpoints
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            
            # Update line points
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    # ========================================
    # MAIN GAME LOOP
    # ========================================

    def update(self, dt: float) -> None:
        """
        Main game loop called 60 times per second.
        
        Handles:
        - Updating all visual elements (grid, tiles, ship)
        - Game physics (movement, scrolling)
        - Score tracking
        - Collision detection and game over logic
        
        Args:
            dt (float): Delta time since last frame
        """
        # Calculate frame-rate independent time factor
        time_factor = dt * 60

        # Update all visual elements
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        # Handle game physics only when game is active
        if not self.state_game_over and self.state_game_has_started:
            # Vertical movement (forward motion)
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor

            # Handle score increment when crossing grid lines
            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = "SCORE: " + str(self.current_y_loop)
                self.generate_tiles_coordinates()

            # Horizontal movement (left/right steering)
            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        # Check for game over (collision detection)
        # Note: Logic is inverted - collision means game over
        if not self.check_ship_collisions() and not self.state_game_over:
            self.state_game_over = True
            self.menu_title = "G  A  M  E    O  V  E  R"
            self.menu_button_title = "RESTART"
            self.menu_widget.opacity = 1
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_voice_game_over, 3)
            print("GAME OVER")

    def play_voice_game_over(self, dt: float) -> None:
        """
        Play game over voice announcement after a delay.
        
        Args:
            dt (float): Delta time (unused, required by Clock.schedule_once)
        """
        if self.state_game_over:
            self.sound_gameover_voice.play()

    # ========================================
    # MENU SYSTEM
    # ========================================

    def on_menu_button_pressed(self) -> None:
        """
        Handle menu button press events.
        
        Manages both game start and restart functionality:
        - Plays appropriate sound effect
        - Starts background music
        - Resets game state
        - Hides menu and starts gameplay
        """
        print("BOUTON")  # Debug output
        
        # Play appropriate sound based on game state
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        
        # Start background music and reset game
        self.sound_music1.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0


class GalaxyApp(App):
    """
    Main Kivy application class.
    
    Minimal implementation that starts the Galaxy Runner game.
    The App class handles application lifecycle and window management.
    """
    pass


# ========================================
# APPLICATION ENTRY POINT
# ========================================
if __name__ == "__main__":
    GalaxyApp().run()