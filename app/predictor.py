from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


class SmartLenderPredictor:
	"""Load the trained loan approval model and generate predictions."""

	def __init__(self, model_dir: Path | None = None) -> None:
		self.base_dir = Path(__file__).resolve().parent.parent
		self.model_dir = (
			Path(model_dir) if model_dir is not None else self.base_dir / "models"
		)

		self.model: Any = None
		self.feature_names: list[str] = []
		self.model_metadata: dict[str, Any] = {}
		self.scaler: Any = None

		self.load_artifacts()

	def load_artifacts(self) -> None:
		"""Load model, features, metadata, and optional scaler from disk."""

		model_path = self.model_dir / "best_model.pkl"
		feature_names_path = self.model_dir / "feature_names.pkl"
		metadata_path = self.model_dir / "model_metadata.json"
		scaler_path = self.model_dir / "scaler.pkl"

		missing_files = [
			str(path.name)
			for path in (model_path, feature_names_path, metadata_path)
			if not path.exists()
		]
		if missing_files:
			raise FileNotFoundError(
				f"Missing required model artifact(s): {', '.join(missing_files)}"
			)

		self.model = joblib.load(model_path)
		self.feature_names = list(joblib.load(feature_names_path))

		with metadata_path.open("r", encoding="utf-8") as file:
			self.model_metadata = json.load(file)

		if scaler_path.exists():
			self.scaler = joblib.load(scaler_path)
		else:
			self.scaler = None

	def preprocess_input(self, input_data: dict[str, Any]) -> pd.DataFrame:
		"""Validate and convert input data into a model-ready DataFrame."""

		if not isinstance(input_data, dict):
			raise TypeError("input_data must be a dictionary.")

		if not self.feature_names:
			raise RuntimeError("Feature names are not loaded.")

		unexpected_features = sorted(set(input_data) - set(self.feature_names))
		if unexpected_features:
			raise ValueError(
				f"Unexpected feature(s) provided: {', '.join(unexpected_features)}"
			)

		missing_features = [
			feature for feature in self.feature_names if feature not in input_data
		]
		if missing_features:
			raise ValueError(
				f"Missing required feature(s): {', '.join(missing_features)}"
			)

		ordered_input = {feature: input_data[feature] for feature in self.feature_names}
		features_df = pd.DataFrame([ordered_input], columns=self.feature_names)

		if self.scaler is not None:
			scaled_values = self.scaler.transform(features_df)
			features_df = pd.DataFrame(scaled_values, columns=self.feature_names)

		return features_df

	def predict(self, input_data: dict[str, Any]) -> dict[str, Any]:
		"""Return the predicted loan approval result."""

		processed_input = self.preprocess_input(input_data)

		try:
			raw_prediction = self.model.predict(processed_input)[0]
		except Exception as exc:
			raise RuntimeError("Model prediction failed.") from exc

		try:
			prediction_value = int(raw_prediction)
		except (TypeError, ValueError) as exc:
			raise RuntimeError("Model returned a non-integer prediction value.") from exc

		if prediction_value not in (0, 1):
			raise RuntimeError("Model prediction must be either 0 or 1.")

		result = "Loan Approved" if prediction_value == 1 else "Loan Not Approved"
		return {
			"prediction": prediction_value,
			"result": result,
		}
