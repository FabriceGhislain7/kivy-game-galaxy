"""Input handlers shared by MainWidget."""

from __future__ import annotations

from typing import List, Tuple


def keyboard_closed(self) -> None:
    """Release keyboard bindings when the widget loses keyboard focus."""
    if self._keyboard is None:
        return

    self._keyboard.unbind(on_key_down=self.on_keyboard_down)
    self._keyboard.unbind(on_key_up=self.on_keyboard_up)
    self._keyboard = None


def on_keyboard_down(self, _keyboard, keycode: Tuple[int, str], _text: str, _modifiers: List[str]) -> bool:
    """Set horizontal speed on left/right key press."""
    if keycode[1] == "left":
        self.current_speed_x = self.SPEED_X
    elif keycode[1] == "right":
        self.current_speed_x = -self.SPEED_X
    return True


def on_keyboard_up(self, _keyboard, _keycode: Tuple[int, str]) -> None:
    """Stop horizontal movement when keys are released."""
    self.current_speed_x = 0


def on_touch_down(self, touch) -> bool:
    """Handle touch/mouse press for mobile and desktop."""
    if not self.state_game_over and self.state_game_has_started:
        if touch.x < self.width / 2:
            self.current_speed_x = self.SPEED_X
        else:
            self.current_speed_x = -self.SPEED_X

    return super(type(self), self).on_touch_down(touch)


def on_touch_up(self, touch) -> bool:
    """Stop horizontal movement when touch/mouse is released."""
    self.current_speed_x = 0
    return super(type(self), self).on_touch_up(touch)
