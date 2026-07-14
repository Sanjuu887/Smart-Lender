import random
from datetime import datetime
from io import BytesIO
from typing import Any

from flask import Flask, Response, render_template, request, session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import DEBUG, SECRET_KEY
from app.predictor import SmartLenderPredictor


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DEBUG"] = DEBUG

predictor = SmartLenderPredictor()

_NUMERIC_FIELDS = {
    "ApplicantIncome": int,
    "CoapplicantIncome": float,
    "LoanAmount": float,
    "Loan_Amount_Term": float,
    "Credit_History": float,
}

_REQUIRED_FORM_FIELDS = (
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
    "Credit_History",
    "Gender",
    "Married",
    "Dependents",
    "Education",
    "Self_Employed",
    "Property_Area",
)


def _convert_numeric(value: str, field_name: str, converter: type) -> int | float:
    try:
        return converter(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid value for {field_name}.") from exc


def _build_prediction_input(form_data: Any) -> dict[str, int | float]:
    missing_fields = [field for field in _REQUIRED_FORM_FIELDS if not form_data.get(field)]
    if missing_fields:
        raise ValueError(f"Missing required form field(s): {', '.join(missing_fields)}")

    gender = form_data.get("Gender", "").strip().lower()
    married = form_data.get("Married", "").strip().lower()
    dependents = form_data.get("Dependents", "").strip()
    education = form_data.get("Education", "").strip().lower()
    self_employed = form_data.get("Self_Employed", "").strip().lower()
    property_area = form_data.get("Property_Area", "").strip().lower()

    feature_mapping: dict[str, int | float] = {}
    for field_name, converter in _NUMERIC_FIELDS.items():
        feature_mapping[field_name] = _convert_numeric(
            form_data.get(field_name, ""),
            field_name,
            converter,
        )

    feature_mapping.update(
        {
            "Gender_Female": 1 if gender == "female" else 0,
            "Gender_Male": 1 if gender == "male" else 0,
            "Married_No": 1 if married == "no" else 0,
            "Married_Yes": 1 if married == "yes" else 0,
            "Dependents_0": 1 if dependents == "0" else 0,
            "Dependents_1": 1 if dependents == "1" else 0,
            "Dependents_2": 1 if dependents == "2" else 0,
            "Dependents_3+": 1 if dependents == "3+" else 0,
            "Education_Graduate": 1 if education == "graduate" else 0,
            "Education_Not Graduate": 1 if education == "not graduate" else 0,
            "Self_Employed_No": 1 if self_employed == "no" else 0,
            "Self_Employed_Yes": 1 if self_employed == "yes" else 0,
            "Property_Area_Rural": 1 if property_area == "rural" else 0,
            "Property_Area_Semiurban": 1 if property_area == "semiurban" else 0,
            "Property_Area_Urban": 1 if property_area == "urban" else 0,
        }
    )

    return feature_mapping


def _build_submission_summary(form_data: Any) -> dict[str, str]:
    return {
        "Applicant Name": form_data.get("ApplicantName", "").strip(),
        "Email Address": form_data.get("EmailAddress", "").strip(),
        "Phone Number": form_data.get("PhoneNumber", "").strip(),
        "Age": form_data.get("Age", "").strip(),
        "Gender": form_data.get("Gender", "").strip(),
        "Marital Status": form_data.get("Married", "").strip(),
        "Education": form_data.get("Education", "").strip(),
        "Self Employment": form_data.get("Self_Employed", "").strip(),
        "Property Area": form_data.get("Property_Area", "").strip(),
        "Dependents": form_data.get("Dependents", "").strip(),
        "Applicant Income": form_data.get("ApplicantIncome", "").strip(),
        "Coapplicant Income": form_data.get("CoapplicantIncome", "").strip(),
        "Loan Amount": form_data.get("LoanAmount", "").strip(),
        "Loan Term": form_data.get("Loan_Amount_Term", "").strip(),
        "Credit History": "Good" if form_data.get("Credit_History", "").strip() == "1" else "Poor",
    }


def _format_currency(val) -> str:
    try:
        numeric_val = float(val)
        return f"₹{int(numeric_val):,}"
    except (ValueError, TypeError):
        return str(val)


def _format_loan_amount_val(val) -> str:
    try:
        numeric_val = float(val)
        val_in_rs = int(numeric_val * 1000)
        return f"{int(numeric_val) if numeric_val.is_integer() else numeric_val} (₹{val_in_rs:,})"
    except (ValueError, TypeError):
        return str(val)


def _format_currency_pdf(val) -> str:
    try:
        numeric_val = float(val)
        return f"Rs. {int(numeric_val):,}"
    except (ValueError, TypeError):
        return str(val)


def _format_loan_amount_val_pdf(val) -> str:
    try:
        numeric_val = float(val)
        val_in_rs = int(numeric_val * 1000)
        return f"{int(numeric_val) if numeric_val.is_integer() else numeric_val} (Rs. {val_in_rs:,})"
    except (ValueError, TypeError):
        return str(val)


def _build_reasons(submitted_values: dict[str, str], prediction_value: int) -> list[str]:
    try:
        applicant_income = float(submitted_values.get("Applicant Income", 0) or 0)
        coapplicant_income = float(submitted_values.get("Coapplicant Income", 0) or 0)
        loan_amount = float(submitted_values.get("Loan Amount", 0) or 0)
        loan_term = float(submitted_values.get("Loan Term", 0) or 0)
        credit_history = submitted_values.get("Credit History", "Good")
        dependents = submitted_values.get("Dependents", "0")
        self_employed = submitted_values.get("Self Employment", "No").strip().lower()
    except (ValueError, TypeError):
        applicant_income = 0.0
        coapplicant_income = 0.0
        loan_amount = 0.0
        loan_term = 0.0
        credit_history = "Good"
        dependents = "0"
        self_employed = "no"

    total_income = applicant_income + coapplicant_income
    reasons = []

    if prediction_value == 1:
        if credit_history == "Good":
            reasons.append("Good credit history")
        if applicant_income >= 35000:
            reasons.append("Stable monthly income")
        if loan_amount <= 200:
            reasons.append("Reasonable loan amount")
        if coapplicant_income > 0:
            reasons.append("Lower financial risk")
        if loan_term <= 360:
            reasons.append("Suitable repayment period")
        if not reasons:
            reasons = ["Good credit history", "Stable monthly income", "Reasonable loan amount"]
    else:
        if credit_history == "Poor":
            reasons.append("Credit history increases lending risk")
        if total_income > 0 and (loan_amount * 1000 / total_income) >= 5.0:
            reasons.append("Requested loan amount is high compared to income")
        if applicant_income < 35000:
            reasons.append("Monthly income may not sufficiently support repayment")
        if dependents != "0":
            reasons.append("Financial obligations increase repayment risk")
        if self_employed == "yes":
            reasons.append("Employment profile requires additional verification")
        if not reasons:
            default_reasons = []
            if credit_history == "Poor":
                default_reasons.append("Credit history increases lending risk")
            if applicant_income < 35000:
                default_reasons.append("Monthly income may not sufficiently support repayment")
            if not default_reasons:
                default_reasons.append("Applicant profile metrics deviate from standard model criteria")
            reasons = default_reasons

    return reasons


def _build_suggestions(prediction_value: int) -> list[str]:
    if prediction_value == 1:
        return [
            "Maintain good repayment behaviour.",
            "Submit all required documents.",
            "Continue maintaining your credit history.",
        ]
    else:
        return [
            "Improve your credit history.",
            "Increase monthly income.",
            "Reduce requested loan amount.",
            "Apply with a co-applicant.",
            "Verify application details before reapplying.",
        ]


def _generate_result_pdf(
    *,
    prediction_label: str,
    prediction_value: int,
    submitted_values: dict[str, str],
    prediction_time: datetime,
    reference_number: str,
) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=34 * mm,
        bottomMargin=20 * mm,
    )

    available_width = A4[0] - 36 * mm
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, textColor=colors.HexColor("#0f172a"), leading=24, spaceAfter=8))
    styles.add(ParagraphStyle(name="SectionHeading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, textColor=colors.HexColor("#1d4ed8"), leading=16, spaceBefore=14, spaceAfter=8, keepWithNext=1))
    styles.add(ParagraphStyle(name="BodyTextSmall", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13, textColor=colors.HexColor("#334155")))
    styles.add(ParagraphStyle(name="BodyTextMuted", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.6, leading=12, textColor=colors.HexColor("#64748b")))

    story: list[Any] = []
    story.append(Paragraph("Smart Lender Decision Report", styles["ReportTitle"]))
    story.append(Paragraph("AI Powered Loan Approval System", styles["BodyTextMuted"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<b>Reference Number:</b> {reference_number}", styles["BodyTextSmall"]))
    story.append(Paragraph(f"<b>Generation Date &amp; Time:</b> {prediction_time.strftime('%d %b %Y, %I:%M %p')}", styles["BodyTextSmall"]))
    story.append(Spacer(1, 10))

    col1_width = 80 * mm
    col2_width = available_width - col1_width

    def _table_from_items(title: str, items: list[tuple[str, str]]) -> None:
        story.append(Paragraph(title, styles["SectionHeading"]))
        rows = [[Paragraph("<b>Field</b>", styles["BodyTextSmall"]), Paragraph("<b>Value</b>", styles["BodyTextSmall"] )]]
        for label, value in items:
            rows.append([Paragraph(label, styles["BodyTextSmall"]), Paragraph(value or "-", styles["BodyTextSmall"])])
        table = Table(rows, colWidths=[col1_width, col2_width], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("LEADING", (0, 0), (-1, -1), 12),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 10))

    _table_from_items(
        "Applicant Information",
        [
            ("Applicant Name", submitted_values.get("Applicant Name", "")),
            ("Email Address", submitted_values.get("Email Address", "")),
            ("Phone Number", submitted_values.get("Phone Number", "")),
            ("Age", submitted_values.get("Age", "")),
            ("Gender", submitted_values.get("Gender", "")),
            ("Marital Status", submitted_values.get("Marital Status", "")),
            ("Education", submitted_values.get("Education", "")),
            ("Self Employment", submitted_values.get("Self Employment", "")),
            ("Property Area", submitted_values.get("Property Area", "")),
            ("Dependents", submitted_values.get("Dependents", "")),
        ],
    )

    _table_from_items(
        "Financial Information",
        [
            ("Applicant Monthly Income", _format_currency_pdf(submitted_values.get("Applicant Income", ""))),
            ("Co-applicant Monthly Income", _format_currency_pdf(submitted_values.get("Coapplicant Income", ""))),
            ("Loan Amount", _format_loan_amount_val_pdf(submitted_values.get("Loan Amount", ""))),
            ("Loan Term", f"{submitted_values.get('Loan Term', '')} Months" if submitted_values.get('Loan Term') else "-"),
            ("Credit History", "Good Credit History (Paid previous loans on time)" if submitted_values.get("Credit History") == "Good" or submitted_values.get("Credit History") == "1" else "Poor Credit History (Previous repayment issues)"),
        ],
    )

    status_color = "#22c55e" if prediction_value == 1 else "#ef4444"
    status_label = "Approved" if prediction_value == 1 else "Needs Review"
    _table_from_items(
        "Prediction Summary",
        [
            ("Prediction", f"<b><font color='{status_color}'>{prediction_label}</font></b>"),
            ("Application Status", f"<b><font color='{status_color}'>{status_label}</font></b>"),
            ("Reference Number", reference_number),
            ("Prediction Time", prediction_time.strftime('%d %b %Y, %I:%M %p')),
        ],
    )

    # === PAGE BREAK ===
    story.append(PageBreak())

    story.append(Paragraph("Explanation &amp; Guidance", styles["ReportTitle"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Why this result?", styles["SectionHeading"]))
    reasons_list = _build_reasons(submitted_values, prediction_value)
    prefix_check = "<font color='#22c55e'>&#10004;</font>" if prediction_value == 1 else "<font color='#ef4444'>&#10004;</font>"
    reasons_html = "<br/>".join([f"{prefix_check} {r}" for r in reasons_list])
    story.append(Paragraph(reasons_html, styles["BodyTextSmall"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Suggestions", styles["SectionHeading"]))
    suggestions_list = _build_suggestions(prediction_value)
    suggestions_html = "<br/>".join([f"• {s}" for s in suggestions_list])
    story.append(Paragraph(suggestions_html, styles["BodyTextSmall"]))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Model Information", styles["SectionHeading"]))
    model_rows = [
        [Paragraph("<b>Model Used</b>", styles["BodyTextSmall"]), Paragraph("XGBoost", styles["BodyTextSmall"])],
        [Paragraph("<b>Training Accuracy</b>", styles["BodyTextSmall"]), Paragraph("98.8%", styles["BodyTextSmall"])],
        [Paragraph("<b>Testing Accuracy</b>", styles["BodyTextSmall"]), Paragraph("75.6%", styles["BodyTextSmall"])],
    ]
    model_table = Table(model_rows, colWidths=[65 * mm, available_width - 65 * mm])
    model_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(model_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph("The above accuracy values represent the performance of the trained model during evaluation.", styles["BodyTextMuted"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Disclaimer", styles["SectionHeading"]))
    disclaimer_text = (
        "This prediction is generated using a trained Machine Learning model. "
        "The reasons and suggestions displayed are general lending guidelines generated from the submitted application details. "
        "They are not the exact internal reasoning used by the Machine Learning model. "
        "Final loan approval always depends on the financial institution."
    )
    story.append(Paragraph(disclaimer_text, styles["BodyTextMuted"]))

    def _draw_header_footer(canvas, _doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#0f172a"))
        canvas.rect(0, A4[1] - 28 * mm, A4[0], 28 * mm, stroke=0, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(18 * mm, A4[1] - 16 * mm, "Smart Lender")
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(A4[0] - 18 * mm, A4[1] - 16 * mm, "AI Powered Loan Approval System")
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.setFont("Helvetica", 8)
        canvas.drawString(18 * mm, 10 * mm, f"Ref: {reference_number} | Saved on: {prediction_time.strftime('%d %b %Y, %I:%M %p')}")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    document.build(story, onFirstPage=_draw_header_footer, onLaterPages=_draw_header_footer)
    buffer.seek(0)
    return buffer.getvalue()


@app.route("/", methods=["GET"])
def index() -> str:
    return render_template("index.html")


@app.route("/predict", methods=["GET"])
def predict_form() -> str:
    return render_template("predict.html")


@app.route("/about", methods=["GET"])
def about_page() -> str:
    return render_template("about.html")


@app.route("/contact", methods=["GET"])
def contact_page() -> str:
    return render_template("contact.html")


@app.route("/predict", methods=["POST"])
def predict_loan() -> str:
    try:
        feature_mapping = _build_prediction_input(request.form)
        result = predictor.predict(feature_mapping)
        submitted_values = _build_submission_summary(request.form)
        prediction_time = datetime.now()
        reference_number = f"SL-2026-{random.randint(100000, 999999)}"
        session["smart_lender_report"] = {
            "prediction": int(result["prediction"]),
            "result": result["result"],
            "submitted_values": submitted_values,
            "prediction_time": prediction_time.isoformat(),
            "reference_number": reference_number,
        }
        return render_template(
            "result.html",
            prediction=result["prediction"],
            result=result["result"],
            submitted_values=submitted_values,
            prediction_time=prediction_time,
            reference_number=reference_number,
            reasons=_build_reasons(submitted_values, int(result["prediction"])),
            suggestions=_build_suggestions(int(result["prediction"])),
        )
    except ValueError as exc:
        return render_template("error.html", error_message=str(exc)), 400
    except RuntimeError as exc:
        return render_template("error.html", error_message=str(exc)), 500
    except Exception:
        return render_template(
            "error.html",
            error_message="An unexpected error occurred while processing the request.",
        ), 500


@app.route("/download-report", methods=["GET"])
def download_report() -> Response:
    report_data = session.get("smart_lender_report")
    if not report_data:
        return render_template("error.html", error_message="No report is available for download."), 404

    prediction_time = datetime.fromisoformat(report_data["prediction_time"])
    reference_number = report_data.get("reference_number") or f"SL-2026-{random.randint(100000, 999999)}"
    pdf_bytes = _generate_result_pdf(
        prediction_label=report_data["result"],
        prediction_value=int(report_data["prediction"]),
        submitted_values=report_data.get("submitted_values", {}),
        prediction_time=prediction_time,
        reference_number=reference_number,
    )
    filename = f"smart-lender-report-{prediction_time.strftime('%Y%m%d-%H%M%S')}.pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.errorhandler(404)
def not_found(_error: Exception) -> tuple[str, int]:
    return render_template("error.html", error_message="Page not found."), 404


@app.errorhandler(500)
def server_error(_error: Exception) -> tuple[str, int]:
    return render_template(
        "error.html",
        error_message="An internal server error occurred.",
    ), 500


if __name__ == "__main__":
    app.run(debug=True)
