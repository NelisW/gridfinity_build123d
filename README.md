# gridfinity_build123d
Gridfinity (design by Zack Freedman) is a grid based storage solution. 

This repository is forked from https://github.com/Ruudjhuu/gridfinity_build123d to make the sacrilegious, unthinkable act of adapting it for a user-defined grid, other than 42 mm. It contains python modules to create gridfinity capable objects in [build123d](https://github.com/gumyr/build123d).

See the [documentation](http://gridfinity-build123d.readthedocs.io/) for more information and examples.

<img src="docs/assets/baseplate.gif" width="320"/> <img src="docs/assets/bin.gif" width="320"/>
<img src="docs/assets/base.gif" width="320"/>

# Installation

```bash
python3 -m pip install git+https://github.com/Ruudjhuu/gridfinity_build123d
```

# Build requirements

The package's own dependencies are declared in `pyproject.toml`. Three further
files in the repository root describe complete, working environments, one per
tool. They are alternatives, not layers: pick the one that matches how you work.

| File | Tool | What it is |
| --- | --- | --- |
| `uv.lock` | uv | Fully resolved lock file, used by CI. The authoritative set. |
| `environment.yml` | conda | Export of the environment the library is developed in on Windows. |
| `requirements.txt` | pip | Plain pip route, pinned to the same verified versions. |

## uv.lock

Generated from `pyproject.toml` by uv, and what the GitHub workflows use to run
the tests and build the documentation:

```bash
uv run -m unittest discover ./tests/ -v -p "test_*"
```

It is a generated file. Do not edit it by hand; change `pyproject.toml` and run
`uv lock` instead.

## environment.yml

A conda export of a known good environment, Python 3.12 with `build123d` and the
`ocp` CAD kernel from conda-forge:

```bash
conda env create -f environment.yml
conda activate b3dp312
pip install -e .
```

The library itself is deliberately not listed in the file, because the file lives
in the library's own repository. Install it afterwards with `pip install -e .`,
which makes the working copy importable and picks up your edits without
reinstalling. `bd_warehouse` is referenced by the git commit pinned in
`pyproject.toml`, since it is not released on PyPI.

This environment runs the library and builds the documentation. It does not
include the test and lint tooling.

## requirements.txt

The pip equivalent, for a plain virtual environment:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

It is grouped into runtime, documentation, tests and linting, and optional
development tools, so you can cut it down to what you need. The documentation
pins match `docs/requirements.txt`, which Read the Docs builds from.

Note that installing `build123d` from PyPI brings the OCP CAD kernel with it as a
large binary wheel, whereas the conda route takes `ocp` from conda-forge. Use one
route or the other in a given environment, not both, or you end up with two
copies of the kernel.

# Usage
```python
import build123d
from gridfinity_build123d import (
    BaseEqual,
    Bin,
    Compartment,
    CompartmentsEqual,
)

part = Bin(
    BaseEqual(grid_x=2, grid_y=1),
    height_in_units=3,
    compartments=CompartmentsEqual(compartment_list=[Compartment()]),
)

build123d.export_stl(part, "bin_2x1x3.stl")
build123d.export_step(part, "bin_2x1x3.step")

```

# Grid size

The grid size, or pitch, is the length of one grid cell. It defaults to 42 mm, the
Gridfinity standard. It is a single global parameter: set it once, at the top of your
script, before creating any object.

```python
from gridfinity_build123d import BasePlateEqual, Bin, BaseEqual, set_grid_size

set_grid_size(61)

plate = BasePlateEqual(size_x=4, size_y=7)          # 244 x 427 mm
part = Bin(BaseEqual(grid_x=2, grid_y=1), height_in_units=3)
```

Bases, bins, compartments and baseplates all follow the new pitch. The interlocking
profile does not scale, and neither do the corner radius, the 0.5 mm fit tolerance, the
7 mm height unit, or the magnet and screw dimensions. That is deliberate: it is what
makes a bin sit in a baseplate, so parts built at the same pitch always fit together
whatever that pitch is.

Two things to keep in mind:

- An object reads the grid size when it is constructed and then keeps it. Set the pitch
  before you build, not after.
- Parts built at a non standard pitch are not compatible with standard Gridfinity parts.
  If you share the models, say which pitch they use.

Values must be larger than 8 mm, twice the corner radius, below which the corners of a
cell would overlap. `get_grid_size()` returns the value currently in effect.

See the [grid size documentation](https://gridfinity-build123d.readthedocs.io/en/latest/grid_size.html)
for the full list of what scales, and the
[examples](https://gridfinity-build123d.readthedocs.io/en/latest/examples.html) for
compartments, labels, scoops, magnets, baseplates and complete drawer scripts.


# Documentation

To rebuild after editing docs:

    C:/Users/username/AppData/Local/anaconda3/envs/b3dp312/python.exe -m sphinx -b html 
    gridfinity_build123d/docs/source 
    gridfinity_build123d/docs/build/html

# Credits
@zackfreedman -- [gridfinity](https://youtu.be/ra_9zU-mnl8)  
[grizzie17](https://www.printables.com/@grizzie17) -- [gridfinity-refined](https://www.printables.com/model/413761-gridfinity-refined)
