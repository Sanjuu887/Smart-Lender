from typing import Any

from flask import Flask, render_template, request

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


@app.route("/", methods=["GET"])
def index() -> str:
    return render_template("index.html")


@app.route("/predict", methods=["GET"])
def predict_form() -> str:
    return render_template("predict.html")


@app.route("/predict", methods=["POST"])
def predict_loan() -> str:
    try:
        feature_mapping = _build_prediction_input(request.form)
        result = predictor.predict(feature_mapping)
        return render_template(
            "result.html",
            prediction=result["prediction"],
            result=result["result"],
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
