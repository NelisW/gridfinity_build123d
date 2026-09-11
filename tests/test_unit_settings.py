import unittest

from gridfinity_build123d import get_grid_size, set_grid_size
from gridfinity_build123d.constants import gridfinity_standard

GRIDFINITY_DEFAULT = 42


class GridSizeSettingTest(unittest.TestCase):
    def tearDown(self) -> None:
        set_grid_size(GRIDFINITY_DEFAULT)

    def test_default_is_gridfinity_standard(self) -> None:
        self.assertEqual(GRIDFINITY_DEFAULT, get_grid_size())

    def test_set_and_get_roundtrip(self) -> None:
        set_grid_size(61)
        self.assertEqual(61, get_grid_size())

    def test_set_updates_constant(self) -> None:
        set_grid_size(61)
        self.assertEqual(61, gridfinity_standard.grid.size)

    def test_set_accepts_float(self) -> None:
        set_grid_size(49.5)
        self.assertAlmostEqual(49.5, get_grid_size())

    def test_reset_back_to_default(self) -> None:
        set_grid_size(61)
        set_grid_size(GRIDFINITY_DEFAULT)
        self.assertEqual(GRIDFINITY_DEFAULT, get_grid_size())

    def test_zero_raises(self) -> None:
        with self.assertRaises(ValueError):
            set_grid_size(0)

    def test_negative_raises(self) -> None:
        with self.assertRaises(ValueError):
            set_grid_size(-42)

    def test_at_or_below_twice_corner_radius_raises(self) -> None:
        # Below this the corner fillets self intersect.
        for size in (8, 7.9, 4):
            with self.subTest(size=size), self.assertRaises(ValueError):
                set_grid_size(size)

    def test_just_above_twice_corner_radius_is_allowed(self) -> None:
        set_grid_size(8.5)
        self.assertAlmostEqual(8.5, get_grid_size())

    def test_failed_set_leaves_value_untouched(self) -> None:
        set_grid_size(61)
        with self.assertRaises(ValueError):
            set_grid_size(-1)
        self.assertEqual(61, get_grid_size())
