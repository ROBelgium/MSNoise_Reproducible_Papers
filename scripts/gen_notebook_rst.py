"""Generate docs/auto_papers/<paper>/index.rst and copy notebooks there.

With nbsphinx, notebooks must live inside the Sphinx source tree (docs/).
This script:

1. Converts each paper's README.md to RST (intro block).
2. Copies papers/<paper>/notebooks/nb_*.pct.py to docs/auto_papers/<paper>/.
3. Generates docs/auto_papers/<paper>/index.rst with a toctree of the
   copied notebooks.

All generated files are gitignored (docs/auto_papers/ is in .gitignore).

Called automatically by docs/conf.py setup() before every Sphinx build,
and manually via ``python scripts/gen_notebook_rst.py``.

Requires: m2r2 >= 0.3  (pip install m2r2)
"""

import pathlib
import shutil
import sys

ROOT   = pathlib.Path(__file__).parent.parent
PAPERS = ROOT / "papers"
OUT    = ROOT / "docs" / "auto_papers"


# ---------------------------------------------------------------------------
# Markdown → RST helpers
# ---------------------------------------------------------------------------

def _convert_md(md_text: str) -> str:
    try:
        from m2r2 import convert
    except ImportError:
        print("ERROR: m2r2 not installed. Run: pip install m2r2", file=sys.stderr)
        sys.exit(1)
    return convert(md_text)


def _ensure_title(rst_text: str, fallback: str) -> str:
    """Ensure the RST block starts with a valid title."""
    stripped = rst_text.lstrip()
    lines = stripped.splitlines()
    if len(lines) >= 2 and set(lines[1].strip()) == {"="}:
        return rst_text
    underline = "=" * len(fallback)
    return f"{fallback}\n{underline}\n\n{rst_text}"


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
        print(f"WARNING: {paper_dir.name} — no README.md, skipping")
        return False

    # Destination inside docs/
    dest = OUT / paper_dir.name
    dest.mkdir(parents=True, exist_ok=True)

    # Convert README.md → RST intro block
    rst_intro = _convert_md(readme_md.read_text(encoding="utf-8"))
    rst_intro = _ensure_title(rst_intro, fallback=paper_dir.name)
    (dest / "intro.rst").write_text(rst_intro, encoding="utf-8")

    # Copy notebook files so Sphinx/nbsphinx can find them
    for nb in notebooks:
        shutil.copy2(nb, dest / nb.name)

    # Generate index.rst with toctree
    # Strip the trailing .py so nbsphinx resolves .pct.py correctly
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
