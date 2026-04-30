"""Generate docs/auto_papers/<paper>/index.rst for every paper.

Each paper page contains:
  1. Citation (Tectonophysics style) + BibTeX block
  2. At-a-glance table (metadata + processing params from project.yaml)
  3. Data bundles table (from bundle_pointer.yaml if present)
  4. How-to-use code snippet
  5. Notebook gallery (if notebooks exist)

Writes docs/_papers_toctree.rst — labeled sidebar toctree (gitignored).

Called automatically by docs/conf.py setup() and manually via:
    python scripts/gen_notebook_rst.py
"""

import ast
import pathlib
import re
import shutil
import textwrap

import bibtexparser
import yaml

ROOT   = pathlib.Path(__file__).parent.parent
PAPERS = ROOT / "papers"
OUT    = ROOT / "docs" / "auto_papers"

# Workflow category order — used to determine pipeline end point
_WORKFLOW_ORDER = [
    "global", "preprocess", "cc", "filter", "stack", "refstack",
    "mwcs", "mwcs_dtt", "mwcs_dtt_dvv",
    "stretching", "stretching_dvv",
    "wavelet", "wavelet_dtt", "wavelet_dtt_dvv",
    "psd", "psd_rms",
]


# ---------------------------------------------------------------------------
# BibTeX / citation helpers
# ---------------------------------------------------------------------------

def _parse_bib(bib_path: pathlib.Path) -> dict:
    raw_text = bib_path.read_text(encoding="utf-8")
    bib = bibtexparser.loads(raw_text)
    e   = bib.entries[0]
    authors_raw = [a.strip() for a in e.get("author", "").split(" and ")]
    return {
        "title":    re.sub(r"[{}]", "", e.get("title", "")),
        "authors":  [_abbreviate(a) for a in authors_raw if a],
        "year":     e.get("year", ""),
        "journal":  re.sub(r"[{}]", "", e.get("journal", "")),
        "volume":   e.get("volume", ""),
        "pages":    e.get("pages", "").replace("--", "\u2013"),
        "doi":      e.get("doi", ""),
        "raw_text": raw_text.strip(),
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
    authors = bib["authors"]
    last    = authors[0].split(",")[0].strip() if authors else "Unknown"
    suffix  = " et al." if len(authors) > 1 else ""
    return f"{bib['year']} \u2014 {last}{suffix}"


def _format_citation(bib: dict, journal_abbrev: str = "") -> str:
    """Tectonophysics-style citation string (RST)."""
    authors   = ", ".join(bib["authors"])
    year      = bib["year"]
    journal   = journal_abbrev or bib["journal"]
    vol_pages = (f", {bib['volume']}" if bib["volume"] else "") + \
                (f", {bib['pages']}"  if bib["pages"]  else "")
    doi_link  = (f"`https://doi.org/{bib['doi']} <https://doi.org/{bib['doi']}>`_"
                 if bib["doi"] else "")
    return f"*{authors} ({year}). {bib['title']}. {journal}{vol_pages}.* {doi_link}"


# ---------------------------------------------------------------------------
# project.yaml parsing
# ---------------------------------------------------------------------------

def _parse_project(proj_path: pathlib.Path) -> dict:
    """Extract key processing parameters from project.yaml."""
    proj = yaml.safe_load(proj_path.read_text(encoding="utf-8")) or {}

    # Period
    g = proj.get("global_1", {})
    period = f"{g.get('startdate', '?')} \u2013 {g.get('enddate', '?')}"

    # Sampling rate + components from first preprocess/cc block
    pre = next((proj[k] for k in proj if re.match(r"preprocess_\d+$", k)), {})
    cc  = next((proj[k] for k in proj if re.match(r"cc_\d+$", k)), {})
    sr  = cc.get("cc_sampling_rate") or pre.get("cc_sampling_rate", "")
    comps = ", ".join(filter(None, [
        cc.get("components_to_compute", ""),
        cc.get("components_to_compute_single_station", ""),
    ])).strip(", ") or "?"

    # Frequency bands from filter steps
    bands = []
    for k in sorted(k for k in proj if re.match(r"filter_\d+$", k)):
        filt = proj[k]
        fmin = filt.get("freqmin", "")
        fmax = filt.get("freqmax", "")
        if fmin and fmax:
            bands.append(f"{fmin}\u2013{fmax} Hz")
    freq_str = ", ".join(bands) if bands else "?"

    # Moving stacks from first stack step
    stk = next((proj[k] for k in proj if re.match(r"stack_\d+$", k)), {})
    ms_raw = stk.get("mov_stack", "")
    try:
        ms_parsed = ast.literal_eval(ms_raw) if isinstance(ms_raw, str) else ms_raw
        ms_str = ", ".join(f"{w}/{s}" for w, s in ms_parsed)
    except Exception:
        ms_str = str(ms_raw)

    # Pipeline end: deepest category present
    present_cats = set()
    for k in proj:
        for cat in _WORKFLOW_ORDER:
            if re.match(rf"{cat}_\d+$", k):
                present_cats.add(cat)
    pipeline_end = next(
        (cat for cat in reversed(_WORKFLOW_ORDER) if cat in present_cats), "?"
    )

    return {
        "period":       period,
        "sampling_rate": f"{sr} Hz" if sr else "?",
        "components":   comps,
        "freq_bands":   freq_str,
        "mov_stacks":   ms_str,
        "pipeline_end": pipeline_end,
    }


# ---------------------------------------------------------------------------
# bundle_pointer.yaml parsing
# ---------------------------------------------------------------------------

def _parse_bundle_pointer(bp_path: pathlib.Path) -> dict:
    """Return {level: {description, url, sha256, size_gb}} or {}."""
    if not bp_path.exists():
        return {}
    bp = yaml.safe_load(bp_path.read_text(encoding="utf-8")) or {}
    return bp.get("levels", {})


# ---------------------------------------------------------------------------
# RST block builders
# ---------------------------------------------------------------------------

def _rst_table(rows: list, col1: int = None, col2: int = None) -> list:
    """Simple two-column RST grid table."""
    col1 = col1 or max(len(r[0]) for r in rows)
    col2 = col2 or max(len(r[1]) for r in rows)
    sep  = f"+{'-'*(col1+2)}+{'-'*(col2+2)}+"
    lines = [sep]
    for k, v in rows:
        lines.append(f"| {k:<{col1}} | {v:<{col2}} |")
        lines.append(sep)
    return lines


def _section(title: str, char: str = "-") -> list:
    return ["", title, char * len(title), ""]


def _build_page(paper_dir: pathlib.Path, bib: dict, meta: dict,
                proj: dict, bundles: dict, notebooks: list) -> str:
    """Assemble the full RST page."""
    full_title  = bib["title"] or paper_dir.name
    paper_id    = paper_dir.name
    journal_abbrev = meta.get("journal_abbrev", "")
    citation    = _format_citation(bib, journal_abbrev)
    short_desc  = meta.get("short_description", "")

    lines = [
        full_title,
        "=" * len(full_title),
        "",
        citation,
        "",
    ]
    if short_desc:
        lines += [short_desc, ""]

    # ------------------------------------------------------------------
    # 1. At a glance
    # ------------------------------------------------------------------
    lines += _section("At a glance")

    rows = []
    if meta.get("network"):
        rows.append(("Network",        meta["network"]))
    if meta.get("region"):
        rows.append(("Region",         meta["region"]))
    if proj.get("period"):
        rows.append(("Period",         proj["period"]))
    if proj.get("sampling_rate"):
        rows.append(("Sampling rate",  proj["sampling_rate"]))
    if proj.get("components"):
        rows.append(("Components",     proj["components"]))
    if proj.get("freq_bands"):
        rows.append(("Frequency bands",proj["freq_bands"]))
    if proj.get("mov_stacks"):
        rows.append(("Moving stacks",  proj["mov_stacks"]))
    if proj.get("pipeline_end"):
        rows.append(("Pipeline end",   proj["pipeline_end"]))
    rows.append(("Data open",  "yes" if meta.get("data_open")  else "no"))
    rows.append(("Validated",  "yes" if meta.get("validated")   else "no"))

    lines += _rst_table(rows)
    lines.append("")

    # ------------------------------------------------------------------
    # 2. BibTeX
    # ------------------------------------------------------------------
    lines += _section("BibTeX")
    lines.append(".. code-block:: bibtex")
    lines.append("")
    for bib_line in bib["raw_text"].splitlines():
        lines.append(f"   {bib_line}")
    lines.append("")

    # ------------------------------------------------------------------
    # 3. Data bundles
    # ------------------------------------------------------------------
    lines += _section("Data bundles")

    if bundles:
        lines += [
            ".. list-table::",
            "   :header-rows: 1",
            "   :width: 100%",
            "   :widths: 10 35 10 15 30",
            "",
            "   * - Level",
            "     - Description",
            "     - Size",
            "     - SHA256",
            "     - URL",
        ]
        for level, info in bundles.items():
            desc    = info.get("description", "")
            size_gb = info.get("size_gb", "")
            sha256  = info.get("sha256", "")[:12] + "..." if info.get("sha256") else ""
            url     = info.get("url", "")
            url_rst = f"`download <{url}>`_" if url else ""
            size_str = f"{size_gb} GB" if size_gb else "?"
            lines += [
                f"   * - ``{level}``",
                f"     - {desc}",
                f"     - {size_str}",
                f"     - ``{sha256}``",
                f"     - {url_rst}",
            ]
        lines.append("")
    else:
        lines += [
            ".. note::",
            "",
            "   No data bundles have been published for this paper yet.",
            "",
        ]

    # ------------------------------------------------------------------
    # 4. How to use
    # ------------------------------------------------------------------
    lines += _section("How to use")

    if bundles:
        first_level = next(iter(bundles))
        size_hint   = bundles[first_level].get("size_gb", "?")
        lines += [
            ".. code-block:: python",
            "",
            "   from msnoise.papers import MRP",
            "",
            "   mrp   = MRP()",
            f"   paper = mrp.get_paper(\"{paper_id}\")",
            "   paper.info()   # show available levels",
            "",
            f"   # Download the '{first_level}' bundle (~{size_hint} GB, cached after first run)",
            f"   project = paper.get_project(\"{first_level}\")",
            "",
            "   for result in project.list(\"stack\"):",
            "       ccfs = result.get_ccf()",
            "",
        ]
    else:
        lines += [
            ".. code-block:: python",
            "",
            "   from msnoise.papers import MRP",
            "",
            "   mrp   = MRP()",
            f"   paper = mrp.get_paper(\"{paper_id}\")",
            "   paper.info()   # show metadata and available levels",
            "",
        ]

    # ------------------------------------------------------------------
    # 5. Notebooks
    # ------------------------------------------------------------------
    if notebooks:
        nb_stems = [nb.name[: -len(".pct.py")] for nb in notebooks]
        toctree_entries = "\n".join(f"   {s}" for s in nb_stems)
        lines += [
            "",
            ".. nbgallery::",
            "   :maxdepth: 1",
            "   :caption: Notebooks",
            "",
            toctree_entries,
            "",
        ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Per-paper generation
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

    # Optional sources
    proj_files = sorted(paper_dir.glob("project*.yaml"))
    proj = _parse_project(proj_files[0]) if proj_files else {}
    bundles = _parse_bundle_pointer(paper_dir / "bundle_pointer.yaml")

    dest = OUT / paper_dir.name
    dest.mkdir(parents=True, exist_ok=True)

    # Notebooks (optional)
    nb_src    = paper_dir / "notebooks"
    notebooks = sorted(nb_src.glob("nb_*.pct.py")) if nb_src.is_dir() else []
    for nb in notebooks:
        shutil.copy2(nb, dest / nb.name)

    page = _build_page(paper_dir, bib, meta, proj, bundles, notebooks)
    (dest / "index.rst").write_text(page, encoding="utf-8")

    return True, _short_title(bib)


# ---------------------------------------------------------------------------
# Sidebar toctree
# ---------------------------------------------------------------------------

def _write_papers_toctree(entries: list):
    out = ROOT / "docs" / "_papers_toctree.rst"
    if not entries:
        out.write_text("", encoding="utf-8")
        return
    toc_lines = [".. toctree::", "   :maxdepth: 1", "   :caption: Papers", ""]
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
