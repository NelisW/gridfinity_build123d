.. gridfinity_build123d documentation master file, created by
   sphinx-quickstart on Sat Dec  9 21:24:49 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to gridfinity_build123d's documentation!
================================================
Gridfinity is a storage system created by Zack Freedman, partly inspired by Alexander Chappell's assortment system.
This repository is a Python library for constructing Gridfinity objects using Build123d, aiming to be one of the most modular Gridfinity generation tools.

.. image:: ../assets/baseplate.gif
   :width: 45%

.. image:: ../assets/bin.gif
   :width: 45%

Overview
========

This module contains a set of "Root objects" that hold arguments to pass through a list of "features".
Features are applied to the root object. For example, the root object BasePlate can include a Feature MagnetHole.
Features have FeatureLocations, providing the user with the flexibility to place features wherever they desire.

Grids
=====
Most Gridfinity tools out there have the posibility to create rectangular object.
Gridfinity_build123d give power users the ability to use a grid definition and create all imaginable shapes.


Grid size
=========
The grid size, or pitch, is the length of one grid cell. It defaults to 42 mm,
the Gridfinity standard, and is a single global parameter you set once at the top
of a script:

.. code-block:: python

   from gridfinity_build123d import set_grid_size, BasePlateEqual

   set_grid_size(61)

   plate = BasePlateEqual(size_x=4, size_y=7)  # 244 x 427 mm

Bases, bins, compartments and baseplates all follow the new pitch, while the
interlocking profile does not scale, so parts built at the same pitch always fit
together. See :doc:`grid_size` for what does and does not scale, and for how to
choose a pitch that fills a drawer.

Index
=====
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   objects.rst
   features.rst
   grid_size.rst
   examples.rst
   reference.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
