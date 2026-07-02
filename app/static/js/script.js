(() => {
	const form = document.getElementById("predictForm");

	if (!form) {
		return;
	}

	const predictButton = document.getElementById("predictBtn");
	const spinner = predictButton?.querySelector(".spinner-border");
	const buttonText = predictButton?.querySelector(".btn-text");
	let isSubmitting = false;
	const numericFields = [
		"ApplicantIncome",
		"CoapplicantIncome",
		"LoanAmount",
		"Loan_Amount_Term",
		"Credit_History",
	];

	const setFieldState = (field, isValid) => {
		if (isSubmitting) {
			event.preventDefault();
			return;
		}

		field.classList.toggle("is-valid", isValid);
		field.classList.toggle("is-invalid", !isValid);
	};

	const validateNumericField = (field) => {
		const value = field.value.trim();
		const isValid = value !== "" && !Number.isNaN(Number(value));
		setFieldState(field, isValid);
		return isValid;
	};

	const validateSelectField = (field) => {
		const isValid = field.value.trim() !== "";
		setFieldState(field, isValid);
		return isValid;
	};

	numericFields.forEach((fieldId) => {
		const field = document.getElementById(fieldId);
		if (!field) {
			return;
		}

		field.addEventListener("input", () => validateNumericField(field));
		field.addEventListener("blur", () => validateNumericField(field));
	});

	form.querySelectorAll("select, input").forEach((field) => {
		field.addEventListener("change", () => {
			if (field.tagName === "SELECT") {
				validateSelectField(field);
			}
		});
	});

	form.addEventListener("submit", (event) => {
		let isFormValid = true;

		numericFields.forEach((fieldId) => {
			const field = document.getElementById(fieldId);
			if (field && !validateNumericField(field)) {
				isFormValid = false;
			}
		});

		form.querySelectorAll("select[required], input[required]").forEach((field) => {
			if (field.tagName === "SELECT") {
				if (!validateSelectField(field)) {
					isFormValid = false;
				}
			} else if (field.type !== "number") {
				const hasValue = field.value.trim() !== "";
				setFieldState(field, hasValue);
				if (!hasValue) {
					isFormValid = false;
				}
			}
		});

		if (!form.checkValidity() || !isFormValid) {
			event.preventDefault();
			event.stopPropagation();
		} else if (predictButton && spinner && buttonText) {
			isSubmitting = true;
			predictButton.disabled = true;
			spinner.classList.remove("d-none");
			buttonText.textContent = "Processing...";
			predictButton.setAttribute("aria-busy", "true");
		}

		form.classList.add("was-validated");
	});
})();
