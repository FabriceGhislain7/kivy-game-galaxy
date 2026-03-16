"""Main game module for Galaxy Runner."""

from __future__ import annotations

import random
from typing import List, Optional, Tuple

from kivy import platform
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.audio import Sound, SoundLoader
from kivy.core.window import Window
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout

Config.set("graphics", "width", "900")
Config.set("graphics", "height", "400")

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    """Main game widget handling rendering, state, and interaction."""

    from transforms import transform, transform_2D, transform_perspective
    from user_actions import (
        keyboard_closed,
        on_keyboard_down,
        on_keyboard_up,
        on_touch_down,
        on_touch_up,
    )

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 8
    V_LINES_SPACING = 0.4
    H_NB_LINES = 8
    H_LINES_SPACING = 0.15

    SPEED = 0.8
    SPEED_X = 3.5

    NB_TILES = 16

    SHIP_WIDTH = 0.1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04

    menu_title = StringProperty("G   A   L   A   X   Y")
    menu_button_title = StringProperty("START")
    score_txt = StringProperty("SCORE: 0")

    sound_begin: Optional[Sound] = None
    sound_galaxy: Optional[Sound] = None
    sound_gameover_impact: Optional[Sound] = None
    sound_gameover_voice: Optional[Sound] = None
    sound_music1: Optional[Sound] = None
    sound_restart: Optional[Sound] = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.vertical_lines: List[Line] = []
        self.horizontal_lines: List[Line] = []
        self.tiles: List[Quad] = []
        self.tiles_coordinates: List[Tuple[int, int]] = []
        self.ship_coordinates: List[Tuple[float, float]] = [(0.0, 0.0)] * 3
        self.ship: Optional[Triangle] = None

        self.current_offset_y = 0.0
        self.current_y_loop = 0
        self.current_speed_x = 0.0
        self.current_offset_x = 0.0

        self.state_game_over = False
        self.state_game_has_started = False

        self._keyboard = None

        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            if self._keyboard is not None:
                self._keyboard.bind(on_key_down=self.on_keyboard_down)
                self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0 / 60.0)
        if self.sound_galaxy:
            self.sound_galaxy.play()

    def _load_sound(self, path: str, volume: float) -> Optional[Sound]:
        sound = SoundLoader.load(path)
        if sound is None:
            print(f"[audio] could not load: {path}")
            return None
        sound.volume = volume
        return sound

    def init_audio(self) -> None:
        self.sound_begin = self._load_sound("audio/begin.wav", 0.25)
        self.sound_galaxy = self._load_sound("audio/galaxy.wav", 0.25)
        self.sound_gameover_impact = self._load_sound("audio/gameover_impact.wav", 0.6)
        self.sound_gameover_voice = self._load_sound("audio/gameover_voice.wav", 0.25)
        self.sound_music1 = self._load_sound("audio/music1.wav", 1.0)
        self.sound_restart = self._load_sound("audio/restart.wav", 0.25)

    def reset_game(self) -> None:
        self.current_offset_y = 0.0
        self.current_y_loop = 0
        self.current_speed_x = 0.0
        self.current_offset_x = 0.0
        self.tiles_coordinates = []
        self.score_txt = "SCORE: 0"
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.state_game_over = False

    @staticmethod
    def is_desktop() -> bool:
        return platform in ("linux", "windows", "macosx")

    def init_ship(self) -> None:
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self) -> None:
        if self.ship is None:
            return

        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height

        self.ship_coordinates[0] = (center_x - half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collisions(self) -> bool:
        for ti_x, ti_y in self.tiles_coordinates:
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x: int, ti_y: int) -> bool:
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)

        for px, py in self.ship_coordinates:
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def init_tiles(self) -> None:
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self) -> None:
        for i in range(10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self) -> None:
        last_x = 0
        last_y = 0

        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if self.tiles_coordinates:
            last_x, last_tile_y = self.tiles_coordinates[-1]
            last_y = last_tile_y + 1

        for _ in range(len(self.tiles_coordinates), self.NB_TILES):
            direction = random.randint(0, 2)

            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1

            if last_x <= start_index:
                direction = 1
            if last_x >= end_index:
                direction = 2

            self.tiles_coordinates.append((last_x, last_y))

            if direction == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            elif direction == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

    def get_tile_coordinates(self, ti_x: int, ti_y: int) -> Tuple[float, float]:
        adjusted_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(adjusted_y)
        return x, y

    def update_tiles(self) -> None:
        for i in range(self.NB_TILES):
            tile = self.tiles[i]
            tile_x, tile_y = self.tiles_coordinates[i]

            xmin, ymin = self.get_tile_coordinates(tile_x, tile_y)
            xmax, ymax = self.get_tile_coordinates(tile_x + 1, tile_y + 1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def init_vertical_lines(self) -> None:
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index: int) -> float:
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        return central_line_x + offset * spacing + self.current_offset_x

    def get_line_y_from_index(self, index: int) -> float:
        spacing_y = self.H_LINES_SPACING * self.height
        return index * spacing_y - self.current_offset_y

    def update_vertical_lines(self) -> None:
        start_index = -int(self.V_NB_LINES / 2) + 1

        for local_idx, line_index in enumerate(range(start_index, start_index + self.V_NB_LINES)):
            line_x = self.get_line_x_from_index(line_index)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[local_idx].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self) -> None:
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self) -> None:
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)

        for i in range(self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt: float) -> None:
        time_factor = dt * 60

        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = f"SCORE: {self.current_y_loop}"
                self.generate_tiles_coordinates()

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        if not self.check_ship_collisions() and not self.state_game_over:
            self.state_game_over = True
            self.menu_title = "G  A  M  E    O  V  E  R"
            self.menu_button_title = "RESTART"
            self.menu_widget.opacity = 1
            if self.sound_music1:
                self.sound_music1.stop()
            if self.sound_gameover_impact:
                self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_voice_game_over, 3)

    def play_voice_game_over(self, _dt: float) -> None:
        if self.state_game_over and self.sound_gameover_voice:
            self.sound_gameover_voice.play()

    def on_menu_button_pressed(self) -> None:
        if self.state_game_over:
            if self.sound_restart:
                self.sound_restart.play()
        else:
            if self.sound_begin:
                self.sound_begin.play()

        if self.sound_music1:
            self.sound_music1.play()

        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0


class GalaxyApp(App):
    """Kivy application entry point."""


if __name__ == "__main__":
    GalaxyApp().run()
