# Smart Lender

## Overview

Smart Lender is an end-to-end machine learning loan approval project built with Flask and scikit-learn. It uses a trained classification model to predict whether a loan application should be approved based on applicant and loan details.

## Features

- Clean Flask web interface
- Professional banking-style responsive UI
- Model-driven loan approval prediction
- Input validation and graceful error handling
- Optional scaler support for preprocessing consistency
- Reusable predictor class with persisted artifacts

## Project Structure

```text
Smart-Lender/
├── app/
│   ├── app.py
│   ├── config.py
│   └── predictor.py
├── data/
├── models/
├── notebooks/
├── static/
│   ├── css/
│   └── js/
├── templates/
├── requirements.txt
├── README.md
└── .gitignore
```

## Machine Learning Models Used

- Logistic Regression

## Technologies Used

- Python
- Flask
- Pandas
- NumPy
- scikit-learn
- Joblib
- Bootstrap 5

## Dataset

The project uses a loan prediction dataset stored in `data/`. It includes applicant information, loan details, and the target loan status used during model training.

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
python app/app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Screenshots

- Home page: placeholder
- Prediction form: placeholder
- Result page: placeholder

## Future Improvements

- Add user authentication and request history
- Extend model comparison and explainability
- Add deployment configuration for cloud hosting
- Add form analytics and monitoring

## Author

Sanju

## License

MIT License

