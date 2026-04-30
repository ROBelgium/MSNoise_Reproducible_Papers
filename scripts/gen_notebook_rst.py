"""Generate docs/auto_papers/<paper>/index.rst for every paper.

Builds each paper's page from meta.yaml + citation.bib.
Papers with notebooks also get their .pct.py files copied into the docs
tree so nbsphinx can render them.

Writes docs/_papers_toctree.rst — a labeled toctree (gitignored) that gives
sidebar entries short sortable titles while the page H1 keeps the full title.

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
# Metadata helpers (shared with gen_papers_index.py)
# ---------------------------------------------------------------------------

def _parse_bib(bib_path: pathlib.Path) -> dict:
    bib = bibtexparser.loads(bib_path.read_text(encoding="utf-8"))
    e   = bib.entries[0]
    raw = [a.strip() for a in e.get("author", "").split(" and ")]
    return {
        "title":   re.sub(r"[{}]", "", e.get("title", "")),
        "authors": [_abbreviate(a) for a in raw if a],
        "year":    e.get("year", ""),
        "journal": re.sub(r"[{}]", "", e.get("journal", "")),
        "volume":  e.get("volume", ""),
        "pages":   e.get("pages", "").replace("--", "\u2013"),
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


def _short_title(bib: dict) -> str:
    """Sortable short title for sidebar: '2014 \u2014 Lecocq et al.'"""
    authors = bib["authors"]
    last    = authors[0].split(",")[0].strip() if authors else "Unknown"
    suffix  = " et al." if len(authors) > 1 else ""
    return f"{bib['year']} \u2014 {last}{suffix}"


def _build_intro(paper_dir: pathlib.Path, bib: dict, meta: dict) -> str:
    """RST intro block: full title as H1, citation, short desc, metadata table."""
    full_title = bib["title"] or paper_dir.name
    authors    = ", ".join(bib["authors"])
    year       = bib["year"]
    journal    = meta.get("journal_abbrev") or bib["journal"]
    volume     = bib.get("volume", "")
    pages      = bib.get("pages", "")
    doi        = bib["doi"]
    short_desc = meta.get("short_description", "")
    network    = meta.get("network", "")
    region     = meta.get("region", "")
    levels     = ", ".join(f"``{l}``" for l in meta.get("levels_available", []))
    validated  = "yes" if meta.get("validated") else "no"
    data_open  = "yes" if meta.get("data_open")  else "no"

    # Tectonophysics-style citation
    vol_pages = ""
    if volume:
        vol_pages += f", {volume}"
    if pages:
        vol_pages += f", {pages}"
    doi_link = f"`https://doi.org/{doi} <https://doi.org/{doi}>`_" if doi else ""
    citation = f"*{authors} ({year}). {full_title}. {journal}{vol_pages}.* {doi_link}"

    lines = [
        full_title,
        "=" * len(full_title),
        "",
        citation,
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
# Per-paper page generation
# ---------------------------------------------------------------------------

def generate_paper(paper_dir: pathlib.Path):
    """Generate a docs page for one paper. Returns (True, short_title) or False."""
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

    dest = OUT / paper_dir.name
    dest.mkdir(parents=True, exist_ok=True)

    # Notebooks (optional)
    nb_src    = paper_dir / "notebooks"
    notebooks = sorted(nb_src.glob("nb_*.pct.py")) if nb_src.is_dir() else []
    for nb in notebooks:
        shutil.copy2(nb, dest / nb.name)

    intro = _build_intro(paper_dir, bib, meta)

    if notebooks:
        nb_stems = [nb.name[: -len(".pct.py")] for nb in notebooks]
        toctree_entries = "\n".join(f"   {s}" for s in nb_stems)
        nb_section = (
            "\n.. nbgallery::\n"
            "   :maxdepth: 1\n"
            "   :caption: Notebooks\n"
            "\n"
            f"{toctree_entries}\n"
        )
    else:
        nb_section = ""

    (dest / "index.rst").write_text(intro + nb_section, encoding="utf-8")
    if notebooks:
        return True, _short_title(bib) + " 🐍"
    return True, _short_title(bib)


# ---------------------------------------------------------------------------
# Sidebar toctree
# ---------------------------------------------------------------------------

def _write_papers_toctree(entries: list):
    """Write docs/_papers_toctree.rst with explicit labeled entries for all papers.

    Short sortable labels (e.g. '2014 — Lecocq et al.') appear in the sidebar
    while the page H1 keeps the full paper title.
    """
    out = ROOT / "docs" / "_papers_toctree.rst"
    if not entries:
        out.write_text("", encoding="utf-8")
        return

    toc_lines = [
        ".. toctree::",
        "   :maxdepth: 1",
        "   :caption: Papers",
        "",
    ]
    for short, paper_id in sorted(entries):
        toc_lines.append(f"   {short} <auto_papers/{paper_id}/index>")
    toc_lines.append("")

    out.write_text("\n".join(toc_lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(papers_root: pathlib.Path = PAPERS):
    ok      = []
    skipped = []
    entries = []

    for paper_dir in sorted(papers_root.iterdir()):
        if not paper_dir.is_dir():
            continue
        result = generate_paper(paper_dir)
        if result:
            _, short = result
            ok.append(paper_dir.name)
            entries.append((short, paper_dir.name))
        else:
            skipped.append(paper_dir.name)

    _write_papers_toctree(entries)

    print(f"Generated paper pages for: {', '.join(ok)}")
    if skipped:
        print(f"Skipped (missing bib/meta): {', '.join(skipped)}")


if __name__ == "__main__":
    generate()
