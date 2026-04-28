#!/usr/bin/env python3
"""Regenerate the Papers table in README.md from registry.yaml.

Run manually or via CI:
    python scripts/update_readme.py
"""
import pathlib
import yaml

ROOT = pathlib.Path(__file__).parent.parent
REGISTRY = ROOT / "registry.yaml"
README = ROOT / "README.md"
START = "<!-- PAPERS_START -->"
END = "<!-- PAPERS_END -->"


def fmt_authors(authors: list) -> str:
    def last(a):
        return a.split(",")[0].strip()
    if len(authors) == 1:
        return last(authors[0])
    if len(authors) == 2:
        return f"{last(authors[0])} & {last(authors[1])}"
    return f"{last(authors[0])} et al."


def build_table(papers: list) -> str:
    rows = [
        "| Year | Reference | Network | Approach |",
        "|------|-----------|---------|----------|",
    ]
    for p in sorted(papers, key=lambda x: x["year"]):
        authors = fmt_authors(p["authors"])
        journal = p.get("journal_abbrev") or p["journal"]
        ref = f"[{authors}, *{journal}*](papers/{p['id']}/)"
        network = f"{p['network']} - {p.get('region', '')}"
        approach = p.get("short_description", "")
        rows.append(f"| {p['year']} | {ref} | {network} | {approach} |")
    return "\n".join(rows)


def update():
    registry = yaml.safe_load(REGISTRY.read_text())
    table = build_table(registry["papers"])

    readme = README.read_text()
    start_idx = readme.index(START) + len(START)
    end_idx = readme.index(END)
    new_readme = (
        readme[:start_idx]
        + "\n"
        + table
        + "\n"
        + readme[end_idx:]
    )
    README.write_text(new_readme)
    print("README.md updated.")


if __name__ == "__main__":
    update()
