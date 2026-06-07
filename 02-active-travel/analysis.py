"""
Glasgow Active Travel - time series analysis and portfolio chart.

Reads the SQLite counter table, runs a seasonal decomposition on the South City Way
monthly series (trend / seasonal / residual), and renders a 4 panel analysis image:
  1. Monthly cyclists by route, with trend
  2. Growth vs 2021 baseline (calibrated: South West City Way +116%)
  3. Weekday profile (commuter peak signature)
  4. Seasonal decomposition trend of South City Way
"""
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

NAVY = "#1F3A5F"; TEAL = "#01696F"; AMBER = "#E8A33D"; RED = "#B23A48"; GREEN = "#437A22"
ROUTE_COLORS = {"South City Way": TEAL, "South West City Way": RED,
                "Connect2 / Clyde path": AMBER, "Sauchiehall Avenue": NAVY}

con = sqlite3.connect("data/active_travel.db")
monthly = pd.read_sql("""
    SELECT route, route_type, year, month, SUM(cyclists) AS monthly_cyclists
    FROM counter_daily GROUP BY route, route_type, year, month
    ORDER BY route, year, month""", con)
weekday = pd.read_sql("""
    SELECT route, weekday, AVG(cyclists) AS avg_cyclists
    FROM counter_daily GROUP BY route, weekday""", con)
annual = pd.read_sql("""
    SELECT route, year, SUM(cyclists) AS total FROM counter_daily
    GROUP BY route, year ORDER BY route, year""", con)
con.close()

monthly["period"] = pd.to_datetime(dict(year=monthly.year, month=monthly.month, day=1))

fig, axes = plt.subplots(2, 2, figsize=(15, 10.5), facecolor="white")
fig.suptitle("Glasgow Active Travel: cycle counter analysis, 2021 to 2025",
             fontsize=18, fontweight="bold", color=NAVY, y=0.985)

# --- Panel 1: monthly cyclists by route ---
ax = axes[0, 0]
for route, g in monthly.groupby("route"):
    ax.plot(g.period, g.monthly_cyclists, label=route, color=ROUTE_COLORS.get(route, "#888"), lw=2)
ax.set_title("Monthly cyclists by route", fontsize=12.5, fontweight="bold", color=NAVY, loc="left")
ax.set_ylabel("Cyclists per month")
ax.legend(frameon=False, fontsize=8.5)
ax.grid(axis="y", alpha=0.3)
for s in ["top", "right"]: ax.spines[s].set_visible(False)

# --- Panel 2: growth vs 2021 ---
ax = axes[0, 1]
base = annual[annual.year == 2021].set_index("route")["total"]
g2024 = annual[annual.year == 2024].set_index("route")["total"]
growth = ((g2024 - base) / base * 100).sort_values()
bars = ax.barh(growth.index, growth.values,
               color=[ROUTE_COLORS.get(r, "#888") for r in growth.index])
for i, v in enumerate(growth.values):
    ax.text(v + 2, i, f"+{v:.0f}%", va="center", fontsize=10, fontweight="bold", color=NAVY)
ax.set_title("Cycle trip growth, 2021 to 2024", fontsize=12.5, fontweight="bold", color=NAVY, loc="left")
ax.set_xlabel("Change vs 2021 baseline (%)")
ax.set_xlim(0, growth.max() * 1.25)
ax.grid(axis="x", alpha=0.3)
for s in ["top", "right"]: ax.spines[s].set_visible(False)

# --- Panel 3: weekday profile ---
ax = axes[1, 0]
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
for route in ["South City Way", "Connect2 / Clyde path"]:
    sub = weekday[weekday.route == route].set_index("weekday").reindex(order)["avg_cyclists"]
    ax.plot(order, sub.values, "-o", label=route, color=ROUTE_COLORS.get(route), lw=2, ms=5)
ax.set_title("Weekday profile: commuter vs leisure signature", fontsize=12.5, fontweight="bold", color=NAVY, loc="left")
ax.set_ylabel("Average cyclists per day")
ax.tick_params(axis="x", rotation=35)
ax.legend(frameon=False, fontsize=9)
ax.grid(axis="y", alpha=0.3)
for s in ["top", "right"]: ax.spines[s].set_visible(False)

# --- Panel 4: seasonal decomposition trend (South City Way) ---
ax = axes[1, 1]
scw = (monthly[monthly.route == "South City Way"]
       .set_index("period")["monthly_cyclists"].asfreq("MS"))
decomp = seasonal_decompose(scw, model="additive", period=12)
ax.plot(scw.index, scw.values, color="#BBBBBB", lw=1, label="Observed")
ax.plot(decomp.trend.index, decomp.trend.values, color=TEAL, lw=2.6, label="Trend (decomposed)")
ax.set_title("South City Way: underlying trend (seasonal decomposition)",
             fontsize=12.5, fontweight="bold", color=NAVY, loc="left")
ax.set_ylabel("Cyclists per month")
ax.legend(frameon=False, fontsize=9)
ax.grid(axis="y", alpha=0.3)
for s in ["top", "right"]: ax.spines[s].set_visible(False)

fig.text(0.5, 0.01,
         "Personal portfolio project. Daily counts modelled on a plausible growth and seasonal curve, "
         "calibrated to public figures (South West City Way about +116% since 2021; South City Way commuter peaks). "
         "Not raw council counter feeds.",
         ha="center", fontsize=8.5, color="#555", style="italic")

plt.tight_layout(rect=[0, 0.03, 1, 0.97])
plt.savefig("active_travel_analysis.png", dpi=130, facecolor="white")
print("Saved active_travel_analysis.png")
print("Growth 2021->2024:")
for r, v in growth.items():
    print(f"  {r}: +{v:.0f}%")
