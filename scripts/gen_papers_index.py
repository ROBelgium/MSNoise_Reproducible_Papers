"""Generate docs/papers_index.rst from registry.yaml.

Called automatically by docs/conf.py setup() before every Sphinx build,
and manually via ``python scripts/gen_papers_index.py``.
"""

import pathlib
import yaml

ROOT = pathlib.Path(__file__).parent.parent
REGISTRY = ROOT / "registry.yaml"
OUT = ROOT / "docs" / "papers_index.rst"


def _levels_str(levels: list) -> str:
    if not levels:
        return "-"
    return ", ".join(f"``{lv}``" for lv in levels)


def _bool_flag(val: bool) -> str:
    return "✅" if val else "❌"


def generate(registry_path: pathlib.Path = REGISTRY, out_path: pathlib.Path = OUT):
    with open(registry_path, encoding="utf-8") as fh:
        registry = yaml.safe_load(fh)

    papers = registry.get("papers", [])

    lines = [
        "Papers",
        "======",
        "",
        f"The registry currently contains **{len(papers)} paper(s)**.",
        "",
        "Columns: **Open** = data freely available via FDSN or public archive;",
        "**Validated** = pipeline run end-to-end by a maintainer.",
        "",
        ".. list-table::",
        "   :header-rows: 1",
        "   :widths: 6 28 6 8 10 18 5 5",
        "",
        "   * - Year",
        "     - Title / Authors",
        "     - Journal",
        "     - Network",
        "     - Region",
        "     - Levels available",
        "     - Open",
        "     - Validated",
    ]

    for p in sorted(papers, key=lambda x: x.get("year", 0)):
        paper_id  = p.get("id", "")
        year      = p.get("year", "")
        title     = p.get("title", paper_id)
        authors   = ", ".join(p.get("authors", []))
        journal   = p.get("journal_abbrev", "")
        network   = p.get("network", "")
        region    = p.get("region", "")
        levels    = _levels_str(p.get("levels_available", []))
        open_flag = _bool_flag(p.get("data_open", False))
        val_flag  = _bool_flag(p.get("validated", False))

        # Link to auto-generated gallery if notebooks exist.
        nb_dir = ROOT / "papers" / paper_id / "notebooks"
        if nb_dir.is_dir() and any(nb_dir.glob("nb_*.py")):
            title_cell = f":doc:`auto_papers/{paper_id}/index`"
        else:
            title_cell = title

        lines += [
            f"   * - {year}",
            f"     - | {title_cell}",
            f"       | *{authors}*",
            f"     - {journal}",
            f"     - {network}",
            f"     - {region}",
            f"     - {levels}",
            f"     - {open_flag}",
            f"     - {val_flag}",
        ]

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Written {out_path} ({len(papers)} papers)")


if __name__ == "__main__":
    generate()