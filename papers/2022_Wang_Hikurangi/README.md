# Wang et al. (2022) — Northern Hikurangi Margin, New Zealand

**Full title:** Temporal velocity variations in the northern Hikurangi margin and the relation to slow slip  
**DOI:** [10.1016/j.epsl.2022.117443](https://doi.org/10.1016/j.epsl.2022.117443)  
**Journal:** Earth and Planetary Science Letters, 584, 117443

## Summary

Single-station SC on 9 HOBITSS ocean-bottom seismometers (OBS) deployed May 2014 – June 2015. Detects a ~0.05% velocity decrease during the 2014 SSE2 slow slip event (Mw 6.8) followed by a post-SSE recovery. Interpreted as fluid migration and/or crustal strain changes during the slow slip cycle. Original study used MSNoise 1.5; project.yaml targets MSNoise 2.x.

## Network & stations

- **Network:** YH (HOBITSS, IRIS-DMC, doi:10.7914/SN/YH_2014)
- **Stations used:** LOBS7, LOBS8, LOBS9 (broadband, Lamont) + EOBS1–5 (short-period 1 Hz, ERI Tokyo)
- **Excluded:** LOBS1/2/4/5/10 (insufficient data or on subducting Pacific plate); LOBS6 (horizontal orientation undetermined); LOBS3 (on subducting plate, excluded from average)
- **Period:** 2014-05-01 – 2015-06-30
- **Data access:** IRIS-DMC, experiment codes YH 2014-15 (seismic) and 8F 2014-15 (pressure)

## Two CC chains

| Step | Stations | `corr_duration` | Reason |
|------|----------|-----------------|--------|
| `cc_1` | LOBS (broadband) | 14400 s (4 hr) | Higher SNR for broadband OBS |
| `cc_2` | EOBS (short-period) | 1800 s (30 min) | Optimized for 1 Hz instruments |

Both chains share identical filter/mwcs/dtt parameters.

## Processing notes

- **Component rotation required:** horizontal components must be rotated to coastline-parallel (R) and coastline-perpendicular (T) **before data import**, using orientations from Zal et al. (2020). MSNoise does not handle this rotation.
- 0.02–2.0 Hz bandpass, decimate to 20 Hz, `winsorizing=3`, spectral whitening (`whitening="C"`), 70% overlap
- Stack: linear 20-day moving window; reference = all available days (after per-station quality filtering with correlation threshold 0.1–0.65 — applied manually outside MSNoise)
- MWCS: 20 s window / 4 s step, lag ±20–70 s, band 2.5–14 s (0.071–0.4 Hz)
- `dtt_mincoh=0.89`, `dtt_maxdtt=0.2 s`, `dtt_maxerr=0.1 s`
- Pipeline: preprocess → cc → filter → stack + refstack → mwcs → mwcs_dtt → mwcs_dtt_dvv
