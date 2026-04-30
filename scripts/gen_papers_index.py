"""Generate docs/papers_index.rst from registry.yaml + papers/*/citation.bib.

Table metadata (levels, network, validated …) comes from registry.yaml.
Citation data (authors, title, journal, DOI …) is parsed fresh from each
paper's citation.bib — single source of truth.

Called automatically by docs/conf.py setup() before every Sphinx build,
and manually via ``python scripts/gen_papers_index.py``.
"""

import pathlib
import re

import bibtexparser
import yaml

ROOT     = pathlib.Path(__file__).parent.parent
REGISTRY = ROOT / "registry.yaml"
OUT      = ROOT / "docs" / "papers_index.rst"


# ---------------------------------------------------------------------------
# BibTeX helpers
# ---------------------------------------------------------------------------

def _parse_bib(bib_path: pathlib.Path) -> dict:
    """Return a dict with citation fields from a .bib file."""
    bib = bibtexparser.loads(bib_path.read_text(encoding="utf-8"))
    e   = bib.entries[0]
    raw_authors = [a.strip() for a in e.get("author", "").split(" and ")]
    return {
        "key":     e.get("ID", ""),
        "title":   _clean_braces(e.get("title", "")),
        "authors": [_abbreviate(a) for a in raw_authors if a],
        "year":    e.get("year", ""),
        "journal": _clean_braces(e.get("journal", "")),
        "volume":  e.get("volume", ""),
        "pages":   e.get("pages", "").replace("--", "-"),
        "doi":     e.get("doi", ""),
    }


def _clean_braces(s: str) -> str:
    """Remove BibTeX brace escapes: {MSNoise} -> MSNoise."""
    return re.sub(r"[{}]", "", s)


def _abbreviate(author: str) -> str:
    """'De Plaen, Raphael S. M.' -> 'De Plaen, R.S.M.'"""
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
    """Format author list for a reference entry."""
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]} & {authors[1]}"
    return ", ".join(authors[:-1]) + f", & {authors[-1]}"


def _ref_label(bib: dict) -> str:
    """Short RST footnote label, e.g. ``DePlaen2016``."""
    first = bib["authors"][0] if bib["authors"] else "Unknown"
    last  = first.split(",")[0].strip().replace(" ", "")
    return f"{last}{bib['year']}"


def _format_citation(bib: dict) -> str:
    """Full formatted citation as a single RST-safe string."""
    parts = [f"{_author_list(bib['authors'])} ({bib['year']})."]
    if bib["title"]:
        parts.append(f"*{bib['title']}*.")
    if bib["journal"]:
        vol_str   = f", **{bib['volume']}**" if bib["volume"] else ""
        pages_str = f", {bib['pages']}"      if bib["pages"]  else ""
        parts.append(f"*{bib['journal']}*{vol_str}{pages_str}.")
    if bib["doi"]:
        parts.append(f"`DOI:{bib['doi']} <https://doi.org/{bib['doi']}>`_")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# RST helpers
# ---------------------------------------------------------------------------

def _levels_str(levels: list) -> str:
    return ", ".join(f"``{lv}``" for lv in levels) if levels else "-"


def _bool_flag(val: bool) -> str:
    return "✅" if val else "❌"


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate(registry_path: pathlib.Path = REGISTRY, out_path: pathlib.Path = OUT):
    with open(registry_path, encoding="utf-8") as fh:
        registry = yaml.safe_load(fh)

    papers = registry.get("papers", [])
    sorted_papers = sorted(papers, key=lambda x: x.get("year", 0))

    # Pre-parse all bib files; skip papers missing one with a warning.
    bib_data = {}
    for p in sorted_papers:
        pid      = p.get("id", "")
        bib_path = ROOT / "papers" / pid / "citation.bib"
        if not bib_path.exists():
            print(f"WARNING: {pid} -- no citation.bib found, skipping reference")
            continue
        bib_data[pid] = _parse_bib(bib_path)

    # ------------------------------------------------------------------
    # Table
    # ------------------------------------------------------------------
    lines = [
        "Papers",
        "======",
        "",
        f"The registry currently contains **{len(papers)} paper(s)**.",
        "",
        "Columns: **Open** = data freely available via FDSN or public archive;",
        "**Validated** = pipeline run end-to-end by a maintainer;",
        "**Notebooks** = analysis notebooks available in this registry.",
        "",
        ".. list-table::",
        "   :header-rows: 1",
        "   :width: 80%",
        "",
        "   * - Title / Authors",
        "     - Network",
        "     - Region",
        "     - Levels available",
        "     - Open",
        "     - Validated",
        "     - Notebooks",
    ]

    for p in sorted_papers:
        pid       = p.get("id", "")
        bib       = bib_data.get(pid)
        network   = p.get("network", "")
        region    = p.get("region", "")
        levels    = _levels_str(p.get("levels_available", []))
        open_flag = _bool_flag(p.get("data_open", False))
        val_flag  = _bool_flag(p.get("validated", False))
        journal   = p.get("journal", "")

        if bib:
            label   = _ref_label(bib)
            title   = bib["title"]
            authors = ", ".join(bib["authors"])
            doi     = bib["doi"]
        else:
            label   = pid
            title   = p.get("title", pid)
            authors = ""
            doi     = p.get("doi", "")

        nb_dir  = ROOT / "papers" / pid / "notebooks"
        has_nbs = nb_dir.is_dir() and any(nb_dir.glob("nb_*.pct.py"))
        nb_flag = "✅" if has_nbs else ""

        # Title cell: gallery link > DOI link > plain text
        if has_nbs:
            title_cell = f":doc:`auto_papers/{pid}/index`"
        elif doi:
            title_cell = f"`{title} <https://doi.org/{doi}>`_"
        else:
            title_cell = title

        lines += [
            f"   * - | {title_cell}",
            f"       | *{authors}*",
            f"       | {journal}",
            f"     - {network}",
            f"     - {region}",
            f"     - {levels}",
            f"     - {open_flag}",
            f"     - {val_flag}",
            f"     - {nb_flag}",
        ]

    # ------------------------------------------------------------------
    # Full references section
    # ------------------------------------------------------------------
    lines += [
        "",
        "Full References",
        "---------------",
        "",
    ]
    for p in sorted_papers:
        pid = p.get("id", "")
        bib = bib_data.get(pid)
        if not bib:
            continue
        label    = _ref_label(bib)
        citation = _format_citation(bib)
        lines.append(f".. [{label}] {citation}")
        lines.append("")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Written {out_path} ({len(papers)} papers)")


if __name__ == "__main__":
    generate()