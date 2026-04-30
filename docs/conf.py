import pathlib
import sys

# -- Path setup ---------------------------------------------------------------

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# -- Project info -------------------------------------------------------------

project = "MSNoise Reproducible Papers"
copyright = "2026, Royal Observatory of Belgium"
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
    "sphinx_gallery.gen_gallery",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "auto_papers"]

graphviz_output_format = "svg"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "msnoise": ("https://msnoise.org/doc", None),
}

# -- sphinx_gallery config ----------------------------------------------------
# Discover all papers/*/notebooks/ directories dynamically.

_papers_root = ROOT / "papers"
_notebook_dirs = sorted(
    d for d in _papers_root.glob("*/notebooks") if d.is_dir()
)

sphinx_gallery_conf = {
    "examples_dirs": [str(d) for d in _notebook_dirs],
    "gallery_dirs":  [f"auto_papers/{d.parent.name}" for d in _notebook_dirs],
    "filename_pattern": r"nb_.*\.py",
    "ignore_pattern": r"__init__\.py",
    # Notebooks are not executed at build time — archives are too large for CI.
    # Set to True locally if you have the project_bundle/ dirs in place.
    "plot_gallery": False,
    "download_all_examples": False,
    "show_signature": False,
    "doc_module": (),
    "reference_url": {},
    "first_notebook_cell": (
        "# This notebook is part of MSNoise Reproducible Papers.\n"
        "# See https://github.com/ROBelgium/MSNoise_Reproducible_Papers\n"
    ),
}

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
