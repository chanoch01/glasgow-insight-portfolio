# Project 3 - Glasgow Air Quality Monthly Reporting Pack

An Excel and Power Query monthly pack that turns raw air quality monitoring readings
into a clean report with automatic exceedance flags against the statutory objectives.

## Business question

Which Glasgow monitoring sites are within the air quality objectives each month, where
is a site trending towards a breach, and has the Low Emission Zone actually moved the
numbers? This is the recurring reporting job a Business Insight Analyst would own for
the Neighbourhoods, Regeneration and Sustainability directorate.

## Data source

Monitoring sites are mapped to Glasgow's real Air Quality Management Areas (City
Centre, Byres Road / Dumbarton Road, Parkhead Cross) taken from the council's open
AQMA layer (`data/glasgow_aqma_reference.csv`). Monthly values are modelled to a
plausible seasonal pattern and calibrated to public facts:

- NO2 annual mean objective is 40 ug/m3.
- Roadside NO2 fell about 34% into 2024 after Low Emission Zone phase 2 enforcement
  began on 1 June 2024.
- Glasgow reached full statutory compliance with air quality objectives in 2024, the
  first time in roughly 30 years.

The monthly readings are not raw council data. This is a personal portfolio pack built
on public information, and the workbook says so on its README sheet.

## What I built

`Glasgow_Air_Quality_Monthly_Pack.xlsx` with four sheets:

1. README - purpose, the documented Power Query steps, objectives, honesty note.
2. Raw Data - 360 readings, one row per site, pollutant and month (2022 to Sep 2025).
3. Monthly Report - each reading with a live status flag (Compliant, Watch at 90% of
   objective, or Exceedance), driven by formulas and colour coded with conditional
   formatting.
4. Annual Summary - annual mean per site and year via AVERAGEIFS, a compliance flag,
   and a KPI block.

Every derived number is a live Excel formula, so the pack is fully auditable. The
Power Query approach is documented on the README sheet: point the query at a folder of
monthly export files, refresh, and the whole pack updates.

## Headline insight

Five NO2 sites breached the 40 ug/m3 objective in 2022. By 2024 none did. Hope Street,
the worst kerbside site, fell from about 53 ug/m3 to about 35, a 34% drop that lands
right on the reported Low Emission Zone effect and the first full statutory compliance
in about three decades.

## How to rebuild

```bash
python3 build_aq_data.py     # writes data/glasgow_aq_monthly_raw.csv
python3 build_workbook.py    # writes Glasgow_Air_Quality_Monthly_Pack.xlsx
```

## Files

| File | What it is |
|------|------------|
| `build_aq_data.py` | Generates the calibrated monthly dataset |
| `build_workbook.py` | Builds the four sheet Excel pack |
| `data/glasgow_aq_monthly_raw.csv` | The monitoring readings |
| `data/glasgow_aqma_reference.csv` | Real Glasgow AQMA layer |
| `Glasgow_Air_Quality_Monthly_Pack.xlsx` | The finished pack |
