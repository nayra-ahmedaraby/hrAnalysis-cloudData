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
from reportlab.platypus.flowables import HRFlowable

from src.config import REPORTS_PATH, FIGURES_PATH, DOCS_PATH


REPORT_PATH = f"{DOCS_PATH}/final_report.pdf"

NAVY    = colors.HexColor("#1a3d6d")
NAVY2   = colors.HexColor("#2a5a9b")
GREY    = colors.HexColor("#555555")
LIGHT   = colors.HexColor("#f3f5f9")
ACCENT  = colors.HexColor("#e07a5f")   # warm accent (used for cover bar + emphasis)
RED     = colors.HexColor("#c0392b")   # high risk
AMBER   = colors.HexColor("#e67e22")   # medium risk
GREEN   = colors.HexColor("#27ae60")   # low risk


def _page_footer(canvas, doc):
    """Footer with page number and a thin separator line."""
    canvas.saveState()
    # thin separator line above footer
    canvas.setStrokeColor(colors.HexColor("#cccccc"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawString(2 * cm, 1 * cm, "HR Analytics — Final Report")
    canvas.drawRightString(A4[0] - 2 * cm, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()


def _cover_canvas(canvas, doc):
    """Special canvas for cover: full-width navy hero block at top + accent bar."""
    canvas.saveState()
    page_w, page_h = A4
    # Full-width navy block from top down to ~12 cm
    canvas.setFillColor(NAVY)
    canvas.rect(0, page_h - 12 * cm, page_w, 12 * cm, fill=1, stroke=0)
    # Accent bar at the bottom of the navy block
    canvas.setFillColor(ACCENT)
    canvas.rect(0, page_h - 12 * cm - 0.3 * cm, page_w, 0.3 * cm, fill=1, stroke=0)
    canvas.restoreState()


class ReportGenerator:

    def __init__(self):
        os.makedirs(DOCS_PATH, exist_ok=True)

        ss = getSampleStyleSheet()
        self.styles = ss

        ss.add(ParagraphStyle(
            name="CoverTitle", parent=ss["Title"], fontSize=32, leading=38,
            textColor=colors.whitesmoke, alignment=TA_CENTER, spaceAfter=10,
        ))
        ss.add(ParagraphStyle(
            name="CoverSub", parent=ss["BodyText"], fontSize=14,
            textColor=colors.whitesmoke, alignment=TA_CENTER, spaceAfter=20,
        ))
        ss.add(ParagraphStyle(
            name="CoverMeta", parent=ss["BodyText"], fontSize=11,
            textColor=GREY, alignment=TA_CENTER, leading=16,
        ))
        ss.add(ParagraphStyle(
            name="H1", parent=ss["Heading1"], fontSize=18, leading=22,
            textColor=NAVY, spaceBefore=12, spaceAfter=4,
        ))
        ss.add(ParagraphStyle(
            name="H2", parent=ss["Heading2"], fontSize=12, leading=16,
            textColor=NAVY2, spaceBefore=8, spaceAfter=4,
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
        ss.add(ParagraphStyle(
            name="KpiLabel", parent=ss["BodyText"], fontSize=9,
            textColor=GREY, alignment=TA_CENTER,
        ))
        ss.add(ParagraphStyle(
            name="KpiValue", parent=ss["BodyText"], fontSize=18,
            textColor=NAVY, alignment=TA_CENTER, fontName="Helvetica-Bold",
            leading=22,
        ))
        ss.add(ParagraphStyle(
            name="TocItem", parent=ss["BodyText"], fontSize=11, leading=18,
            textColor=NAVY,
        ))

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

    def _section_divider(self):
        return HRFlowable(
            width="100%", thickness=1.2, color=NAVY,
            spaceBefore=2, spaceAfter=8,
        )

    def _table(self, df, col_widths=None, wrap_cols=None, extra_styles=None):
        df = df.copy()
        wrap_cols = set(wrap_cols or [])

        header = [Paragraph(str(c), self.styles["CellBold"]) for c in df.columns]
        body = []
        for _, row in df.iterrows():
            cells = []
            for c in df.columns:
                val = row[c]
                if pd.isna(val):
                    val = ""
                cells.append(Paragraph(str(val), self.styles["Cell"]))
            body.append(cells)

        t = Table([header] + body, colWidths=col_widths, repeatRows=1)
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8),
            ("GRID",       (0, 0), (-1, -1), 0.25, colors.HexColor("#bbbbbb")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, LIGHT]),
            ("VALIGN",     (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING",   (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
        ]
        if extra_styles:
            style.extend(extra_styles)
        t.setStyle(TableStyle(style))
        return t

    def _image(self, name, width=11 * cm):
        path = f"{FIGURES_PATH}/{name}"
        if os.path.exists(path):
            return Image(path, width=width, height=width * 0.6, kind="proportional")
        return None

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------
    def _cover(self):
        story = []
        # Inside the navy hero block — vertical position controlled by spacers
        story.append(Spacer(1, 4 * cm))
        story.append(Paragraph("HR Analytics", self.styles["CoverTitle"]))
        story.append(Paragraph("Final Report", self.styles["CoverTitle"]))
        story.append(Spacer(1, 0.6 * cm))
        story.append(Paragraph(
            "Predictive Workforce Insights &amp; Strategic Recommendations",
            self.styles["CoverSub"],
        ))
        # Push past the navy block (~12cm) plus accent bar
        story.append(Spacer(1, 6 * cm))
        story.append(Paragraph(
            f"<b>Generated</b><br/>{datetime.now().strftime('%B %d, %Y')}",
            self.styles["CoverMeta"],
        ))
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(
            "<b>Dataset</b><br/>IBM HR Employee Attrition · 1,470 employees",
            self.styles["CoverMeta"],
        ))
        story.append(Spacer(1, 0.4 * cm))
        story.append(Paragraph(
            "<b>Pipeline</b><br/>PySpark · scikit-learn · K-Means · Power BI",
            self.styles["CoverMeta"],
        ))
        story.append(PageBreak())
        return story

    def _toc(self):
        items = [
            ("1.", "Executive Summary",        "3"),
            ("2.", "Methodology",              "4"),
            ("3.", "EDA Highlights",           "5"),
            ("4.", "Modelling Results",        "7"),
            ("5.", "Workforce Segmentation",   "8"),
            ("6.", "Strategic Recommendations","9"),
            ("7.", "Conclusion",               "10"),
        ]
        rows = [[
            Paragraph(f"<b>{num}</b>", self.styles["TocItem"]),
            Paragraph(title, self.styles["TocItem"]),
            Paragraph(page, self.styles["TocItem"]),
        ] for num, title, page in items]

        t = Table(rows, colWidths=[1 * cm, 12 * cm, 2 * cm])
        t.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
            ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",(0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ]))

        return [
            Paragraph("Table of Contents", self.styles["H1"]),
            self._section_divider(),
            Spacer(1, 0.4 * cm),
            t,
            PageBreak(),
        ]

    def _kpi_grid(self, summary):
        """Render KPIs as a 2-row x 4-col grid of large-value cards (8 cells)."""
        order = [
            ("total_employees",     "Total Employees",   "{}"),
            ("attrition_rate",      "Attrition Rate",    "{}%"),
            ("avg_risk",            "Avg Risk Score",    "{}"),
            ("high_risk_count",     "High-Risk (>0.6)",  "{}"),
            ("avg_monthly_income",  "Avg Income (USD)",  "{}"),
            ("avg_age",             "Avg Age",           "{}"),
            ("avg_tenure_years",    "Avg Tenure (yrs)",  "{}"),
        ]
        cards = []
        for key, label, fmt in order:
            v = summary.get(key)
            if v is None:
                continue
            cards.append((label, fmt.format(v)))

        # 8th card — Best Model highlight (always render as the closing card)
        cards.append(("Best Model", "GBT"))

        if not cards:
            return None

        per_row = 4
        rows = []
        for i in range(0, len(cards), per_row):
            chunk = cards[i:i + per_row]
            label_row = [Paragraph(lbl, self.styles["KpiLabel"]) for lbl, _ in chunk]
            value_row = [Paragraph(val, self.styles["KpiValue"]) for _, val in chunk]
            while len(label_row) < per_row:
                label_row.append("")
                value_row.append("")
            rows.append(value_row)
            rows.append(label_row)

        col_widths = [(17 / per_row) * cm] * per_row
        t = Table(rows, colWidths=col_widths)
        styles = [
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
        # alternate value-row backgrounds
        for r_idx in range(0, len(rows), 2):
            styles.append(("BACKGROUND", (0, r_idx), (-1, r_idx), LIGHT))
        # Highlight the Best Model card (last cell, last 2 rows) with accent
        last_row_idx_value = len(rows) - 2
        last_row_idx_label = len(rows) - 1
        styles.append(("BACKGROUND", (per_row - 1, last_row_idx_value),
                       (per_row - 1, last_row_idx_label), NAVY))
        t.setStyle(TableStyle(styles))

        # Re-style the Best Model cell text to white
        # (do this by overriding the paragraphs already in the table)
        # The two cells we need are at (per_row-1, last_row_idx_value) and (..., last_row_idx_label).
        white_value = ParagraphStyle(
            name="kw1", parent=self.styles["KpiValue"], textColor=colors.whitesmoke,
        )
        white_label = ParagraphStyle(
            name="kw2", parent=self.styles["KpiLabel"], textColor=colors.whitesmoke,
        )
        rows[last_row_idx_value][per_row - 1] = Paragraph("GBT", white_value)
        rows[last_row_idx_label][per_row - 1] = Paragraph("Best Model", white_label)
        # Rebuild the table with the updated cells
        t = Table(rows, colWidths=col_widths)
        t.setStyle(TableStyle(styles))
        return t

    def _executive_summary(self, summary):
        story = [
            Paragraph("1. Executive Summary", self.styles["H1"]),
            self._section_divider(),
        ]

        kpi = self._kpi_grid(summary)
        if kpi is not None:
            story.append(kpi)
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

        story.append(Paragraph("Key findings", self.styles["H2"]))
        bullets = [
            "Overall attrition rate is around 16%, concentrated in Sales and R&amp;D.",
            "OverTime is the single strongest predictor — overtime workers leave roughly 3x more often.",
            "Lower MonthlyIncome and shorter tenure both raise attrition risk significantly.",
            "Gradient Boosting reaches the best ROC-AUC (~0.80) among the three classifiers.",
            "Three clear personas emerge: Loyal Long-Term, Average Workforce, and High Attrition Risk.",
        ]
        for b in bullets:
            story.append(Paragraph(
                f'<font color="#e07a5f"><b>•</b></font>&nbsp;&nbsp;{b}',
                self.styles["Body2"],
            ))

        return story

    def _methodology(self):
        story = [
            PageBreak(),
            Paragraph("2. Methodology", self.styles["H1"]),
            self._section_divider(),
        ]

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
        story = [
            PageBreak(),
            Paragraph("3. EDA Highlights", self.styles["H1"]),
            self._section_divider(),
        ]

        story.append(Paragraph("3.1 Top 10 insights", self.styles["H2"]))
        insights = [
            "Overall attrition rate is around 16% — moderately high vs the typical 10% benchmark.",
            "OverTime is the strongest single driver — overtime employees leave roughly 3x more often.",
            "Sales has the highest department attrition rate, followed by R&amp;D and HR.",
            "Younger employees (under 30) leave more often than older cohorts.",
            "Lower MonthlyIncome correlates with higher attrition risk.",
            "Low JobSatisfaction strongly predicts leaving.",
            "WorkLifeBalance score of 1 has noticeably higher attrition than scores 2–4.",
            "Frequent business travelers leave more often than rare or non-travelers.",
            "Single employees show higher attrition than Married or Divorced.",
            "Long gaps since last promotion (more than 5 years) raise attrition risk.",
        ]
        for i, ins in enumerate(insights, 1):
            story.append(Paragraph(
                f'<font color="#1a3d6d"><b>{i:>2}.</b></font>&nbsp;&nbsp;{ins}',
                self.styles["Body2"],
            ))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("3.2 Visual highlights", self.styles["H2"]))
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
        story = [
            PageBreak(),
            Paragraph("4. Modelling Results", self.styles["H1"]),
            self._section_divider(),
        ]

        story.append(Paragraph("4.1 Attrition model comparison", self.styles["H2"]))
        cmp = self._read_csv("attrition_models_comparison.csv")
        if not cmp.empty:
            cmp = self._round_numeric(cmp, 4)
            story.append(self._table(cmp))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("4.2 Top 10 attrition drivers", self.styles["H2"]))
        top = self._read_csv("top_10_features.csv")
        if not top.empty:
            if "Unnamed: 0" in top.columns:
                top.columns = ["feature", "importance"]
            elif top.shape[1] == 2 and "feature" not in top.columns:
                top.columns = ["feature", "importance"]
            if "importance" in top.columns:
                top["importance"] = top["importance"].astype(float).round(4)
            story.append(self._table(top, col_widths=[7 * cm, 4 * cm]))
        story.append(Spacer(1, 0.4 * cm))

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

    def _persona_cards(self, personas):
        """3 horizontal colored cards summarising each persona."""
        # Map persona name → (header bg color, accent description)
        color_map = {
            "high attrition risk":      (RED,    "Critical priority"),
            "loyal long-term employees": (GREEN, "Medium priority"),
            "highly engaged":            (NAVY2, "High priority"),
            "average workforce":         (colors.HexColor("#7f8c8d"), "Standard priority"),
        }

        # Build one mini-table per persona, then put them side-by-side
        cards_row = []
        for _, row in personas.iterrows():
            persona_name = str(row.get("Persona", "Cluster"))
            key = persona_name.lower()
            color = next((c for k, (c, _) in color_map.items() if k in key), NAVY)
            priority = next((p for k, (_, p) in color_map.items() if k in key), "—")

            cluster_id = row.get("Cluster", "")
            # Pull a few headline numbers
            risk_v = row.get("risk_score", row.get("Risk", "—"))
            engage_v = row.get("EngagementScore", row.get("Engage", "—"))
            loyalty_v = row.get("LoyaltyIndex", row.get("Loyalty", "—"))

            inner_data = [
                [Paragraph(f'<font color="white"><b>Cluster {cluster_id}</b></font>',
                           self.styles["Body2"])],
                [Paragraph(f'<font color="white"><b>{persona_name}</b></font>',
                           self.styles["Body2"])],
                [Paragraph(f'<font color="white" size=8>{priority}</font>',
                           self.styles["Body2"])],
                [""],  # spacer
                [Paragraph(f"<b>Risk:</b> {risk_v}", self.styles["Body2"])],
                [Paragraph(f"<b>Engage:</b> {engage_v}", self.styles["Body2"])],
                [Paragraph(f"<b>Loyalty:</b> {loyalty_v}", self.styles["Body2"])],
            ]
            inner = Table(inner_data, colWidths=[5.2 * cm])
            inner.setStyle(TableStyle([
                # colored header band (first 3 rows)
                ("BACKGROUND",   (0, 0), (-1, 2), color),
                ("TEXTCOLOR",    (0, 0), (-1, 2), colors.whitesmoke),
                ("LEFTPADDING",  (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING",   (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
                ("LINEABOVE",    (0, 4), (-1, 4), 0.5, colors.HexColor("#dddddd")),
                ("BOX",          (0, 0), (-1, -1), 0.5, colors.HexColor("#bbbbbb")),
            ]))
            cards_row.append(inner)

        # Place all cards side-by-side in a single 1-row table
        if not cards_row:
            return None
        wrap = Table([cards_row], colWidths=[5.4 * cm] * len(cards_row))
        wrap.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        return wrap

    def _segmentation(self):
        story = [
            PageBreak(),
            Paragraph("5. Workforce Segmentation", self.styles["H1"]),
            self._section_divider(),
        ]
        personas = self._read_csv("personas.csv")
        if not personas.empty:
            personas = self._round_numeric(personas, 3)
            cols = personas.columns.tolist()
            if "Persona" in cols:
                ordered = ["Cluster", "Persona"] + [c for c in cols
                                                    if c not in ("Cluster", "Persona")]
                personas = personas[[c for c in ordered if c in cols]]

            # Visual persona cards (3 colored boxes)
            cards = self._persona_cards(personas)
            if cards is not None:
                story.append(cards)
                story.append(Spacer(1, 0.5 * cm))

            # Detailed table — same as before, with shortened numeric headers
            rename_map = {
                "EngagementScore":   "Engage",
                "TenureRatio":       "Tenure",
                "PromotionVelocity": "PromoVel",
                "IncomeDeviation":   "IncDev",
                "LoyaltyIndex":      "Loyalty",
                "risk_score":        "Risk",
            }
            personas_disp = personas.rename(columns=rename_map)

            widths = []
            for c in personas_disp.columns:
                if c == "Cluster":
                    widths.append(1.4 * cm)
                elif c == "Persona":
                    widths.append(4.2 * cm)
                else:
                    widths.append(1.7 * cm)

            story.append(Paragraph("Detailed cluster profile",
                                   self.styles["H2"]))
            story.append(self._table(
                personas_disp, col_widths=widths, wrap_cols=["Persona"],
            ))
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
        story = [
            PageBreak(),
            Paragraph("6. Strategic Recommendations", self.styles["H1"]),
            self._section_divider(),
        ]

        # 6.1 Top 20 — color the risk_score column based on band
        story.append(Paragraph("6.1 Top 20 high-risk employees", self.styles["H2"]))
        top20 = self._read_csv("top20_high_risk.csv")
        if not top20.empty:
            cols = [c for c in ["EmployeeNumber", "Department", "JobRole",
                                "risk_score", "recommendation"] if c in top20.columns]
            sub = top20[cols].copy()
            if "risk_score" in sub.columns:
                sub["risk_score"] = sub["risk_score"].round(3)

            # Build extra styles to color the risk_score cell
            extra = []
            if "risk_score" in sub.columns:
                rs_idx = sub.columns.get_loc("risk_score")
                for i, val in enumerate(sub["risk_score"].tolist(), start=1):
                    if val >= 0.6:
                        bg, fg = RED, colors.whitesmoke
                    elif val >= 0.3:
                        bg, fg = AMBER, colors.whitesmoke
                    else:
                        bg, fg = GREEN, colors.whitesmoke
                    extra.append(("BACKGROUND", (rs_idx, i), (rs_idx, i), bg))
                    extra.append(("TEXTCOLOR",  (rs_idx, i), (rs_idx, i), fg))
                    extra.append(("FONTNAME",   (rs_idx, i), (rs_idx, i), "Helvetica-Bold"))
                    extra.append(("ALIGN",      (rs_idx, i), (rs_idx, i), "CENTER"))

            story.append(self._table(
                sub,
                col_widths=[2.6 * cm, 2.4 * cm, 2.8 * cm, 1.7 * cm, 7.5 * cm],
                wrap_cols=["recommendation", "JobRole", "Department"],
                extra_styles=extra,
            ))
        story.append(Spacer(1, 0.4 * cm))

        # 6.2 Persona strategies — color Priority cells
        story.append(Paragraph("6.2 Persona strategies", self.styles["H2"]))
        ps = self._read_csv("persona_strategies.csv")
        if not ps.empty:
            extra = []
            if "Priority" in ps.columns:
                pri_idx = ps.columns.get_loc("Priority")
                for i, p in enumerate(ps["Priority"].tolist(), start=1):
                    s = str(p).lower()
                    if "critical" in s:
                        bg = RED
                    elif "high" in s:
                        bg = AMBER
                    elif "medium" in s:
                        bg = colors.HexColor("#f1c40f")
                    else:
                        bg = GREEN
                    extra.append(("BACKGROUND", (pri_idx, i), (pri_idx, i), bg))
                    extra.append(("TEXTCOLOR",  (pri_idx, i), (pri_idx, i), colors.whitesmoke))
                    extra.append(("FONTNAME",   (pri_idx, i), (pri_idx, i), "Helvetica-Bold"))
                    extra.append(("ALIGN",      (pri_idx, i), (pri_idx, i), "CENTER"))
            story.append(self._table(
                ps,
                col_widths=[1.5 * cm, 4 * cm, 2 * cm, 9.5 * cm],
                wrap_cols=["Strategy", "Persona"],
                extra_styles=extra,
            ))
        story.append(Spacer(1, 0.4 * cm))

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
            self._section_divider(),
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
        story += self._toc()
        story += self._executive_summary(summary)
        story += self._methodology()
        story += self._eda()
        story += self._modelling()
        story += self._segmentation()
        story += self._recommendations()
        story += self._conclusion()

        # Cover gets the navy hero canvas; later pages get the standard footer.
        doc.build(story, onFirstPage=_cover_canvas, onLaterPages=_page_footer)
        print(f"[saved] PDF report → {REPORT_PATH}")


if __name__ == "__main__":
    ReportGenerator().build()
