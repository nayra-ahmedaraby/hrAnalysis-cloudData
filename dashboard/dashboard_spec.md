# HR Analytics — Power BI Dashboard

**File:** `dashboard/HR_Analytics.pbix`
**Owner:** Member 5

The Python pipeline writes these CSVs into `dashboard/`:

| File | Purpose |
| --- | --- |
| `executive_summary.csv`     | KPI cards (one row of headline numbers) |
| `risk_heatmap.csv`          | Department × risk_band counts |
| `employees_risk.csv`        | Per-employee detail (drill-through) |
| `department_drilldown.csv`  | Per-department aggregates + recommendation |
| `personas.csv`              | Cluster centers + persona strategy |

---

## Page 1 — Executive Summary
- **6 KPI cards** from `executive_summary.csv` (employees, attrition_rate, avg_risk, high_risk_count, avg_monthly_income).
- **Bar chart:** Department vs attrition_rate (`department_drilldown.csv`).
- **Donut:** risk_band split (`risk_heatmap.csv`).
- Slicers: Department, JobRole.

## Page 2 — Risk Heatmap
- **Matrix:** rows = Department, columns = risk_band, values = employees (with conditional color).
- **Drill-through table:** all fields of `employees_risk.csv`.

## Page 3 — Department Drill-down
- Slicer: Department.
- KPI cards filtered by department.
- Bar: top 10 highest-risk employees in the selected department.
- Scatter: MonthlyIncome vs risk_score, colored by risk_band.

## Page 4 — Personas
- KPI cards per persona (count, priority).
- Bar: cluster sizes.
- Multi-row card: Persona + Strategy.

---

## Build steps
1. Open Power BI Desktop → **Get Data → Folder** → point at `dashboard/`.
2. Promote first row as header for each CSV; check column types.
3. Manage Relationships:
   - `employees_risk[Cluster]` → `personas[Cluster]`
   - `employees_risk[Department]` → `department_drilldown[Department]`
4. Use red/amber/green colors for High/Medium/Low risk_band.
5. Save as `dashboard/HR_Analytics.pbix`.
