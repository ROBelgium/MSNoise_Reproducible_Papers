"""Generate docs/auto_papers/<paper>/index.rst and copy notebooks there.

Builds the intro block from meta.yaml + citation.bib — no README.md or
external binary (pandoc/m2r2) required.

For each paper that has a notebooks/ directory containing nb_*.pct.py files:

1. Reads meta.yaml and citation.bib for structured metadata.
2. Copies nb_*.pct.py to docs/auto_papers/<paper>/ (nbsphinx source tree).
3. Writes docs/auto_papers/<paper>/index.rst with an inline intro and
   a toctree of the copied notebooks.

All generated files are gitignored (docs/auto_papers/ is in .gitignore).

Called automatically by docs/conf.py setup() before every Sphinx build,
and manually via ``python scripts/gen_notebook_rst.py``.
"""

import pathlib
import re
import shutil

import bibtexparser
import yaml

ROOT   = pathlib.Path(__file__).parent.parent
PAPERS = ROOT / "papers"
OUT    = ROOT / "docs" / "auto_papers"


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def _parse_bib(bib_path: pathlib.Path) -> dict:
    bib = bibtexparser.loads(bib_path.read_text(encoding="utf-8"))
    e   = bib.entries[0]
    authors_raw = [a.strip() for a in e.get("author", "").split(" and ")]
    authors = [_abbreviate(a) for a in authors_raw if a]
    return {
        "title":   re.sub(r"[{}]", "", e.get("title", "")),
        "authors": authors,
        "year":    e.get("year", ""),
        "journal": re.sub(r"[{}]", "", e.get("journal", "")),
        "doi":     e.get("doi", ""),
    }


def _abbreviate(author: str) -> str:
    if "," not in author:
        return author
    last, rest = author.split(",", 1)
    given = rest.strip()
    if re.match(r"^[A-Z]\.(\s?[A-Z]\.)*$", given):
        return f"{last.strip()}, {given}"
    initials = "".join(
        f"{w[0].upper()}." for w in re.split(r"[\s\-]+", given) if w and w[0].isupper()
    )
    return f"{last.strip()}, {initials}"


def _author_list(authors: list) -> str:
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]} & {authors[1]}"
    return ", ".join(authors[:-1]) + f", & {authors[-1]}"


def _build_intro(paper_dir: pathlib.Path, bib: dict, meta: dict) -> str:
    """Build an RST intro block from bib + meta data."""
    title      = bib["title"] or paper_dir.name
    authors    = _author_list(bib["authors"])
    year       = bib["year"]
    journal    = meta.get("journal_abbrev") or bib["journal"]
    doi        = bib["doi"]
    short_desc = meta.get("short_description", "")
    network    = meta.get("network", "")
    region     = meta.get("region", "")
    levels     = ", ".join(f"``{l}``" for l in meta.get("levels_available", []))
    validated  = "yes" if meta.get("validated") else "no"
    data_open  = "yes" if meta.get("data_open")  else "no"

    doi_line = f"`DOI:{doi} <https://doi.org/{doi}>`_" if doi else ""

    lines = [
        title,
        "=" * len(title),
        "",
        f"*{authors} ({year}). {journal}.* {doi_line}",
        "",
    ]
    if short_desc:
        lines += [short_desc, ""]

    # Metadata table
    rows = []
    if network:
        rows.append(("Network", network))
    if region:
        rows.append(("Region", region))
    if levels:
        rows.append(("Levels available", levels))
    rows.append(("Data open", data_open))
    rows.append(("Validated", validated))

    if rows:
        col1 = max(len(r[0]) for r in rows)
        col2 = max(len(r[1]) for r in rows)
        sep  = f"+{'-'*(col1+2)}+{'-'*(col2+2)}+"
        lines.append(sep)
        for k, v in rows:
            lines.append(f"| {k:<{col1}} | {v:<{col2}} |")
            lines.append(sep)
        lines.append("")

    return "\n".join(lines)


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

    bib_path  = paper_dir / "citation.bib"
    meta_path = paper_dir / "meta.yaml"

    if not bib_path.exists():
        print(f"WARNING: {paper_dir.name} -- no citation.bib, skipping")
        return False
    if not meta_path.exists():
        print(f"WARNING: {paper_dir.name} -- no meta.yaml, skipping")
        return False

    bib  = _parse_bib(bib_path)
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}

    # Destination inside docs/
    dest = OUT / paper_dir.name
    dest.mkdir(parents=True, exist_ok=True)

    # Copy notebook files so nbsphinx can find them
    for nb in notebooks:
        shutil.copy2(nb, dest / nb.name)

    # Toctree entries: strip the full .pct.py suffix so Sphinx resolves
    # the nbsphinx-registered source suffix correctly.
    nb_stems = [nb.name[: -len(".pct.py")] for nb in notebooks]
    toctree_entries = "\n".join(f"   {s}" for s in nb_stems)

    intro = _build_intro(paper_dir, bib, meta)

    index_rst = f"""{intro}
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
