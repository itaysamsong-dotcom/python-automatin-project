from dataclasses import dataclass
from typing import Any, Optional, TypedDict


@dataclass(frozen=True)
class LoginDetails:
    email: str
    password: str


@dataclass(frozen=True)
class BillingAddress:
    country: str
    postal_code: str
    house_num: str
    street: str
    city: str
    state: str


@dataclass(frozen=True)
class RegisterDetails(LoginDetails, BillingAddress):
    first_name: str
    last_name: str
    birth_date: str
    phone: str


@dataclass(frozen=True)
class Product:
    name: str
    unit_price: float
    carbon_rating: str


class InvoiceResponse(TypedDict):
    billing_street: str
    billing_city: str
    billing_state: str
    billing_country: str
    billing_postal_code: str
    user_id: str
    invoice_date: str
    invoice_number: str
    id: str
    created_at: str
    subtotal: float
    total: float
    additional_discount_percentage: Optional[float]
    additional_discount_amount: float
    eco_discount_percentage: float
    eco_discount_amount: float


FieldMap = dict[str, str]
JsonObject = dict[str, Any]
