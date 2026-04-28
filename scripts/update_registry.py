#!/usr/bin/env python3
"""Sync registry.yaml from papers/ folder contents.

Auto-derived from citation.bib + project.yaml:
    title, authors, year, doi, journal, volume, pages,
    network, period, components, cc_types, n_filters, data_source

Preserved from existing registry.yaml (manual fields):
    short_description, journal_abbrev, levels_available,
    msnoise_version_min, region

Run manually or via CI:
    python scripts/update_registry.py
"""
import pathlib
import re
import sys

import bibtexparser
import yaml

ROOT = pathlib.Path(__file__).parent.parent
REGISTRY = ROOT / "registry.yaml"

# Fields that are hand-curated — never overwritten by auto-derivation
MANUAL_FIELDS = ("short_description", "journal_abbrev", "levels_available",
                 "msnoise_version_min", "region")

MANUAL_DEFAULTS = {
    "short_description": "",
    "journal_abbrev": "",
    "levels_available": [],
    "msnoise_version_min": "2.0.0",
    "region": "",
}


def parse_bib(path: pathlib.Path) -> dict:
    bib = bibtexparser.loads(path.read_text(encoding="utf-8"))
    e = bib.entries[0]
    authors = [a.strip() for a in e.get("author", "").split(" and ")]
    # Normalise author format to "Last, Initials" where bib has full names
    authors = [_normalise_author(a) for a in authors]
    title = e.get("title", "").replace("{", "").replace("}", "")
    # Replace unicode hyphens / non-breaking hyphens with plain hyphen
    title = title.replace("\u2010", "-").replace("\u2011", "-")
    vol = e.get("volume", "")
    return {
        "title": title,
        "authors": authors,
        "year": int(e.get("year", 0)),
        "doi": e.get("doi", ""),
        "journal": e.get("journal", ""),
        "volume": int(vol) if vol.isdigit() else None,
        "pages": e.get("pages", "").replace("--", "-") or None,
    }


def _normalise_author(author: str) -> str:
    """Shorten 'De Plaen, Raphael S. M.' → 'De Plaen, R.S.M.'"""
    if "," not in author:
        return author
    last, rest = author.split(",", 1)
    # Extract initials from given names
    given = rest.strip()
    # If already initials-only (e.g. "T."), keep as-is
    if re.match(r"^[A-Z]\.(\s?[A-Z]\.)*$", given):
        return f"{last.strip()}, {given}"
    # Convert full given names to initials
    initials = "".join(
        f"{w[0].upper()}." for w in re.split(r"[\s\-]+", given) if w and w[0].isupper()
    )
    return f"{last.strip()}, {initials}"


def parse_project(path: pathlib.Path) -> dict:
    proj = yaml.safe_load(path.read_text())

    g = proj.get("global_1", {})
    period = [str(g.get("startdate", "")), str(g.get("enddate", ""))]

    n_filters = sum(1 for k in proj if re.match(r"filter_\d+$", k))

    cc = proj.get("cc_1", {})
    comps = set()
    for field in ("components_to_compute", "components_to_compute_single_station"):
        val = cc.get(field, "") or ""
        comps.update(c.strip() for c in val.split(",") if c.strip())
    components = sorted(comps)

    cc_types = set()
    for field in ("cc_type", "cc_type_single_station_AC", "cc_type_single_station_SC"):
        val = cc.get(field)
        if val in ("CC", "PCC"):
            cc_types.add(val)
    cc_types_list = sorted(cc_types)

    ds = proj.get("data_sources") or [{}]
    data_source = ds[0].get("uri", "") if ds else ""

    # Network from stations endpoint URL
    stations = proj.get("stations") or {}
    ep = stations.get("station_endpoint", "") if isinstance(stations, dict) else ""
    m = re.search(r"[?&]network=([^&]+)", ep)
    network = m.group(1) if m else ""

    return {
        "network": network,
        "period": period,
        "components": components,
        "cc_types": cc_types_list,
        "n_filters": n_filters,
        "data_source": data_source,
    }


def load_existing() -> dict:
    """Return existing registry entries keyed by id."""
    if not REGISTRY.exists():
        return {}
    data = yaml.safe_load(REGISTRY.read_text()) or {}
    return {p["id"]: p for p in data.get("papers", [])}


def build_entry(paper_dir: pathlib.Path, existing: dict) -> dict:
    pid = paper_dir.name
    prev = existing.get(pid, {})

    bib = parse_bib(paper_dir / "citation.bib")
    proj = parse_project(paper_dir / "project.yaml")

    entry = {"id": pid}
    entry.update(bib)
    entry.update(proj)

    # Restore / default manual fields
    for field in MANUAL_FIELDS:
        entry[field] = prev.get(field, MANUAL_DEFAULTS[field])

    # Canonical key order
    key_order = [
        "id", "title", "authors", "year", "doi", "journal", "journal_abbrev",
        "volume", "pages", "network", "region", "period", "components", "cc_types",
        "n_filters", "short_description", "msnoise_version_min", "levels_available",
        "data_source",
    ]
    return {k: entry[k] for k in key_order if k in entry}


def update():
    existing = load_existing()
    papers_root = ROOT / "papers"
    paper_dirs = sorted(d for d in papers_root.iterdir() if d.is_dir())

    if not paper_dirs:
        print("No paper folders found.", file=sys.stderr)
        sys.exit(1)

    papers = []
    for d in paper_dirs:
        if not (d / "citation.bib").exists() or not (d / "project.yaml").exists():
            print(f"SKIP {d.name} — missing citation.bib or project.yaml")
            continue
        entry = build_entry(d, existing)
        papers.append(entry)
        print(f"  OK  {d.name}")

    # Sort by year, then id
    papers.sort(key=lambda p: (p["year"], p["id"]))

    header = (
        "# MSNoise Reproducible Papers - machine-readable registry\n"
        "# Each entry corresponds to a folder under papers/\n"
        "# Validated by _schema/registry.schema.yaml on PR\n"
        "# Generated by: python scripts/update_registry.py\n\n"
    )
    body = yaml.dump({"papers": papers}, allow_unicode=True, sort_keys=False,
                     default_flow_style=False)
    REGISTRY.write_text(header + body)
    print(f"registry.yaml updated ({len(papers)} papers).")


if __name__ == "__main__":
    update()
