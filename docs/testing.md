# Testing Guide

## Manual Smoke Test

1. Start app (`python main.py`)
2. Confirm player renders
3. Move with left/right arrows
4. Wait for obstacles spawn
5. Confirm collision leads to game over
6. Press `R` and confirm restart

## Regression Checklist

- No crash on window resize
- Score increments only during active run
- Restart clears obstacles and resets score
- Player remains inside screen bounds

## Future Automated Tests

- Unit test collision function
- Unit test restart state reset
- Property tests for obstacle spawn bounds
