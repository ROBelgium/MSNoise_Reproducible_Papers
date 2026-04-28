# Yates et al. (2024) — Mt. Ruapehu, New Zealand

**Full title:** Seasonal Snow Cycles and Their Possible Influence on Seismic Velocity Changes and Eruptive Activity at Ruapehu Volcano, New Zealand  
**DOI:** [10.1029/2024JB029568](https://doi.org/10.1029/2024JB029568)  
**Journal:** Journal of Geophysical Research: Solid Earth, 129, e2024JB029568

## Summary

Single-station SC on 9 GeoNet stations around Ruapehu over 2005–2009. Seasonal velocity changes (±0.5%) are closely correlated with winter snow cover at summit stations. Velocity changes at off-volcano stations follow groundwater (precipitation) cycles instead. Depth inversion suggests seasonal changes occur within the upper few hundred meters. The timing of the 2006 and 2007 spring phreatic eruptions coincides with an earlier velocity decrease at 200–300 m depth linked to snow unloading.

## MSNoise scope

MSNoise handles **CCF computation only** (preprocess → cc → filter → stack + refstack). Velocity changes are computed **externally** using the cross-wavelet transform approach of Mao et al. (2020) via PyCWT — not MSNoise's built-in wavelet step.

## Network & stations

- **Network:** NZ (GeoNet) — 7 short-period + 2 broadband
- **Stations:** DRZ, TRVZ, FWVZ, WNVZ, OTVZ, NGZ, TUVZ, WPVZ, MTVZ
- **Available via:** GeoNet FDSN (doi:10.21420/G19Y-9D40)
- **Period:** 2005-01-01 – 2009-01-01

## Processing notes

- 0.01–10 Hz → decimate to 25 Hz, whitening 0.1–8.0 Hz (`whitening="C"`), `winsorizing=3`, 30-min windows, 10-day linear stack
- SC only (EN, EZ, NZ); AC excluded — 1-bit whitening incompatible with classical AC (`whitening="C"` handles this)
- No instrument response removal (single-station approach)
- Reference stack: all available days
- **External velocity analysis:** cross-wavelet transform (Morlet, 0.1–8.0 Hz), coda start=5 s, dynamic end=20 cycles (max 120 s), coherence threshold=0.7, max dt=0.3 s, ≥25% non-zero weights required
- **Depth inversion:** Haney & Tsai (2017) Rayleigh wave kernels, 4-layer Vs model from Godfrey et al. (2017)
