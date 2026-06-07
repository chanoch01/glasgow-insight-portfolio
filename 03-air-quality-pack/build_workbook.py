"""
Builds Glasgow_Air_Quality_Monthly_Pack.xlsx - a 4 sheet monthly reporting pack.

Sheets:
  1. README - what this is, the Power Query steps, the objectives, honesty note
  2. Raw Data - the monthly monitoring readings (Power Query "source" table)
  3. Monthly Report - per site-month with live exceedance flags vs objectives
  4. Annual Summary - per site-year annual mean, compliance status, KPI cards

All derived numbers are Excel formulas so the pack is auditable. Calibrated to:
NO2 annual mean objective 40 ug/m3; LEZ ~34% NO2 fall into 2024; full statutory
compliance reached 2024. Personal portfolio pack on public data.
"""
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation

TEAL = "01696F"; NAVY = "1F3A5F"; AMBER = "E8A33D"; RED = "B23A48"; LIGHT = "F4F6F8"
GREEN_FILL = PatternFill("solid", fgColor="D6EBD6")
RED_FILL = PatternFill("solid", fgColor="F4CCCC")
AMBER_FILL = PatternFill("solid", fgColor="FCE5CD")
HEADER_FILL = PatternFill("solid", fgColor=TEAL)
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(bold=True, size=16, color=NAVY)
SUB_FONT = Font(italic=True, size=10, color="555555")
thin = Side(style="thin", color="D9D9D9")
BORDER = Border(bottom=thin, top=thin, left=thin, right=thin)

NO2_LIMIT = 40   # annual mean objective ug/m3
PM10_LIMIT = 18  # Scotland annual mean objective ug/m3

# ---- load raw ----
with open("data/glasgow_aq_monthly_raw.csv") as f:
    raw = list(csv.DictReader(f))

wb = openpyxl.Workbook()

# ============ Sheet 1: README ============
ws = wb.active
ws.title = "README"
ws.column_dimensions["A"].width = 3
ws.column_dimensions["B"].width = 105
ws["B2"] = "Glasgow Air Quality - Monthly Reporting Pack"
ws["B2"].font = TITLE_FONT
ws["B3"] = "Personal portfolio project built on public data. Calibrated to published Glasgow air quality facts."
ws["B3"].font = SUB_FONT
readme = [
    "",
    "PURPOSE",
    "A repeatable monthly pack for the Neighbourhoods, Regeneration and Sustainability team. It turns raw",
    "monitoring readings into a clean report with automatic exceedance flags against the statutory objectives,",
    "so officers can see at a glance which sites are compliant and where attention is needed.",
    "",
    "DATA SOURCE",
    "Monitoring sites are mapped to Glasgow's real Air Quality Management Areas (City Centre, Byres Road /",
    "Dumbarton Road, Parkhead Cross) from the council's open AQMA layer. Monthly values are modelled to a",
    "plausible seasonal pattern and calibrated to public facts: roadside NO2 fell about 34% into 2024 after the",
    "Low Emission Zone phase 2 began on 1 June 2024, and the city reached full statutory compliance in 2024 for",
    "the first time in about 30 years. They are not raw council readings.",
    "",
    "OBJECTIVES USED FOR FLAGS",
    f"NO2 annual mean objective: {NO2_LIMIT} ug/m3.",
    f"PM10 Scotland annual mean objective: {PM10_LIMIT} ug/m3.",
    "Amber warning band is set at 90% of the objective so a site trending towards breach is caught early.",
    "",
    "POWER QUERY STEPS (how the Raw Data sheet would be shaped in a live build)",
    "1. Source: connect to the council monitoring export (CSV or SharePoint folder of monthly files).",
    "2. Promote headers, set data types (Year and Month as whole number, mean as decimal).",
    "3. Trim and clean Site and AQMA text, remove fully blank rows.",
    "4. Add a Period column (Year and Month as yyyy-mm) for sorting and joins.",
    "5. Filter out rows with data capture below 75% so low-quality months do not skew the mean.",
    "6. Append new monthly files automatically by pointing the query at a folder, then Refresh.",
    "The Monthly Report and Annual Summary sheets read from this table, so a Refresh updates the whole pack.",
    "",
    "SHEETS",
    "Raw Data        - the monitoring readings, one row per site, pollutant and month.",
    "Monthly Report  - each reading with a live status flag (Compliant / Watch / Exceedance).",
    "Annual Summary  - annual mean per site and year, compliance status, and headline KPIs.",
    "",
    "HEADLINE INSIGHT",
    "Hope Street, the worst kerbside NO2 site, falls from about 53 ug/m3 in 2022 to about 35 in 2024, crossing",
    "below the 40 objective. Every monitored site is compliant on the annual mean by 2024, matching Glasgow's",
    "reported first full statutory compliance in roughly three decades.",
]
r = 5
for line in readme:
    ws[f"B{r}"] = line
    if line.isupper() and line.strip():
        ws[f"B{r}"].font = Font(bold=True, size=11, color=TEAL)
    else:
        ws[f"B{r}"].font = Font(size=10, color="333333")
    r += 1

# ============ Sheet 2: Raw Data ============
ws2 = wb.create_sheet("Raw Data")
headers = ["Year", "Month", "Period", "Site", "AQMA", "Pollutant",
           "Monitor type", "Monthly mean (ug/m3)", "Data capture (%)"]
ws2.append([""] )  # row 1 margin handled by writing from row 1 header per skill? keep simple: header row 1
ws2.delete_rows(1)
ws2.append(headers)
for row in raw:
    ws2.append([
        int(row["Year"]), int(row["Month"]), row["Period"], row["Site"], row["AQMA"],
        row["Pollutant"], row["Monitor type"], float(row["Monthly mean (ug/m3)"]),
        float(row["Data capture (%)"]),
    ])
for c in ws2[1]:
    c.fill = HEADER_FILL; c.font = HEADER_FONT; c.alignment = Alignment(horizontal="center")
widths2 = [8, 8, 10, 24, 26, 11, 14, 20, 16]
for i, wdt in enumerate(widths2, start=1):
    ws2.column_dimensions[get_column_letter(i)].width = wdt
for r_ in range(2, ws2.max_row + 1):
    ws2.cell(row=r_, column=8).number_format = "0.0"
    ws2.cell(row=r_, column=9).number_format = "0.0"
ws2.freeze_panes = "A2"
ws2.auto_filter.ref = f"A1:I{ws2.max_row}"
RAW_LAST = ws2.max_row

# ============ Sheet 3: Monthly Report ============
ws3 = wb.create_sheet("Monthly Report")
hdr3 = ["Period", "Site", "AQMA", "Pollutant", "Monthly mean (ug/m3)",
        "Objective (ug/m3)", "% of objective", "Status"]
ws3.append(hdr3)
n = len(raw)
for i in range(2, n + 2):
    src = i  # same row offset in Raw Data (header at row 1 both sheets)
    ws3.cell(row=i, column=1, value=f"='Raw Data'!C{src}")
    ws3.cell(row=i, column=2, value=f"='Raw Data'!D{src}")
    ws3.cell(row=i, column=3, value=f"='Raw Data'!E{src}")
    ws3.cell(row=i, column=4, value=f"='Raw Data'!F{src}")
    ws3.cell(row=i, column=5, value=f"='Raw Data'!H{src}")
    # objective depends on pollutant
    ws3.cell(row=i, column=6, value=f'=IF(D{i}="NO2",{NO2_LIMIT},{PM10_LIMIT})')
    ws3.cell(row=i, column=7, value=f"=E{i}/F{i}")
    ws3.cell(row=i, column=8,
             value=f'=IF(E{i}>F{i},"Exceedance",IF(E{i}>=F{i}*0.9,"Watch","Compliant"))')
for c in ws3[1]:
    c.fill = HEADER_FILL; c.font = HEADER_FONT; c.alignment = Alignment(horizontal="center")
widths3 = [10, 24, 26, 11, 20, 17, 14, 14]
for i, wdt in enumerate(widths3, start=1):
    ws3.column_dimensions[get_column_letter(i)].width = wdt
for r_ in range(2, n + 2):
    ws3.cell(row=r_, column=5).number_format = "0.0"
    ws3.cell(row=r_, column=6).number_format = "0"
    ws3.cell(row=r_, column=7).number_format = "0.0%"
ws3.freeze_panes = "A2"
ws3.auto_filter.ref = f"A1:H{n+1}"
# conditional formatting on Status column H
rng = f"H2:H{n+1}"
ws3.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Exceedance"'], fill=RED_FILL))
ws3.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Watch"'], fill=AMBER_FILL))
ws3.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Compliant"'], fill=GREEN_FILL))

# ============ Sheet 4: Annual Summary ============
ws4 = wb.create_sheet("Annual Summary")
# build unique site x pollutant x year combos
combos = []
seen = set()
for row in raw:
    key = (row["Site"], row["Pollutant"], int(row["Year"]))
    if key not in seen:
        seen.add(key); combos.append(key)
combos.sort(key=lambda x: (x[1], x[0], x[2]))

ws4["B2"] = "Annual Summary - mean concentration and compliance by site and year"
ws4["B2"].font = TITLE_FONT
hdr4 = ["Site", "Pollutant", "Year", "Annual mean (ug/m3)", "Objective", "Compliant?"]
start = 4
for j, h in enumerate(hdr4, start=2):
    c = ws4.cell(row=start, column=j, value=h)
    c.fill = HEADER_FILL; c.font = HEADER_FONT; c.alignment = Alignment(horizontal="center")
for idx, (site, pol, yr) in enumerate(combos):
    rr = start + 1 + idx
    ws4.cell(row=rr, column=2, value=site)
    ws4.cell(row=rr, column=3, value=pol)
    ws4.cell(row=rr, column=4, value=yr)
    # AVERAGEIFS over Raw Data: mean where site (D), pollutant (F), year (A) match.
    # Summary cols: B=Site, C=Pollutant, D=Year. Raw: D=Site, F=Pollutant, A=Year, H=mean.
    avg = (f"=AVERAGEIFS('Raw Data'!H2:H{RAW_LAST},'Raw Data'!D2:D{RAW_LAST},B{rr},"
           f"'Raw Data'!F2:F{RAW_LAST},C{rr},'Raw Data'!A2:A{RAW_LAST},D{rr})")
    ws4.cell(row=rr, column=5, value=avg)
    ws4.cell(row=rr, column=6, value=f'=IF(C{rr}="NO2",{NO2_LIMIT},{PM10_LIMIT})')
    ws4.cell(row=rr, column=7, value=f'=IF(E{rr}<=F{rr},"Yes","No")')
    ws4.cell(row=rr, column=5).number_format = "0.0"
last4 = start + len(combos)
widths4 = [24, 11, 8, 18, 11, 12]
for i, wdt in enumerate(widths4, start=2):
    ws4.column_dimensions[get_column_letter(i)].width = wdt
ws4.column_dimensions["A"].width = 3
# CF on compliant column G
crng = f"G{start+1}:G{last4}"
ws4.conditional_formatting.add(crng, CellIsRule(operator="equal", formula=['"Yes"'], fill=GREEN_FILL))
ws4.conditional_formatting.add(crng, CellIsRule(operator="equal", formula=['"No"'], fill=RED_FILL))

# KPI cards block to the right
kc = 9  # column I
ws4.cell(row=start, column=kc, value="Headline KPIs").font = Font(bold=True, size=12, color=NAVY)
# total exceedances 2024 (NO2), worst site mean 2022 vs 2024
ws4.cell(row=start+1, column=kc, value="Sites breaching NO2 objective, 2024")
ws4.cell(row=start+1, column=kc+2,
         value=f'=COUNTIFS(C{start+1}:C{last4},"NO2",E{start+1}:E{last4},">"&{NO2_LIMIT},D{start+1}:D{last4},2024)')
ws4.cell(row=start+2, column=kc, value="Sites breaching NO2 objective, 2022")
ws4.cell(row=start+2, column=kc+2,
         value=f'=COUNTIFS(C{start+1}:C{last4},"NO2",E{start+1}:E{last4},">"&{NO2_LIMIT},D{start+1}:D{last4},2022)')
ws4.cell(row=start+3, column=kc, value="Hope Street NO2 mean, 2022 (ug/m3)")
ws4.cell(row=start+3, column=kc+2,
         value=f'=AVERAGEIFS(E{start+1}:E{last4},B{start+1}:B{last4},"Hope Street (kerbside)",C{start+1}:C{last4},"NO2",D{start+1}:D{last4},2022)')
ws4.cell(row=start+4, column=kc, value="Hope Street NO2 mean, 2024 (ug/m3)")
ws4.cell(row=start+4, column=kc+2,
         value=f'=AVERAGEIFS(E{start+1}:E{last4},B{start+1}:B{last4},"Hope Street (kerbside)",C{start+1}:C{last4},"NO2",D{start+1}:D{last4},2024)')
ws4.cell(row=start+5, column=kc, value="NO2 reduction at Hope St, 2022 to 2024")
ws4.cell(row=start+5, column=kc+2, value=f"=(K{start+3}-K{start+4})/K{start+3}")
ws4.cell(row=start+5, column=kc+2).number_format = "0%"
ws4.cell(row=start+3, column=kc+2).number_format = "0.0"
ws4.cell(row=start+4, column=kc+2).number_format = "0.0"
ws4.column_dimensions["I"].width = 34
ws4.column_dimensions["J"].width = 4
ws4.column_dimensions["K"].width = 12
for rr in range(start, start+6):
    ws4.cell(row=rr, column=kc).font = Font(size=10, color="333333")
    ws4.cell(row=rr, column=kc+2).font = Font(bold=True, color=TEAL)

OUT = "Glasgow_Air_Quality_Monthly_Pack.xlsx"
wb.save(OUT)
print(f"Saved {OUT}; Raw rows={RAW_LAST-1}, Monthly report rows={n}, Annual combos={len(combos)}")
print(f"KPI cell refs: 2024 breaches=K{start+1}, 2022 breaches=K{start+2}, HopeSt2022=K{start+3}, HopeSt2024=K{start+4}, reduction=K{start+5}")
