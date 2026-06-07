"""
Project 3 data builder - Glasgow Air Quality Monthly Reporting Pack.

Generates a realistic monthly monitoring dataset for Glasgow's diffusion tube and
continuous analyser network, calibrated to published facts:
  - UK / Scotland annual mean objective for NO2 is 40 ug/m3.
  - UK 24-hour PM10 objective is 50 ug/m3 (not to be exceeded more than 7 times/yr
    under the Scottish objective); annual mean 18 ug/m3 (Scotland).
  - Glasgow's Low Emission Zone (phase 2 enforcement from 1 June 2024) is associated
    with roadside NO2 falling about 34%.
  - Glasgow reached full statutory compliance with air quality objectives in 2024,
    the first time in roughly 30 years.
This is a personal portfolio dataset calibrated to those public facts. Site level
monthly values are modelled to a plausible seasonal pattern, not raw council readings.
"""
import csv
import math
import random
from datetime import date

random.seed(42)

# Monitoring sites mapped to the real AQMAs in glasgow_aqma_reference.csv
SITES = [
    # site, aqma, pollutant, type, 2022 baseline annual mean (ug/m3)
    ("Hope Street (kerbside)",      "City Centre",              "NO2",  "Continuous", 52.0),
    ("North Street",               "City Centre",              "NO2",  "Diffusion",  46.0),
    ("Royston Road",               "City Centre",              "NO2",  "Diffusion",  41.0),
    ("Dumbarton Road",             "Byres Road/Dumbarton Road","NO2",  "Diffusion",  43.0),
    ("Byres Road",                 "Byres Road/Dumbarton Road","NO2",  "Diffusion",  39.0),
    ("Parkhead Cross",             "Parkhead Cross",           "NO2",  "Diffusion",  42.0),
    ("Hope Street (kerbside)",      "City Centre",              "PM10", "Continuous", 19.0),
    ("Townhead",                   "City Centre",              "PM10", "Continuous", 16.0),
]

# NO2 annual mean trajectory factor by year vs 2022 baseline.
# LEZ phase 2 enforced June 2024 -> sharp roadside drop; full compliance reached 2024.
YEAR_FACTOR = {2022: 1.00, 2023: 0.93, 2024: 0.66, 2025: 0.62}  # ~34% drop into 2024

# PM10 declines more gently
PM10_FACTOR = {2022: 1.00, 2023: 0.96, 2024: 0.90, 2025: 0.88}

# Monthly seasonal multipliers - higher in winter (heating, inversions, less dispersion)
SEASON = {
    1: 1.18, 2: 1.14, 3: 1.05, 4: 0.97, 5: 0.92, 6: 0.88,
    7: 0.86, 8: 0.88, 9: 0.95, 10: 1.04, 11: 1.12, 12: 1.20,
}

rows = []
for year in (2022, 2023, 2024, 2025):
    for month in range(1, 13):
        # only go to current period for 2025 (stop at September)
        if year == 2025 and month > 9:
            continue
        for site, aqma, pol, stype, base in SITES:
            yf = YEAR_FACTOR[year] if pol == "NO2" else PM10_FACTOR[year]
            seasonal = SEASON[month]
            noise = random.uniform(0.95, 1.05)
            mean = base * yf * seasonal * noise
            # data capture rate (continuous analysers near 100%, diffusion tubes monthly)
            capture = round(random.uniform(95, 100), 1) if stype == "Continuous" else 100.0
            rows.append({
                "Year": year,
                "Month": month,
                "Period": f"{year}-{month:02d}",
                "Site": site,
                "AQMA": aqma,
                "Pollutant": pol,
                "Monitor type": stype,
                "Monthly mean (ug/m3)": round(mean, 1),
                "Data capture (%)": capture,
            })

with open("data/glasgow_aq_monthly_raw.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} monthly rows across {len(SITES)} site-pollutant series, 2022 to 2025-09")
# quick sanity: NO2 city centre annual means by year
for y in (2022, 2024):
    vals = [r["Monthly mean (ug/m3)"] for r in rows
            if r["Year"] == y and r["Site"] == "Hope Street (kerbside)" and r["Pollutant"] == "NO2"]
    print(f"Hope Street NO2 mean {y}: {sum(vals)/len(vals):.1f} ug/m3")
