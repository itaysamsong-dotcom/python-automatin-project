from time import time_ns
from uuid import uuid4

from src.models.types import BillingAddress, RegisterDetails

BILLING_ADDRESS = BillingAddress(
    country="Israel",
    postal_code="12345",
    street="Domenick Road",
    state="State",
    city="Reingerchester",
    house_num="10",
)

REGISTER_USERS = {
    "correct_user_field": RegisterDetails(
        email=f"customer-{time_ns()}@example.com",
        password=f"I{uuid4()}",
        first_name="Itay",
        last_name="Hakim",
        birth_date="2005-09-04",
        phone="0521234567",
        **BILLING_ADDRESS.__dict__,
    )
}

