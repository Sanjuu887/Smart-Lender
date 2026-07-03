(() => {
  const form = document.getElementById('predictForm');

  if (!form) {
    return;
  }

  const submitButton = document.getElementById('predictBtn');
  const buttonText = submitButton?.querySelector('.btn-text');
  const spinner = submitButton?.querySelector('.spinner-border');
  const overlay = document.getElementById('predictionOverlay');
  const summary = document.getElementById('validationSummary');
  const creditError = document.getElementById('creditHistoryError');

  const fields = {
    ApplicantName: document.getElementById('ApplicantName'),
    EmailAddress: document.getElementById('EmailAddress'),
    PhoneNumber: document.getElementById('PhoneNumber'),
    Age: document.getElementById('Age'),
    Gender: document.getElementById('Gender'),
    Married: document.getElementById('Married'),
    ApplicantIncome: document.getElementById('ApplicantIncome'),
    CoapplicantIncome: document.getElementById('CoapplicantIncome'),
    LoanAmount: document.getElementById('LoanAmount'),
    Loan_Amount_Term: document.getElementById('Loan_Amount_Term'),
    Education: document.getElementById('Education'),
    Self_Employed: document.getElementById('Self_Employed'),
    Dependents: document.getElementById('Dependents'),
    Property_Area: document.getElementById('Property_Area'),
    confirmationCheck: document.getElementById('confirmationCheck'),
  };

  const radioButtons = Array.from(form.querySelectorAll('input[name="Credit_History"]'));

  const showSummary = (messages) => {
    if (!summary) {
      return;
    }

    const items = messages.map((message) => `<li>${message}</li>`).join('');
    summary.innerHTML = `<strong>Please review the highlighted fields.</strong><ul>${items}</ul>`;
    summary.classList.remove('d-none');
  };

  const hideSummary = () => {
    summary?.classList.add('d-none');
    if (summary) {
      summary.innerHTML = '';
    }
  };

  const markInvalid = (field, message) => {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    const feedback = field.parentElement?.querySelector('.invalid-feedback');
    if (feedback && message) {
      feedback.textContent = message;
    }
  };

  const markValid = (field) => {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
  };

  const value = (field) => (field?.value ?? '').trim();

  const validateText = (field, requiredMessage) => {
    if (!field) return true;
    if (!value(field)) {
      markInvalid(field, requiredMessage);
      return false;
    }
    markValid(field);
    return true;
  };

  const validateEmail = (field) => {
    if (!field) return true;
    const emailValue = value(field);
    const isValid = emailValue && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailValue);
    if (!isValid) {
      markInvalid(field, 'Please enter a valid email.');
      return false;
    }
    markValid(field);
    return true;
  };

  const validatePhone = (field) => {
    if (!field) return true;
    const phoneValue = value(field);
    if (!phoneValue) {
      markInvalid(field, 'Please enter a valid 10-digit phone number.');
      return false;
    }
    const isValid = /^\d{10}$/.test(phoneValue);
    if (!isValid) {
      markInvalid(field, 'Please enter a valid 10-digit phone number. E.g. 9876543210');
      return false;
    }
    markValid(field);
    return true;
  };

  const validateAge = (field) => {
    if (!field) return true;
    const ageValue = value(field);
    if (!ageValue) {
      markInvalid(field, 'Please enter a valid age between 18 and 70.');
      return false;
    }
    const ageNumber = Number(ageValue);
    const isValid = Number.isInteger(ageNumber) && ageNumber >= 18 && ageNumber <= 70;
    if (!isValid) {
      markInvalid(field, 'Please enter a valid age between 18 and 70.');
      return false;
    }
    markValid(field);
    return true;
  };

  const validateNumber = (field, options) => {
    if (!field) return true;
    const numberValue = value(field);
    if (!numberValue) {
      markInvalid(field, options.requiredMessage);
      return false;
    }
    const parsedValue = Number(numberValue);
    const min = options.min ?? 0;
    const isValid = Number.isFinite(parsedValue) && (options.strict ? parsedValue > min : parsedValue >= min);
    if (!isValid) {
      markInvalid(field, options.invalidMessage);
      return false;
    }
    markValid(field);
    return true;
  };

  const validateSelect = (field, requiredMessage) => {
    if (!field) return true;
    if (!value(field)) {
      markInvalid(field, requiredMessage);
      return false;
    }
    markValid(field);
    return true;
  };

  const validateCreditHistory = () => {
    const selected = radioButtons.find((radio) => radio.checked);
    if (!selected) {
      creditError?.classList.remove('d-none');
      return false;
    }
    creditError?.classList.add('d-none');
    radioButtons.forEach((radio) => {
      radio.classList.remove('is-invalid');
      radio.classList.add('is-valid');
    });
    return true;
  };

  const clearCreditState = () => {
    creditError?.classList.add('d-none');
    radioButtons.forEach((radio) => radio.classList.remove('is-valid', 'is-invalid'));
  };

  const bindLiveValidation = () => {
    fields.ApplicantName?.addEventListener('input', () => validateText(fields.ApplicantName, 'Please enter your full name.'));
    fields.ApplicantName?.addEventListener('blur', () => validateText(fields.ApplicantName, 'Please enter your full name.'));

    fields.EmailAddress?.addEventListener('input', () => validateEmail(fields.EmailAddress));
    fields.EmailAddress?.addEventListener('blur', () => validateEmail(fields.EmailAddress));

    fields.PhoneNumber?.addEventListener('input', () => validatePhone(fields.PhoneNumber));
    fields.PhoneNumber?.addEventListener('blur', () => validatePhone(fields.PhoneNumber));

    fields.Age?.addEventListener('input', () => validateAge(fields.Age));
    fields.Age?.addEventListener('blur', () => validateAge(fields.Age));

    fields.Gender?.addEventListener('change', () => validateSelect(fields.Gender, 'Please select a gender.'));
    fields.Married?.addEventListener('change', () => validateSelect(fields.Married, 'Please select the marital status.'));
    fields.ApplicantIncome?.addEventListener('input', () => validateNumber(fields.ApplicantIncome, {
      requiredMessage: 'Applicant income is required.',
      invalidMessage: 'Applicant income must be positive and greater than zero.',
      min: 0,
      strict: true,
    }));
    fields.ApplicantIncome?.addEventListener('blur', () => validateNumber(fields.ApplicantIncome, {
      requiredMessage: 'Applicant income is required.',
      invalidMessage: 'Applicant income must be positive and greater than zero.',
      min: 0,
      strict: true,
    }));

    fields.CoapplicantIncome?.addEventListener('input', () => validateNumber(fields.CoapplicantIncome, {
      requiredMessage: 'Coapplicant income is required.',
      invalidMessage: 'Co-applicant income must be 0 or greater.',
      min: 0,
      strict: false,
    }));
    fields.CoapplicantIncome?.addEventListener('blur', () => validateNumber(fields.CoapplicantIncome, {
      requiredMessage: 'Coapplicant income is required.',
      invalidMessage: 'Co-applicant income must be 0 or greater.',
      min: 0,
      strict: false,
    }));

    fields.LoanAmount?.addEventListener('input', () => validateNumber(fields.LoanAmount, {
      requiredMessage: 'Loan amount is required.',
      invalidMessage: 'Loan amount must be positive and greater than zero.',
      min: 0,
      strict: true,
    }));
    fields.LoanAmount?.addEventListener('blur', () => validateNumber(fields.LoanAmount, {
      requiredMessage: 'Loan amount is required.',
      invalidMessage: 'Loan amount must be positive and greater than zero.',
      min: 0,
      strict: true,
    }));

    fields.Loan_Amount_Term?.addEventListener('change', () => validateSelect(fields.Loan_Amount_Term, 'Loan term is required.'));
    fields.Education?.addEventListener('change', () => validateSelect(fields.Education, 'Please select education.'));
    fields.Self_Employed?.addEventListener('change', () => validateSelect(fields.Self_Employed, 'Please select employment status.'));
    fields.Dependents?.addEventListener('change', () => validateSelect(fields.Dependents, 'Please select dependents.'));
    fields.Property_Area?.addEventListener('change', () => validateSelect(fields.Property_Area, 'Please select property area.'));
    fields.confirmationCheck?.addEventListener('change', () => {
      if (fields.confirmationCheck.checked) {
        fields.confirmationCheck.classList.remove('is-invalid');
        fields.confirmationCheck.classList.add('is-valid');
      } else {
        fields.confirmationCheck.classList.remove('is-valid');
      }
    });

    radioButtons.forEach((radio) => {
      radio.addEventListener('change', validateCreditHistory);
    });
  };

  const setLoadingState = () => {
    if (!submitButton) {
      return;
    }
    submitButton.disabled = true;
    submitButton.setAttribute('aria-busy', 'true');
    spinner?.classList.remove('d-none');
    if (buttonText) {
      buttonText.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Predicting...';
    }
    overlay?.classList.remove('d-none');
  };

  const clearLoadingState = () => {
    if (!submitButton) {
      return;
    }
    submitButton.disabled = false;
    submitButton.removeAttribute('aria-busy');
    spinner?.classList.add('d-none');
    if (buttonText) {
      buttonText.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles me-2"></i>Predict Loan Approval';
    }
    overlay?.classList.add('d-none');
  };

  // Initialize tooltips
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach((tooltipTriggerEl) => {
      new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }

  bindLiveValidation();
  clearLoadingState();

  form.addEventListener('submit', (event) => {
    hideSummary();

    const messages = [];
    if (!validateText(fields.ApplicantName, 'Please enter your full name.')) messages.push('Please enter your full name.');
    if (!validateEmail(fields.EmailAddress)) messages.push('Please enter a valid email.');
    if (!validatePhone(fields.PhoneNumber)) messages.push('Please enter a valid 10-digit phone number.');
    if (!validateAge(fields.Age)) messages.push('Please enter a valid age between 18 and 70.');
    if (!validateSelect(fields.Gender, 'Please select a gender.')) messages.push('Please select a gender.');
    if (!validateSelect(fields.Married, 'Please select the marital status.')) messages.push('Please select the marital status.');
    if (!validateNumber(fields.ApplicantIncome, {
      requiredMessage: 'Applicant income is required.',
      invalidMessage: 'Applicant income must be positive and greater than zero.',
      min: 0,
      strict: true,
    })) messages.push('Applicant income must be positive and greater than zero.');
    if (!validateNumber(fields.CoapplicantIncome, {
      requiredMessage: 'Coapplicant income is required.',
      invalidMessage: 'Co-applicant income must be 0 or greater.',
      min: 0,
      strict: false,
    })) messages.push('Coapplicant income must be 0 or greater.');
    if (!validateNumber(fields.LoanAmount, {
      requiredMessage: 'Loan amount is required.',
      invalidMessage: 'Loan amount must be positive and greater than zero.',
      min: 0,
      strict: true,
    })) messages.push('Loan amount must be positive and greater than zero.');
    if (!validateSelect(fields.Loan_Amount_Term, 'Loan term is required.')) messages.push('Loan term is required.');
    if (!validateSelect(fields.Education, 'Please select education.')) messages.push('Please select education.');
    if (!validateSelect(fields.Self_Employed, 'Please select employment status.')) messages.push('Please select employment status.');
    if (!validateSelect(fields.Dependents, 'Please select dependents.')) messages.push('Please select dependents.');
    if (!validateSelect(fields.Property_Area, 'Please select property area.')) messages.push('Please select property area.');
    if (!validateCreditHistory()) messages.push('Please select a credit history option.');

    const validConfirmation = fields.confirmationCheck?.checked;
    if (!validConfirmation && fields.confirmationCheck) {
      fields.confirmationCheck.classList.add('is-invalid');
      messages.push('Please confirm the information before submitting.');
    }

    if (messages.length > 0) {
      event.preventDefault();
      showSummary(messages);
      const firstInvalid = form.querySelector('.is-invalid');
      firstInvalid?.focus({ preventScroll: false });
      return;
    }

    event.preventDefault();
    setLoadingState();
    window.setTimeout(() => form.submit(), 120);
  });

  form.addEventListener('reset', () => {
    window.setTimeout(() => {
      hideSummary();
      clearLoadingState();
      form.querySelectorAll('.is-valid, .is-invalid').forEach((element) => {
        element.classList.remove('is-valid', 'is-invalid');
      });
      clearCreditState();
      if (fields.confirmationCheck) {
        fields.confirmationCheck.checked = false;
      }
    }, 0);
  });

  window.addEventListener('pageshow', () => {
    clearLoadingState();
  });

  // Initialize Bootstrap Tooltips
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
})();
