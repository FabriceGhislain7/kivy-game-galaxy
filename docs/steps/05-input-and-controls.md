# Step 05 - Input and Controls

## Goal
Implement responsive keyboard controls.

Supported keys:

- left / A
- right / D
- R (restart)

Important points:

- bind keyboard in widget init
- unbind safely when keyboard closes
- keep movement state booleans (`_pressed_left`, `_pressed_right`)
