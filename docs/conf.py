import pathlib
import sys

# -- Path setup ---------------------------------------------------------------

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# -- Project info -------------------------------------------------------------

project = "MSNoise Reproducible Papers"
copyright = "2026, Thomas Lecocq"
author = "Thomas Lecocq et al."

# version is not semver here — use the registry paper count or leave blank
version = ""
release = ""

# -- General configuration ----------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.graphviz",
    "numpydoc",
    "sphinxcontrib.jquery",
    "nbsphinx",
    "sphinx_gallery.load_style",   # gallery CSS only — no gen_gallery
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

graphviz_output_format = "svg"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "msnoise": ("https://msnoise.org/doc", None),
}

# -- nbsphinx config ----------------------------------------------------------
# .pct.py files are Jupytext percent-format notebooks converted via jupytext.
# Execution is disabled by default — data bundles are too large for CI.
# Set nbsphinx_execute = 'always' locally once project_bundle/ dirs are ready.

nbsphinx_custom_formats = {
    ".pct.py": ["jupytext.reads", {"fmt": "py:percent"}],
}
import os
nbsphinx_execute      = os.environ.get("MRP_EXECUTE_NOTEBOOKS", "never")
nbsphinx_allow_errors = True

# -- autodoc ------------------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

# -- HTML output --------------------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 3,
    "titles_only": False,
}
html_static_path = ["_static"]
html_css_files = ["my-styles.css"]

# -- numpydoc -----------------------------------------------------------------

numpydoc_show_class_members = False

# -- Pre-build hooks ----------------------------------------------------------

def setup(app):
    """Generate derived RST files before Sphinx reads sources."""
    import subprocess
    scripts = ROOT / "scripts"
    for script in ("gen_notebook_rst.py", "gen_papers_index.py"):
        subprocess.check_call([sys.executable, str(scripts / script)])
