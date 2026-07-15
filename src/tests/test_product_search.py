import allure
import pytest
from playwright.sync_api import Page

from src.utils.product_utils import search_items_by_name_under_price


@pytest.mark.page_path("/")
@allure.epic("Practice Software Testing")
@allure.feature("Product search")
@allure.title("Search returns up to five pliers under the maximum price")
def test_search_pliers_under_price(page: Page) -> None:
    urls = search_items_by_name_under_price(page, "Pliers", max_price=15, limit=5)

    assert len(urls) == 5
    assert all(url.startswith("https://practicesoftwaretesting.com/product/") for url in urls)
