Contributing a Paper
====================

Anyone can add a published study to the registry via a pull request.
The CI will validate the schema and attempt a ``db init`` dry-run for
every ``project*.yaml`` you add.


Folder structure
----------------

Create ``papers/<YYYY_FirstAuthor_ShortTitle>/`` containing::

    project.yaml        ← MSNoise 2.x config (required)
    citation.bib        ← BibTeX entry (required)
    meta.yaml           ← editorial fields (required)
    README.md           ← paper summary & processing notes (required)
    bundle_pointer.yaml ← data bundle URLs (optional, add when bundles exist)
    notebooks/          ← analysis notebooks (optional)
        nb_01_dvv.py
        nb_02_map.py

Papers with two independent datasets use multiple project files:
``project_<site>.yaml`` (e.g. ``project_pdf.yaml``, ``project_ruapehu.yaml``).


``meta.yaml``
-------------

Copy and fill in all fields::

    journal_abbrev: ""          # e.g. GRL, SRL, JGR Solid Earth
    region: ""                  # geographic region / volcano name
    network: ""                 # FDSN network code(s)
    short_description: ""       # one-line approach summary for the table
    msnoise_version_min: "2.0.0"
    levels_available: []        # populated when bundles are published
    data_open: false            # true if data is freely available via FDSN
    uses_msnoise: true          # false for reproductions of pre-MSNoise studies
    validated: false            # set to true once pipeline runs end-to-end

Once a paper is fully validated (data download → pipeline → dv/v plots),
set ``validated: true`` and re-run the registry scripts (see below).


``project.yaml``
----------------

Start from the closest existing paper as a template, or from the
`minimal AC-only template <https://github.com/ROBelgium/MSNoise_Reproducible_Papers/blob/main/project_yaml_howto.md>`_.

Key rules:

- Must start with ``msnoise_project_version: 1``
- All workflow keys must be ``category_N`` (e.g. ``filter_1``, ``cc_2``)
- Config keys must match the relevant ``msnoise/config/config_<category>.csv`` exactly

.. warning::

    A few non-obvious key names differ from MSNoise 1.x notation:

    ==================  =================  =========================
    Category            Correct key        Wrong (silently ignored)
    ==================  =================  =========================
    ``mwcs``            ``freqmin``        ``mwcs_low``
    ``mwcs_dtt``        ``dtt_maxdtt``     ``dtt_maxdt``
    ``wavelet_dtt``     ``wct_dtt_freqmin`` ``wct_freqmin``
    ==================  =================  =========================

``data_sources`` requirement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every ``data_sources`` entry must include a ``name`` field that is not
``"local"`` (reserved by MSNoise for the default SDS source)::

    data_sources:
      - name: geonet-fdsn          # required; unique, not "local"
        uri: "fdsn://https://service.geonet.org.nz"
        network: "NZ"
        channels: "HH?"

Omitting ``name`` causes a ``KeyError`` during ``db init``.


``README.md``
-------------

This file is the canonical human-readable description of the paper.
It is converted automatically to RST at docs build time and becomes
the header of the paper's notebook gallery section.

Suggested sections:

- Paper reference (authors, title, journal, DOI, year)
- Network and period
- Key processing choices (frequency bands, correlation type, dv/v method)
- Data access (FDSN service, open/restricted, embargo notes)
- Known issues or deviations from the published processing


Adding notebooks
----------------

Notebooks go in ``papers/<paper_id>/notebooks/`` in
`Jupytext percent format <https://jupytext.readthedocs.io>`_.
Name them ``nb_<NN>_<short_label>.py`` (the ``nb_`` prefix is required
by the Sphinx gallery filename pattern).

The first executable cell should follow this template::

    # %%
    # Configure the data source.
    # By default, data is fetched via MRP (Path C).
    # Override LEVEL or PROJECT_DIR to use a local archive or live project.

    PAPER_ID = "2016_DePlaen_PitonDeLaFournaise"
    LEVEL = "stack"
    PROJECT_DIR = None   # set to a local path to skip the MRP download

    from msnoise.papers import MRP
    from msnoise.project import MSNoiseProject

    if PROJECT_DIR:
        project = MSNoiseProject.from_project_dir(PROJECT_DIR)
    else:
        project = MRP().get_paper(PAPER_ID).get_project(LEVEL)


Updating the registry
---------------------

After creating the paper folder, regenerate the two auto-derived files
and commit them::

    python scripts/gen_notebook_rst.py    # writes papers/*/notebooks/README.rst
    python scripts/gen_papers_index.py    # writes docs/papers_index.rst
    python scripts/update_registry.py     # writes registry.yaml
    python scripts/update_readme.py       # updates root README.md papers table
    git add .
    git commit -m "Add 2016_DePlaen_PitonDeLaFournaise"

Then open a pull request.  CI will validate schemas, check registry
consistency, and run ``msnoise db init --from-yaml`` for every
``project*.yaml`` in the repository.
diff --git a/scripts/gen_papers_index.py b/scripts/gen_papers_index.py
