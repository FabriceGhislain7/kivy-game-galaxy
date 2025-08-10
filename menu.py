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
        
        Args:
            touch: Kivy touch object containing touch coordinates and properties
                
        Returns:
            Union[bool, None]:
                - False: When menu is hidden (opacity == 0)
                - bool/None: Result from parent class when menu is visible
        """
        if self.opacity == 0:
            return False
        
        return super(RelativeLayout, self).on_touch_down(touch)