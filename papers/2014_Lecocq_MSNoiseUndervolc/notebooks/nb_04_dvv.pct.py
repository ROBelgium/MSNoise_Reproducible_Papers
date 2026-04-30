# %% [markdown]
# # Figures 7 & 8 — dv/v Timeseries
#
# Reproduces Figures 7 and 8 of Lecocq, Caudron & Brenguier (2014), SRL 85(3).
#
# **Figure 7:** dv/v for the 10-day moving-window stack (paper compares
# MSNoise vs D. Clarke's FORTRAN — only MSNoise shown here).
#
# **Figure 8:** Detrended dv/v for five moving-window stacks (1, 2, 5, 10,
# 30 days).  Red = ``ALL`` network mean; green = weighted mean of pairs.
# Red vertical bands = eruptions of Piton de la Fournaise.
#
# **Bundle level required:** ``dvv``
#
# sphinx_gallery_thumbnail_number = 2

# %%
# ------------------------------------------------------------
# 0 — Data source
# ------------------------------------------------------------
PAPER_ID    = "2014_Lecocq_MSNoiseUndervolc"
LEVEL       = "dvv"
PROJECT_DIR = None

from msnoise.papers import MRP
from msnoise.project import MSNoiseProject

if PROJECT_DIR:
    project = MSNoiseProject.from_project_dir(PROJECT_DIR)
else:
    project = MRP().get_paper(PAPER_ID).get_project(LEVEL)

print(f"Project dir: {project.project_dir}")

# %%
# ------------------------------------------------------------
# 1 — Locate the mwcs_dtt_dvv result for filter_1
# ------------------------------------------------------------
FILTER    = "filter_1"
PAIR_TYPE = "CC"
COMPONENT = "ZZ"

dvv_results = [r for r in project.list("mwcs_dtt_dvv")
               if FILTER in r.lineage_names]
assert dvv_results, f"No mwcs_dtt_dvv results for {FILTER}"

result_dvv = dvv_results[0]
print(result_dvv)

params     = result_dvv.params
mov_stacks = params.stack.mov_stack   # list of ("1D","1D") tuples
print("Moving-window stacks:", mov_stacks)

# %%
# ------------------------------------------------------------
# 2 — Load all DVV datasets
# ------------------------------------------------------------
import pandas as pd
import numpy as np

dvv_data = {}
for ms in mov_stacks:
    ds = result_dvv.get_dvv(pair_type=PAIR_TYPE,
                             components=COMPONENT,
                             mov_stack=ms)
    if ds is not None:
        print(f"{ms}: vars={list(ds.data_vars)}")
        dvv_data[ms] = ds

# %%
# ------------------------------------------------------------
# 3 — Helpers
# ------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
from matplotlib.patches import Patch

ERUPTIONS = [
    ("2009-11-05", "2009-11-06"),
    ("2009-12-10", "2009-12-14"),
    ("2010-01-02", "2010-01-12"),
    ("2010-10-14", "2010-10-31"),
    ("2010-12-09", "2010-12-10"),
]
XLIM = (pd.Timestamp("2009-10-01"), pd.Timestamp("2011-07-01"))
YLIM = (-0.20, 0.20)


def shade_eruptions(ax):
    for t0, t1 in ERUPTIONS:
        ax.axvspan(pd.Timestamp(t0), pd.Timestamp(t1),
                   color="red", alpha=0.4, zorder=-1)


def fmt_xaxis(ax):
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


def detrend_valid(arr):
    """Linear detrend ignoring NaN."""
    mask = ~np.isnan(arr)
    if mask.sum() < 2:
        return arr
    out = arr.copy()
    x   = np.where(mask)[0]
    p   = np.polyfit(x, arr[mask], 1)
    out[mask] -= np.polyval(p, x)
    return out


def extract_series(ds):
    """Return (times, mean, std, wmean, wstd) pandas Series from a DVV dataset."""
    times = pd.to_datetime(ds.coords["times"].values)
    mean  = pd.Series(ds["mean"].values,  index=times)
    std   = pd.Series(ds["std"].values,   index=times) if "std"  in ds else None
    wmean = pd.Series(ds["weighted_mean"].values, index=times) if "weighted_mean" in ds else None
    wstd  = pd.Series(ds["weighted_std"].values,  index=times) if "weighted_std"  in ds else None
    return times, mean, std, wmean, wstd

# %%
# ------------------------------------------------------------
# 4 — Figure 7: dv/v — 10-day moving-window stack
# ------------------------------------------------------------
MS_FIG7 = ("10D", "1D")

if MS_FIG7 in dvv_data:
    ds7 = dvv_data[MS_FIG7]
    times, mean, std, wmean, wstd = extract_series(ds7)

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(times, mean, c="r", lw=0.8, label="MSNoise ALL")
    if std is not None:
        ax.fill_between(times, mean - std, mean + std,
                        color="r", alpha=0.2)
    if wmean is not None:
        ax.plot(times, wmean, c="g", lw=0.8,
                label="Weighted mean of pairs")
        if wstd is not None:
            ax.fill_between(times, wmean - wstd, wmean + wstd,
                            color="g", alpha=0.2)

    shade_eruptions(ax)
    ax.set_ylabel(r"$\delta v/v$ in %")
    ax.set_ylim(YLIM)
    ax.invert_yaxis()
    ax.set_xlim(XLIM)
    ax.grid(True, lw=0.3)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title(
        "Lecocq et al. (2014) — Fig. 7: "
        r"$\delta v/v$, 10-day moving-window, ZZ, 0.2–0.85 Hz"
    )
    fmt_xaxis(ax)
    plt.tight_layout()
    plt.savefig("fig7_dvv_10day.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Saved fig7_dvv_10day.png")
else:
    print(f"WARNING: {MS_FIG7} not available — skipping Fig 7")

# %%
# ------------------------------------------------------------
# 5 — Figure 8: detrended dv/v — five moving-window stacks
# ------------------------------------------------------------
n_rows = len(dvv_data)

if n_rows == 0:
    print("No DVV data available — skipping Fig 8")
else:
    fig, axes = plt.subplots(n_rows, 1, figsize=(14, 3 * n_rows),
                              sharex=True)
    if n_rows == 1:
        axes = [axes]

    for ax, ms in zip(axes, dvv_data):
        ds = dvv_data[ms]
        times, mean, std, wmean, wstd = extract_series(ds)

        mean_det = pd.Series(detrend_valid(mean.values), index=times)

        ax.plot(times, mean_det, c="r", lw=0.8,
                label=r"ALL: $\delta v/v$ of mean network")
        if std is not None:
            ax.fill_between(times, mean_det - std, mean_det + std,
                            color="r", alpha=0.2)

        if wmean is not None:
            wm_det = pd.Series(detrend_valid(wmean.values), index=times)
            ax.plot(times, wm_det, c="g", lw=0.8,
                    label=r"Weighted mean of $\delta v/v$ of individual pairs")
            if wstd is not None:
                ax.fill_between(times, wm_det - wstd, wm_det + wstd,
                                color="g", alpha=0.2)

        shade_eruptions(ax)
        ax.set_ylabel(r"$\delta v/v$ in %")
        ax.set_ylim(YLIM)
        ax.invert_yaxis()
        ax.set_xlim(XLIM)
        ax.grid(True, lw=0.3)
        ax.set_title(f"{ms[0]} Moving-Window", fontsize=10)

        if ax is axes[0]:
            ax.legend(handles=[
                plt.Line2D([], [], c="r", lw=1,
                           label=r"ALL: $\delta v/v$ of mean network"),
                plt.Line2D([], [], c="g", lw=1,
                           label=r"Weighted mean of $\delta v/v$ of individual pairs"),
                Patch(fc="red", alpha=0.4, label="Eruptions"),
            ], loc="upper right", fontsize=8)

    fmt_xaxis(axes[-1])
    fig.suptitle(
        "Lecocq et al. (2014) — Fig. 8: Detrended dv/v, five moving-window stacks\n"
        "ZZ, filter 0.2–0.85 Hz, lag 5–50 s",
        fontsize=11,
    )
    plt.tight_layout()
    plt.savefig("fig8_dvv_multimovstack.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Saved fig8_dvv_multimovstack.png")
