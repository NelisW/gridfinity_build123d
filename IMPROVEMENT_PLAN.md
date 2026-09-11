<!-- Markdown flavour: Native/KaTeX. No PDF front matter. -->

# gridfinity_build123d improvement plan

A review of the library source, its tests, and its tooling. Two defects were
fixed in place. Everything else is recorded here as a recommendation only, with
no change made to the code.

## Contents

- [Review basis](#review-basis)
- [Defects fixed](#defects-fixed)
- [Defect diagnosed but not fixed](#defect-diagnosed-but-not-fixed)
- [Dependency and environment findings](#dependency-and-environment-findings)
- [Recommendations](#recommendations)
- [Reproducing this review](#reproducing-this-review)

## Review basis

| Item | Value |
|---|---|
| Commit reviewed | `79a04c1`, branch `parametric-grid-size` |
| Python | 3.12.14, conda environment `b3dp312` |
| build123d | 0.9.1 from conda-forge |
| Tooling | `ruff` 0.16.7, `vulture`, `pytest` 9.1.1, `coverage` |
| Test result | 147 passed, 4 failed |

The review was carried out on the `parametric-grid-size` branch, whose suite
includes 19 tests for the grid size feature. On a checkout without that branch
the same run reports 128 passed and the same 4 failed.

The four failures are not caused by the grid size work. They are present on
`fc29ac6`, the upstream commit this branch is based on, and are analysed below.

## Defects fixed

### Duplicate entry in `__all__`

`src/gridfinity_build123d/__init__.py` listed `"FeatureLocation"` twice. Found
by `ruff` rule `RUF068`, introduced in commit `2514211`. The duplicate was
removed.

The effect was cosmetic rather than functional, since `from ... import *`
deduplicates, but a duplicated export is a reliable sign that the list is
maintained by hand and drifting. After the fix, `__all__` holds 37 unique
entries and every one of them resolves on the package.

### `tools/dev_check.sh` called a removed tool

The script ran `python -m mypy --pretty ./src ./tests`. Commit `c02b73e`
replaced mypy with basedpyright, removing mypy from the dev dependency group in
`pyproject.toml`, so the script failed partway through for anyone who ran it.
The call is now `python -m basedpyright ./src`, which matches the
`[tool.basedpyright]` configuration in `pyproject.toml`, where `tests` is
already excluded.

## Defect diagnosed but not fixed

### `BottomSides` derives rotation from edge orientation

All four failing tests trace to one cause. Three exercise `BottomSides`
directly; `test_refined_base` reaches it through
`GridfinityRefinedConnectionCutout`.

The failure signature is that the observed count is exactly half the expected
count in every case, 4 against 2 and 10 against 5. That ratio is the clue: the
locations are all generated, but half of them are rotated wrongly, so half the
cutouts are offset away from the solid and remove nothing.

`BottomSides._get_locations_on_edges` in
`src/gridfinity_build123d/feature_locations.py` computes each cutout's rotation
from the direction of a perpendicular line raised on the edge:

```python
pp_edge = edge.perpendicular_line(0.1, 0.5, Plane(face))
angle = pp_edge.tangent_at(0).get_signed_angle(to_front.tangent_at(0))
```

This is correct only if opposite edges of the face run antiparallel, as they do
when traversed around a wire. Under build123d 0.9.1 they do not. Both
X-parallel edges of the bottom face report a tangent of `(1, 0, 0)`, so both
receive the same perpendicular `(0, 1, 0)` and the same 180 degree rotation,
where the pair should differ by 180 degrees:

| Edge centre | Edge tangent | Perpendicular | Angle |
|---|---|---|---|
| `(0, 25, -15)` | `(1, 0, 0)` | `(0, 1, 0)` | 180 |
| `(0, -25, -15)` | `(1, 0, 0)` | `(0, 1, 0)` | 180 |
| `(-25, 0, -15)` | `(0, 1, 0)` | `(-1, 0, 0)` | -90 |
| `(25, 0, -15)` | `(0, 1, 0)` | `(-1, 0, 0)` | -90 |

The root cause is the dependency on edge orientation, which is an
implementation detail of the kernel and of `Face.edges()`, not a documented
guarantee.

**Why no fix was made.** The project's `uv.lock` resolves build123d to 0.10.0,
and CI runs against that. The expected values encoded in the tests were
presumably calibrated there. Changing the rotation logic without being able to
run the suite on 0.10.0 risks fixing this environment and breaking CI.
Verification on 0.10.0 was attempted and is not possible here: build123d 0.10.0
requires a newer OCP than the conda-installed 7.8.1.2, and its import fails on
`ocp_gordon`, which in turn needs `OCP.collections`.

**Recommended fix**, to be applied by someone who can run the suite on 0.10.0:
derive the outward direction geometrically rather than from edge orientation.
The vector from the face centre to the edge midpoint gives the outward normal of
that side directly, is independent of how the kernel happens to orient the edge,
and yields the same result on both versions. See item R1 below.

## Dependency and environment findings

### The conda route cannot reach the version CI targets

`uv.lock` pins build123d 0.10.0. The newest build123d on conda-forge is 0.9.1,
confirmed with `conda search -c conda-forge build123d`. A conda-based
environment therefore cannot currently reach the version the project targets,
and any conda contributor will see the four `BottomSides` failures described
above.

This is a constraint, not a mistake, but it must be stated wherever the conda
route is offered. `environment.yml` pins build123d 0.9.1 because that is the
only version conda-forge offers.

### Version skew between the two dependency descriptions

| Route | build123d | Suite result |
|---|---|---|
| `uv.lock` | 0.10.0 | assumed green, not verifiable here |
| `environment.yml`, `requirements.txt` | 0.9.1 | 147 passed, 4 failed |

`requirements.txt` pins 0.9.1 to match the verified environment. A contributor
who wants a green suite should use the uv route until conda-forge catches up.

## Recommendations

No change has been made for any item in this section. They are ordered by value
against effort.

| Id | Area | Recommendation | Effort |
|---|---|---|---|
| R1 | `feature_locations.py` | Derive the `BottomSides` outward direction geometrically | Medium |
| R2 | `bin.py` | Correct or rename the `height` argument, whose meaning is not what it says | Low |
| R3 | `compartments.py` | Validate `compartment_list` length instead of raising `IndexError` | Low |
| R4 | `settings.py` | Offer a context manager alongside the global setter | Low |
| R5 | `constants.py` | Make `inner_radius_v` lazy | Low |
| R6 | `pyproject.toml` | Clean up the `ruff` configuration | Low |
| R7 | `tools/dev_check.sh` | Run `vulture` over tests as well as `src` | Low |
| R8 | repository | Delete the orphaned `mypy.ini` | Low |
| R9 | source-wide | Correct misspelled public identifiers | High |
| R10 | `__init__.py` | Make the public surface explicit | Medium |

### R1 -- Derive the `BottomSides` outward direction geometrically

Replace the perpendicular-line construction with the vector from the face centre
to the edge midpoint, normalised, and take the rotation from that. It removes
the dependency on edge orientation entirely, which is what makes the current
code version-sensitive. Add a test asserting the four rotations directly rather
than counting inner wires, so a future regression names the real problem instead
of reporting a wire count.

### R2 -- The `height` argument does not mean what it says

`Bin.__init__` documents `height` as "Height of the bin in mm". It is the amount
extruded above the base, so a `Bin(base, height=45)` is 52.8 mm tall, the 45 mm
plus the 7.8 mm base. `height_in_units`, by contrast, is the total. Two
arguments that both look like heights but measure from different datums is a
trap, and the docstring currently reinforces it.

Either correct the docstring, or add a separate argument for overall height and
subtract the base internally. The second is the smaller surprise for callers but
is a breaking change if anyone relies on current behaviour.

### R3 -- `compartment_list` fails with an opaque `IndexError`

`Compartments.create` indexes `compartment_list[item - 1]` when a list is
passed, and reuses the object when a bare `Compartment` is passed. A list
shorter than the number of cells raises `IndexError: list index out of range`
from deep inside the build, naming neither the argument nor the shortfall.

Validate the length against the grid in `__init__` and raise a message that
states both numbers. The two calling conventions are useful and worth keeping;
only the failure mode needs work.

### R4 -- A context manager for the grid size

`set_grid_size` is a global setter, which is the right default for the single
pitch per script case. Tests need `tearDown` to restore 42 mm, and any code that
wants a temporary pitch must remember to restore it.

A context manager would remove that burden:

```python
with grid_size(61):
    plate = BasePlateEqual(size_x=4, size_y=7)
```

This is roughly ten lines wrapping the existing setter. It was deliberately left
out of the original change as speculative; it stops being speculative the first
time a script needs two pitches.

### R5 -- `inner_radius_v` is computed at import time

`gf_bin.inner_radius_v` in `constants.py` is evaluated once when the module is
imported, from `grid.radius` and `grid.tollerance`. It is correct today because
neither is settable at runtime. If either is ever made parametric, this value
will silently keep its import-time figure, producing wrong fillets with no
error. Making it a property or a function removes a latent trap for whoever
makes that change.

### R6 -- `ruff` configuration has drifted

Three issues, all noise rather than defects:

- `ANN101` is in the ignore list but has been removed from ruff, so every run
  prints a warning that ignoring it has no effect.
- `CPY001`, missing copyright notice, fires on all 11 source files. The project
  does not use file headers, so the rule should be disabled rather than
  permanently failing.
- `PLR0913` is ignored but `PLR0917`, a newer split of the same idea, is not,
  so nine constructors are flagged for too many positional arguments. Ignore it
  as well, or add keyword-only markers.

### R7 -- `vulture` reports false positives

`tools/dev_check.sh` runs `python -m vulture ./src`. Because tests are outside
that path, anything used only by tests looks dead. It currently reports
`BaseBlockPlatform` and `UnsuportedEnumValueError`, both of which are exercised
in `tests/test_unit_base.py` and `tests/test_unit_utils.py`. Scan `./src
./tests`, or keep a whitelist, so that a real finding is not lost among
predictable false ones.

### R8 -- `mypy.ini` is orphaned

Nothing references mypy any more: not `pyproject.toml`, not the workflows, not
`.pre-commit-config.yaml`, and, after the fix above, not `tools/dev_check.sh`.
The file is a leftover of the basedpyright migration and can be deleted. It is
listed here rather than removed because it is unrelated to the work on this
branch.

### R9 -- Misspelled public identifiers

Several names and docstrings carry typos. The two in the public API are the
expensive ones, since correcting them breaks callers:

| Location | Current | Should be |
|---|---|---|
| `utils.py:39` | `UnsuportedEnumValueError` | `UnsupportedEnumValueError` |
| `constants.py:27` | `grid.tollerance` | `grid.tolerance` |
| `baseplate.py:261` | "recatngular" | "rectangular" |
| `bin.py:57` | "Heigth" | "Height" |
| `compartments.py:150` | "aranged" | "arranged" |
| `compartments.py:290` | "Deafults" | "defaults" |

The docstring typos are free to fix. For the two identifiers, the usual path is
to introduce the correct spelling, alias the old name, and remove the alias at
the next major version. Worth doing before the API has many users, not after.

### R10 -- The public surface is implicit

Twelve public classes are defined but not exported in `__all__`, among them
`BasePlateBlock`, which users must subclass to make a custom block, and the
`Feature` and `Corners` abstract bases. Nothing marks them as internal either,
since none is underscore-prefixed, so the boundary between supported API and
implementation detail is currently a matter of reading `__init__.py`.

Decide for each whether it is public, and either export it or prefix it. The
extension points in particular should be exported, since subclassing them is the
documented way to extend the library.

## Reproducing this review

```bash
python -m pytest tests/ -q
python -m ruff check src/ --statistics
python -m vulture src/ tests/ --min-confidence 60
python -m coverage run -m unittest discover ./tests/ -p "test_unit*"
python -m coverage report -m --fail-under=100
```

Coverage of `src` is 100 percent on every module, including the modules touched
by this review, so the `--fail-under=100` gate in CI is not at risk from either
fix.
