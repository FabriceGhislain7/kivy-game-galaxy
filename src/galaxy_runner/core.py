"""Pure gameplay logic utilities (no Kivy dependency)."""

from __future__ import annotations


def clamp(value: float, low: float, high: float) -> float:
    """Clamp a value to a closed interval."""
    return max(low, min(high, value))


def aabb_overlap(
    ax: float,
    ay: float,
    aw: float,
    ah: float,
    bx: float,
    by: float,
    bw: float,
    bh: float,
) -> bool:
    """Return True when two axis-aligned rectangles overlap."""
    return (ax < bx + bw) and (ax + aw > bx) and (ay < by + bh) and (ay + ah > by)


def next_player_x(current_x: float, direction: int, speed: float, dt: float, max_x: float) -> float:
    """Compute bounded horizontal movement for player."""
    return clamp(current_x + direction * speed * dt, 0, max_x)
