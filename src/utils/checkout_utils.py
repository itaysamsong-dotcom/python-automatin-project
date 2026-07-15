import re
from urllib.parse import urlparse

from playwright.sync_api import Page, expect

from src.config.routes import BASE_URLS, URL_PATHS
from src.mapping.selectors import CHECKOUT_LABELS, CHECKOUT_SELECTORS, PRODUCT_SELECTORS
from src.models.types import BillingAddress, InvoiceResponse, LoginDetails, Product
from src.utils.common_utils import endpoint
from src.utils.login_utils import login_user
from src.utils.register_utils import fill_billing_address


def add_items_to_cart(page: Page, product_id: str, product: Product) -> None:
    expect(page).to_have_url(endpoint(f"{URL_PATHS['product']}/{product_id}"))
    expect(page.get_by_test_id(PRODUCT_SELECTORS["product_name"])).to_have_text(product.name)
    expect(page.get_by_test_id(PRODUCT_SELECTORS["unit_price"])).to_have_text(str(product.unit_price))
    expect(page.get_by_test_id(PRODUCT_SELECTORS["quantity"])).to_have_value("1")
    page.get_by_test_id(PRODUCT_SELECTORS["increase_quantity"]).click()
    expect(page.get_by_test_id(PRODUCT_SELECTORS["quantity"])).to_have_value("2")

    with page.expect_response(_is_add_item_response, timeout=30_000) as response_info:
        page.get_by_test_id(PRODUCT_SELECTORS["add_to_cart"]).click()

    response = response_info.value
    if not response.ok:
        raise RuntimeError(
            f"Adding the product to the cart failed with status {response.status}: {response.text()}"
        )


def _is_add_item_response(response) -> bool:
    request_url = urlparse(response.url)
    api_url = urlparse(BASE_URLS["api"])
    return (
        response.request.method == "POST"
        and (request_url.scheme, request_url.netloc) == (api_url.scheme, api_url.netloc)
        and re.fullmatch(r"/carts/[^/]+", request_url.path) is not None
    )


def assert_cart_total_not_exceeds(page: Page, budget_per_item: float, items_count: int) -> None:
    page.goto(URL_PATHS["checkout"])
    expect(page).to_have_url(endpoint(URL_PATHS["checkout"]))

    cart_total = page.get_by_test_id(CHECKOUT_SELECTORS["cart_total"])
    expect(cart_total).to_be_visible()

    displayed_total = cart_total.inner_text()
    numeric_total = re.sub(r"[^\d.,-]", "", displayed_total).replace(",", ".")
    try:
        total = float(numeric_total)
    except ValueError as error:
        raise AssertionError(f'Could not parse the cart total from "{displayed_total}".') from error

    maximum_total = budget_per_item * items_count
    page.screenshot(path="test-results/cart-total.png", full_page=True)
    assert total <= maximum_total, f"Cart total {total} exceeds the allowed total {maximum_total}."


def proceed_to_checkout(page: Page, login_details: LoginDetails, billing_address: BillingAddress) -> None:
    page.goto(URL_PATHS["checkout"])
    expect(page).to_have_url(endpoint(URL_PATHS["checkout"]))
    page.get_by_test_id(CHECKOUT_SELECTORS["proceed_to_login"]).click()
    login_user(page, login_details, wait_for_auth=True)
    with page.expect_response(
        lambda response: response.request.method == "GET"
        and urlparse(response.url).netloc == urlparse(BASE_URLS["api"]).netloc
        and urlparse(response.url).path == "/users/me"
        and response.ok,
        timeout=30_000,
    ):
        page.get_by_test_id(CHECKOUT_SELECTORS["proceed_to_billing_address"]).click()
    page.wait_for_load_state("networkidle", timeout=30_000)
    fill_billing_address(page, billing_address)
    page.get_by_test_id(CHECKOUT_SELECTORS["proceed_to_payment"]).click()
    page.get_by_test_id(CHECKOUT_SELECTORS["payment_method"]).select_option(
        label=CHECKOUT_LABELS["cash_payment_method"]
    )
    page.get_by_test_id(CHECKOUT_SELECTORS["finish"]).click()
    expect(page.get_by_test_id(CHECKOUT_SELECTORS["payment_success_message"])).to_be_visible()


def check_product_creation(page: Page) -> None:
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and response.url == f"{BASE_URLS['api']}{URL_PATHS['invoices']}",
        timeout=30_000,
    ) as response_info:
        page.get_by_test_id(CHECKOUT_SELECTORS["finish"]).click()

    response = response_info.value
    if not response.ok:
        raise RuntimeError(
            f"Invoice request failed with status {response.status}: {response.text()}"
        )
    invoice: InvoiceResponse = response.json()
    expect(page.locator(CHECKOUT_SELECTORS["invoice_number"])).to_have_text(invoice["invoice_number"])
