LOGIN_SELECTORS = {
    "email_input": "email",
    "password_input": "password",
    "login_submit_btn": "login-submit",
}
LOGIN_FIELD_SELECTORS = {
    "email": LOGIN_SELECTORS["email_input"],
    "password": LOGIN_SELECTORS["password_input"],
}

REGISTER_SELECTORS = {
    "first_name": "first-name",
    "last_name": "last-name",
    "birth_date": "dob",
    "country": "country",
    "postal_code": "postal_code",
    "house_num": "house_number",
    "phone": "phone",
    "street": "street",
    "city": "city",
    "state": "state",
    "register_btn": "register-submit",
}
REGISTER_TEXT_FIELD_SELECTORS = {
    key: REGISTER_SELECTORS[key] for key in ("first_name", "last_name", "birth_date", "phone")
}
BILLING_ADDRESS_FIELD_SELECTORS = {
    key: REGISTER_SELECTORS[key] for key in ("postal_code", "house_num", "street", "city", "state")
}

PRODUCT_SELECTORS = {
    "product_name": "product-name",
    "unit_price": "unit-price",
    "quantity": "quantity",
    "increase_quantity": "increase-quantity",
    "add_to_cart": "add-to-cart",
}

CHECKOUT_SELECTORS = {
    "continue_shopping": "continue-shopping",
    "payment_method": "payment-method",
    "proceed_to_login": "proceed-1",
    "proceed_to_billing_address": "proceed-2",
    "proceed_to_payment": "proceed-3",
    "finish": "finish",
    "invoice_number": "#order-confirmation span",
    "payment_success_message": "payment-success-message",
}
CHECKOUT_LABELS = {"cash_payment_method": "Cash on Delivery"}

TOAST_MESSAGE_SELECTORS = {"container": "#toast-container"}
ERROR_MESSAGE_SELECTORS = {"email": "email-error", "password": "password-error"}

