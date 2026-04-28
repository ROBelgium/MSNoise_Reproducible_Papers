# MSNoise Reproducible Papers

A curated registry of published studies that used [MSNoise](https://github.com/ROBelgium/MSNoise), or NOT!
Each paper comes with a fully documented configuration and (where available) archived data bundles
so results can be reproduced or used as a starting point for new studies.

## What's in each paper folder

| File | Purpose |
|------|---------|
| `project.yaml` | Complete MSNoise configuration — importable directly via `msnoise db init --from-yaml` |
| `citation.bib` | BibTeX reference |
| `README.md` | Paper summary, network/period notes, known caveats |
| `bundle_pointer.yaml` | *(when available)* URLs + checksums for pre-computed data bundles |
| `notebooks/` | *(when available)* Jupytext notebooks to reproduce the figures |

## How to use a configuration

```bash
# 1. Clone this registry
git clone https://github.com/ROBelgium/MSNoise_Reproducible_Papers

# 2. Create a new MSNoise project and import a config
mkdir my_project && cd my_project
msnoise db init --from-yaml ../MSNoise_Reproducible_Papers/papers/2014_Lecocq_MSNoiseUndervolc/project.yaml

# 3. Run from scratch (requires FDSN access for example) or import a bundle
msnoise run preprocess
```

## Papers

<!-- PAPERS_START -->
| Year | Reference | Network | Approach | Data | MSNoise | E2E ✔ | Project |
|------|-----------|---------|----------|------|---------|-------|---------|
| 2014 | [Lecocq et al., *SRL*](https://doi.org/10.1785/0220130073) | YA - Piton de la Fournaise, La Réunion | Foundation of MSNoise, CC-ZZ only | ✅ | ✅ | ❌ | [🔗](papers/2014_Lecocq_MSNoiseUndervolc) |
| 2016 | [De Plaen et al., *GRL*](https://doi.org/10.1002/2016GL070078) | PF - Piton de la Fournaise, La Réunion | Single-station SC + AC, 4 frequency bands | ✅ | ✅ | ❌ | [🔗](papers/2016_DePlaen_PitonDeLaFournaise) |
| 2019 | [De Plaen et al., *Front. Earth Sci.*](https://doi.org/10.3389/feart.2018.00251) | IV - Mt. Etna, Sicily, Italy | AC with PCC, velocity changes from volcanic activity | ❌ | ✅ | ❌ | [🔗](papers/2019_DePlaen_Etna) |
| 2019 | [Yates et al., *GRL*](https://doi.org/10.1029/2018GL080580) | NZ - White Island (Whakaari), New Zealand | Single-station SC + AC, 2 frequency bands, volcanic/coseismic/seasonal separation | ✅ | ✅ | ❌ | [🔗](papers/2019_Yates_WhiteIsland) |
| 2022 | [Wang et al., *EPSL*](https://doi.org/10.1016/j.epsl.2022.117443) | YH - Northern Hikurangi margin, New Zealand (offshore) | SC on OBS data, dv/v related to slow slip events, MWCS | ✅ | ✅ | ❌ | [🔗](papers/2022_Wang_Hikurangi) |
| 2023 | [Yates et al., *GJI*](https://doi.org/10.1093/gji/ggac469) | YA, NZ - Piton de la Fournaise, La Réunion + Mt. Ruapehu, New Zealand | CC + hierarchical clustering to assess CCF similarity; 2 sites, 2 frequency bands each | ✅ | ✅ | ❌ | [🔗](papers/2023_Yates_ClusteringCCFs) |
| 2024 | [Yates et al., *JGR Solid Earth*](https://doi.org/10.1029/2024JB029568) | NZ - Mt. Ruapehu, New Zealand | SC + cross-wavelet transform; seasonal snow influence on dv/v and spring eruption timing | ✅ | ✅ | ❌ | [🔗](papers/2024_Yates_RuapehuSnow) |
<!-- PAPERS_END -->

## Contributing

To add a paper, open a PR with a new folder under `papers/` following this checklist:

**Required files** (CI will reject the PR if any are missing):

| File | Content |
|------|---------|
| `project.yaml` | Full MSNoise config, importable via `msnoise db init --from-yaml` |
| `citation.bib` | BibTeX entry |
| `README.md` | Paper summary, network/period notes, known caveats |
| `meta.yaml` | Display fields — copy from an existing paper and edit |

**Before opening the PR**, run both scripts locally to regenerate the auto-derived files and verify everything looks correct:

```bash
python scripts/update_registry.py   # regenerates registry.yaml from all papers/*/meta.yaml + citation.bib + project.yaml
python scripts/update_readme.py     # regenerates the papers table in this README
```

Commit the updated `registry.yaml` and `README.md` as part of the PR.
The CI will re-run both scripts and fail if the committed files are out of sync.
