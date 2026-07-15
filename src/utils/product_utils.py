from urllib.parse import urljoin

from playwright.sync_api import Locator, Page, Playwright

from src.config.routes import BASE_URLS, URL_PATHS
from src.mapping.selectors import SEARCH_SELECTORS


def _set_max_price_filter(page: Page, max_price: float) -> None:
    """Use the page's maximum-price control when it exposes an accessible slider."""
    sliders = page.locator("input[type='range'], [role='slider']")
    if sliders.count() == 0:
        return

    max_slider = sliders.last
    minimum = float(max_slider.get_attribute("min") or max_slider.get_attribute("aria-valuemin") or 0)
    maximum = float(max_slider.get_attribute("max") or max_slider.get_attribute("aria-valuemax") or max_price)
    target = min(max(max_price, minimum), maximum)

    if max_slider.evaluate("element => element.tagName === 'INPUT'"):
        max_slider.fill(str(target))
        max_slider.dispatch_event("change")
        return

    step = float(max_slider.get_attribute("aria-valuestep") or 1)
    max_slider.press("Home")
    for _ in range(round((target - minimum) / step)):
        max_slider.press("ArrowRight")


def _price(product_link: Locator) -> float:
    price_text = product_link.get_by_test_id(SEARCH_SELECTORS["product_price"]).inner_text()
    return float(price_text.replace("$", "").replace(",", "").strip())


def search_items_by_name_under_price(
    page: Page, query: str, max_price: float, limit: int = 5
) -> list[str]:
    """Return up to ``limit`` product URLs matching ``query`` at or below ``max_price``."""
    if max_price < 0:
        raise ValueError("max_price must be non-negative")
    if limit <= 0:
        return []

    page.get_by_test_id(SEARCH_SELECTORS["query"]).fill(query)
    with page.expect_response(lambda response: "/products" in response.url):
        page.get_by_test_id(SEARCH_SELECTORS["submit"]).click()

    _set_max_price_filter(page, max_price)
    urls: list[str] = []

    while len(urls) < limit:
        # XPath is intentionally used here because it is part of the exercise.
        product_links = page.locator(
            f"xpath=//a[starts-with(@data-test, '{SEARCH_SELECTORS['product_prefix']}')]"
        )
        for index in range(product_links.count()):
            product_link = product_links.nth(index)
            if _price(product_link) <= max_price:
                href = product_link.get_attribute("href")
                if href:
                    absolute_url = urljoin(page.url, href)
                    if absolute_url not in urls:
                        urls.append(absolute_url)
            if len(urls) == limit:
                break

        if len(urls) == limit:
            break

        next_page = page.get_by_test_id(SEARCH_SELECTORS["pagination_next"])
        if next_page.count() == 0:
            break
        disabled = (
            next_page.get_attribute("aria-disabled") == "true"
            or "disabled" in (next_page.get_attribute("class") or "").split()
            or "disabled" in (next_page.locator("xpath=..").get_attribute("class") or "").split()
        )
        if disabled:
            break

        current_url = page.url
        next_page.click()
        page.wait_for_function("previousUrl => window.location.href !== previousUrl", current_url)

    return urls


def get_product_id_by_name(playwright: Playwright, product_name: str) -> str:
    api_context = playwright.request.new_context(base_url=BASE_URLS["api"])
    try:
        response = api_context.get(URL_PATHS["products_api"])
        if not response.ok:
            raise RuntimeError(f"Products request failed with status {response.status}.")
        product = next(
            (item for item in response.json()["data"] if item["name"].lower() == product_name.lower()),
            None,
        )
        if product is None:
            raise LookupError(f'Product "{product_name}" not found')
        return product["id"]
    finally:
        api_context.dispose()
