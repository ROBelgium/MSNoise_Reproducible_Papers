# Yates et al. (2023) — Piton de la Fournaise & Mt. Ruapehu

**Full title:** Assessing similarity in continuous seismic cross-correlation functions using hierarchical clustering: application to Ruapehu and Piton de la Fournaise volcanoes  
**DOI:** [10.1093/gji/ggac469](https://doi.org/10.1093/gji/ggac469)  
**Journal:** Geophysical Journal International, 233, 472–489

## Summary

MSNoise is used to compute CCFs and apparent velocity changes (stretching → stretching_dvv).
The main analysis — agglomerative hierarchical clustering of 10-day stacked CCFs — is performed externally with `scipy.cluster.hierarchy`.
Two sites, two frequency bands each.

## Two project files

| File | Site | Network | Period |
|------|------|---------|--------|
| `project_pdf.yaml` | Piton de la Fournaise | YA (UnderVolc/RESIF) | 2009-09-01 – 2011-05-01 |
| `project_ruapehu.yaml` | Mt. Ruapehu | NZ (GeoNet) | 2005-01-01 – 2008-12-31 |

## Processing notes

- 0.01–10 Hz bandpass, decimate to 25 Hz, **1-bit normalization** (`winsorizing=-1`), spectral whitening, 30-min windows, 10-day linear stack
- PdF: no instrument response removal (flat BB response); Ruapehu: response removal applied
- Ruapehu polarity note: DRZ and FWVZ had reversed polarity — flip waveforms before import
- Pipeline: preprocess → cc → filter → stack + refstack → stretching → stretching_dvv
- **PdF** (both bands): static lag — band 1: [10–45] s, band 2: [10–30] s
- **Ruapehu** (both bands): dynamic lag (`stretching_lag=dynamic`, `stretching_v=0.5` km/s = 500 m/s)
- Max stretch: ±1% (`stretching_max=0.01`)
- Clustering notebook: [github.com/asyates/hclusterCCFs](https://github.com/asyates/hclusterCCFs)

## Data access

- PdF (YA): RESIF — `http://ws.resif.fr` (doi:10.18715/REUNION.OVPF)
- Ruapehu (NZ): GeoNet — `https://service.geonet.org.nz` (doi:10.21420/G19Y-9D40)
