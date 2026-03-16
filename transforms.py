"""Coordinate transformations for the Galaxy Runner perspective effect."""

from __future__ import annotations

from typing import Tuple


def transform(self, x: float, y: float) -> Tuple[int, int]:
    """Dispatch transformation mode used by the renderer."""
    return self.transform_perspective(x, y)


def transform_2D(self, x: float, y: float) -> Tuple[int, int]:
    """Identity transform useful for debugging geometry without perspective."""
    return int(x), int(y)


def transform_perspective(self, x: float, y: float) -> Tuple[int, int]:
    """Project a world point into perspective screen space."""
    if self.height <= 0 or self.perspective_point_y <= 0:
        return int(x), int(y)

    lin_y = y * self.perspective_point_y / self.height
    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y

    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - lin_y

    factor_y = (diff_y / self.perspective_point_y) ** 4

    tr_x = self.perspective_point_x + (diff_x * factor_y)
    tr_y = self.perspective_point_y - (factor_y * self.perspective_point_y)

    return int(tr_x), int(tr_y)
