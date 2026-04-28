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
        "| Year | Reference | Network | Approach | Data | MSNoise | E2E ✔ | Project |",
        "|------|-----------|---------|----------|------|---------|-------|---------|",
    ]
    for p in sorted(papers, key=lambda x: x["year"]):
        authors = fmt_authors(p["authors"])
        journal = p.get("journal_abbrev") or p["journal"]
        ref = f"[{authors}, *{journal}*](https://doi.org/{p['doi']})"
        network = f"{p['network']} - {p.get('region', '')}"
        approach = p.get("short_description", "")
        data_flag = "✅" if p.get("data_open") else "❌"
        msnoise_flag = "✅" if p.get("uses_msnoise") else "❌"
        validated_flag = "✅" if p.get("validated") else "❌"
        project_link = f"[🔗](papers/{p['id']})"
        rows.append(f"| {p['year']} | {ref} | {network} | {approach} | {data_flag} | {msnoise_flag} | {validated_flag} | {project_link} |")
    return "\n".join(rows)


def update():
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    table = build_table(registry["papers"])

    readme = README.read_text(encoding="utf-8")
    if START not in readme or END not in readme:
        raise ValueError(
            f"Markers {START!r} / {END!r} not found in README.md — did you git pull?"
        )
    start_idx = readme.index(START) + len(START)
    end_idx = readme.index(END)
    new_readme = (
        readme[:start_idx]
        + "\n"
        + table
        + "\n"
        + readme[end_idx:]
    )
    README.write_text(new_readme, encoding="utf-8")
    print("README.md updated.")


if __name__ == "__main__":
    update()
