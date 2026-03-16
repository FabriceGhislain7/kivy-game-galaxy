# Changelog

All notable changes to this project are documented in this file.

The format is inspired by Keep a Changelog and follows semantic-style sections.

## [Unreleased]

### Added
- Added `LICENSE` file with MIT license text.
- Added `CONTRIBUTING.md` with contribution workflow and coding standards.
- Added this `CHANGELOG.md` to track repository evolution.

### Changed
- Rewrote `README.md` with a professional structure, setup guide, controls, troubleshooting, and architecture summary.
- Refactored `main.py` for clearer state initialization, safer keyboard binding lifecycle, and defensive audio loading.
- Improved `transforms.py` with guard conditions for invalid viewport metrics.
- Simplified and clarified `user_actions.py` keyboard/touch handlers.
- Simplified `menu.py` touch interception behavior.
- Updated `galaxy.kv` and `menu.kv` for cleaner layout definitions and UI consistency.
- Reorganized `requirements.txt` with clearer sections and Windows markers for platform-specific dependencies.
- Replaced `API_REFERENCE.md` content with a clean, consistent technical reference.

### Fixed
- Fixed keyboard unbinding logic to use the actual bound callbacks.
- Fixed potential crashes when audio assets fail to load by guarding playback calls.
- Fixed vertical line update indexing to avoid fragile negative indexing assumptions.

## [1.0.0] - 2026-02-27

### Added
- Initial public game version with Kivy-based tunnel runner gameplay.
- Procedural tile path generation and collision detection.
- Keyboard and touch control support.
- Audio assets and menu flow.
