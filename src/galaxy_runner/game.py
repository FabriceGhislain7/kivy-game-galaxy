"""Core gameplay widget for Galaxy Runner."""

from __future__ import annotations

import random
from dataclasses import dataclass

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, Quad, Rectangle, Triangle
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.widget import Widget

from . import config
from .core import clamp

Rgb = tuple[float, float, float]
ObstaclePalette = tuple[Rgb, Rgb, Rgb]


@dataclass
class Star:
    """Single background star state."""

    x: float
    y: float
    speed: float
    size: float
    rect: Rectangle


@dataclass
class Obstacle:
    """Obstacle in depth-space rendered as a pseudo-3D block."""

    lane: int
    depth: float
    color_front: Color
    color_top: Color
    color_side: Color
    quad_front: Quad
    quad_top: Quad
    quad_side: Quad


class RunnerWidget(Widget):
    """Main game area containing pseudo-3D tunnel gameplay."""

    score = NumericProperty(0)
    status_text = StringProperty("Press LEFT/RIGHT (or A/D) to move")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        if self._keyboard is not None:
            self._keyboard.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

        self._pressed_left = False
        self._pressed_right = False
        self._is_game_over = False

        self._player_offset = 0.0
        self._spawn_timer = 0.0
        self._difficulty_timer = 0.0
        self._obstacle_speed = float(config.OBSTACLE_SPEED_START)
        self._last_lane = 0

        self._stars: list[Star] = []
        self._obstacles: list[Obstacle] = []
        self._grid_vertical: list[Line] = []
        self._grid_horizontal: list[Line] = []

        with self.canvas:
            Color(0.02, 0.03, 0.08, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)

            Color(0.75, 0.85, 1, 0.85)
            for _ in range(config.STAR_COUNT):
                self._stars.append(self._build_star())

            Color(0.16, 0.88, 1, 0.85)
            for _ in range(config.GRID_VERTICAL_LINES):
                self._grid_vertical.append(Line(width=1.05))
            for _ in range(config.GRID_HORIZONTAL_LINES):
                self._grid_horizontal.append(Line(width=1.0))

            Color(1, 0.36, 0.5, 0.92)
            self._ship = Triangle()

        self.bind(size=self._on_resize, pos=self._on_resize)
        Clock.schedule_interval(self._update, 1.0 / config.FPS)

    def _build_star(self) -> Star:
        size = random.uniform(1.0, 2.8)
        x = random.uniform(0, max(1.0, self.width or config.WINDOW_WIDTH))
        y = random.uniform(0, max(1.0, self.height or config.WINDOW_HEIGHT))
        speed = random.uniform(20, 100)
        rect = Rectangle(pos=(x, y), size=(size, size))
        return Star(x=x, y=y, speed=speed, size=size, rect=rect)

    @property
    def _horizon_y(self) -> float:
        return self.height * config.HORIZON_Y_RATIO

    @property
    def _tunnel_half_width_bottom(self) -> float:
        return self.width * config.TUNNEL_HALF_WIDTH_BOTTOM_RATIO

    def _on_resize(self, *_args) -> None:
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _on_keyboard_closed(self) -> None:
        if self._keyboard is not None:
            self._keyboard.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
            self._keyboard = None

    def _on_key_down(self, _keyboard, keycode, _text, _modifiers) -> bool:
        key = keycode[1].lower()

        if key == "r" and self._is_game_over:
            self.restart()
            return True
        if key in ("left", "a"):
            self._pressed_left = True
            return True
        if key in ("right", "d"):
            self._pressed_right = True
            return True
        return False

    def _on_key_up(self, _keyboard, keycode) -> bool:
        key = keycode[1].lower()

        if key in ("left", "a"):
            self._pressed_left = False
            return True
        if key in ("right", "d"):
            self._pressed_right = False
            return True
        return False

    def restart(self) -> None:
        self.score = 0
        self._spawn_timer = 0.0
        self._difficulty_timer = 0.0
        self._obstacle_speed = float(config.OBSTACLE_SPEED_START)
        self._is_game_over = False
        self._player_offset = 0.0
        self.status_text = "Run active"

        for obstacle in self._obstacles:
            self.canvas.remove(obstacle.quad_front)
            self.canvas.remove(obstacle.quad_top)
            self.canvas.remove(obstacle.quad_side)
            self.canvas.remove(obstacle.color_front)
            self.canvas.remove(obstacle.color_top)
            self.canvas.remove(obstacle.color_side)
        self._obstacles.clear()

    def _project(self, lane_value: float, depth: float) -> tuple[float, float, float]:
        """Map logical lane/depth into screen x/y/half-width."""
        d = clamp(depth, 0.0, 1.0)
        width_factor = d**1.72

        y = self._horizon_y - (self._horizon_y - config.TUNNEL_BOTTOM_Y) * d
        half_width = config.TUNNEL_HALF_WIDTH_TOP + (
            self._tunnel_half_width_bottom - config.TUNNEL_HALF_WIDTH_TOP
        ) * width_factor

        lane_scale = 0.64
        x = self.center_x + (lane_value * half_width * lane_scale)
        return x, y, half_width

    def _update_player(self, dt: float) -> None:
        if self._is_game_over:
            return

        direction = 0
        if self._pressed_left:
            direction -= 1
        if self._pressed_right:
            direction += 1

        self._player_offset = clamp(
            self._player_offset + direction * config.PLAYER_SPEED * dt,
            -config.PLAYER_MAX_OFFSET,
            config.PLAYER_MAX_OFFSET,
        )

    @staticmethod
    def _random_obstacle_palette() -> ObstaclePalette:
        palettes = [
            ((0.20, 0.87, 1.00), (0.52, 0.95, 1.00), (0.06, 0.60, 0.82)),
            ((1.00, 0.54, 0.16), (1.00, 0.74, 0.38), (0.80, 0.35, 0.05)),
            ((0.70, 0.46, 1.00), (0.84, 0.70, 1.00), (0.44, 0.24, 0.82)),
            ((1.00, 0.28, 0.60), (1.00, 0.56, 0.78), (0.78, 0.14, 0.40)),
        ]
        return random.choice(palettes)

    def _spawn_obstacle(self) -> None:
        lane_options = (-1, 0, 1)
        lane = random.choice(lane_options)
        if lane == self._last_lane and random.random() < 0.45:
            lane = random.choice(lane_options)
        self._last_lane = lane

        front_rgb, top_rgb, side_rgb = self._random_obstacle_palette()

        with self.canvas:
            color_front = Color(*front_rgb, 0.95)
            quad_front = Quad()
            color_top = Color(*top_rgb, 0.98)
            quad_top = Quad()
            color_side = Color(*side_rgb, 0.96)
            quad_side = Quad()

        self._obstacles.append(
            Obstacle(
                lane=lane,
                depth=config.OBSTACLE_DEPTH_START,
                color_front=color_front,
                color_top=color_top,
                color_side=color_side,
                quad_front=quad_front,
                quad_top=quad_top,
                quad_side=quad_side,
            )
        )

    def _update_obstacles_logic(self, dt: float) -> None:
        if self._is_game_over:
            return

        for obstacle in self._obstacles:
            obstacle.depth += self._obstacle_speed * dt

        alive: list[Obstacle] = []
        for obstacle in self._obstacles:
            if obstacle.depth <= config.OBSTACLE_DEPTH_END:
                alive.append(obstacle)
            else:
                self.canvas.remove(obstacle.quad_front)
                self.canvas.remove(obstacle.quad_top)
                self.canvas.remove(obstacle.quad_side)
                self.canvas.remove(obstacle.color_front)
                self.canvas.remove(obstacle.color_top)
                self.canvas.remove(obstacle.color_side)
        self._obstacles = alive

    def _update_obstacles_projection(self) -> None:
        for obstacle in self._obstacles:
            x, y, _ = self._project(obstacle.lane - self._player_offset * 0.45, obstacle.depth)
            d = clamp(obstacle.depth, 0.0, 1.0)

            width = config.OBSTACLE_BASE_WIDTH * (0.24 + d * 1.10)
            height = config.OBSTACLE_BASE_HEIGHT * (0.28 + d * 1.04)
            extrude = max(3.0, height * 0.36)
            skew = max(2.0, width * 0.10)

            # Front face
            x1, y1 = x - width / 2, y - height / 2
            x2, y2 = x - width / 2, y + height / 2
            x3, y3 = x + width / 2, y + height / 2
            x4, y4 = x + width / 2, y - height / 2
            obstacle.quad_front.points = [x1, y1, x2, y2, x3, y3, x4, y4]

            # Top face
            tx1, ty1 = x2, y2
            tx2, ty2 = x2 + skew, y2 + extrude
            tx3, ty3 = x3 + skew, y3 + extrude
            tx4, ty4 = x3, y3
            obstacle.quad_top.points = [tx1, ty1, tx2, ty2, tx3, ty3, tx4, ty4]

            # Side face (right)
            sx1, sy1 = x3, y3
            sx2, sy2 = x3 + skew, y3 + extrude
            sx3, sy3 = x4 + skew, y4 + extrude
            sx4, sy4 = x4, y4
            obstacle.quad_side.points = [sx1, sy1, sx2, sy2, sx3, sy3, sx4, sy4]

            # Slight atmospheric fade with depth
            alpha = 0.30 + 0.70 * d
            obstacle.color_front.a = alpha
            obstacle.color_top.a = min(1.0, alpha + 0.08)
            obstacle.color_side.a = max(0.2, alpha - 0.06)

    def _check_collisions(self) -> None:
        if self._is_game_over:
            return

        player_lane = self._player_offset * 1.35
        for obstacle in self._obstacles:
            if obstacle.depth >= 0.90 and abs(obstacle.lane - player_lane) < 0.52:
                self._is_game_over = True
                self.status_text = "Game Over - Press R to restart"
                return

    def _update_stars(self, dt: float) -> None:
        drift = self._player_offset * 36.0
        height = max(1.0, self.height)
        width = max(1.0, self.width)

        for star in self._stars:
            star.y -= star.speed * dt
            star.x -= drift * dt

            if star.y < -star.size:
                star.y = height + star.size
                star.x = random.uniform(0, width)
            if star.x < -star.size:
                star.x = width + star.size
            elif star.x > width + star.size:
                star.x = -star.size

            star.rect.pos = (star.x, star.y)
            scale = 1.0 + (1.0 - star.y / height) * 0.9
            star.rect.size = (star.size * scale, star.size * scale)

    def _update_tunnel_grid(self) -> None:
        start = -int(config.GRID_VERTICAL_LINES / 2)
        for i, line in enumerate(self._grid_vertical):
            lane_value = (start + i) / max(1.0, start * -1)
            x1, y1, _ = self._project(lane_value - self._player_offset * 0.22, 0.02)
            x2, y2, _ = self._project(lane_value - self._player_offset * 0.22, 1.0)
            line.points = [x1, y1, x2, y2]

        for i, line in enumerate(self._grid_horizontal):
            depth = i / max(1, config.GRID_HORIZONTAL_LINES - 1)
            xl, y, _ = self._project(-1.05 - self._player_offset * 0.22, depth)
            xr, _, _ = self._project(1.05 - self._player_offset * 0.22, depth)
            line.points = [xl, y, xr, y]

    def _update_ship(self) -> None:
        ship_x = self.center_x + self._player_offset * self._tunnel_half_width_bottom * 0.62
        base_y = config.PLAYER_BASE_Y
        half_w = config.PLAYER_WIDTH / 2
        height = config.PLAYER_HEIGHT

        x1, y1 = ship_x - half_w, base_y
        x2, y2 = ship_x, base_y + height
        x3, y3 = ship_x + half_w, base_y
        self._ship.points = [x1, y1, x2, y2, x3, y3]

    def _update(self, dt: float) -> None:
        self._update_player(dt)

        self._spawn_timer += dt
        if not self._is_game_over and self._spawn_timer >= config.OBSTACLE_SPAWN_INTERVAL:
            self._spawn_timer = 0.0
            self._spawn_obstacle()

        self._update_obstacles_logic(dt)
        self._check_collisions()

        if not self._is_game_over:
            self.score += dt * config.SCORE_RATE
            self._difficulty_timer += dt
            while self._difficulty_timer >= config.OBSTACLE_SPEED_INCREASE_INTERVAL:
                self._difficulty_timer -= config.OBSTACLE_SPEED_INCREASE_INTERVAL
                self._obstacle_speed += config.OBSTACLE_SPEED_INCREMENT
            self.status_text = "Run active"

        self._update_stars(dt)
        self._update_tunnel_grid()
        self._update_obstacles_projection()
        self._update_ship()
