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
- A three page report design: executive KPIs, a 32 council benchmark, and a net zero
  view. `recycling_netzero_dashboard.png` (matplotlib) and `recycling-netzero-mockup.svg`
  show the planned pages so the work can be seen without Power BI.
- A Power BI build in `powerbi/`, **in progress**: the data model and the first page
  (Recycling Comparison) are in place; pages 2 and 3 are still to build. It uses an
  enriched fact table (adds a Scotland total, rates, year on year and since-2011 changes,
  and projections to 2030) and an extended calendar (fiscal years, baseline, COVID and
  target-year flags), plus a custom report theme.

## Headline insight

Glasgow recycles about 27% of household waste against a Scottish average near 44%,
an 18 point gap that ranks the city third lowest of 32. The rate has been broadly
flat for a decade. Carbon per resident from waste has fallen about 28% since 2011,
mostly by moving material away from landfill into other diversion, which shows the
net zero lever is real but recycling capacity, not just diversion, is the next step.
This lines up with the new Easter Queenslie recycling facility due in 2027.

## How to rebuild

```bash
pip install -r ../requirements.txt
python3 build_dataset.py      # writes the three CSVs into data/
python3 build_dashboard.py    # writes recycling_netzero_dashboard.png
```

To work on the Power BI report, open `powerbi/recycling-netzero.pbix` in Power BI
Desktop. If refresh fails, point the sources at `powerbi/data/` (Transform data, then
Data source settings). Apply the theme from `powerbi/recycling-netzero-theme.json`
(View, then Themes, then Browse for themes), and use `DAX_MEASURES.md` for the measures.

Known gap: the extended calendar runs to 2026, while projections run to 2030, so extend
`powerbi/data/dim_calendar.csv` before building the 2030 target view.

## Files

| File | What it is |
|------|------------|
| `build_dataset.py` | Builds the calibrated star schema |
| `build_dashboard.py` | Renders the report image |
| `DAX_MEASURES.md` | Every measure, copy ready for Power BI |
| `data/fact_waste.csv` | Fact table |
| `data/dim_local_authority.csv` | Council dimension |
| `data/dim_calendar.csv` | Calendar dimension |
| `recycling_netzero_dashboard.png` | The report mock (matplotlib) |
| `recycling-netzero-mockup.svg` | Page layout mockup |
| `powerbi/recycling-netzero.pbix` | Power BI report, in progress |
| `powerbi/recycling-netzero-theme.json` | Report theme (greens for recycling, blue accent) |
| `powerbi/data/fact_waste_enriched.csv` | Fact table with derived measures and 2025 to 2030 projections |
| `powerbi/data/dim_calendar.csv` | Extended calendar for the Power BI model |
