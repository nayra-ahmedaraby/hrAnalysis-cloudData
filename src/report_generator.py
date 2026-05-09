# Member 5 — Final PDF Report
# Builds docs/final_report.pdf from the CSVs and figures created upstream.

import os
import json
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak,
)

from src.config import REPORTS_PATH, FIGURES_PATH, DOCS_PATH


REPORT_PATH = f"{DOCS_PATH}/final_report.pdf"


class ReportGenerator:

    def __init__(self):
        os.makedirs(DOCS_PATH, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name="H", fontName="Helvetica-Bold", fontSize=15,
            spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#1a3d6d"),
        ))
        self.styles.add(ParagraphStyle(
            name="SubH", fontName="Helvetica-Bold", fontSize=11,
            spaceBefore=6, spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            name="Body2", fontName="Helvetica", fontSize=10, leading=13, spaceAfter=4,
        ))

    def _read_summary(self):
        path = f"{REPORTS_PATH}/executive_summary.json"
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {}

    def _read_csv(self, name):
        p = f"{REPORTS_PATH}/{name}"
        return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

    def _table(self, df, max_rows=10, max_cols=6):
        df = df.head(max_rows).iloc[:, :max_cols]
        data = [df.columns.tolist()] + df.astype(str).values.tolist()
        t = Table(data, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3d6d")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 8),
            ("GRID",       (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        return t

    def _image(self, name, width=15 * cm):
        path = f"{FIGURES_PATH}/{name}"
        if os.path.exists(path):
            return Image(path, width=width, height=width * 0.6, kind="proportional")
        return None

    def build(self):
        doc = SimpleDocTemplate(
            REPORT_PATH, pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        )
        story = []

        # Title
        story.append(Paragraph("HR Analytics — Final Report", self.styles["Title"]))
        story.append(Paragraph("Predictive Workforce Insights & Recommendations",
                               self.styles["Body2"]))
        story.append(Spacer(1, 0.5 * cm))

        # 1. Executive summary
        summary = self._read_summary()
        story.append(Paragraph("1. Executive Summary", self.styles["H"]))
        if summary:
            rows = [["KPI", "Value"]] + [[k.replace("_", " ").title(), str(v)]
                                         for k, v in summary.items()]
            t = Table(rows, colWidths=[7 * cm, 5 * cm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3d6d")),
                ("TEXTCOLOR",  (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID",       (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ]))
            story.append(t)
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(
            "This report covers an HR analytics study on the IBM HR Attrition dataset. "
            "The pipeline uses Spark for preprocessing, scikit-learn for predictive models, "
            "and a Power BI dashboard for visualization.",
            self.styles["Body2"],
        ))

        # 2. Methodology
        story.append(PageBreak())
        story.append(Paragraph("2. Methodology", self.styles["H"]))
        story.append(Paragraph(
            "Data is loaded with Spark (DataFrame, SQL, RDD), cleaned, encoded, and "
            "scaled. Five engineered features (EngagementScore, TenureRatio, "
            "PromotionVelocity, IncomeDeviation, LoyaltyIndex) are added. "
            "Three classifiers (Logistic Regression, Random Forest, Gradient Boosting) "
            "are compared with 5-fold cross-validation; class imbalance is handled "
            "with class_weight='balanced'. Performance is modelled both as "
            "regression (RMSE) and classification (F1). K-Means clustering "
            "groups employees into personas using silhouette score.",
            self.styles["Body2"],
        ))

        # 3. EDA
        story.append(PageBreak())
        story.append(Paragraph("3. EDA Highlights", self.styles["H"]))
        for name, caption in [
            ("attrition_distribution.png", "Attrition is imbalanced (~16%)."),
            ("overtime_vs_attrition.png", "OverTime is the strongest single driver."),
            ("correlation_heatmap.png", "Numeric correlations across features."),
        ]:
            img = self._image(name)
            if img is not None:
                story.append(img)
                story.append(Paragraph(caption, self.styles["Body2"]))
                story.append(Spacer(1, 0.2 * cm))

        # 4. Models
        story.append(PageBreak())
        story.append(Paragraph("4. Modelling Results", self.styles["H"]))

        story.append(Paragraph("4.1 Attrition models", self.styles["SubH"]))
        cmp = self._read_csv("attrition_models_comparison.csv")
        if not cmp.empty:
            story.append(self._table(cmp))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("4.2 Top 10 attrition drivers", self.styles["SubH"]))
        top = self._read_csv("top_10_features.csv")
        if not top.empty:
            story.append(self._table(top))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("4.3 Performance models", self.styles["SubH"]))
        reg = self._read_csv("performance_regression_comparison.csv")
        if not reg.empty:
            story.append(self._table(reg))
        clf = self._read_csv("performance_classification_comparison.csv")
        if not clf.empty:
            story.append(Spacer(1, 0.2 * cm))
            story.append(self._table(clf))

        # 5. Personas
        story.append(PageBreak())
        story.append(Paragraph("5. Workforce Segmentation", self.styles["H"]))
        personas = self._read_csv("personas.csv")
        if not personas.empty:
            story.append(self._table(personas, max_rows=8))

        # 6. Recommendations
        story.append(PageBreak())
        story.append(Paragraph("6. Strategic Recommendations", self.styles["H"]))
        story.append(Paragraph("6.1 Top 20 high-risk employees", self.styles["SubH"]))
        top20 = self._read_csv("top20_high_risk.csv")
        if not top20.empty:
            cols = [c for c in ["EmployeeNumber", "Department", "JobRole",
                                "risk_score", "recommendation"] if c in top20.columns]
            story.append(self._table(top20[cols], max_rows=20, max_cols=5))

        story.append(Paragraph("6.2 Persona strategies", self.styles["SubH"]))
        ps = self._read_csv("persona_strategies.csv")
        if not ps.empty:
            story.append(self._table(ps))

        story.append(Paragraph("6.3 Department recommendations", self.styles["SubH"]))
        dr = self._read_csv("department_recommendations.csv")
        if not dr.empty:
            story.append(self._table(dr))

        # 7. Conclusion
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph("7. Conclusion", self.styles["H"]))
        story.append(Paragraph(
            "The combined predictive model and clustering let HR target retention "
            "spend on the segments that matter most: high-risk employees in "
            "overtime-heavy roles and the Sales / R&D departments. The Power BI "
            "dashboard turns these results into something managers can act on.",
            self.styles["Body2"],
        ))

        doc.build(story)
        print(f"[saved] PDF report → {REPORT_PATH}")


if __name__ == "__main__":
    ReportGenerator().build()
