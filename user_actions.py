"""
Galaxy Runner - User Input Management Module

This module handles all user input for the Galaxy Runner game, providing
cross-platform support for both desktop (keyboard) and mobile (touch) controls.

The input system manages horizontal movement through continuous velocity control:
- Left input: Move left (positive SPEED_X)
- Right input: Move right (negative SPEED_X)  
- No input: Stop movement (speed = 0)

Author: [Your Name]
Version: 1.0
License: MIT
"""

from typing import Tuple, List, Optional
from kivy.uix.relativelayout import RelativeLayout


def keyboard_closed(self) -> None:
    """
    Clean up keyboard event bindings when keyboard is closed.
    
    This method is called when the keyboard input system is being shut down
    (e.g., when the application loses focus or is closed). It properly
    unbinds all keyboard event handlers and releases the keyboard reference
    to prevent memory leaks.
    
    Note:
        This cleanup is essential for proper resource management in Kivy applications.
        Without proper unbinding, event handlers could remain in memory even after
        the widget is destroyed.
    """
    # Unbind keyboard event handlers
    self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    self._keyboard.unbind(on_key_up=self._on_keyboard_up)
    
    # Release keyboard reference
    self._keyboard = None


def on_keyboard_down(self, keyboard, keycode: Tuple[int, str], text: str, modifiers: List[str]) -> bool:
    """
    Handle keyboard key press events for desktop platforms.
    
    Processes keyboard input and translates it into horizontal movement commands.
    Uses continuous velocity control where holding a key maintains movement
    in that direction.
    
    Movement mapping:
    - Left Arrow Key: Move left (positive SPEED_X)
    - Right Arrow Key: Move right (negative SPEED_X)
    - Other keys: Ignored
    
    Args:
        keyboard: Kivy keyboard object (unused)
        keycode (Tuple[int, str]): Key information tuple containing:
            - keycode[0]: Numeric key code
            - keycode[1]: String key name (e.g., 'left', 'right')
        text (str): Text representation of the key (unused)
        modifiers (List[str]): List of modifier keys (e.g., ['shift', 'ctrl'])
        
    Returns:
        bool: Always returns True to indicate the key event was handled
        
    Technical Details:
        The coordinate system uses:
        - Positive SPEED_X: Ship moves left (grid shifts right)
        - Negative SPEED_X: Ship moves right (grid shifts left)
        
        This creates the illusion that the ship is moving horizontally
        while actually the entire tunnel grid is shifting around the
        stationary ship position.
    """
    if keycode[1] == 'left':
        # Move left: Set positive horizontal speed
        self.current_speed_x = self.SPEED_X
    elif keycode[1] == 'right':
        # Move right: Set negative horizontal speed  
        self.current_speed_x = -self.SPEED_X
    
    # Return True to indicate we handled this key event
    return True


def on_keyboard_up(self, keyboard, keycode: Tuple[int, str]) -> None:
    """
    Handle keyboard key release events for desktop platforms.
    
    When any key is released, stops horizontal movement immediately.
    This provides responsive control where movement only occurs while
    a key is actively being held down.
    
    Args:
        keyboard: Kivy keyboard object (unused)
        keycode (Tuple[int, str]): Key information tuple
            - keycode[0]: Numeric key code  
            - keycode[1]: String key name
            
    Note:
        This function stops movement regardless of which key was released.
        Since only left/right arrows trigger movement, this behavior is
        correct and provides immediate responsiveness.
    """
    # Stop horizontal movement when any key is released
    self.current_speed_x = 0


def on_touch_down(self, touch) -> bool:
    """
    Handle touch/mouse press events for mobile and desktop platforms.
    
    Implements screen-split touch controls where the screen is divided
    into left and right halves. Touching either half triggers movement
    in that direction.
    
    Touch Control Mapping:
    - Touch left half of screen: Move left (positive SPEED_X)
    - Touch right half of screen: Move right (negative SPEED_X)
    
    Game State Filtering:
    Only processes input when:
    - Game is not over (state_game_over = False)
    - Game has started (state_game_has_started = True)
    
    Args:
        touch: Kivy touch object containing:
            - touch.x: X coordinate of touch point
            - touch.y: Y coordinate of touch point
            - Other touch properties (pressure, etc.)
            
    Returns:
        bool: Result from parent class touch handling
        
    Technical Details:
        Screen division logic:
        - Left half: touch.x < self.width / 2
        - Right half: touch.x >= self.width / 2
        
        The function uses the same coordinate system as keyboard input
        for consistency in movement behavior.
    """
    # Only process input during active gameplay
    if not self.state_game_over and self.state_game_has_started:
        
        if touch.x < self.width / 2:
            # Touch on left half of screen: Move left
            self.current_speed_x = self.SPEED_X
        else:
            # Touch on right half of screen: Move right
            self.current_speed_x = -self.SPEED_X
    
    # Call parent class touch handler to maintain proper event propagation
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch) -> None:
    """
    Handle touch/mouse release events for mobile and desktop platforms.
    
    When touch input is released, immediately stops horizontal movement.
    This provides the same responsive control behavior as keyboard input,
    where movement only occurs while input is actively being applied.
    
    Args:
        touch: Kivy touch object (unused in this implementation)
        
    Note:
        Unlike keyboard input, this function doesn't need to check which
        area was touched since any touch release should stop movement.
        This ensures consistent behavior regardless of where the user
        lifts their finger.
        
    Design Decision:
        The function stops movement unconditionally rather than tracking
        which touch started the movement. This simplifies the logic and
        provides immediate response, which is preferable for this type
        of game control.
    """
    # Stop horizontal movement when touch is released
    self.current_speed_x = 0