"""
Galaxy Runner - 3D Perspective Transformation Module

This module provides mathematical transformation functions for converting 
2D world coordinates into perspective-transformed screen coordinates, 
creating a realistic 3D tunnel effect.

The perspective system uses a vanishing point to simulate depth perception,
making distant objects appear smaller and converge toward a central point.

Author: [Your Name]
Version: 1.0
License: MIT
"""

from typing import Tuple


def transform(self, x: float, y: float) -> Tuple[int, int]:
    """
    Main transformation function that applies the current transformation mode.
    
    This function serves as a switch between different transformation modes:
    - 2D mode: For debugging or flat display (commented out)
    - Perspective mode: For 3D tunnel effect (default)
    
    Args:
        x (float): X coordinate in world space
        y (float): Y coordinate in world space
        
    Returns:
        Tuple[int, int]: Transformed screen coordinates (x, y)
    """
    return self.transform_perspective(x, y)


def transform_2D(self, x: float, y: float) -> Tuple[int, int]:
    """
    Simple 2D transformation that preserves original coordinates.
    
    This function is primarily used for debugging purposes when you want
    to see the game world without perspective distortion. It simply
    converts floating-point coordinates to integers without any
    mathematical transformation.
    
    Args:
        x (float): X coordinate in world space
        y (float): Y coordinate in world space
        
    Returns:
        Tuple[int, int]: Same coordinates converted to integers
    """
    return int(x), int(y)


def transform_perspective(self, x: float, y: float) -> Tuple[int, int]:
    """
    Apply 3D perspective transformation to convert world coordinates to screen coordinates.
    
    This function creates a realistic tunnel effect by:
    1. Normalizing Y coordinates relative to the perspective point
    2. Calculating distance from the vanishing point
    3. Applying a perspective factor that increases exponentially with distance
    4. Transforming X coordinates based on this perspective factor
    
    Mathematical approach:
    - Uses a vanishing point (perspective_point_x, perspective_point_y)
    - Objects closer to the vanishing point appear smaller
    - Uses pow(factor_y, 4) for realistic perspective curve
    - Prevents division by zero with lin_y clamping
    
    Args:
        x (float): X coordinate in world space
        y (float): Y coordinate in world space
        
    Returns:
        Tuple[int, int]: Perspective-transformed screen coordinates
    """
    lin_y = y * self.perspective_point_y / self.height
    
    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y
    
    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - lin_y
    
    factor_y = diff_y / self.perspective_point_y
    factor_y = pow(factor_y, 4)
    
    offset_x = diff_x * factor_y
    tr_x = self.perspective_point_x + offset_x
    tr_y = self.perspective_point_y - factor_y * self.perspective_point_y
    
    return int(tr_x), int(tr_y)