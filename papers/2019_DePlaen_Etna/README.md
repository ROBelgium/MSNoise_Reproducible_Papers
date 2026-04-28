# De Plaen et al. (2019) — Mt. Etna, Sicily, Italy

**Full title:** Temporal Changes of Seismic Velocity Caused by Volcanic Activity at Mt. Etna Revealed by the Autocorrelation of Ambient Seismic Noise  
**DOI:** [10.3389/feart.2018.00251](https://doi.org/10.3389/feart.2018.00251)  
**Journal:** Frontiers in Earth Science, 6, 251

## Summary

AC-only study using PCC (Phase Cross-Correlation) on three broadband stations at Mt. Etna over 2013–2014. Detects velocity changes associated with volcanic activity. Demonstrates PCC advantage for autocorrelations (zero-lag spike suppression vs standard CC).

## Network & stations

- **Network:** IV (INGV) — stations ECPN, EPDN, EPLC (broadband 3-component, 100 Hz)
- **Data access:** ⚠️ IV network data not freely available via open FDSN
- **Period:** 2013-04-01 – 2014-10-31

## Processing notes

- 0.01–8 Hz bandpass, decimate to 20 Hz
- AC only (`components_to_compute_single_station: "ZZ,EE,NN"`); `cc_type_single_station_AC: PCC`
- `whitening="N"`: no whitening for AC (PCC handles zero-lag suppression natively)
- Pipeline: preprocess → cc → filter → stack + refstack → mwcs → mwcs_dtt → mwcs_dtt_dvv
