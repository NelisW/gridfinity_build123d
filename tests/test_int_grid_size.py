import testutils
from build123d import BuildPart

from gridfinity_build123d import (
    BaseEqual,
    BasePlateBlockFrame,
    BasePlateBlockFull,
    BasePlateBlockSkeleton,
    BasePlateEqual,
    Bin,
    BottomCorners,
    Compartment,
    CompartmentsEqual,
    MagnetHole,
    set_grid_size,
)

GRIDFINITY_DEFAULT = 42
PITCH = 61
TOLERANCE = 0.5


class CustomGridSizeTest(testutils.UtilTestCase):
    """Every grid dependent object must follow a custom pitch."""

    def setUp(self) -> None:
        set_grid_size(PITCH)

    def tearDown(self) -> None:
        set_grid_size(GRIDFINITY_DEFAULT)

    def test_base(self) -> None:
        with BuildPart() as part:
            BaseEqual(grid_x=2, grid_y=1)
        self.assertVectorAlmostEqual(
            (PITCH * 2 - TOLERANCE, PITCH - TOLERANCE, 7.803553390593281),
            part.part.bounding_box().size,
        )

    def test_bin(self) -> None:
        with BuildPart() as part:
            Bin(
                BaseEqual(grid_x=2, grid_y=1),
                height_in_units=3,
                compartments=CompartmentsEqual(compartment_list=[Compartment()]),
            )
        self.assertVectorAlmostEqual(
            (PITCH * 2 - TOLERANCE, PITCH - TOLERANCE, 21),
            part.part.bounding_box().size,
        )

    def test_base_plate_frame(self) -> None:
        with BuildPart() as part:
            BasePlateEqual(size_x=2, size_y=3, baseplate_block=BasePlateBlockFrame())
        self.assertVectorAlmostEqual(
            (PITCH * 2, PITCH * 3, 4.65),
            part.part.bounding_box().size,
        )

    def test_base_plate_full(self) -> None:
        with BuildPart() as part:
            BasePlateEqual(size_x=2, size_y=3, baseplate_block=BasePlateBlockFull())
        self.assertVectorAlmostEqual(
            (PITCH * 2, PITCH * 3, 11.05),
            part.part.bounding_box().size,
        )

    def test_base_plate_skeleton(self) -> None:
        with BuildPart() as part:
            BasePlateEqual(size_x=2, size_y=2, baseplate_block=BasePlateBlockSkeleton())
        self.assertVectorAlmostEqual(
            (PITCH * 2, PITCH * 2, 11.05),
            part.part.bounding_box().size,
        )
        self.assertTrue(part.part.is_valid())

    def test_base_plate_with_feature(self) -> None:
        with BuildPart() as part:
            BasePlateEqual(
                size_x=2,
                size_y=2,
                baseplate_block=BasePlateBlockFull(features=MagnetHole(BottomCorners())),
            )
        self.assertVectorAlmostEqual(
            (PITCH * 2, PITCH * 2, 11.05),
            part.part.bounding_box().size,
        )

    def test_bin_fits_base_plate(self) -> None:
        """A bin must stay TOLERANCE smaller than its baseplate cells."""
        with BuildPart() as bin_part:
            Bin(
                BaseEqual(grid_x=2, grid_y=2),
                height_in_units=3,
                compartments=CompartmentsEqual(compartment_list=[Compartment()]),
            )
        with BuildPart() as plate_part:
            BasePlateEqual(size_x=2, size_y=2, baseplate_block=BasePlateBlockFrame())

        bin_size = bin_part.part.bounding_box().size
        plate_size = plate_part.part.bounding_box().size
        self.assertAlmostEqual(TOLERANCE, plate_size.X - bin_size.X)
        self.assertAlmostEqual(TOLERANCE, plate_size.Y - bin_size.Y)


class DefaultGridSizeUnchangedTest(testutils.UtilTestCase):
    """set_grid_size must not disturb the gridfinity standard default."""

    def tearDown(self) -> None:
        set_grid_size(GRIDFINITY_DEFAULT)

    def test_default_base_plate_is_unchanged_after_reset(self) -> None:
        set_grid_size(PITCH)
        set_grid_size(GRIDFINITY_DEFAULT)
        with BuildPart() as part:
            BasePlateEqual(size_x=2, size_y=3, baseplate_block=BasePlateBlockFrame())
        self.assertVectorAlmostEqual((84, 126, 4.65), part.part.bounding_box().size)
        self.assertAlmostEqual(7684.943883967003, part.part.volume)

    def test_default_skeleton_is_unchanged(self) -> None:
        with BuildPart() as part:
            BasePlateEqual(size_x=2, size_y=2, baseplate_block=BasePlateBlockSkeleton())
        self.assertAlmostEqual(25090.778951, part.part.volume, 5)
