# Project 1 - Glasgow Recycling and Net Zero Tracker

Power BI style performance report on Glasgow's household recycling and the carbon
impact of how the city manages its waste, benchmarked against all 32 Scottish councils.

## Business question

Where does Glasgow sit against the rest of Scotland on household recycling, is the
gap closing, and how does the way we handle waste connect to the council's net zero
2030 ambition? A Business Insight Analyst in Neighbourhoods, Regeneration and
Sustainability would be asked exactly this kind of question.

## Data source

Realistic dataset calibrated to published SEPA Household Waste statistics:
- Scotland recycling rate 44.3% in 2024
- Glasgow about 27%, third lowest of the 32 councils
- £12.8m a year spent exporting waste for treatment

Per-authority yearly values are modelled to a plausible trend, not exact SEPA
figures, and every view says so. In a production build the three CSVs would be
swapped for the live SEPA feed using the same star schema. This is a personal
portfolio project built on public data, not commissioned council work.

## What I built

- A star schema: one fact table (`fact_waste`, 448 rows = 32 councils x 14 years)
  and two dimensions (`dim_local_authority`, `dim_calendar`).
- DAX measures for recycling rate, gap to the national average, council ranking,
  year on year and since-2011 change, carbon per resident, and the waste mix. See
  `DAX_MEASURES.md`.
- A three page report: executive KPIs, a 32 council benchmark, and a net zero view.
  The matplotlib image in this folder is a faithful mock of those pages so the work
  can be shown without opening Power BI.

## Headline insight

Glasgow recycles about 27% of household waste against a Scottish average near 44%,
an 18 point gap that ranks the city third lowest of 32. The rate has been broadly
flat for a decade. Carbon per resident from waste has fallen about 28% since 2011,
mostly by moving material away from landfill into other diversion, which shows the
net zero lever is real but recycling capacity, not just diversion, is the next step.
This lines up with the new Easter Queenslie recycling facility due in 2027.

## How to rebuild

```bash
python3 build_dataset.py      # writes the three CSVs into data/
python3 build_dashboard.py    # writes recycling_netzero_dashboard.png
```

To rebuild in Power BI Desktop: load the three CSVs from `data/`, set the
relationships in the table above, paste the measures from `DAX_MEASURES.md`, and lay
out the three pages described in the comments at the top of `build_dashboard.py`.

## Files

| File | What it is |
|------|------------|
| `build_dataset.py` | Builds the calibrated star schema |
| `build_dashboard.py` | Renders the report image |
| `DAX_MEASURES.md` | Every measure, copy ready for Power BI |
| `data/fact_waste.csv` | Fact table |
| `data/dim_local_authority.csv` | Council dimension |
| `data/dim_calendar.csv` | Calendar dimension |
| `recycling_netzero_dashboard.png` | The report mock |
