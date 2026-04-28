# Lecocq, Caudron & Brenguier (2014) — Piton de la Fournaise, La Réunion

**Full title:** MSNoise, a Python Package for Monitoring Seismic Velocity Changes Using Ambient Seismic Noise  
**DOI:** [10.1785/0220130073](https://doi.org/10.1785/0220130073)  
**Journal:** Seismological Research Letters, 85(3), 715–726

## Summary

The paper introducing MSNoise. Demonstrates inter-station CC on the UnderVolc temporary network at Piton de la Fournaise over a ~2-year period including multiple eruptions. ZZ cross-correlations only, 5 overlapping moving-stack windows, full MWCS→DVV pipeline.

## Network & stations

- **Network:** YA (UnderVolc, IPGP) — 21 broadband 3-component stations, 100 Hz
- **Available via:** RESIF (doi:10.18715/REUNION.OVPF)
- **Period:** 2009-09-01 – 2011-07-01

## Processing notes

- Z-component only (inter-station ZZ pairs)
- 0.01–8 Hz bandpass, decimate to 20 Hz, 30-min windows, `winsorizing=3`
- 1 filter band; 5 moving-stack sizes
- Pipeline: preprocess → cc → filter → stack + refstack → mwcs → mwcs_dtt → mwcs_dtt_dvv
