# Yates et al. (2019) — White Island (Whakaari), New Zealand

**Full title:** Volcanic, Coseismic, and Seasonal Changes Detected at White Island (Whakaari) Volcano, New Zealand, Using Seismic Ambient Noise  
**DOI:** [10.1029/2018GL080580](https://doi.org/10.1029/2018GL080580)  
**Journal:** Geophysical Research Letters, 46, 99–108

## Summary

Single-station ambient noise interferometry at White Island volcano over a 10-year period (2007–2017).
Detects velocity changes related to volcanic unrest, large earthquakes, and seasonal environmental processes.
Distant onshore stations (HAZ, MWZ, MXZ, OPRZ, PUZ) provide a reference to separate volcanic from non-volcanic signals.

## Network & stations

- **Network:** NZ (GeoNet — publicly available)
- **On-volcano:** WIZ, WSRZ (3-component broadband)
- **Onshore reference:** HAZ, MWZ, MXZ, OPRZ, PUZ
- **Period:** 2007-01-01 – 2017-01-01
- **Channels:** HHE, HHN, HHZ

## Processing notes

- Two frequency bands with distinct cc/mwcs parameters (thesis Table A.5–A.7)
- `whitening="A"`: applied to all except autocorrelations (MSNoise handles AC automatically)
- `winsorizing=3`: clip at 3× RMS
- Band 1 (0.1–1.0 Hz): `corr_duration=7200 s`, MWCS wlen=16 s, minlag=20 s, width=60 s
- Band 2 (1.0–2.0 Hz): `corr_duration=14400 s`, MWCS wlen=12 s, minlag=10 s, width=30 s
- Parameters from MSNoise v1.5.1 (thesis appendix); adapted to MSNoise 2.x conventions

## Data access

Seismic data available via GeoNet FDSN: `https://service.geonet.org.nz`
