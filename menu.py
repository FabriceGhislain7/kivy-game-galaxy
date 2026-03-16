"""Menu overlay widget for start/restart flow."""

from __future__ import annotations

from typing import Optional

from kivy.uix.relativelayout import RelativeLayout


class MenuWidget(RelativeLayout):
    """Overlay menu that intercepts touches only while visible."""

    def on_touch_down(self, touch) -> Optional[bool]:
        if self.opacity == 0:
            return False
        return super().on_touch_down(touch)
