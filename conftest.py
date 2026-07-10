from collections.abc import Generator
from pathlib import Path
import re

import allure
import pytest
from playwright.sync_api import BrowserContext, Page, Playwright

from src.config.routes import URL_PATHS
from src.test_data.product_test_data import PRODUCTS
from src.utils.product_utils import get_product_id_by_name

SCREENSHOT_NAME_PATTERN = re.compile(r"^test-failed-\d+\.png$")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item: pytest.Item, nextitem: pytest.Item) -> Generator[None, None, None]:
    """Attach screenshots saved by pytest-playwright to the current Allure test."""
    yield
    artifacts_dir = item.funcargs.get("output_path")
    if not artifacts_dir:
        return

    artifacts_path = Path(artifacts_dir)
    if not artifacts_path.is_dir():
        return

    for screenshot in artifacts_path.iterdir():
        if screenshot.is_file() and SCREENSHOT_NAME_PATTERN.match(screenshot.name):
            allure.attach.file(
                str(screenshot),
                name=screenshot.name,
                attachment_type=allure.attachment_type.PNG,
            )


@pytest.fixture(scope="session", autouse=True)
def configure_test_ids(playwright: Playwright) -> None:
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def page(context: BrowserContext, base_url: str, request: pytest.FixtureRequest) -> Generator[Page, None, None]:
    marker = request.node.get_closest_marker("page_path")
    page_path = marker.args[0] if marker else URL_PATHS["login"]
    page = context.new_page()
    page.set_default_timeout(5_000)
    page.goto(f"{base_url}{page_path}")
    yield page
    page.close()


@pytest.fixture
def product(request: pytest.FixtureRequest):
    marker = request.node.get_closest_marker("product")
    product_name = marker.args[0] if marker else "CombinationPliers"
    return PRODUCTS[product_name]


@pytest.fixture
def product_id(playwright: Playwright, product) -> str:
    return get_product_id_by_name(playwright, product.name)


@pytest.fixture
def product_page(page: Page, base_url: str, product_id: str) -> Page:
    page.goto(f"{base_url}{URL_PATHS['product']}/{product_id}")
    return page
