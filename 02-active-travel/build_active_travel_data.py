"""
Project 2 data builder - Glasgow Active Travel counter analysis.

Generates a daily cycle counter dataset for Glasgow's flagship segregated routes,
loads it into SQLite, and writes the aggregated tables the dashboard reads.

Calibrated to published facts:
  - South City Way: cycling reached about 16.1% mode share at a key point (Sept 2025).
  - South West City Way: cycle trips up about 116% since 2021.
  - Commuting routes show clear weekday morning and evening peaks; leisure routes peak
    at weekends and in summer.
These are modelled daily counts on a plausible growth and seasonal curve, calibrated to
those public headline figures. Personal portfolio project on public data, not raw
council counter feeds.
"""
import sqlite3
import csv
import math
import random
from datetime import date, timedelta

random.seed(7)

# route, type, 2021 baseline mean daily cyclists, annual growth, weekend factor
ROUTES = [
    ("South City Way",        "Commuter", 420, 0.10, 0.55),
    ("South West City Way",   "Commuter", 180, 0.295, 0.60),   # ~+116% over 4 yrs
    ("Connect2 / Clyde path", "Leisure",  300, 0.06, 1.45),
    ("Sauchiehall Avenue",    "Mixed",    250, 0.08, 0.80),
]

START = date(2021, 1, 1)
END = date(2025, 9, 30)

def seasonal(d):
    # peak in summer, trough in deep winter
    doy = d.timetuple().tm_yday
    return 1.0 + 0.35 * math.sin((doy - 80) / 365 * 2 * math.pi)

def weather_noise():
    return random.uniform(0.7, 1.15)

rows = []
d = START
while d <= END:
    years_in = (d - START).days / 365.25
    is_weekend = d.weekday() >= 5
    for route, rtype, base, growth, wknd in ROUTES:
        trend = base * ((1 + growth) ** years_in)
        s = seasonal(d)
        wf = wknd if is_weekend else 1.0
        count = trend * s * wf * weather_noise()
        rows.append({
            "count_date": d.isoformat(),
            "year": d.year,
            "month": d.month,
            "weekday": d.strftime("%A"),
            "is_weekend": int(is_weekend),
            "route": route,
            "route_type": rtype,
            "cyclists": int(round(count)),
        })
    d += timedelta(days=1)

# write raw csv
with open("data/active_travel_daily.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

# load into SQLite
con = sqlite3.connect("data/active_travel.db")
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS counter_daily")
cur.execute("""
CREATE TABLE counter_daily (
    count_date TEXT, year INTEGER, month INTEGER, weekday TEXT,
    is_weekend INTEGER, route TEXT, route_type TEXT, cyclists INTEGER
)""")
cur.executemany(
    "INSERT INTO counter_daily VALUES (:count_date,:year,:month,:weekday,:is_weekend,:route,:route_type,:cyclists)",
    rows)
con.commit()

# ---- aggregations via SQL (these are the queries documented in QUERIES.sql) ----
# monthly totals per route
monthly = cur.execute("""
    SELECT route, route_type, year, month,
           SUM(cyclists) AS monthly_cyclists,
           ROUND(AVG(cyclists),0) AS avg_daily
    FROM counter_daily
    GROUP BY route, route_type, year, month
    ORDER BY route, year, month
""").fetchall()
with open("data/agg_monthly.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["route","route_type","year","month","monthly_cyclists","avg_daily"])
    w.writerows(monthly)

# annual totals + growth vs 2021
annual = cur.execute("""
    SELECT route, year, SUM(cyclists) AS annual_cyclists
    FROM counter_daily
    GROUP BY route, year
    ORDER BY route, year
""").fetchall()
with open("data/agg_annual.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["route","year","annual_cyclists"])
    w.writerows(annual)

# weekday profile (avg per weekday)
weekday = cur.execute("""
    SELECT route, route_type, weekday, ROUND(AVG(cyclists),0) AS avg_cyclists
    FROM counter_daily
    GROUP BY route, route_type, weekday
""").fetchall()
with open("data/agg_weekday.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["route","route_type","weekday","avg_cyclists"])
    w.writerows(weekday)

con.close()

# sanity checks vs real anchors
import pandas as pd
ann = pd.read_csv("data/agg_annual.csv")
for route in ("South West City Way", "South City Way"):
    sub = ann[ann.route == route].set_index("year")["annual_cyclists"]
    g = (sub.get(2024, sub.iloc[-1]) - sub[2021]) / sub[2021] * 100
    print(f"{route}: {g:+.0f}% growth 2021 to 2024")
print(f"Total daily rows: {len(rows)}, monthly agg rows: {len(monthly)}")
