"""settings.

Module containing the runtime settable gridfinity parameters.

The grid size (pitch) is the one dimension a user is expected to change. It is a
single global value, set once at the top of a script before any object is built::

    from gridfinity_build123d import set_grid_size

    set_grid_size(61)

Everything derived from the pitch follows: bases, bins, compartments and
baseplates. The stacking profile itself does not scale, so bins built at a given
pitch stay compatible with baseplates built at that same pitch.
"""

from __future__ import annotations

from gridfinity_build123d.constants import gridfinity_standard


def set_grid_size(size: float) -> None:
    """Set the gridfinity grid size (pitch) in mm.

    Applies to every object created afterwards. Objects already built keep the
    pitch they were created with.

    Args:
        size (float): Grid size in mm. Defaults to 42 (the gridfinity standard).

    Raises:
        ValueError: Size is not bigger than twice the grid corner radius, below
            which the corner fillets would self intersect.
    """
    minimum = 2 * gridfinity_standard.grid.radius
    if size <= minimum:
        msg = f"Grid size must be bigger than {minimum} mm, got {size}"
        raise ValueError(msg)

    gridfinity_standard.grid.size = size


def get_grid_size() -> float:
    """Get the current gridfinity grid size (pitch) in mm.

    Returns:
        float: The grid size in mm.
    """
    return gridfinity_standard.grid.size
