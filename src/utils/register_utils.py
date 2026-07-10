from playwright.sync_api import Page

from src.mapping.selectors import (
    BILLING_ADDRESS_FIELD_SELECTORS,
    REGISTER_SELECTORS,
    REGISTER_TEXT_FIELD_SELECTORS,
)
from src.models.types import BillingAddress, RegisterDetails
from src.utils.common_utils import fill_text_fields
from src.utils.login_utils import fill_mail_and_password


def fill_billing_address(page: Page, billing_address: BillingAddress) -> None:
    fill_text_fields(page, billing_address, BILLING_ADDRESS_FIELD_SELECTORS)
    page.get_by_test_id(REGISTER_SELECTORS["country"]).select_option(billing_address.country)


def fill_register_details(page: Page, register_details: RegisterDetails) -> None:
    fill_mail_and_password(page, register_details)
    fill_text_fields(page, register_details, REGISTER_TEXT_FIELD_SELECTORS)
    fill_billing_address(page, register_details)
    page.get_by_test_id(REGISTER_SELECTORS["register_btn"]).dblclick()

