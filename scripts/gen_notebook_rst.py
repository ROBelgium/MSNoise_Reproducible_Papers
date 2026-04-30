"""Generate docs/auto_papers/<paper>/index.rst and copy notebooks there.

With nbsphinx, notebooks must live inside the Sphinx source tree (docs/).
This script:

1. Converts each paper's README.md to RST via pandoc (no m2r2 dependency).
2. Copies papers/<paper>/notebooks/nb_*.pct.py to docs/auto_papers/<paper>/.
3. Generates docs/auto_papers/<paper>/index.rst with a toctree of the
   copied notebooks.

All generated files are gitignored (docs/auto_papers/ is in .gitignore).

Called automatically by docs/conf.py setup() before every Sphinx build,
and manually via ``python scripts/gen_notebook_rst.py``.

Requires: pandoc (system binary) — https://pandoc.org/installing.html
"""

import pathlib
import shutil
import subprocess
import sys

ROOT   = pathlib.Path(__file__).parent.parent
PAPERS = ROOT / "papers"
OUT    = ROOT / "docs" / "auto_papers"


# ---------------------------------------------------------------------------
# Markdown -> RST via pandoc
# ---------------------------------------------------------------------------

def _convert_md(md_path: pathlib.Path) -> str:
    """Convert a Markdown file to RST using pandoc."""
    result = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "rst", str(md_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: pandoc failed for {md_path}:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


# ---------------------------------------------------------------------------
# Per-paper generation
# ---------------------------------------------------------------------------

def generate_paper(paper_dir: pathlib.Path) -> bool:
    """Process one paper. Returns True if notebooks were found and copied."""
    nb_src = paper_dir / "notebooks"
    if not nb_src.is_dir():
        return False

    notebooks = sorted(nb_src.glob("nb_*.pct.py"))
    if not notebooks:
        return False

    readme_md = paper_dir / "README.md"
    if not readme_md.exists():
        print(f"WARNING: {paper_dir.name} -- no README.md, skipping")
        return False

    # Destination inside docs/
    dest = OUT / paper_dir.name
    dest.mkdir(parents=True, exist_ok=True)

    # Convert README.md -> RST intro block
    (dest / "intro.rst").write_text(
        _convert_md(readme_md), encoding="utf-8"
    )

    # Copy notebook files so Sphinx/nbsphinx can find them
    for nb in notebooks:
        shutil.copy2(nb, dest / nb.name)

    # Generate index.rst with toctree.
    # Strip the trailing .py: nbsphinx resolves .pct.py via source_suffix.
    nb_stems = [nb.stem for nb in notebooks]   # e.g. nb_02_interferogram.pct
    toctree_entries = "\n".join(f"   {s}" for s in nb_stems)

    index_rst = f"""\
.. include:: intro.rst

.. toctree::
   :maxdepth: 1
   :caption: Notebooks

{toctree_entries}
"""
    (dest / "index.rst").write_text(index_rst, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(papers_root: pathlib.Path = PAPERS):
    written = []
    skipped = []

    for paper_dir in sorted(papers_root.iterdir()):
        if not paper_dir.is_dir():
            continue
        if generate_paper(paper_dir):
            written.append(paper_dir.name)
        else:
            skipped.append(paper_dir.name)

    if written:
        print(f"Generated notebook docs for: {', '.join(written)}")
    if skipped:
        print(f"Skipped (no notebooks): {', '.join(skipped)}")


if __name__ == "__main__":
    generate()
