# Project 2 - Glasgow Active Travel Analysis

A SQL, Python and Streamlit analysis of cycle counter data on Glasgow's flagship
segregated routes, showing how active travel has grown and what the usage patterns say
about who is cycling and when.

## Business question

Is investment in segregated cycle routes paying off, and how do commuter routes differ
from leisure routes? This connects directly to the council's active travel and net zero
goals and to the kind of monitoring a Business Insight Analyst would produce for
transport and sustainability colleagues.

## Data source

Daily counts for four routes (South City Way, South West City Way, a Clyde leisure
path, and Sauchiehall Avenue), mapped to real Glasgow active travel infrastructure.
Counts are modelled on a plausible growth and seasonal curve and calibrated to published
figures:

- South West City Way: cycle trips up about 116% since 2021.
- South City Way: a strong commuter signature, weekday peaks and a high mode share at a
  key point (about 16% in 2025).

These are not raw council counter feeds. This is a personal portfolio project built on
public information, and every view says so. In a live build the SQLite table would be
replaced by the council's cycle counter API, which needs an Azure subscription key, with
the same schema and the same SQL.

## What I built

- A SQLite database (`data/active_travel.db`) with one fact table, `counter_daily`.
- A documented SQL aggregation layer (`QUERIES.sql`): monthly totals, annual growth via
  a self join on the 2021 baseline, weekday profiles, and weekday versus weekend splits.
- A Python time series analysis (`analysis.py`) that runs a seasonal decomposition with
  statsmodels to separate the underlying trend from the seasonal swing, and renders a
  four panel portfolio chart (`active_travel_analysis.png`).
- An interactive Streamlit dashboard (`streamlit_app.py`) with route and year filters,
  headline KPIs, a monthly trend, a weekday profile, and a growth table.

## Headline insight

South West City Way cycle trips are up about 116% since 2021, the steepest growth of any
route. The weekday profile cleanly separates commuter routes (South City Way, flat and
high Monday to Friday, dropping at weekends) from leisure routes (Clyde path, peaking on
Saturday and Sunday). The seasonal decomposition shows the South City Way trend rising
steadily underneath the summer and winter swing, so the growth is structural, not just a
good-weather effect.

## How to rebuild and run

```bash
python3 build_active_travel_data.py   # builds CSVs + SQLite db + aggregates
python3 analysis.py                   # writes active_travel_analysis.png
streamlit run streamlit_app.py        # launches the interactive dashboard
```

## Files

| File | What it is |
|------|------------|
| `build_active_travel_data.py` | Builds the dataset, SQLite db and aggregates |
| `QUERIES.sql` | The SQL aggregation layer, documented |
| `analysis.py` | Seasonal decomposition and portfolio chart |
| `streamlit_app.py` | Interactive dashboard |
| `active_travel_analysis.png` | The four panel analysis image |
| `data/active_travel.db` | SQLite counter database |
| `data/active_travel_daily.csv` | Daily counts |
| `data/agg_*.csv` | Pre-aggregated tables |
