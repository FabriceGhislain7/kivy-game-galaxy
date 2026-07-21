from src.galaxy_runner.core import aabb_overlap, clamp, next_player_x


def test_clamp_bounds() -> None:
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(11, 0, 10) == 10


def test_aabb_overlap_true() -> None:
    assert aabb_overlap(0, 0, 10, 10, 5, 5, 10, 10)


def test_aabb_overlap_false() -> None:
    assert not aabb_overlap(0, 0, 10, 10, 11, 11, 2, 2)


def test_next_player_x() -> None:
    assert next_player_x(10, 1, 100, 0.1, 200) == 20
    assert next_player_x(10, -1, 100, 0.2, 200) == 0
    assert next_player_x(195, 1, 100, 0.2, 200) == 200
