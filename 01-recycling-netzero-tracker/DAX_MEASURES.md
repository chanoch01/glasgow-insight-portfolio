# DAX Measures - Glasgow Recycling and Net Zero Tracker

These are the measures behind the report. The Python dashboard mirrors them exactly so the
screenshot and a rebuilt Power BI file produce the same numbers. Star schema:
`fact_waste` (1 row per local authority per year) joined to `dim_local_authority`
(one row per council) and `dim_calendar` (one row per year).

## Model relationships

| From | Column | To | Column | Cardinality |
|------|--------|----|--------|-------------|
| fact_waste | local_authority | dim_local_authority | local_authority | many-to-one |
| fact_waste | year | dim_calendar | year | many-to-one |

## Core recycling measures

```dax
Tonnes Recycled = SUM ( fact_waste[tonnes_recycled] )

Tonnes Generated = SUM ( fact_waste[tonnes_generated] )

Recycling Rate % =
DIVIDE ( [Tonnes Recycled], [Tonnes Generated] )
```
Format as percentage, 1 decimal. Aggregates correctly at any level because it
re-divides the summed numerator and denominator rather than averaging row rates.

```dax
Scotland Recycling Rate % =
CALCULATE (
    [Recycling Rate %],
    ALL ( dim_local_authority )
)
```
Removes the council filter so the same visual can show the national figure as a
reference line regardless of which council is selected.

```dax
Gap to Scotland (pts) =
( [Recycling Rate %] - [Scotland Recycling Rate %] ) * 100
```
Glasgow sits about 18 points below the Scottish average in the latest year.

## Ranking

```dax
Council Rank =
RANKX (
    ALL ( dim_local_authority[local_authority] ),
    [Recycling Rate %],
    ,
    DESC,
    DENSE
)
```
Used to surface the "29 / 32" KPI and to drive conditional formatting on the
benchmark bar chart. Glasgow lands in the third lowest band.

## Time intelligence

```dax
Recycling Rate % LY =
CALCULATE (
    [Recycling Rate %],
    DATEADD ( dim_calendar[date], -1, YEAR )
)

YoY Change (pts) =
( [Recycling Rate %] - [Recycling Rate % LY] ) * 100

Change Since 2011 (pts) =
VAR Base =
    CALCULATE ( [Recycling Rate %], dim_calendar[year] = 2011 )
RETURN ( [Recycling Rate %] - Base ) * 100
```
The headline KPI uses Change Since 2011 rather than YoY because Glasgow's rate has
been broadly flat year on year, so a single year delta hides the longer trend.

## Net zero / carbon

```dax
Carbon Impact (tCO2e) = SUM ( fact_waste[carbon_impact_tco2e] )

Population = SUM ( fact_waste[population] )

Carbon per Resident (kg) =
DIVIDE ( [Carbon Impact (tCO2e)] * 1000, [Population] )

Carbon Change Since 2011 % =
VAR Base =
    CALCULATE ( [Carbon Impact (tCO2e)], dim_calendar[year] = 2011 )
RETURN
    DIVIDE ( [Carbon Impact (tCO2e)] - Base, Base )
```
Carbon per resident is the metric that ties this report to the council's net zero
2030 target. Diverting waste from landfill cuts methane, so a falling recycling
gap and a falling carbon per resident tell a joined-up story.

## Waste mix (stacked bar)

```dax
Tonnes Landfilled = SUM ( fact_waste[tonnes_landfilled] )
Tonnes Other Diversion = SUM ( fact_waste[tonnes_other_diversion] )
% Landfilled = DIVIDE ( [Tonnes Landfilled], [Tonnes Generated] )
```

## Note on data

The dataset is a realistic model calibrated to published SEPA Household Waste
statistics (Scotland 44.3% in 2024; Glasgow about 27%, third lowest of 32).
Per-authority yearly values are modelled, not exact SEPA figures, and the report
labels this clearly. In a production build these tables would be replaced by the
SEPA open data feed with the same schema and the measures above would not change.
