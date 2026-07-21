"""Application entrypoint and UI composition."""

from __future__ import annotations

from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from . import config
from .game import RunnerWidget

Config.set("graphics", "width", str(config.WINDOW_WIDTH))
Config.set("graphics", "height", str(config.WINDOW_HEIGHT))


class GalaxyRunnerApp(App):
    """Top-level Kivy application."""

    def build(self):
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        self.score_label = Label(text="Score: 0", size_hint=(1, 0.1), font_size=22)
        self.status_label = Label(text="Starting...", size_hint=(1, 0.08), font_size=16)
        self.game = RunnerWidget(size_hint=(1, 0.82))

        root.add_widget(self.score_label)
        root.add_widget(self.status_label)
        root.add_widget(self.game)

        self.bind(on_start=self._on_start)
        return root

    def _on_start(self, *_args):
        from kivy.clock import Clock

        Clock.schedule_interval(self._sync_hud, 1.0 / config.FPS)

    def _sync_hud(self, _dt: float):
        self.score_label.text = f"Score: {int(self.game.score)}"
        self.status_label.text = self.game.status_text


def run() -> None:
    GalaxyRunnerApp().run()
