# Member 5 — Insights & Strategic Recommendations
#
# Reads:  employees_with_clusters.csv, risk_scores.csv, personas.csv, top_10_features.csv
# Writes:
#   reports/recommendations.md
#   reports/top20_high_risk.csv
#   reports/persona_strategies.csv
#   reports/department_recommendations.csv
#   reports/executive_summary.json
#   dashboard/executive_summary.csv
#   dashboard/risk_heatmap.csv
#   dashboard/department_drilldown.csv
#   dashboard/personas.csv
#   dashboard/employees_risk.csv

import os
import json
import pandas as pd

from src.config import (
    DATA_PATH, FEATURES_DATA_PATH, PROCESSED_DATA_PATH,
    REPORTS_PATH, DASHBOARD_PATH,
    ID_COL, TARGET_ATTRITION,
)


class InsightsGenerator:

    def __init__(self):
        os.makedirs(REPORTS_PATH, exist_ok=True)
        os.makedirs(DASHBOARD_PATH, exist_ok=True)

        self.employees = None
        self.personas = None
        self.top_features = None
        self.top20 = None
        self.persona_recs = None
        self.dept_recs = None
        self.summary = {}

    # --- Load all upstream files into one master table ----------------
    def load(self):
        clusters_path = f"{REPORTS_PATH}/employees_with_clusters.csv"
        if os.path.exists(clusters_path):
            base = pd.read_csv(clusters_path)
        elif os.path.exists(FEATURES_DATA_PATH):
            base = pd.read_csv(FEATURES_DATA_PATH)
        else:
            base = pd.read_csv(PROCESSED_DATA_PATH)

        # Merge human-readable categorical names from the raw CSV
        # (preprocessing label-encoded these columns; the report needs the names).
        try:
            raw = pd.read_csv(DATA_PATH)
            raw_cols = ["Department", "JobRole", "OverTime", "MaritalStatus",
                        "BusinessTravel", "Gender", "EducationField"]
            keep = [c for c in raw_cols if c in raw.columns]
            if ID_COL in raw.columns and keep:
                base = base.drop(columns=[c for c in keep if c in base.columns],
                                 errors="ignore")
                base = base.merge(raw[[ID_COL] + keep], on=ID_COL, how="left")
        except Exception as e:
            print(f"[load] could not merge raw labels: {e}")

        risk_path = f"{REPORTS_PATH}/risk_scores.csv"
        if os.path.exists(risk_path):
            risks = pd.read_csv(risk_path)
            if "risk_score" not in base.columns:
                base = base.merge(risks, on=ID_COL, how="left")
        else:
            base["risk_score"] = float("nan")
            base["risk_band"] = "Unknown"

        per_path = f"{REPORTS_PATH}/personas.csv"
        self.personas = pd.read_csv(per_path) if os.path.exists(per_path) else pd.DataFrame()

        top_path = f"{REPORTS_PATH}/top_10_features.csv"
        if os.path.exists(top_path):
            self.top_features = pd.read_csv(top_path)
            # Handle both formats: "feature,importance" and unnamed-index legacy.
            if "Unnamed: 0" in self.top_features.columns:
                self.top_features.columns = ["feature", "importance"]
            elif self.top_features.shape[1] == 2:
                self.top_features.columns = ["feature", "importance"]
            self.top_features["importance"] = self.top_features["importance"].round(4)
        else:
            self.top_features = pd.DataFrame(columns=["feature", "importance"])

        self.employees = base
        print(f"[load] employees={len(base)} | personas={len(self.personas)}")
        return self

    # --- Top 20 high-risk + recommendations ---------------------------
    def build_top20(self):
        df = self.employees.copy()
        if "risk_score" not in df.columns:
            return self

        df = df.sort_values("risk_score", ascending=False).head(20).reset_index(drop=True)

        recs = []
        for _, r in df.iterrows():
            parts = []
            if r.get("OverTime") in ("Yes", 1):
                parts.append("Reduce overtime")
            if r.get("MonthlyIncome", 0) and r["MonthlyIncome"] < 4000:
                parts.append("Salary review (below $4k)")
            if r.get("JobSatisfaction", 5) <= 2:
                parts.append("1:1 satisfaction discussion")
            if r.get("WorkLifeBalance", 5) <= 2:
                parts.append("Offer flexible schedule")
            if r.get("YearsSinceLastPromotion", 0) >= 5:
                parts.append("Promotion review")
            if not parts:
                parts.append("Schedule retention conversation")
            recs.append(" | ".join(parts))

        df["recommendation"] = recs
        keep = [c for c in [
            ID_COL, "Department", "JobRole", "Age", "MonthlyIncome",
            "OverTime", "JobSatisfaction", "Cluster",
            "risk_score", "risk_band", "recommendation",
        ] if c in df.columns]

        self.top20 = df[keep]
        self.top20.to_csv(f"{REPORTS_PATH}/top20_high_risk.csv", index=False)
        return self

    # --- Persona strategies -------------------------------------------
    def build_persona_strategies(self):
        if self.personas.empty:
            return self

        out = []
        for _, row in self.personas.iterrows():
            persona = str(row.get("Persona", "Unknown"))
            cluster = row.get("Cluster", -1)

            if "High Attrition Risk" in persona:
                strategy = ("Urgent retention: salary review, flexible hours, "
                            "mentor pairing, monthly check-ins.")
                priority = "Critical"
            elif "Highly Engaged" in persona:
                strategy = ("Leverage as champions: leadership tracks, "
                            "stretch assignments, visible recognition.")
                priority = "High"
            elif "Loyal" in persona:
                strategy = ("Protect tenure: lateral moves, specialist titles, "
                            "review long-overdue promotions.")
                priority = "Medium"
            else:
                strategy = ("Standard cadence: quarterly 1:1s, "
                            "annual development plan.")
                priority = "Standard"

            out.append({"Cluster": cluster, "Persona": persona,
                        "Priority": priority, "Strategy": strategy})

        self.persona_recs = pd.DataFrame(out)
        self.persona_recs.to_csv(f"{REPORTS_PATH}/persona_strategies.csv", index=False)
        return self

    # --- Department recommendations -----------------------------------
    def build_department_recommendations(self):
        df = self.employees.copy()
        if "Department" not in df.columns:
            return self

        agg_cols = {"employees": ("Department", "size")}
        if TARGET_ATTRITION in df.columns:
            agg_cols["attrition_rate"] = (TARGET_ATTRITION, "mean")
        if "risk_score" in df.columns:
            agg_cols["avg_risk"] = ("risk_score", "mean")
        if "MonthlyIncome" in df.columns:
            agg_cols["avg_income"] = ("MonthlyIncome", "mean")

        agg = df.groupby("Department").agg(**agg_cols).reset_index()
        if "attrition_rate" in agg.columns:
            agg["attrition_rate"] = (agg["attrition_rate"] * 100).round(2)
        for c in ["avg_risk", "avg_income"]:
            if c in agg.columns:
                agg[c] = agg[c].round(2)

        recs = []
        for _, r in agg.iterrows():
            tactics = []
            if r.get("attrition_rate", 0) > 20:
                tactics.append("Exit-interview audit")
            if r.get("avg_risk", 0) > 0.4:
                tactics.append("Retention bonus for top performers")
            if not tactics:
                tactics.append("Quarterly health check")
            recs.append(" | ".join(tactics))

        agg["recommendation"] = recs
        if "avg_risk" in agg.columns:
            agg = agg.sort_values("avg_risk", ascending=False)

        self.dept_recs = agg
        self.dept_recs.to_csv(f"{REPORTS_PATH}/department_recommendations.csv", index=False)
        return self

    # --- Recommendations.md -------------------------------------------
    def write_recommendations_md(self):
        df = self.employees
        n = len(df)
        attr_rate = (df[TARGET_ATTRITION].mean() * 100) if TARGET_ATTRITION in df.columns else None
        avg_risk = df["risk_score"].mean() if "risk_score" in df.columns else None
        high_risk = int((df["risk_score"] > 0.6).sum()) if "risk_score" in df.columns else 0

        lines = ["# Strategic HR Recommendations", "", "## Executive Summary",
                 f"- Workforce: **{n}** employees"]
        if attr_rate is not None:
            lines.append(f"- Attrition rate: **{attr_rate:.2f}%**")
        if avg_risk is not None:
            lines.append(f"- Mean risk: **{avg_risk:.3f}**")
        lines.append(f"- High-risk employees (>0.6): **{high_risk}**")
        lines.append("")

        lines.append("## Top 20 High-Risk Employees")
        if self.top20 is not None:
            lines.append(self.top20.to_markdown(index=False))
        lines.append("")

        lines.append("## Persona Strategies")
        if self.persona_recs is not None:
            lines.append(self.persona_recs.to_markdown(index=False))
        lines.append("")

        lines.append("## Department Recommendations")
        if self.dept_recs is not None:
            lines.append(self.dept_recs.to_markdown(index=False))
        lines.append("")

        lines.append("## Top Attrition Drivers (model)")
        if not self.top_features.empty:
            lines.append(self.top_features.head(10).to_markdown(index=False))

        with open(f"{REPORTS_PATH}/recommendations.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return self

    # --- Dashboard CSVs -----------------------------------------------
    def build_dashboard_csvs(self):
        df = self.employees.copy()

        # KPI summary (one row, used by report + dashboard cards)
        kpis = {
            "total_employees": int(len(df)),
            "attrition_rate": round(float(df[TARGET_ATTRITION].mean() * 100), 2)
                              if TARGET_ATTRITION in df.columns else None,
            "avg_risk": round(float(df["risk_score"].mean()), 4)
                        if "risk_score" in df.columns else None,
            "high_risk_count": int((df.get("risk_score", pd.Series([])) > 0.6).sum()),
            "avg_monthly_income": round(float(df["MonthlyIncome"].mean()), 2)
                                  if "MonthlyIncome" in df.columns else None,
        }
        pd.DataFrame([kpis]).to_csv(f"{DASHBOARD_PATH}/executive_summary.csv", index=False)
        self.summary = kpis

        # Risk heatmap (Department × risk_band)
        if "Department" in df.columns and "risk_band" in df.columns:
            heat = df.groupby(["Department", "risk_band"]).size().reset_index(name="employees")
            heat.to_csv(f"{DASHBOARD_PATH}/risk_heatmap.csv", index=False)

            cols = [c for c in [ID_COL, "Department", "JobRole", "MonthlyIncome",
                                "OverTime", "risk_score", "risk_band", "Cluster"]
                    if c in df.columns]
            df[cols].to_csv(f"{DASHBOARD_PATH}/employees_risk.csv", index=False)

        # Department drill-down — reuse the dept recs table
        if self.dept_recs is not None:
            self.dept_recs.to_csv(f"{DASHBOARD_PATH}/department_drilldown.csv", index=False)

        # Personas (with strategies merged in)
        if not self.personas.empty:
            personas_out = self.personas.copy()
            if self.persona_recs is not None:
                personas_out = personas_out.merge(
                    self.persona_recs[["Cluster", "Priority", "Strategy"]],
                    on="Cluster", how="left",
                )
            personas_out.to_csv(f"{DASHBOARD_PATH}/personas.csv", index=False)

        # JSON consumed by report_generator.py
        with open(f"{REPORTS_PATH}/executive_summary.json", "w", encoding="utf-8") as f:
            json.dump(kpis, f, indent=2)

        print(f"[saved] dashboard CSVs → {DASHBOARD_PATH}")
        return self

    def run(self):
        (self
            .load()
            .build_top20()
            .build_persona_strategies()
            .build_department_recommendations()
            .write_recommendations_md()
            .build_dashboard_csvs())
        print("[Insights] Done.")
        return self


if __name__ == "__main__":
    InsightsGenerator().run()
