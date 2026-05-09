# HR Analytics — Power BI Dashboard

**File:** `dashboard/HR_Analytics.pbix`
**Owner:** Member 5

## ⭐ Recommended approach — Single fact table

Use **`employees_full.csv` ONLY** as your main data source. It has every employee
with every column (Department name, salary, satisfaction, risk_score, risk_band,
Cluster, all engineered features, Attrition flag).

Optional: Add `personas.csv` as a small lookup table linked by `Cluster`.

This avoids:
- ❌ "Sum of attrition_rate" errors (the rate is calculated, not pre-aggregated)
- ❌ Broken slicers (everything filters from one table)
- ❌ Complex DAX measures (Power BI handles it natively)

| File | Use as | Notes |
| --- | --- | --- |
| **`employees_full.csv`** | **Main fact table** | All per-employee data — single source of truth |
| `personas.csv`           | Lookup (optional)   | Cluster → Persona name + Strategy |

---

## How to build each visual using only `employees_full`

### Page 1 — Executive Summary

| Visual | Field / Setting |
| --- | --- |
| **Total Employees card**   | Count of `EmployeeNumber` |
| **Attrition Rate card**    | `Attrition` → Average × 100 (or use a DAX measure: `Attrition_Rate = AVERAGE([Attrition]) * 100`) |
| **Avg Risk Score card**    | Average of `risk_score` |
| **High-Risk count card**   | Count where `risk_band` = "High" (use a Filter) |
| **Avg Income card**        | Average of `MonthlyIncome` |
| **Bar — Attrition by Dept**| Axis: `Department`, Value: `Attrition` (Average × 100) |
| **Donut — Risk band**      | Legend: `risk_band`, Value: Count |
| **Slicers**                | `Department`, `JobRole`, `OverTime` |

### Page 2 — Risk Heatmap
- **Matrix:** Rows = `Department`, Columns = `risk_band`, Values = Count of `EmployeeNumber`. Apply conditional formatting (background color) on the values.
- **Detail table:** Drag `EmployeeNumber`, `Department`, `JobRole`, `MonthlyIncome`, `risk_score`, `risk_band`, `Cluster` into a Table visual.

### Page 3 — Department Drill-down
- **Slicer:** `Department`
- **Cards** (auto-filtered): Count of `EmployeeNumber`, Avg `risk_score`, Avg `MonthlyIncome`, Avg `JobSatisfaction`
- **Top-N table:** sort employees by `risk_score` DESC, top 10
- **Scatter:** X = `MonthlyIncome`, Y = `risk_score`, Color = `risk_band`

### Page 4 — Personas
- Join `employees_full[Cluster]` ↔ `personas[Cluster]`.
- **Cards:** Persona, Priority (from `personas`), Count of employees
- **Bar:** Cluster vs employee count
- **Multi-row card:** Persona + Strategy

---

## Useful DAX measures (optional, makes life easier)

```DAX
Attrition Rate = AVERAGE(employees_full[Attrition]) * 100

Total Employees = COUNTROWS(employees_full)

High Risk Count =
CALCULATE(COUNTROWS(employees_full),
          employees_full[risk_band] = "High")

Avg Risk = AVERAGE(employees_full[risk_score])

Overtime Attrition Rate =
CALCULATE(AVERAGE(employees_full[Attrition]),
          employees_full[OverTime] = "Yes") * 100
```

---

## Build steps

1. **Get Data → Folder** → point at the `dashboard/` folder.
2. Keep only `employees_full.csv` (and optionally `personas.csv`).
3. In Power Query, confirm types (numeric for risk_score, MonthlyIncome, etc.).
4. **Close & Apply.**
5. (Optional) Add the DAX measures above (Modeling → New Measure).
6. Build the 4 pages.
7. Theme: red = High risk, amber = Medium, green = Low.
8. Save as `dashboard/HR_Analytics.pbix`.
