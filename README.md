# Glasgow Insight Portfolio

[![Rebuild](https://github.com/chanoch01/glasgow-insight-portfolio/actions/workflows/rebuild.yml/badge.svg)](https://github.com/chanoch01/glasgow-insight-portfolio/actions/workflows/rebuild.yml)

Three short data projects on public Glasgow data, built for the kind of work a Business
Insight Analyst does in Neighbourhoods, Regeneration and Sustainability (NRS) at Glasgow
City Council.

These are personal projects, not commissioned council work. The datasets are
modelled and calibrated to published figures (SEPA household waste statistics, Glasgow
Low Emission Zone air quality results, Cycling Scotland active travel surveys), not raw
council feeds. Every project says so in its own README and in the deliverable itself.

## The projects

| # | Project | Tools | Headline insight |
|---|---------|-------|------------------|
| 1 | [Recycling and Net Zero Tracker](01-recycling-netzero-tracker/) | Power BI style, star schema, DAX, Python | Glasgow recycles about 27%, third lowest of 32 councils, an 18 point gap to the national average, broadly flat for a decade, while waste carbon per resident is down about 28% since 2011 |
| 2 | [Active Travel Analysis](02-active-travel/) | SQL, Python, statsmodels, Streamlit | South West City Way cycle trips up about 116% since 2021; commuter and leisure routes show clearly different weekday signatures; the growth trend is structural |
| 3 | [Air Quality Monthly Reporting Pack](03-air-quality-pack/) | Excel, Power Query, openpyxl | Five NO2 sites breached the objective in 2022; none did by 2024, with Hope Street down about 34%, matching Glasgow's first full statutory compliance in 30 years |

## Run it

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Then follow each project's README. Every dataset, chart and the template workbook can be
rebuilt from the scripts, and the `Rebuild` check on GitHub does exactly that on every push.

| Project | Rebuild | Open the finished work |
|---------|---------|------------------------|
| 1 | `python3 build_dataset.py && python3 build_dashboard.py` | `recycling_netzero_dashboard.png`; Power BI report in `powerbi/` (in progress) |
| 2 | `python3 build_active_travel_data.py && python3 analysis.py` | `streamlit run streamlit_app.py` |
| 3 | `python3 build_aq_data.py && python3 build_workbook.py` | `Glasgow_Air_Quality_Monthly_Pack.xlsx` in Excel |

## Repository layout

```
01-recycling-netzero-tracker/   star schema, DAX, report mock, Power BI build in powerbi/
02-active-travel/               SQLite, SQL layer, seasonal decomposition, Streamlit app
03-air-quality-pack/            Excel pack with Power Query, plus its generator scripts
requirements.txt                one environment for all three projects
```

## Why these three

The role is about data fusion, analysis, visualisation and reporting that helps NRS make
better decisions. Each project deliberately exercises a different part of that:

- Project 1 is the strategic benchmarking report a senior officer or committee would read.
- Project 2 is the deeper analytical and interactive work, SQL through to a live tool.
- Project 3 is the unglamorous, repeatable monthly pack that performance teams live on.

Together they cover the three main tools the post asks for (Power BI, Python and SQL,
Excel and Power Query) and tie each one to a real Glasgow performance question.

## Honesty note

The data in every project is modelled and calibrated to published public figures. It is
not official statistics and is not presented as such. In a live build, each modelled
dataset would be replaced by the corresponding official feed (SEPA, council monitoring,
the cycle counter API) using the same schema, and the analysis would not change.
