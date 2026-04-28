# Repository Structure & Development Notes

*Last updated: April 2026*

---

## Overview

`MSNoise_Reproducible_Papers` is a lightweight registry of published studies that used (or can be reproduced with) [MSNoise](https://github.com/ROBelgium/MSNoise). Each paper folder contains everything needed to re-initialise an MSNoise 2.x project from scratch and, where data bundles are published, to run the full analysis pipeline.

---

## Repository layout

```
MSNoise_Reproducible_Papers/
├── README.md                          ← auto-generated papers table
├── registry.yaml                      ← machine-readable index (auto-generated)
├── LICENCE.TXT
├── _schema/
│   ├── registry.schema.yaml           ← JSON-schema for registry.yaml
│   ├── meta.schema.yaml               ← JSON-schema for each meta.yaml
│   └── bundle_pointer.schema.yaml     ← JSON-schema for bundle_pointer.yaml
├── scripts/
│   ├── update_registry.py             ← regenerates registry.yaml from papers/
│   ├── update_readme.py               ← regenerates the papers table in README.md
│   └── check_projects.py             ← runs msnoise db init on every project*.yaml
├── papers/
│   └── <YYYY_FirstAuthor_ShortTitle>/
│       ├── project.yaml               ← MSNoise 2.x config (importable)
│       ├── citation.bib               ← BibTeX reference
│       ├── meta.yaml                  ← display/editorial fields
│       ├── README.md                  ← paper summary & processing notes
│       └── bundle_pointer.yaml        ← (optional) URLs to archived data bundles
└── .github/workflows/
    ├── validate.yml                   ← schema + registry consistency CI
    └── validate_projects.yml          ← MSNoise db init end-to-end CI
```

### Files per paper

| File | Auto-derived from | Purpose |
|------|------------------|---------|
| `project.yaml` | manual | Full MSNoise 2.x config; importable via `msnoise db init --from-yaml` |
| `citation.bib` | manual | BibTeX entry |
| `meta.yaml` | manual | Display fields: `journal_abbrev`, `region`, `network`, `short_description`, `msnoise_version_min`, `levels_available`, `data_open`, `uses_msnoise`, `validated` |
| `README.md` | manual | Paper summary, network/period, processing notes, data access |
| `registry.yaml` | `update_registry.py` | Machine-readable index aggregated from all `citation.bib` + `project.yaml` + `meta.yaml` |
| `README.md` (root) | `update_readme.py` | Papers table with emoji flags |

Papers with two independent datasets use multiple project files: `project_<site>.yaml` (e.g. `project_pdf.yaml`, `project_ruapehu.yaml`).

---

## Current papers (7)

| Year | Paper | Network | Pipeline end |
|------|-------|---------|-------------|
| 2014 | Lecocq, Caudron & Brenguier — *SRL* | YA (PdF, RESIF) | `mwcs_dtt_dvv` |
| 2016 | De Plaen et al. — *GRL* | PF (PdF, RESIF) | `mwcs_dtt_dvv` |
| 2019 | De Plaen et al. — *Front. Earth Sci.* | IV (Etna, INGV — not public) | `mwcs_dtt_dvv` |
| 2019 | Yates et al. — *GRL* | NZ (White Island, GeoNet) | `mwcs_dtt_dvv` × 2 bands |
| 2022 | Wang et al. — *EPSL* | YH (Hikurangi OBS, IRIS) | `mwcs_dtt_dvv` × 2 instrument types |
| 2023 | Yates et al. — *GJI* | YA + NZ (PdF + Ruapehu, RESIF/GeoNet) | `stretching_dvv` × 2 sites × 2 bands |
| 2024 | Yates et al. — *JGR Solid Earth* | NZ (Ruapehu, GeoNet) | `wavelet_dtt_dvv` |

---

## CI checks

### `validate.yml` (lightweight, runs on every push/PR)

- Validates `registry.yaml` against `_schema/registry.schema.yaml`
- Validates every `meta.yaml` against `_schema/meta.schema.yaml`
- Validates every `bundle_pointer.yaml` (if present) against `_schema/bundle_pointer.schema.yaml`
- Checks that every folder in `papers/` is listed in `registry.yaml` and vice versa
- Checks that every paper folder contains `README.md`, `citation.bib`, `project*.yaml`, `meta.yaml`
- Checks that `registry.yaml` is up to date (runs `update_registry.py` and diffs)
- Checks that `README.md` papers table is up to date (runs `update_readme.py` and diffs)

### `validate_projects.yml` (heavier, runs when `project*.yaml` files change)

Installs MSNoise from `master` once, then calls `scripts/check_projects.py` which loops over all `papers/**/project*.yaml` and runs:

```
msnoise db init --tech 1 --from-yaml <path>
```

in a fresh temporary directory for each file. All failures are collected before exiting so the full picture is visible in one run. Can also be run locally:

```bash
pip install "git+https://github.com/ROBelgium/MSNoise.git@master"

# test all papers
python scripts/check_projects.py

# test a single paper
python scripts/check_projects.py papers/2024_Yates_RuapehuSnow/project.yaml
```

---

## Adding a paper

1. Create `papers/<YYYY_Author_Title>/` with:
   - `project.yaml` — copy closest existing paper as template
   - `citation.bib` — BibTeX entry
   - `meta.yaml` — copy template below, fill in all fields
   - `README.md` — summary, network/period, processing notes, data access

2. Run both scripts and commit the results:

```bash
python scripts/update_registry.py   # regenerates registry.yaml
python scripts/update_readme.py     # regenerates papers table in README.md
git add .
git commit -m "Add <YYYY_Author_Title>"
```

3. Open a PR — CI will validate schemas, registry consistency, and attempt `db init` for every project file.

### `meta.yaml` template

```yaml
journal_abbrev: ""          # e.g. GRL, SRL, JGR Solid Earth
region: ""                  # geographic region / volcano name
network: ""                 # FDSN network code(s)
short_description: ""       # one-line approach summary for the table
msnoise_version_min: "2.0.0"
levels_available: []        # populated when bundles are published
data_open: false            # true if data is freely available (FDSN or archive)
uses_msnoise: true          # false for reproductions of pre-MSNoise studies
validated: false            # set to true once pipeline runs end-to-end
```

### `data_sources` requirement in `project.yaml`

Every `data_sources` entry must have a `name` field distinct from `"local"` (which is reserved by MSNoise as the default local SDS source):

```yaml
data_sources:
  - name: geonet-fdsn          # required; must be unique, not "local"
    uri: "fdsn://https://service.geonet.org.nz"
    network: "NZ"
    channels: "HH?"
```

---

## `validated` flag

The `validated: false` flag in `meta.yaml` tracks whether a project has been run end-to-end (data download → full pipeline → final dv/v plots). The CI only tests `db init` (structural validity). Once a paper is fully validated:

1. Set `validated: true` in `meta.yaml`
2. Run `python scripts/update_registry.py && python scripts/update_readme.py`
3. The ✅ column in the README table updates automatically

---

## Known config key names (MSNoise 2.x)

A few non-obvious mappings that differ from MSNoise 1.x or from paper notation:

| Category | Correct key | Wrong (ignored) |
|----------|-------------|-----------------|
| `mwcs` | `freqmin`, `freqmax` | `mwcs_low`, `mwcs_high` |
| `mwcs_dtt` | `dtt_maxdtt` | `dtt_maxdt` |
| `wavelet_dtt` | `wct_dtt_freqmin`, `wct_dtt_freqmax` | `wct_freqmin`, `wct_freqmax` |
| `data_sources` | requires `name:` field | omitting `name` → `KeyError` |
