-- Glasgow Active Travel - SQL aggregation layer
-- Source table: counter_daily (one row per route per day)
-- These queries build the aggregates the Python analysis and Streamlit app read.

-- 1. Monthly totals and average daily count per route
SELECT route, route_type, year, month,
       SUM(cyclists)            AS monthly_cyclists,
       ROUND(AVG(cyclists), 0)  AS avg_daily
FROM   counter_daily
GROUP  BY route, route_type, year, month
ORDER  BY route, year, month;

-- 2. Annual totals per route (used to compute growth vs the 2021 baseline)
SELECT route, year, SUM(cyclists) AS annual_cyclists
FROM   counter_daily
GROUP  BY route, year
ORDER  BY route, year;

-- 3. Growth since 2021 per route (self join on the baseline year)
WITH annual AS (
    SELECT route, year, SUM(cyclists) AS total
    FROM   counter_daily
    GROUP  BY route, year
)
SELECT a.route,
       a.year,
       a.total,
       b.total AS baseline_2021,
       ROUND( (a.total - b.total) * 100.0 / b.total, 1) AS pct_change_vs_2021
FROM   annual a
JOIN   annual b ON a.route = b.route AND b.year = 2021
ORDER  BY a.route, a.year;

-- 4. Weekday profile - average cyclists by weekday (commuter vs leisure signature)
SELECT route, route_type, weekday,
       ROUND(AVG(cyclists), 0) AS avg_cyclists
FROM   counter_daily
GROUP  BY route, route_type, weekday;

-- 5. Weekday vs weekend split per route type
SELECT route_type,
       CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
       ROUND(AVG(cyclists), 0) AS avg_cyclists
FROM   counter_daily
GROUP  BY route_type, day_type
ORDER  BY route_type, day_type;
