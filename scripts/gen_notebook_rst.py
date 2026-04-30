"""Generate papers/*/notebooks/README.rst from papers/*/README.md.

sphinx_gallery requires a README.rst in every examples_dir to use as the
gallery section header.  This script converts the hand-written README.md
(which GitHub renders nicely) to RST via m2r2, so there is a single source
of truth.

Called automatically by docs/conf.py setup() before every Sphinx build,
and manually via ``python scripts/gen_notebook_rst.py``.

Requires: m2r2 >= 0.3  (pip install m2r2)
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent
PAPERS = ROOT / "papers"


def _convert(md_text: str) -> str:
    """Convert Markdown to RST using m2r2."""
    try:
        from m2r2 import convert
    except ImportError:
        print("ERROR: m2r2 not installed. Run: pip install m2r2", file=sys.stderr)
        sys.exit(1)
    return convert(md_text)


def _ensure_title(rst_text: str, fallback_title: str) -> str:
    """sphinx_gallery needs the first non-empty line to be a valid RST title.

    m2r2 preserves the first ``#`` heading as a title, so this is usually a
    no-op.  We only prepend a synthetic title if the RST starts with something
    other than a title block (e.g. a raw directive or a paragraph).
    """
    stripped = rst_text.lstrip()
    lines = stripped.splitlines()
    # A valid RST title has an underline of ``=`` on line 1 (0-indexed).
    if len(lines) >= 2 and set(lines[1].strip()) == {"="}:
        return rst_text  # already has a proper title
    # Prepend one.
    title = fallback_title
    underline = "=" * len(title)
    return f"{title}\n{underline}\n\n{rst_text}"


def generate(papers_root: pathlib.Path = PAPERS):
    skipped = []
    written = []

    for paper_dir in sorted(papers_root.iterdir()):
        if not paper_dir.is_dir():
            continue
        nb_dir = paper_dir / "notebooks"
        if not nb_dir.is_dir():
            skipped.append(paper_dir.name)
            continue

        readme_md = paper_dir / "README.md"
        if not readme_md.exists():
            print(f"WARNING: {paper_dir.name} has notebooks/ but no README.md — skipping")
            continue

        rst_text = _convert(readme_md.read_text(encoding="utf-8"))
        rst_text = _ensure_title(rst_text, fallback_title=paper_dir.name)

        out = nb_dir / "README.rst"
        out.write_text(rst_text, encoding="utf-8")
        written.append(paper_dir.name)

