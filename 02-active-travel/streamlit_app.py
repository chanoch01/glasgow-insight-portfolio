"""
Glasgow Active Travel - Streamlit dashboard.

Run locally with:
    streamlit run streamlit_app.py

Reads the SQLite counter table built by build_active_travel_data.py and lets a user
filter by route and date range, see headline KPIs, monthly trend, weekday profile, and
growth vs the 2021 baseline. Personal portfolio project on public, calibrated data.
"""
import sqlite3
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Glasgow Active Travel", layout="wide")

TEAL = "#01696F"; NAVY = "#1F3A5F"

@st.cache_data
def load():
    con = sqlite3.connect("data/active_travel.db")
    df = pd.read_sql("SELECT * FROM counter_daily", con, parse_dates=["count_date"])
    con.close()
    return df

df = load()

st.title("Glasgow Active Travel dashboard")
st.caption("Personal portfolio project. Daily cycle counts modelled on a plausible "
           "growth and seasonal curve, calibrated to published Glasgow figures "
           "(South West City Way about +116% since 2021). Not raw council counter feeds.")

# ---- sidebar filters ----
routes = sorted(df.route.unique())
sel_routes = st.sidebar.multiselect("Routes", routes, default=routes)
yr_min, yr_max = int(df.year.min()), int(df.year.max())
sel_years = st.sidebar.slider("Years", yr_min, yr_max, (yr_min, yr_max))

f = df[df.route.isin(sel_routes) & df.year.between(*sel_years)]

# ---- KPIs ----
c1, c2, c3 = st.columns(3)
total = int(f.cyclists.sum())
avg_daily = int(f.groupby("count_date").cyclists.sum().mean()) if len(f) else 0
# growth for South West City Way if present
g_txt = "n/a"
if "South West City Way" in sel_routes:
    a = df[df.route == "South West City Way"].groupby("year").cyclists.sum()
    if 2021 in a.index and 2024 in a.index:
        g_txt = f"+{(a[2024]-a[2021])/a[2021]*100:.0f}%"
c1.metric("Total cyclists (filtered)", f"{total:,}")
c2.metric("Average daily total", f"{avg_daily:,}")
c3.metric("South West City Way growth, 2021 to 2024", g_txt)

# ---- monthly trend ----
st.subheader("Monthly cyclists by route")
m = (f.groupby(["route", "year", "month"]).cyclists.sum().reset_index())
m["period"] = pd.to_datetime(dict(year=m.year, month=m.month, day=1))
line = alt.Chart(m).mark_line().encode(
    x=alt.X("period:T", title="Month"),
    y=alt.Y("cyclists:Q", title="Cyclists per month"),
    color=alt.Color("route:N", title="Route"),
).properties(height=320)
st.altair_chart(line, width="stretch")

# ---- weekday profile ----
st.subheader("Weekday profile")
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
wd = f.groupby(["route", "weekday"]).cyclists.mean().reset_index()
bar = alt.Chart(wd).mark_bar().encode(
    x=alt.X("weekday:N", sort=order, title="Weekday"),
    y=alt.Y("cyclists:Q", title="Average cyclists per day"),
    color=alt.Color("route:N", title="Route"),
    xOffset="route:N",
).properties(height=320)
st.altair_chart(bar, width="stretch")

st.subheader("Growth vs 2021 baseline")
a = df[df.route.isin(sel_routes)].groupby(["route", "year"]).cyclists.sum().reset_index()
base = a[a.year == 2021].set_index("route").cyclists
latest = a[a.year == sel_years[1]].set_index("route").cyclists
growth = ((latest - base) / base * 100).round(0).reset_index()
growth.columns = ["Route", f"Growth 2021 to {sel_years[1]} (%)"]
st.dataframe(growth, width="stretch", hide_index=True)
