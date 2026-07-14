# Smart Lender

## Project Overview

Smart Lender is a web-based loan approval prediction assistant. It evaluates whether a loan application is likely to be approved or rejected based on criteria like applicant income, credit history, loan amount, and marital status. The system is designed to provide quick first-level screening assistance in a professional, responsive bank-style interface.

 Deployment link : https://smart-lender-ai.onrender.com/

## Features

- **Loan Approval Prediction:** Real-time calculation of loan eligibility using a machine learning model.
- **Applicant Information & Financial Summary:** Dynamic form interface capture for marital status, dependents, education, income metrics, and requested loan terms.
- **Rule-based Explanation:** Displays localized primary reasons explaining why the check approved or needs review.
- **Downloadable PDF Report:** Generates a professional 2-page summary PDF showing the inputs, result, and suggestions.
- **Responsive Layout:** A clean, optimized CSS interface designed to fit desktop, tablet, and mobile screens.


- <img width="912" height="425" alt="Screenshot 2026-07-13 143409" src="https://github.com/user-attachments/assets/82d3ac5f-e380-4704-87d0-0860cd9da98c" />


## Machine Learning Model

The application uses a trained tree-based model:
- **Model Deployed:** XGBoost
- **Training Accuracy:** 98.8%
- **Testing Accuracy:** 75.6%
- **Why XGBoost:** Bypasses linear bias assumptions that penalize high-income applicants, resulting in highly stable predictions and realistic loan approval logic compared to other classifiers.

### Models Evaluated during Development
- Logistic Regression (Rejects high-income outliers due to negative coefficient weight bias)
- Decision Tree
- Random Forest
- Gradient Boosting
- KNN
- XGBoost (Selected)

## Project Structure

```text
Smart-Lender/
├── app/
│   ├── app.py              # Main Flask application with API endpoints and PDF generator
│   ├── config.py           # Configuration variables and security parameters
│   ├── predictor.py        # Model loading, validation, and preprocessing pipeline
│   ├── static/
│   │   ├── css/            # CSS styling sheets for web screens
│   │   └── js/             # Javascript validation and form interactions
│   └── templates/          # HTML layout templates
├── data/
│   └── loan_prediction.csv # Dataset used for training and cross-validation
├── models/
│   ├── best_model.pkl      # Saved XGBoost classifier model
│   ├── scaler.pkl          # Saved StandardScaler configuration
│   ├── feature_names.pkl   # List of 20 feature matrix inputs
│   └── model_metadata.json # Metadata with model statistics and parameters
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation
└── .gitignore              # Ignored file configurations
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Sanjuu887/Smart-Lender
   cd Smart-Lender
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # On Windows:
   .\.venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

Start the Flask application:
```bash
python -m app.app
```
Then visit `http://127.0.0.1:5000` in your web browser.


<img width="1918" height="1026" alt="Screenshot 2026-07-13 162450" src="https://github.com/user-attachments/assets/0e8dab81-bfdd-44e7-9340-e706f5b56d5c" />




## Technologies Used

- **Backend:** Flask, Python
- **Machine Learning:** XGBoost, scikit-learn, Pandas, NumPy, Joblib
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, FontAwesome
- **PDF Export:** ReportLab

## Future Improvements

- Add user authentication and record storage.
- Support multi-model testing toggles inside a control panel.
- Increase prediction feature counts (e.g. debt-to-income ratio, active credit accounts).

## Contact

- **Email:** sanjaydharmireddi3@gmail.com
- **LinkedIn:** [Sanjay Dharmireddi on LinkedIn](https://www.linkedin.com/in/sanjay-dharmireddi-33b648348/)

