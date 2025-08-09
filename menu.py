"""
Galaxy Runner - Menu Widget Module

This module provides the MenuWidget class, which manages the game's menu system
including the start screen and game over overlay. The widget uses opacity-based
visibility control to show/hide the menu interface.

The menu system supports:
- Dynamic title text (game title or game over message)
- Dynamic button text (start or restart)
- Opacity-based interaction control
- Seamless integration with the main game widget

Author: [Your Name]
Version: 1.0
License: MIT
"""

from typing import Union
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget


class MenuWidget(RelativeLayout):
    """
    Menu overlay widget that handles start screen and game over functionality.
    
    This widget serves as an overlay that appears on top of the game during:
    - Initial game start (showing title and "START" button)
    - Game over state (showing "GAME OVER" and "RESTART" button)
    
    The widget uses opacity-based visibility control:
    - opacity = 1: Menu visible and interactive
    - opacity = 0: Menu hidden and non-interactive
    
    Key Features:
    - Smart touch event filtering based on visibility
    - Dynamic content through parent widget properties
    - Overlay design that doesn't interfere with game rendering
    - Seamless show/hide transitions
    
    UI Elements (defined in menu.kv):
    - Semi-transparent background overlay
    - Dynamic title label (menu_title property from parent)
    - Action button (menu_button_title property from parent)
    - Custom fonts for space-themed appearance
    """

    def on_touch_down(self, touch) -> Union[bool, None]:
        """
        Handle touch events with opacity-based interaction filtering.
        
        This method provides smart interaction control by checking the widget's
        opacity before processing touch events. When the menu is hidden 
        (opacity = 0), touch events are ignored, allowing the underlying 
        game to receive input. When visible (opacity = 1), normal touch 
        processing occurs.
        
        Touch Event Flow:
        1. Check if menu is visible (opacity != 0)
        2. If hidden: Return False (don't consume the touch event)
        3. If visible: Process touch normally through parent class
        
        Args:
            touch: Kivy touch object containing:
                - touch.x, touch.y: Touch coordinates
                - touch.time_start: When touch began
                - Other touch properties and methods
                
        Returns:
            Union[bool, None]:
                - False: When menu is hidden (opacity == 0)
                - bool/None: Result from parent class when menu is visible
                
        Design Benefits:
        - Prevents menu interaction when hidden
        - Allows game controls to work when menu is invisible
        - Maintains proper event propagation chain
        - Enables smooth transitions between menu and game states
        
        Technical Details:
        The opacity check uses == 0 rather than <= 0 because:
        - Opacity 0 specifically indicates "completely hidden"
        - Values between 0 and 1 represent partial transparency
        - Partially transparent menus should still be interactive
        - This allows for fade-in/fade-out animations while maintaining interaction
        
        Example Usage:
        ```python
        # Hide menu and make it non-interactive
        menu_widget.opacity = 0
        
        # Show menu and make it interactive  
        menu_widget.opacity = 1
        
        # Partially visible but still interactive
        menu_widget.opacity = 0.8
        ```
        """
        # Check if menu is completely hidden
        if self.opacity == 0:
            # Menu is invisible, don't consume the touch event
            # This allows underlying widgets (the game) to receive input
            return False
        
        # Menu is visible (any opacity > 0), process touch normally
        # Delegate to parent class for standard RelativeLayout touch handling
        return super(RelativeLayout, self).on_touch_down(touch)