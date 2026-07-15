from playwright.sync_api import Page, expect

from src.config.routes import BASE_URLS, URL_PATHS
from src.mapping.selectors import CHECKOUT_LABELS, CHECKOUT_SELECTORS, PRODUCT_SELECTORS
from src.models.types import BillingAddress, InvoiceResponse, LoginDetails, Product
from src.utils.common_utils import endpoint
from src.utils.login_utils import login_user
from src.utils.register_utils import fill_billing_address


def add_items_to_cart(page: Page, product_id: str, product: Product) -> None:
    expect(page).to_have_url(endpoint(f"{URL_PATHS['product']}/{product_id}"))
    page.get_by_test_id(PRODUCT_SELECTORS["add_to_cart"]).click()
    expect(page.get_by_test_id(PRODUCT_SELECTORS["product_name"])).to_have_text(product.name)
    expect(page.get_by_test_id(PRODUCT_SELECTORS["unit_price"])).to_have_text(str(product.unit_price))
    expect(page.get_by_test_id(PRODUCT_SELECTORS["quantity"])).to_have_value("1")
    page.get_by_test_id(PRODUCT_SELECTORS["increase_quantity"]).click()
    expect(page.get_by_test_id(PRODUCT_SELECTORS["quantity"])).to_have_value("2")


def proceed_to_checkout(page: Page, login_details: LoginDetails, billing_address: BillingAddress) -> None:
    page.goto(URL_PATHS["checkout"])
    expect(page).to_have_url(endpoint(URL_PATHS["checkout"]))
    page.get_by_test_id(CHECKOUT_SELECTORS["proceed_to_login"]).click()
    login_user(page, login_details)
    page.get_by_test_id(CHECKOUT_SELECTORS["proceed_to_billing_address"]).click()
    fill_billing_address(page, billing_address)
    page.get_by_test_id(CHECKOUT_SELECTORS["proceed_to_payment"]).click()
    page.get_by_test_id(CHECKOUT_SELECTORS["payment_method"]).select_option(
        label=CHECKOUT_LABELS["cash_payment_method"]
    )


def check_product_creation(page: Page) -> None:
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and response.url == f"{BASE_URLS['api']}{URL_PATHS['invoices']}"
    ) as response_info:
        page.get_by_test_id(CHECKOUT_SELECTORS["finish"]).click()

    response = response_info.value
    if not response.ok:
        raise RuntimeError(f"Invoice request failed with status {response.status}.")
    invoice: InvoiceResponse = response.json()
    expect(page.get_by_test_id(CHECKOUT_SELECTORS["payment_success_message"])).to_be_visible()
    expect(page.locator(CHECKOUT_SELECTORS["invoice_number"])).to_have_text(invoice["invoice_number"])
