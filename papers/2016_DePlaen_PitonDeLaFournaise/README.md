# De Plaen et al. (2016) — Piton de la Fournaise, La Réunion

**Full title:** Single-station monitoring of volcanoes using seismic ambient noise  
**DOI:** [10.1002/2016GL070078](https://doi.org/10.1002/2016GL070078)  
**Journal:** Geophysical Research Letters, 43, 8511–8518

## Summary

Introduces and validates the single-station approach (SC + AC) as an alternative to inter-station CC at volcanoes with sparse networks. Applied to Piton de la Fournaise around the June 2014 eruption. SC results match the classical approach; AC is less stable without spectral whitening.

## Network & stations

- **Network:** PF (OVPF/IPGP) — stations CSS, FJS, FOR (broadband 3-component)
- **Available via:** RESIF
- **Period:** 2014-01-01 – 2014-07-31

## Processing notes

- 0.01–8 Hz bandpass, decimate to 20 Hz, `winsorizing=3`
- `whitening="C"`: applied only when components differ (SC), not AC
- 4 frequency bands → 4 separate filter/stack/mwcs/dtt lineages
- Pipeline: preprocess → cc → filter × 4 → stack + refstack → mwcs → mwcs_dtt → mwcs_dtt_dvv
