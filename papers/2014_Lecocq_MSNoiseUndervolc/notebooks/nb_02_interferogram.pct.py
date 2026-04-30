# %% [markdown]
"""
# Figure 3 — Interferogram and Correlation Coefficients

Reproduces Figure 3 of Lecocq, Caudron & Brenguier (2014), SRL 85(3).

**Top panel:** daily stacked CCFs for pair YA.UV02–YA.UV05 displayed
as a time–lag image.

**Lower panels:** absolute correlation coefficient of different
moving-window stacks against the reference stack, for negative and
positive lag windows independently.

**Bundle level required:** `stack`
"""

# %%
# ------------------------------------------------------------
# 0 — Data source
# Set PROJECT_DIR to skip the MRP download and use a local path.
# ------------------------------------------------------------
PAPER_ID    = "2014_Lecocq_MSNoiseUndervolc"
LEVEL       = "stack"
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
# 1 — Locate stack and refstack results for filter_1
# ------------------------------------------------------------
FILTER = "filter_1"

stack_results    = [r for r in project.list("stack")
                    if FILTER in r.lineage_names]
refstack_results = [r for r in project.list("refstack")
                    if FILTER in r.lineage_names]

assert stack_results,    f"No stack results for {FILTER}"
assert refstack_results, f"No refstack results for {FILTER}"

result_stack    = stack_results[0]
result_refstack = refstack_results[0]
print(result_stack)

# %%
# ------------------------------------------------------------
# 2 — Parameters from the project config
# ------------------------------------------------------------
import numpy as np
import pandas as pd

params     = result_stack.params
mov_stacks = params.stack.mov_stack   # list of ("1D","1D") tuples
print("Moving-window stacks:", mov_stacks)

PAIR      = "YA.UV02:YA.UV05"   # NET.STA:NET.STA format
COMPONENT = "ZZ"
MINLAG    = 10.0                 # s — lag window for corr. coef. (original code)
MAXLAG    = 45.0                 # s

# %%
# ------------------------------------------------------------
# 3 — Load 1-day stacked CCFs (interferogram matrix)
# ------------------------------------------------------------
ccf_1d = result_stack.get_ccf(pair=PAIR, components=COMPONENT,
                               mov_stack=mov_stacks[0])
print(ccf_1d)

times = pd.to_datetime(ccf_1d.coords["times"].values)
taxis = ccf_1d.coords["taxis"].values    # lag time in seconds

# %%
# ------------------------------------------------------------
# 4 — Load reference stack
# ------------------------------------------------------------
ref     = result_refstack.get_ref(pair=PAIR, components=COMPONENT)
ref_arr = ref.values.squeeze()           # 1-D (taxis,)

# %%
# ------------------------------------------------------------
# 5 — Compute correlation coefficients vs reference per mov_stack
# ------------------------------------------------------------
from scipy.stats import pearsonr

sr     = params.cc.cc_sampling_rate
center = len(taxis) // 2
i_lML  = center - int(MAXLAG * sr)
i_lmL  = center - int(MINLAG * sr)
i_rML  = center + int(MINLAG * sr)
i_rRL  = center + int(MAXLAG * sr)

ref_neg = ref_arr[i_lML:i_lmL]
ref_pos = ref_arr[i_rML:i_rRL]


def cc_vs_ref(da):
    arr    = da.values
    cc_neg = np.full(len(arr), np.nan)
    cc_pos = np.full(len(arr), np.nan)
    for i, row in enumerate(arr):
        if not np.all(np.isnan(row)):
            cc_neg[i] = abs(pearsonr(ref_neg, row[i_lML:i_lmL])[0])
            cc_pos[i] = abs(pearsonr(ref_pos, row[i_rML:i_rRL])[0])
    return cc_neg, cc_pos


cc_data = {}
for ms in mov_stacks:
    da = result_stack.get_ccf(pair=PAIR, components=COMPONENT, mov_stack=ms)
    cc_data[ms] = cc_vs_ref(da)

# %%
# ------------------------------------------------------------
# 6 — Plot (Figure 3)
# ------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates

ERUPTIONS = [
    ("2009-11-05", "2009-11-06"),
    ("2009-12-10", "2009-12-14"),
    ("2010-01-02", "2010-01-12"),
    ("2010-10-14", "2010-10-31"),
    ("2010-12-09", "2010-12-10"),
]


def shade_eruptions(ax):
    for t0, t1 in ERUPTIONS:
        ax.axvspan(pd.Timestamp(t0), pd.Timestamp(t1),
                   color="red", alpha=0.4, zorder=-1)


n_ms    = len(mov_stacks)
heights = [5] + [1] * n_ms

fig = plt.figure(figsize=(16, 4 + 2 * n_ms))
gs  = gridspec.GridSpec(1 + n_ms, 1, height_ratios=heights, hspace=0.05)

# -- Interferogram (1-day stack) --
ax0 = fig.add_subplot(gs[0])
extent = [mdates.date2num(times[0]), mdates.date2num(times[-1]),
          taxis[0], taxis[-1]]
im = ax0.imshow(ccf_1d.values.T, extent=extent, aspect="auto",
                origin="lower", cmap="seismic", interpolation="none")
ax0.set_ylabel("Lag Time (s)")
ax0.set_ylim(-50, 50)
ax0.axhline(0, lw=0.5, c="k")
for lag in (-MAXLAG, -MINLAG, MINLAG, MAXLAG):
    ax0.axhline(lag, ls="--", lw=1.5, c="k")
ax0.set_title("YA.UV02 : YA.UV05")
ax0.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
shade_eruptions(ax0)
plt.colorbar(im, ax=ax0, pad=0.01, fraction=0.015, label="Amplitude")

# -- Correlation coefficient panels --
for idx, ms in enumerate(mov_stacks, start=1):
    ax = fig.add_subplot(gs[idx], sharex=ax0)
    cc_neg, cc_pos = cc_data[ms]
    ax.plot(times, cc_neg, c="g", lw=0.8, label="Negative Lags")
    ax.plot(times, cc_pos, c="r", lw=0.8, label="Positive Lags")
    shade_eruptions(ax)
    ax.set_ylabel("Corr. Coef")
    ax.set_ylim(0.2, 1.05)
    ax.grid(True, lw=0.3)
    ax.set_title(f"{ms[0]} Moving-Window", fontsize=9)
    if idx == 1:
        ax.legend(loc=4, fontsize=8)
    visible = (idx == n_ms)
    plt.setp(ax.get_xticklabels(), visible=visible)
    if visible:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

fig.suptitle(
    "Lecocq et al. (2014) — Fig. 3\n"
    "Interferogram + Correlation Coefficients — YA.UV02–YA.UV05, ZZ, 0.2–0.85 Hz",
    fontsize=11,
)
plt.savefig("fig3_interferogram.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved fig3_interferogram.png")
