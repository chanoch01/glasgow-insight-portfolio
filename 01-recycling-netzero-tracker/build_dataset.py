"""
Project 1: Glasgow Recycling and Net Zero Tracker
Build a star-schema dataset for the Power BI / dashboard build.

DATA PROVENANCE (read carefully, state this honestly in interview):
- This is a REALISTIC RECONSTRUCTED dataset for a personal portfolio project.
- It is calibrated to real published SEPA Household Waste statistics:
    * Scotland national recycling rate 2024 = 44.3% (SEPA, Oct 2025)
    * Scotland rate rose slowly from ~39.6% (2011) to 44.3% (2024)
    * Glasgow City sits ~27% (third lowest of 32 councils; STV/scrutiny cttee 2025)
    * National carbon impact per person 2024 = 0.96 tCO2e, down 21.5% vs 2011
- Per-authority yearly values between the anchor points are modelled, not the
  exact SEPA figures. The SEPA council-level time series lives on
  statistics.gov.scot, which was not reachable from the build environment.
- For a production build, replace fact_waste.csv with the real SEPA
  "Household waste generated and managed by local authority" download.

Output: a star schema (1 fact table + 2 dimension tables) as CSV.
"""
import numpy as np
import pandas as pd

np.random.seed(42)

YEARS = list(range(2011, 2025))  # 2011..2024

# 32 Scottish local authorities with a classification and a 2024 anchor recycling rate.
# Anchors are set from the real national picture: national avg 44.3% in 2024,
# top performers ~55-57%, Glasgow ~27% (3rd lowest). Urban/Rural/Island flag is
# used for the benchmarking page.
authorities = [
    # name, class, 2024 recycling rate anchor (%), population (approx, for per-capita)
    ("Glasgow City",            "Urban",  27.2, 622820),
    ("City of Edinburgh",       "Urban",  39.0, 514990),
    ("Aberdeen City",           "Urban",  42.5, 224190),
    ("Dundee City",             "Urban",  35.0, 148270),
    ("North Lanarkshire",       "Urban",  41.0, 341370),
    ("South Lanarkshire",       "Mixed",  47.0, 327030),
    ("Renfrewshire",            "Urban",  43.0, 184500),
    ("Fife",                    "Mixed",  52.0, 374730),
    ("West Lothian",            "Mixed",  54.0, 187280),
    ("Falkirk",                 "Mixed",  45.0, 161370),
    ("Highland",                "Rural",  43.0, 235540),
    ("Aberdeenshire",           "Rural",  43.5, 262690),
    ("Scottish Borders",        "Rural",  44.0, 116020),
    ("Dumfries and Galloway",   "Rural",  48.0, 148790),
    ("South Ayrshire",          "Mixed",  53.0, 112450),
    ("North Ayrshire",          "Mixed",  56.0, 134220),
    ("East Ayrshire",           "Mixed",  54.0, 121840),
    ("Perth and Kinross",       "Rural",  52.0, 153810),
    ("Angus",                   "Rural",  53.3, 116200),
    ("Stirling",                "Mixed",  56.0,  93470),
    ("Clackmannanshire",        "Mixed",  57.2,  51540),
    ("Moray",                   "Rural",  56.7,  96580),
    ("East Lothian",            "Mixed",  55.3, 110330),
    ("Midlothian",              "Mixed",  52.0,  95150),
    ("East Dunbartonshire",     "Mixed",  56.0, 108840),
    ("West Dunbartonshire",     "Urban",  46.0,  87790),
    ("East Renfrewshire",       "Mixed",  62.0,  96580),
    ("Inverclyde",              "Urban",  52.0,  76700),
    ("Argyll and Bute",         "Rural",  45.0,  86220),
    ("Na h-Eileanan Siar",      "Island", 24.0,  26500),
    ("Orkney Islands",          "Island", 23.0,  22270),
    ("Shetland Islands",        "Island", 14.0,  22940),
]

dim_la = pd.DataFrame(authorities, columns=["local_authority", "classification", "rate_2024", "population"])

# National rate path used to shape each authority's trajectory over time.
# Real anchors: 2011 ~39.6%, 2018 dip, 2024 = 44.3%.
nat_path = {
    2011: 39.6, 2012: 41.0, 2013: 42.2, 2014: 42.8, 2015: 44.2, 2016: 45.2,
    2017: 45.6, 2018: 44.7, 2019: 44.9, 2020: 41.6, 2021: 42.7, 2022: 43.3,
    2023: 43.5, 2024: 44.3,
}

rows = []
for _, la in dim_la.iterrows():
    # each authority tracks the national shape, offset to hit its 2024 anchor,
    # with a little year-to-year noise. Glasgow stays stubbornly flat (real story).
    offset = la["rate_2024"] - nat_path[2024]
    flat = la["local_authority"] == "Glasgow City"
    for y in YEARS:
        if flat:
            # Glasgow: stagnant around 24-27% across the whole period (the real narrative)
            base = 24.0 + (y - 2011) * (3.2 / 13.0)  # 24.0 -> ~27.2 very slowly
            rate = base + np.random.normal(0, 0.4)
        else:
            rate = nat_path[y] + offset + np.random.normal(0, 0.8)
        rate = float(np.clip(rate, 8, 70))

        # tonnes generated scales with population; mild downward trend in waste generated
        per_head = 0.46 - (y - 2011) * 0.004 + np.random.normal(0, 0.005)  # tonnes/person
        generated = la["population"] * per_head
        recycled = generated * rate / 100.0
        # of the remainder: landfill share falls sharply over time, incineration rises
        remainder = generated - recycled
        landfill_share = max(0.10, 0.50 - (y - 2011) * 0.030)  # ~50% (2011) -> ~11% (2024)
        landfilled = remainder * landfill_share
        other_diversion = remainder - landfilled  # mainly incineration / other

        # carbon impact: landfill is more carbon-intensive than recycling/diversion.
        # tCO2e factors (illustrative, directionally correct). Calibrated so the
        # per-resident fall over 2011-2024 lands near the real national ~21% reduction.
        carbon = (landfilled * 0.32) + (other_diversion * 0.20) + (recycled * 0.05)

        rows.append({
            "year": y,
            "local_authority": la["local_authority"],
            "tonnes_generated": round(generated, 1),
            "tonnes_recycled": round(recycled, 1),
            "tonnes_landfilled": round(landfilled, 1),
            "tonnes_other_diversion": round(other_diversion, 1),
            "carbon_impact_tco2e": round(carbon, 1),
        })

fact = pd.DataFrame(rows)

# Dimension: calendar (year)
dim_cal = pd.DataFrame({"year": YEARS})
dim_cal["is_latest"] = dim_cal["year"] == max(YEARS)

# Tidy the LA dimension (drop the helper anchor column from the published file)
dim_la_out = dim_la[["local_authority", "classification", "population"]].copy()

fact.to_csv("data/fact_waste.csv", index=False)
dim_la_out.to_csv("data/dim_local_authority.csv", index=False)
dim_cal.to_csv("data/dim_calendar.csv", index=False)

# Sanity checks against the real anchors
g = fact[(fact.local_authority == "Glasgow City") & (fact.year == 2024)].iloc[0]
nat_2024 = (fact[fact.year == 2024].tonnes_recycled.sum() /
            fact[fact.year == 2024].tonnes_generated.sum() * 100)
glasgow_rate_2024 = g.tonnes_recycled / g.tonnes_generated * 100
ranks = (fact[fact.year == 2024]
         .assign(rate=lambda d: d.tonnes_recycled / d.tonnes_generated * 100)
         .sort_values("rate", ascending=False)
         .reset_index(drop=True))
glasgow_rank = ranks.index[ranks.local_authority == "Glasgow City"][0] + 1

print(f"Rows in fact table: {len(fact)} (should be 32 x 14 = {32*14})")
print(f"Scotland 2024 modelled rate: {nat_2024:.1f}% (real anchor 44.3%)")
print(f"Glasgow 2024 modelled rate:  {glasgow_rate_2024:.1f}% (real anchor ~27.2%)")
print(f"Glasgow rank out of 32:      {glasgow_rank} (real: 3rd lowest, i.e. ~30th)")
print("Files written: data/fact_waste.csv, data/dim_local_authority.csv, data/dim_calendar.csv")
