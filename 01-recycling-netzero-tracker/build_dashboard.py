"""
Project 1 dashboard renderer.
Produces a 3-panel dashboard image mirroring the Power BI report pages:
  Page 1: Executive summary (KPIs + Glasgow vs Scotland trend)
  Page 2: Benchmarking (all 32 councils, latest year, Glasgow highlighted)
  Page 3: Net zero (carbon impact trend + waste management mix)
The same metrics are defined as DAX measures in DAX_MEASURES.md.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import gridspec

fact = pd.read_csv("data/fact_waste.csv")
dim_la = pd.read_csv("data/dim_local_authority.csv")
fact = fact.merge(dim_la, on="local_authority", how="left")
fact["rate"] = fact.tonnes_recycled / fact.tonnes_generated * 100

LATEST = fact.year.max()
NAVY = "#1F3A5F"; TEAL = "#01696F"; AMBER = "#E8A33D"; RED = "#B23A48"; GREY = "#9AA5B1"
GLASGOW = "#C8102E"

# ---- measures ----
def nat_rate(y):
    d = fact[fact.year == y]
    return d.tonnes_recycled.sum() / d.tonnes_generated.sum() * 100

glas = fact[fact.local_authority == "Glasgow City"].sort_values("year")
g_latest = glas[glas.year == LATEST].iloc[0]
g_prev = glas[glas.year == LATEST - 1].iloc[0]
g_rate = g_latest.rate
g_yoy = g_latest.rate - g_prev.rate
g_2011_rate = glas[glas.year == 2011].iloc[0].rate
g_change_since_2011 = g_rate - g_2011_rate
nat_latest = nat_rate(LATEST)
gap = g_rate - nat_latest
ranks = (fact[fact.year == LATEST].sort_values("rate", ascending=False).reset_index(drop=True))
g_rank = int(ranks.index[ranks.local_authority == "Glasgow City"][0] + 1)
g_carbon_pc = g_latest.carbon_impact_tco2e / g_latest.population * 1000  # kg per person
g_carbon_2011 = glas[glas.year == 2011].iloc[0]
carbon_change = (g_latest.carbon_impact_tco2e - g_carbon_2011.carbon_impact_tco2e) / g_carbon_2011.carbon_impact_tco2e * 100

# ---- figure ----
fig = plt.figure(figsize=(15, 13.5), facecolor="white")
gs = gridspec.GridSpec(3, 4, height_ratios=[0.7, 1.35, 1.15], hspace=0.42, wspace=0.62)

fig.suptitle("Glasgow Recycling and Net Zero Tracker",
             fontsize=22, fontweight="bold", color=NAVY, x=0.5, y=1.00)
fig.text(0.5, 0.965, f"Household waste performance, 32 Scottish councils, 2011 to {LATEST}  |  Strategic performance view",
         ha="center", fontsize=11, color="#555")

# ---------- Row 1: KPI cards ----------
kpis = [
    (f"{g_rate:.1f}%", "Glasgow recycling rate", f"{g_change_since_2011:+.1f} pts since 2011", AMBER),
    (f"{gap:+.1f} pts", "Gap to Scotland average", f"Scotland {nat_latest:.1f}%", RED),
    (f"{g_rank} / 32", "Glasgow rank (councils)", "Third lowest band", RED),
    (f"{g_carbon_pc:.0f} kg", "Carbon impact per resident", f"{carbon_change:+.0f}% since 2011", TEAL),
]
for i, (big, label, sub, col) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i]); ax.axis("off")
    ax.add_patch(plt.Rectangle((0.02, 0.08), 0.96, 0.86, transform=ax.transAxes,
                 facecolor="#F4F6F8", edgecolor=col, linewidth=2.5, zorder=0))
    ax.text(0.5, 0.66, big, ha="center", va="center", fontsize=24, fontweight="bold", color=col)
    ax.text(0.5, 0.36, label, ha="center", va="center", fontsize=9.8, color=NAVY, fontweight="bold")
    ax.text(0.5, 0.18, sub, ha="center", va="center", fontsize=9, color="#555")

# ---------- Row 2 left: trend Glasgow vs Scotland ----------
ax1 = fig.add_subplot(gs[1, :2])
years = sorted(fact.year.unique())
nat_series = [nat_rate(y) for y in years]
g_series = glas.set_index("year").reindex(years)["rate"].values
ax1.plot(years, nat_series, "-o", color=NAVY, lw=2.4, ms=5, label="Scotland average")
ax1.plot(years, g_series, "-o", color=GLASGOW, lw=2.4, ms=5, label="Glasgow City")
ax1.fill_between(years, g_series, nat_series, color=GLASGOW, alpha=0.12)
ax1.set_title("Recycling rate over time: Glasgow vs Scotland", fontsize=12.5, fontweight="bold", color=NAVY, loc="left")
ax1.set_ylabel("Household recycling rate (%)", fontsize=10)
ax1.set_ylim(15, 55); ax1.grid(axis="y", alpha=0.3); ax1.legend(frameon=False, fontsize=10)
ax1.annotate(f"Gap {gap:+.1f} pts", xy=(LATEST, (g_rate+nat_latest)/2),
             xytext=(LATEST-4.0, 32), fontsize=10.5, color="#8C1019", fontweight="bold")
for s in ["top", "right"]: ax1.spines[s].set_visible(False)

# ---------- Row 2 right: benchmarking bar ----------
ax2 = fig.add_subplot(gs[1, 2:])
bench = ranks.copy()
colors = [GLASGOW if la == "Glasgow City" else GREY for la in bench.local_authority]
ax2.barh(range(len(bench)), bench["rate"], color=colors)
ax2.axvline(nat_latest, color=NAVY, ls="--", lw=1.4)
ax2.text(nat_latest+0.4, len(bench)-1.5, f"Scotland avg {nat_latest:.1f}%", fontsize=8.5, color=NAVY)
ax2.set_yticks(range(len(bench)))
ax2.set_yticklabels(bench.local_authority, fontsize=8.2)
ax2.invert_yaxis()
ax2.set_title(f"All 32 councils ranked, {LATEST} (Glasgow highlighted)", fontsize=12.5, fontweight="bold", color=NAVY, loc="left")
ax2.set_xlabel("Recycling rate (%)", fontsize=10)
g_idx = list(bench.local_authority).index("Glasgow City")
ax2.text(bench.iloc[g_idx]["rate"]+0.6, g_idx, f"Glasgow {g_rate:.1f}%", va="center", fontsize=8, color=GLASGOW, fontweight="bold")
for s in ["top", "right"]: ax2.spines[s].set_visible(False)

# ---------- Row 3 left: carbon impact trend (Glasgow) ----------
ax3 = fig.add_subplot(gs[2, :2])
g_carbon_pc_series = glas["carbon_impact_tco2e"].values / glas["population"].values * 1000
ax3.plot(glas.year, g_carbon_pc_series, "-o", color=TEAL, lw=2.4, ms=5)
ax3.fill_between(glas.year, g_carbon_pc_series, color=TEAL, alpha=0.12)
ax3.set_title("Glasgow carbon impact per resident (kg CO2e)", fontsize=12.5, fontweight="bold", color=NAVY, loc="left")
ax3.set_ylabel("kg CO2e per resident", fontsize=10)
ax3.grid(axis="y", alpha=0.3)
ax3.annotate(f"{carbon_change:+.0f}% since 2011", xy=(glas.year.max(), g_carbon_pc_series[-1]),
             xytext=(2016, g_carbon_pc_series[-1]+25), fontsize=10.5, color="#024C51", fontweight="bold")
for s in ["top", "right"]: ax3.spines[s].set_visible(False)

# ---------- Row 3 right: waste management mix (Glasgow, stacked) ----------
ax4 = fig.add_subplot(gs[2, 2:])
gg = glas.set_index("year")
rec = gg["tonnes_recycled"]; lf = gg["tonnes_landfilled"]; od = gg["tonnes_other_diversion"]
ax4.bar(gg.index, rec, color=TEAL, label="Recycled")
ax4.bar(gg.index, od, bottom=rec, color=AMBER, label="Other diversion / incineration")
ax4.bar(gg.index, lf, bottom=rec+od, color=RED, label="Landfilled")
ax4.set_title("Glasgow waste management mix (tonnes)", fontsize=12.5, fontweight="bold", color=NAVY, loc="left")
ax4.set_ylabel("Tonnes", fontsize=10)
ax4.legend(frameon=False, fontsize=8, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.30))
ax4.grid(axis="y", alpha=0.3)
for s in ["top", "right"]: ax4.spines[s].set_visible(False)

fig.text(0.5, 0.012,
         "Personal portfolio project. Realistic dataset calibrated to published SEPA Household Waste statistics "
         "(Scotland 44.3% in 2024; Glasgow ~27%, 3rd lowest of 32). Per-authority yearly values are modelled, not exact SEPA figures.",
         ha="center", fontsize=9, color="#555", style="italic")

plt.savefig("recycling_netzero_dashboard.png", dpi=130, bbox_inches="tight", facecolor="white")
print("Saved recycling_netzero_dashboard.png")
print(f"KPIs -> Glasgow {g_rate:.1f}%, gap {gap:+.1f} pts, rank {g_rank}/32, carbon/res {g_carbon_pc:.0f} kg ({carbon_change:+.0f}% since 2011)")
