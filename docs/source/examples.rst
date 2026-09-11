Examples
========

Worked examples of the things you actually do with this library: build a part,
divide it up, add features, and write it to a file you can print.

.. testsetup:: *

    from gridfinity_build123d import *

.. testcleanup:: *

    set_grid_size(42)

Exporting a part
----------------

Every object this library produces is a plain build123d ``Part``, so it is
exported with build123d's own functions. This is usually the last line of a
script:

.. testcode::

    import tempfile
    from pathlib import Path

    import build123d as b3d

    part = Bin(BaseEqual(grid_x=2, grid_y=1), height_in_units=3)

    with tempfile.TemporaryDirectory() as tmp:
        stl = Path(tmp) / "bin_2x1x3.stl"
        step = Path(tmp) / "bin_2x1x3.step"
        b3d.export_stl(part, str(stl))
        b3d.export_step(part, str(step))
        print(stl.exists(), step.exists())

.. testoutput::

    True True

Use STL for slicing and printing, and STEP if you want to open the model in
another CAD program.

Viewing a part while you work
-----------------------------

``ocp_vscode`` shows the model in an OCP CAD Viewer window as you edit the
script. It is a development dependency, not something the models need:

.. code-block:: python

    from ocp_vscode import show_object

    part = Bin(BaseEqual(grid_x=2, grid_y=1), height_in_units=3)
    show_object(part, name="bin_2x1x3")

Bin height
----------

Height is given either in Gridfinity height units of 7 mm, or directly in
millimetres. The two arguments are mutually exclusive, and they do not measure
the same thing:

.. testcode::

    base = BaseEqual(grid_x=1, grid_y=1)
    units = Bin(BaseEqual(grid_x=1, grid_y=1), height_in_units=6)
    raised = Bin(BaseEqual(grid_x=1, grid_y=1), height=45)

    print(f"base alone      {base.bounding_box().size.Z:5.2f} mm")
    print(f"height_in_units {units.bounding_box().size.Z:5.2f} mm")
    print(f"height=45       {raised.bounding_box().size.Z:5.2f} mm")

.. testoutput::

    base alone       7.80 mm
    height_in_units 42.00 mm
    height=45       52.80 mm

``height_in_units`` is the **total** height of the finished bin, 6 units of 7 mm
being 42 mm. ``height`` is the amount extruded **on top of the base**, so the
finished bin is taller than the number you give by the height of the base.

To hit an exact overall height, which is the usual reason for using ``height``
at all, subtract the base height:

.. testcode::

    TARGET = 45

    base = BaseEqual(grid_x=1, grid_y=1)
    part = Bin(base, height=TARGET - base.bounding_box().size.Z)

    print(f"{part.bounding_box().size.Z:.1f} mm")

.. testoutput::

    45.0 mm

A stacking lip is added on top of either measurement and is not counted in it.

A bin with no ``compartments`` argument is solid. Pass ``compartments`` to hollow
it out.

Dividing a bin into compartments
--------------------------------

:class:`~gridfinity_build123d.compartments.CompartmentsEqual` splits the bin into
equal cells. ``div_x`` and ``div_y`` are the number of compartments, not the
number of walls:

.. testcode::

    part = Bin(
        BaseEqual(grid_x=3, grid_y=2),
        height_in_units=4,
        compartments=CompartmentsEqual(compartment_list=Compartment(), div_x=3, div_y=2),
    )
    print(f"{part.bounding_box().size.X:.1f} mm wide")

.. testoutput::

    125.5 mm wide

.. important::

    A single :class:`~gridfinity_build123d.compartments.Compartment` passed on its
    own is reused for every cell. A **list** is indexed per cell instead, so it
    must hold one entry for each cell or you get an ``IndexError``:

    .. testcode::

        # One compartment, reused everywhere. Six cells, one object.
        CompartmentsEqual(compartment_list=Compartment(), div_x=3, div_y=2)

        # A list must cover every cell.
        CompartmentsEqual(
            compartment_list=[Compartment() for _ in range(6)],
            div_x=3,
            div_y=2,
        )

    Pass the bare object when every compartment is the same, and a list when you
    want them to differ.

Compartments of different sizes
-------------------------------

:class:`~gridfinity_build123d.compartments.Compartments` takes a grid of numbers.
Cells sharing a number become one compartment, so repeating a number makes that
compartment span several cells. The list supplies compartment number 1, 2, 3 and
so on, in order:

.. testcode::

    part = Bin(
        BaseEqual(grid_x=3, grid_y=2),
        height_in_units=4,
        compartments=Compartments(
            grid=[
                [1, 1, 2],
                [1, 1, 3],
            ],
            compartment_list=[
                Compartment(),                      # 1, the large square
                Compartment(features=Label()),      # 2, top right
                Compartment(features=Scoop()),      # 3, bottom right
            ],
        ),
    )
    print(f"{part.bounding_box().size.X:.1f} x {part.bounding_box().size.Y:.1f} mm")

.. testoutput::

    125.5 x 83.5 mm

Labels, scoops and a stacking lip
---------------------------------

A label is the angled tab at the back of a compartment for a written tag. A scoop
is the curved ramp at the front that lets you sweep parts out with a finger. A
stacking lip is the rim around the top of the bin that lets another bin sit on
it:

.. testcode::

    part = Bin(
        BaseEqual(grid_x=2, grid_y=1),
        height_in_units=5,
        lip=StackingLip(),
        compartments=CompartmentsEqual(
            compartment_list=Compartment(features=[Label(), Scoop()]),
            div_x=2,
        ),
    )
    print(f"{part.bounding_box().size.Z:.2f} mm tall")

.. testoutput::

    39.12 mm tall

Both features are adjustable. ``Label(angle=...)`` changes the tab angle and
``Scoop(radius=...)`` the size of the ramp:

.. testcode::

    shallow = Compartment(features=[Label(angle=45), Scoop(radius=12)])
    part = Bin(
        BaseEqual(grid_x=2, grid_y=1),
        height_in_units=5,
        compartments=CompartmentsEqual(compartment_list=shallow),
    )
    print(part.is_valid())

.. testoutput::

    True

Magnets and screws
------------------

Features are applied to a base or a baseplate, and a
:class:`~gridfinity_build123d.feature_locations.FeatureLocation` decides where
they go. :class:`~gridfinity_build123d.feature_locations.BottomCorners` is the
usual choice, putting one hole in each corner of every cell:

.. testcode::

    part = Bin(
        BaseEqual(
            grid_x=2,
            grid_y=1,
            features=[MagnetHole(BottomCorners()), ScrewHole(BottomCorners())],
        ),
        height_in_units=3,
        compartments=CompartmentsEqual(compartment_list=Compartment()),
    )
    print(part.is_valid())

.. testoutput::

    True

Hole sizes have standard defaults but can be overridden, for example for magnets
you already own:

.. testcode::

    base = BaseEqual(
        grid_x=1,
        grid_y=1,
        features=MagnetHole(BottomCorners(), radius=3, depth=2),
    )
    print(base.is_valid())

.. testoutput::

    True

Baseplates
----------

A baseplate is the tray the bins drop into. Three block types trade material
against rigidity:

.. testcode::

    frame = BasePlateEqual(size_x=2, size_y=2, baseplate_block=BasePlateBlockFrame())
    full = BasePlateEqual(size_x=2, size_y=2, baseplate_block=BasePlateBlockFull())
    skeleton = BasePlateEqual(size_x=2, size_y=2, baseplate_block=BasePlateBlockSkeleton())

    for name, plate in (("frame", frame), ("full", full), ("skeleton", skeleton)):
        size = plate.bounding_box().size
        print(f"{name:9s} {size.Z:5.2f} mm tall, {plate.volume / 1000:6.1f} cm3")

.. testoutput::

    frame      4.65 mm tall,    5.1 cm3
    full      11.05 mm tall,   50.2 cm3
    skeleton  11.05 mm tall,   25.1 cm3

:class:`~gridfinity_build123d.baseplate.BasePlateBlockFrame` is the thin rim and
uses the least plastic. :class:`~gridfinity_build123d.baseplate.BasePlateBlockFull`
has a solid floor, needed if you want magnets or screws.
:class:`~gridfinity_build123d.baseplate.BasePlateBlockSkeleton` is the solid floor
with the middle hollowed out, roughly halving the material.

Features go on the block, so that every cell gets them:

.. testcode::

    plate = BasePlateEqual(
        size_x=2,
        size_y=2,
        baseplate_block=BasePlateBlockFull(
            features=[
                MagnetHole(BottomCorners()),
                ScrewHoleCountersink(BottomCorners()),
            ],
        ),
    )
    print(plate.is_valid())

.. testoutput::

    True

Non rectangular layouts
-----------------------

``BaseEqual`` and ``BasePlateEqual`` are shortcuts for rectangles. The underlying
:class:`~gridfinity_build123d.base.Base` and
:class:`~gridfinity_build123d.baseplate.BasePlate` take a grid of booleans
instead, so you can build an L shape or anything else that fits around an
obstruction:

.. testcode::

    layout = [
        [True, True, True],
        [True, False, False],
        [True, False, False],
    ]

    plate = BasePlate(grid=layout, baseplate_block=BasePlateBlockFrame())
    size = plate.bounding_box().size
    print(f"{size.X:.0f} x {size.Y:.0f} mm")

.. testoutput::

    126 x 126 mm

The bounding box still covers the full 3 x 3 rectangle, but only the five cells
marked ``True`` exist. The same grid works for
:class:`~gridfinity_build123d.base.Base`, so a bin can match the plate.

A complete drawer
-----------------

Putting it together: pick a pitch that suits the drawer, build the baseplate and
a set of bins to fill it, and write everything out. This is the shape of a real
project script:

.. testcode::

    import tempfile
    from pathlib import Path

    import build123d as b3d

    set_grid_size(61)

    CELLS_X, CELLS_Y = 4, 7
    BIN_LAYOUT = [(1, 1), (2, 1), (1, 3)]   # cells wide, cells deep

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)

        plate = BasePlateEqual(
            size_x=CELLS_X,
            size_y=CELLS_Y,
            baseplate_block=BasePlateBlockFull(features=MagnetHole(BottomCorners())),
        )
        b3d.export_stl(plate, str(out / f"baseplate_{CELLS_X}x{CELLS_Y}.stl"))

        for cells_x, cells_y in BIN_LAYOUT:
            part = Bin(
                BaseEqual(grid_x=cells_x, grid_y=cells_y),
                height_in_units=3,
                lip=StackingLip(),
                compartments=CompartmentsEqual(compartment_list=Compartment(features=Label())),
            )
            b3d.export_stl(part, str(out / f"bin_{cells_x}x{cells_y}x3.stl"))

        print(sorted(p.name for p in out.glob("*.stl")))

.. testoutput::

    ['baseplate_4x7.stl', 'bin_1x1x3.stl', 'bin_1x3x3.stl', 'bin_2x1x3.stl']

Checking the fit
----------------

The gap between a bin and its baseplate cell is a fixed 0.5 mm at any pitch. It
is worth asserting in a script that generates many parts:

.. testcode::

    set_grid_size(61)

    part = Bin(BaseEqual(grid_x=2, grid_y=2), height_in_units=3)
    plate = BasePlateEqual(size_x=2, size_y=2)

    clearance = plate.bounding_box().size.X - part.bounding_box().size.X
    print(f"{clearance:.1f} mm")

.. testoutput::

    0.5 mm
