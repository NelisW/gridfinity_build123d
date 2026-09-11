Grid size
=========

Gridfinity is built on a square grid. The length of one cell is the **grid size**,
or pitch. It defaults to ``42`` mm, the Gridfinity standard, and it is the one
dimension this library lets you change.

.. testsetup:: *

    from gridfinity_build123d import *

.. testcleanup:: *

    set_grid_size(42)

Setting the grid size
---------------------

The grid size is a single global parameter. Set it once, at the top of your
script, before creating any object:

.. testcode::

    from gridfinity_build123d import set_grid_size, get_grid_size

    set_grid_size(61)
    print(get_grid_size())

.. testoutput::

    61

Every object created afterwards uses the new pitch:

.. testcode::

    set_grid_size(61)

    plate = BasePlateEqual(size_x=4, size_y=7)
    size = plate.bounding_box().size
    print(f"{size.X:.0f} x {size.Y:.0f} mm")

.. testoutput::

    244 x 427 mm

:func:`~gridfinity_build123d.settings.get_grid_size` returns the value currently
in effect, which is useful when your own code needs to do grid arithmetic.

What the grid size controls
---------------------------

Changing the pitch resizes the *cell*. It deliberately does not resize the
interlocking profile, because that profile is what makes a bin sit in a
baseplate. A bin and a baseplate built at the same pitch therefore always fit
together, whatever that pitch is.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Scales with the grid size
     - Stays fixed
   * - Base and bin footprint
     - Stacking and baseplate profile heights
   * - Baseplate cell size and overall size
     - Corner radius (4 mm)
   * - Compartment sizes inside a bin
     - Fit tolerance between bin and baseplate (0.5 mm)
   * - Skeleton baseplate lightening cutouts
     - Magnet and screw hole dimensions
   * -
     - Feature offsets from the cell edge
   * -
     - Bin height unit (7 mm)

Because magnet and screw holes are positioned by a fixed offset from the cell
edge, they stay in the corners of the cell as it grows. They do not drift toward
the middle.

Rules and gotchas
-----------------

**Set it before you build.** An object reads the grid size while it is being
constructed and then keeps it. Changing the pitch afterwards does not resize
anything that already exists:

.. testcode::

    set_grid_size(42)
    small = BaseEqual(grid_x=1, grid_y=1)

    set_grid_size(61)
    large = BaseEqual(grid_x=1, grid_y=1)

    print(f"{small.bounding_box().size.X:.1f}  {large.bounding_box().size.X:.1f}")

.. testoutput::

    41.5  60.5

**It is one global value.** There is no per-object grid size. To build parts at
two pitches in one script, build all the parts at the first pitch, then switch
and build the rest:

.. testcode::

    set_grid_size(42)
    standard_parts = [BaseEqual(grid_x=n, grid_y=1) for n in (1, 2)]

    set_grid_size(61)
    drawer_parts = [BaseEqual(grid_x=n, grid_y=1) for n in (1, 2)]

    print(len(standard_parts), len(drawer_parts))

.. testoutput::

    2 2

**Parts built at a custom pitch are not standard Gridfinity.** A 61 mm bin will
not sit in anyone else's 42 mm baseplate, and vice versa. If you share the
models, say what pitch they use.

Valid values
------------

The grid size must be larger than twice the corner radius, that is larger than
8 mm. Below that the corner fillets of a cell would overlap each other. Anything
smaller raises a :class:`ValueError` and leaves the current value untouched:

.. testcode::

    try:
        set_grid_size(5)
    except ValueError as exc:
        print(exc)

.. testoutput::

    Grid size must be bigger than 8 mm, got 5

There is no upper limit. Very large cells are slower to build and to print, but
they are geometrically valid.

Choosing a grid size
--------------------

A common reason to change the pitch is to fill a drawer exactly. Divide the
usable interior by a candidate pitch and take the whole number of cells, then
check how much is left over:

.. testcode::

    drawer_x, drawer_y = 250, 430  # usable interior in mm

    for pitch in (42, 50, 61):
        cells_x = int(drawer_x // pitch)
        cells_y = int(drawer_y // pitch)
        waste_x = drawer_x - cells_x * pitch
        waste_y = drawer_y - cells_y * pitch
        print(f"{pitch} mm -> {cells_x} x {cells_y} cells, {waste_x:.0f} x {waste_y:.0f} mm unused")

.. testoutput::

    42 mm -> 5 x 10 cells, 40 x 10 mm unused
    50 mm -> 5 x 8 cells, 0 x 30 mm unused
    61 mm -> 4 x 7 cells, 6 x 3 mm unused

Here 61 mm wastes the least space. Leave a millimetre or two of clearance so the
baseplate still drops into the drawer.

API
---

.. currentmodule:: gridfinity_build123d.settings

.. autofunction:: set_grid_size
   :no-index:

.. autofunction:: get_grid_size
   :no-index:
