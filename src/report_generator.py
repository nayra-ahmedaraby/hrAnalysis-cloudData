# Member 5 — Final PDF Report
# Builds docs/final_report.pdf from the artifacts produced upstream.

import os
import json
from datetime import datetime

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether,
)

from src.config import REPORTS_PATH, FIGURES_PATH, DOCS_PATH


REPORT_PATH = f"{DOCS_PATH}/final_report.pdf"

NAVY  = colors.HexColor("#1a3d6d")
GREY  = colors.HexColor("#555555")
LIGHT = colors.HexColor("#f3f5f9")


def _page_footer(canvas, doc):
    """Adds 'Page N — HR Analytics Report' to every page."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawString(2 * cm, 1 * cm, "HR Analytics — Final Report")
    canvas.drawRightString(A4[0] - 2 * cm, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()


class ReportGenerator:

    def __init__(self):
        os.makedirs(DOCS_PATH, exist_ok=True)

        ss = getSampleStyleSheet()
        self.styles = ss
        ss.add(ParagraphStyle(
            name="CoverTitle", parent=ss["Title"], fontSize=26, leading=30,
            textColor=NAVY, alignment=TA_CENTER, spaceAfter=10,
        ))
        ss.add(ParagraphStyle(
            name="CoverSub", parent=ss["BodyText"], fontSize=13,
            textColor=GREY, alignment=TA_CENTER, spaceAfter=20,
        ))
        ss.add(ParagraphStyle(
            name="H1", parent=ss["Heading1"], fontSize=16, leading=20,
            textColor=NAVY, spaceBefore=10, spaceAfter=8,
        ))
        ss.add(ParagraphStyle(
            name="H2", parent=ss["Heading2"], fontSize=12, leading=16,
            textColor=NAVY, spaceBefore=6, spaceAfter=4,
        ))
        ss.add(ParagraphStyle(
            name="Body2", parent=ss["BodyText"], fontSize=10, leading=14,
            spaceAfter=5, alignment=TA_JUSTIFY,
        ))
        ss.add(ParagraphStyle(
            name="Cell", parent=ss["BodyText"], fontSize=8, leading=10,
        ))
        ss.add(ParagraphStyle(
            name="CellBold", parent=ss["BodyText"], fontSize=8, leading=10,
            fontName="Helvetica-Bold", textColor=colors.whitesmoke,
        ))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _read_summary(self):
        path = f"{REPORTS_PATH}/executive_summary.json"
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {}

    def _read_csv(self, name):
        p = f"{REPORTS_PATH}/{name}"
        return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

    def _round_numeric(self, df, ndigits=3):
        df = df.copy()
        for c in df.select_dtypes(include="number").columns:
            df[c] = df[c].round(ndigits)
        return df

    def _table(self, df, col_widths=None, wrap_cols=None):
        """Build a styled Table. wrap_cols = list of column names to wrap as Paragraph."""
        df = df.copy()
        wrap_cols = set(wrap_cols or [])

        # Build header row
        header = [Paragraph(str(c), self.styles["CellBold"]) for c in df.columns]

        # Build body rows
        body = []
        for _, row in df.iterrows():
            cells = []
            for c in df.columns:
                val = row[c]
                if pd.isna(val):
                    val = ""
                if c in wrap_cols:
                    cells.append(Paragraph(str(val), self.styles["Cell"]))
                else:
                    cells.append(Paragraph(str(val), self.styles["Cell"]))
            body.append(cells)

        t = Table([header] + body, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8),
            ("GRID",       (0, 0), (-1, -1), 0.25, colors.HexColor("#999999")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, LIGHT]),
            ("VALIGN",     (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING",   (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
        ]))
        return t

    def _image(self, name, width=14 * cm):
        path = f"{FIGURES_PATH}/{name}"
        if os.path.exists(path):
            return Image(path, width=width, height=width * 0.6, kind="proportional")
        return None

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------
    def _cover(self):
        story = []
        story.append(Spacer(1, 6 * cm))
        story.append(Paragraph("HR Analytics", self.styles["CoverTitle"]))
        story.append(Paragraph("Final Report", self.styles["CoverTitle"]))
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(
            "Predictive Workforce Insights &amp; Strategic Recommendations",
            self.styles["CoverSub"],
        ))
        story.append(Spacer(1, 4 * cm))
        story.append(Paragraph(
            f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d')}",
            ParagraphStyle(name="cd", fontSize=10, alignment=TA_CENTER, textColor=GREY),
        ))
        story.append(Paragraph(
            "<b>Dataset:</b> IBM HR Employee Attrition (1,470 employees)",
            ParagraphStyle(name="cs", fontSize=10, alignment=TA_CENTER, textColor=GREY),
        ))
        story.append(PageBreak())
        return story

    def _executive_summary(self, summary):
        story = [Paragraph("1. Executive Summary", self.styles["H1"])]

        if summary:
            labels = {
                "total_employees":      "Total Employees",
                "attrition_rate":       "Attrition Rate (%)",
                "avg_risk":             "Average Risk Score",
                "high_risk_count":      "High-Risk Count (>0.6)",
                "avg_monthly_income":   "Avg Monthly Income (USD)",
                "avg_age":              "Average Age",
                "avg_tenure_years":     "Average Tenure (years)",
            }
            rows = [["Metric", "Value"]]
            for k, label in labels.items():
                if k in summary and summary[k] is not None:
                    rows.append([label, str(summary[k])])
            t = Table(rows, colWidths=[8 * cm, 5 * cm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR",  (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",   (0, 0), (-1, -1), 10),
                ("GRID",       (0, 0), (-1, -1), 0.25, colors.HexColor("#999999")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, LIGHT]),
                ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING",  (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING",   (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph(
            "This study uses the IBM HR Attrition dataset to identify the drivers of "
            "employee turnover and to segment the workforce into actionable personas. "
            "A Spark-based pipeline ingests the raw data, generates engineered features, "
            "and feeds three classifiers to predict attrition risk per employee. "
            "Cluster analysis groups employees into personas, and a Power BI dashboard "
            "exposes the results to managers.",
            self.styles["Body2"],
        ))

        # Key findings bullet list
        story.append(Paragraph("<b>Key findings</b>", self.styles["H2"]))
        bullets = [
            "Overall attrition rate is around 16%, concentrated in Sales and R&amp;D.",
            "OverTime is the single strongest predictor — overtime workers leave roughly 3x more often.",
            "Lower MonthlyIncome and shorter tenure both raise attrition risk significantly.",
            "Gradient Boosting reaches the best ROC-AUC (~0.80) among the three classifiers.",
            "Three clear personas emerge: Loyal Long-Term, Average Workforce, and High Attrition Risk.",
        ]
        for b in bullets:
            story.append(Paragraph(f"• {b}", self.styles["Body2"]))

        return story

    def _methodology(self):
        story = [PageBreak(), Paragraph("2. Methodology", self.styles["H1"])]

        story.append(Paragraph("2.1 Data preparation", self.styles["H2"]))
        story.append(Paragraph(
            "The raw CSV is loaded with PySpark and cleaned: constant columns "
            "(EmployeeCount, Over18, StandardHours) are dropped, missing numeric values "
            "are imputed with the column median, and missing categorical values are "
            "imputed with the mode. Categorical features are label-encoded using "
            "Spark <i>StringIndexer</i>; numeric features are standard-scaled. "
            "All three Spark paradigms are demonstrated in code: DataFrame API for "
            "transformations, Spark SQL for analytical queries, and RDD-style aggregations.",
            self.styles["Body2"],
        ))

        story.append(Paragraph("2.2 Feature engineering", self.styles["H2"]))
        story.append(Paragraph(
            "Five domain features are added: <b>EngagementScore</b> (mean of "
            "JobSatisfaction, EnvironmentSatisfaction, JobInvolvement, WorkLifeBalance), "
            "<b>TenureRatio</b> (YearsAtCompany / TotalWorkingYears), "
            "<b>PromotionVelocity</b> (JobLevel / YearsAtCompany), "
            "<b>IncomeDeviation</b> (MonthlyIncome relative to peer-group mean), and "
            "<b>LoyaltyIndex</b> (YearsAtCompany / NumCompaniesWorked).",
            self.styles["Body2"],
        ))

        story.append(Paragraph("2.3 Modelling approach", self.styles["H2"]))
        story.append(Paragraph(
            "Three classifiers — Logistic Regression, Random Forest, Gradient Boosting — "
            "are compared with stratified 5-fold cross-validation. Class imbalance "
            "(~16% positive class) is handled via <i>class_weight='balanced'</i>. "
            "The model with the highest ROC-AUC is selected and used to score every "
            "employee, producing a probability-based <i>risk_score</i> and a "
            "Low/Medium/High <i>risk_band</i>.",
            self.styles["Body2"],
        ))

        story.append(Paragraph("2.4 Performance modelling", self.styles["H2"]))
        story.append(Paragraph(
            "A composite PerfScore is built from EngagementScore, PerformanceRating, "
            "LoyaltyIndex, TenureRatio and PromotionVelocity. Three regressors predict "
            "PerfScore (Linear, Random Forest, Gradient Boosting) and three classifiers "
            "predict the original PerformanceRating, evaluated by RMSE and weighted F1.",
            self.styles["Body2"],
        ))

        story.append(Paragraph("2.5 Workforce segmentation", self.styles["H2"]))
        story.append(Paragraph(
            "Employees are clustered with K-Means using the engineered features plus "
            "the predicted risk_score. The optimal K is selected by silhouette score "
            "across K = 2..10. Each cluster is profiled and assigned a persona label "
            "(High Attrition Risk, Highly Engaged, Loyal Long-Term, or Average).",
            self.styles["Body2"],
        ))

        return story

    def _eda(self):
        story = [PageBreak(), Paragraph("3. EDA Highlights", self.styles["H1"])]
        for name, caption in [
            ("attrition_distribution.png",
             "Attrition is imbalanced — about 16% of employees leave."),
            ("overtime_vs_attrition.png",
             "OverTime is the strongest single predictor."),
            ("correlation_heatmap.png",
             "Correlation across all numeric features."),
        ]:
            img = self._image(name)
            if img is not None:
                story.append(KeepTogether([
                    img,
                    Paragraph(f"<i>{caption}</i>", self.styles["Body2"]),
                    Spacer(1, 0.3 * cm),
                ]))
        return story

    def _modelling(self):
        story = [PageBreak(), Paragraph("4. Modelling Results", self.styles["H1"])]

        # 4.1 Attrition models
        story.append(Paragraph("4.1 Attrition model comparison", self.styles["H2"]))
        cmp = self._read_csv("attrition_models_comparison.csv")
        if not cmp.empty:
            cmp = self._round_numeric(cmp, 4)
            story.append(self._table(cmp))
        story.append(Spacer(1, 0.4 * cm))

        # 4.2 Top 10 drivers
        story.append(Paragraph("4.2 Top 10 attrition drivers", self.styles["H2"]))
        top = self._read_csv("top_10_features.csv")
        if not top.empty:
            # Normalize header
            if "Unnamed: 0" in top.columns:
                top.columns = ["feature", "importance"]
            elif top.shape[1] == 2 and top.columns[0].startswith("feature") is False \
                    and "feature" not in top.columns:
                top.columns = ["feature", "importance"]
            if "importance" in top.columns:
                top["importance"] = top["importance"].astype(float).round(4)
            story.append(self._table(top, col_widths=[7 * cm, 4 * cm]))
        story.append(Spacer(1, 0.4 * cm))

        # 4.3 Performance models
        story.append(Paragraph("4.3 Performance models", self.styles["H2"]))
        reg = self._read_csv("performance_regression_comparison.csv")
        if not reg.empty:
            reg = self._round_numeric(reg, 4)
            story.append(Paragraph("Regression (target: PerfScore)", self.styles["Body2"]))
            story.append(self._table(reg, col_widths=[7 * cm, 4 * cm]))
            story.append(Spacer(1, 0.3 * cm))
        clf = self._read_csv("performance_classification_comparison.csv")
        if not clf.empty:
            clf = self._round_numeric(clf, 4)
            story.append(Paragraph("Classification (target: PerformanceRating)",
                                   self.styles["Body2"]))
            story.append(self._table(clf, col_widths=[7 * cm, 4 * cm]))

        return story

    def _segmentation(self):
        story = [PageBreak(), Paragraph("5. Workforce Segmentation", self.styles["H1"])]
        personas = self._read_csv("personas.csv")
        if not personas.empty:
            personas = self._round_numeric(personas, 3)
            # Reorder so Persona is right after Cluster if present
            cols = personas.columns.tolist()
            if "Persona" in cols:
                ordered = ["Cluster", "Persona"] + [c for c in cols
                                                    if c not in ("Cluster", "Persona")]
                personas = personas[[c for c in ordered if c in cols]]
            story.append(self._table(personas))
            story.append(Spacer(1, 0.4 * cm))
            story.append(Paragraph(
                "Each cluster represents a distinct workforce profile. The "
                "<i>High Attrition Risk</i> group warrants the most urgent action; "
                "the <i>Loyal Long-Term</i> group needs protection from stagnation; "
                "the <i>Average Workforce</i> majority benefits from standard "
                "engagement practices.",
                self.styles["Body2"],
            ))
        return story

    def _recommendations(self):
        story = [PageBreak(), Paragraph("6. Strategic Recommendations", self.styles["H1"])]

        # 6.1 Top 20
        story.append(Paragraph("6.1 Top 20 high-risk employees", self.styles["H2"]))
        top20 = self._read_csv("top20_high_risk.csv")
        if not top20.empty:
            cols = [c for c in ["EmployeeNumber", "Department", "JobRole",
                                "risk_score", "recommendation"] if c in top20.columns]
            sub = top20[cols].copy()
            if "risk_score" in sub.columns:
                sub["risk_score"] = sub["risk_score"].round(3)
            # Word-wrap the recommendation column
            story.append(self._table(
                sub,
                col_widths=[2.2 * cm, 2.5 * cm, 3 * cm, 1.8 * cm, 7.5 * cm],
                wrap_cols=["recommendation", "JobRole", "Department"],
            ))
        story.append(Spacer(1, 0.4 * cm))

        # 6.2 Persona strategies
        story.append(Paragraph("6.2 Persona strategies", self.styles["H2"]))
        ps = self._read_csv("persona_strategies.csv")
        if not ps.empty:
            story.append(self._table(
                ps,
                col_widths=[1.5 * cm, 4 * cm, 2 * cm, 9.5 * cm],
                wrap_cols=["Strategy", "Persona"],
            ))
        story.append(Spacer(1, 0.4 * cm))

        # 6.3 Department recommendations
        story.append(Paragraph("6.3 Department-level recommendations", self.styles["H2"]))
        dr = self._read_csv("department_recommendations.csv")
        if not dr.empty:
            dr = self._round_numeric(dr, 2)
            story.append(self._table(
                dr,
                col_widths=None,
                wrap_cols=["recommendation", "Department"],
            ))
        return story

    def _conclusion(self):
        return [
            Spacer(1, 0.6 * cm),
            Paragraph("7. Conclusion", self.styles["H1"]),
            Paragraph(
                "The combined predictive model and clustering analysis allow HR "
                "to direct retention investment where it has the highest expected "
                "return: high-risk employees in overtime-heavy roles within the "
                "Sales and R&amp;D departments. The Power BI dashboard packages the "
                "results so individual managers can act on them at the team level — "
                "reviewing the top-N risk list for their function, tracking persona "
                "mix, and following the strategy guidance per cluster.",
                self.styles["Body2"],
            ),
            Paragraph(
                "Future work could include cost-sensitive thresholding (turning the "
                "risk score into expected dollar loss), survival analysis for "
                "time-to-attrition, and a feedback loop where manager actions are "
                "logged and used to retrain the model.",
                self.styles["Body2"],
            ),
        ]

    # ------------------------------------------------------------------
    def build(self):
        doc = SimpleDocTemplate(
            REPORT_PATH, pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
            title="HR Analytics — Final Report",
            author="HR Analytics Team",
        )

        summary = self._read_summary()

        story = []
        story += self._cover()
        story += self._executive_summary(summary)
        story += self._methodology()
        story += self._eda()
        story += self._modelling()
        story += self._segmentation()
        story += self._recommendations()
        story += self._conclusion()

        doc.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
        print(f"[saved] PDF report → {REPORT_PATH}")


if __name__ == "__main__":
    ReportGenerator().build()
