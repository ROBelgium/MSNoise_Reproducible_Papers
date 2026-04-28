#!/usr/bin/env python3
"""Sync registry.yaml from papers/ folder contents.

Auto-derived from citation.bib + project.yaml:
    title, authors, year, doi, journal, volume, pages,
    network, period, components, cc_types, n_filters, data_source

Read from meta.yaml (source of truth for manual fields):
    short_description, journal_abbrev, region,
    msnoise_version_min, levels_available

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

MANUAL_DEFAULTS = {
    "short_description": "",
    "journal_abbrev": "",
    "levels_available": [],
    "msnoise_version_min": "2.0.0",
    "region": "",
    "network": "",
    "data_open": False,
}


def parse_bib(path: pathlib.Path) -> dict:
    bib = bibtexparser.loads(path.read_text(encoding="utf-8"))
    e = bib.entries[0]
    authors = [_normalise_author(a.strip()) for a in e.get("author", "").split(" and ")]
    title = e.get("title", "").replace("{", "").replace("}", "")
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
    given = rest.strip()
    if re.match(r"^[A-Z]\.(\s?[A-Z]\.)*$", given):
        return f"{last.strip()}, {given}"
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

    cc_types = set()
    for field in ("cc_type", "cc_type_single_station_AC", "cc_type_single_station_SC"):
        val = cc.get(field)
        if val in ("CC", "PCC"):
            cc_types.add(val)

    ds = proj.get("data_sources") or [{}]
    data_source = ds[0].get("uri", "") if ds else ""

    return {
        "network": "",
        "period": period,
        "components": sorted(comps),
        "cc_types": sorted(cc_types),
        "n_filters": n_filters,
        "data_source": data_source,
    }


def parse_meta(path: pathlib.Path) -> dict:
    """Read meta.yaml — source of truth for all manual fields."""
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def build_entry(paper_dir: pathlib.Path) -> dict:
    pid = paper_dir.name
    bib = parse_bib(paper_dir / "citation.bib")
    proj = parse_project(paper_dir / "project.yaml")
    meta = parse_meta(paper_dir / "meta.yaml")

    entry = {"id": pid}
    entry.update(bib)
    entry.update(proj)

    # Manual fields: meta.yaml wins, fall back to defaults
    for field, default in MANUAL_DEFAULTS.items():
        entry[field] = meta.get(field, default)

    key_order = [
        "id", "title", "authors", "year", "doi", "journal", "journal_abbrev",
        "volume", "pages", "network", "region", "period", "components", "cc_types",
        "n_filters", "short_description", "msnoise_version_min", "levels_available", "data_open",
        "data_source",
    ]
    return {k: entry[k] for k in key_order if k in entry}


def update():
    papers_root = ROOT / "papers"
    paper_dirs = sorted(d for d in papers_root.iterdir() if d.is_dir())

    if not paper_dirs:
        print("No paper folders found.", file=sys.stderr)
        sys.exit(1)

    papers = []
    ok = True
    for d in paper_dirs:
        if not (d / "citation.bib").exists() or not (d / "project.yaml").exists():
            print(f"SKIP {d.name} — missing citation.bib or project.yaml")
            continue
        if not (d / "meta.yaml").exists():
            print(f"WARN {d.name} — missing meta.yaml, using defaults")
        entry = build_entry(d)
        if not entry.get("short_description"):
            print(f"WARN {d.name} — short_description is empty in meta.yaml")
            ok = False
        papers.append(entry)
        print(f"  OK  {d.name}")

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
    if not ok:
        print("WARNING: some short_description fields are empty — fill in meta.yaml",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    update()
