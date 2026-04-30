Using MSNoise Reproducible Papers
==================================

Installation
------------

Install MSNoise and the documentation/notebook dependencies::

    pip install msnoise pooch zstandard

No separate package is needed for the registry itself — the
:class:`msnoise.papers.MRP` client fetches everything on demand.


Quickstart — Path C (registry paper)
--------------------------------------

This is the recommended entry point for reproducing a published result::

    from msnoise.papers import MRP

    mrp = MRP()
    mrp.list_papers()          # print available papers

    paper = mrp.get_paper("2016_DePlaen_PitonDeLaFournaise")
    paper.info()               # DOI, network, available levels

    # Download and extract the stack-level archive (~7 GB, cached after first run)
    project = paper.get_project("stack")

    # List all stacked CCF results across all lineages
    for result in project.list("stack"):
        ccfs = result.get_ccf()

The downloaded archive is cached in
``platformdirs.user_cache_dir("msnoise-mrp")``.  Subsequent calls are
instantaneous.

.. note::

    ``get_project()`` raises :exc:`msnoise.papers.LevelNotAvailable` if
    the requested level has not been published for that paper yet.
    Check ``paper.info()`` first.


Path A — live project
---------------------

If you are working inside an existing MSNoise project directory::

    from msnoise.project import MSNoiseProject

    project = MSNoiseProject.from_current()        # reads msnoise.ini in cwd
    for result in project.list("stack"):
        ccfs = result.get_ccf()

The DB is connected automatically; you can continue running the pipeline via
``project.db`` if needed.


Path B — local archive
----------------------

If you have a ``.tar.zst`` project archive on disk::

    from msnoise.project import MSNoiseProject

    project = MSNoiseProject.from_archive("/data/level_stack.tar.zst")
    for result in project.list("stack"):
        ccfs = result.get_ccf()

The archive is extracted to a temporary directory that lives as long as
``project`` is in scope.  Pass ``project_dir="/some/path"`` to extract to a
persistent location instead.


Running notebooks locally
-------------------------

Each paper's notebooks live under ``papers/<paper_id>/notebooks/`` and follow
the `Jupytext percent format <https://jupytext.readthedocs.io>`_.  To open one::

    pip install jupytext
    jupytext --to notebook papers/2016_DePlaen_PitonDeLaFournaise/notebooks/nb_dvv_timeseries.py
    jupyter notebook nb_dvv_timeseries.ipynb

Notebooks are written to work out of the box via Path C (MRP download).
The first cell always contains a ``LEVEL`` and ``PAPER_ID`` variable you
can override to point at a local archive or live project instead.


Cache management
----------------

Downloaded archives can be inspected or removed::

    mrp = MRP()
    mrp.clear_cache("2016_DePlaen_PitonDeLaFournaise")   # one paper
    mrp.clear_cache()                                      # all papers

The registry index (``registry.yaml``) is never deleted by ``clear_cache()``.
To force a registry refresh::

    mrp = MRP(force_refresh=True)
