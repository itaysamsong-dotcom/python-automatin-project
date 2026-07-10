import allure
import pytest
from playwright.sync_api import Page

from src.test_data.login_test_data import LOGIN_USERS
from src.test_data.register_test_data import BILLING_ADDRESS
from src.utils.checkout_utils import add_item_to_shopping_cart, check_product_creation, proceed_to_checkout


@pytest.mark.product("CombinationPliers")
@allure.epic("Practice Software Testing")
@allure.feature("Checkout")
@allure.title("Buying a product creates a matching invoice")
def test_buying_product_saves_invoice(product_page: Page, product, product_id: str) -> None:
    add_item_to_shopping_cart(product_page, product_id, product)
    proceed_to_checkout(product_page, LOGIN_USERS["approved"], BILLING_ADDRESS)
    check_product_creation(product_page)
