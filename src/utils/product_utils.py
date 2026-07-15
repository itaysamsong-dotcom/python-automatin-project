from urllib.parse import urljoin, urlparse

from playwright.sync_api import Locator, Page, Playwright

from src.config.routes import BASE_URLS, URL_PATHS
from src.mapping.selectors import SEARCH_SELECTORS


def _is_products_response(response) -> bool:
    response_url = urlparse(response.url)
    api_url = urlparse(BASE_URLS["api"])
    return (
        response.request.method in ("GET", "QUERY")
        and (response_url.scheme, response_url.netloc) == (api_url.scheme, api_url.netloc)
        and response_url.path.startswith(URL_PATHS["products_api"])
    )


def _wait_for_products_response(page: Page, action) -> None:
    with page.expect_response(_is_products_response, timeout=10_000) as response_info:
        action()

    response = response_info.value
    if not response.ok:
        raise RuntimeError(f"Product search failed with status {response.status}.")


def _set_max_price_filter(page: Page, max_price: float) -> None:
    """Use the page's maximum-price control when it exposes an accessible slider."""
    native_ranges = page.locator("input[type='range']")
    if native_ranges.count() > 0:
        maximum_range = native_ranges.last

        def set_native_range() -> None:
            maximum_range.evaluate(
                """(element, requestedPrice) => {
                    const minimum = Number(element.min || 0);
                    const maximum = Number(element.max || requestedPrice);
                    element.value = String(Math.min(maximum, Math.max(minimum, requestedPrice)));
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                }""",
                max_price,
            )

        _wait_for_products_response(page, set_native_range)
        return

    sliders = page.locator("[role='slider']")
    if sliders.count() == 0:
        return

    max_slider = sliders.last
    minimum = float(max_slider.get_attribute("aria-valuemin") or 0)
    maximum = float(max_slider.get_attribute("aria-valuemax") or max_price)
    target = min(max(max_price, minimum), maximum)

    step = float(max_slider.get_attribute("aria-valuestep") or 1)
    max_slider.focus()
    _wait_for_products_response(page, lambda: max_slider.press("Home"))

    current_value = float(max_slider.get_attribute("aria-valuenow") or minimum)
    while current_value < target:
        _wait_for_products_response(page, lambda: max_slider.press("ArrowRight"))

        next_value = float(max_slider.get_attribute("aria-valuenow") or current_value + step)
        if next_value <= current_value:
            raise RuntimeError("The maximum-price slider did not advance.")
        current_value = next_value


def _price(product_link: Locator) -> float:
    price = product_link.locator(
        f"xpath=.//*[@data-test='{SEARCH_SELECTORS['product_price']}']"
    )
    if price.count() == 0:
        price = product_link.locator(
            "xpath=ancestor::*[.//*[@data-test="
            f"'{SEARCH_SELECTORS['product_price']}']][1]"
            f"//*[@data-test='{SEARCH_SELECTORS['product_price']}']"
        )
    price_text = price.first.text_content() or ""
    return float("".join(character for character in price_text if character.isdigit() or character in ".-"))


def search_items_by_name_under_price(
    page: Page, query: str, max_price: float, limit: int = 5
) -> list[str]:
    """Return up to ``limit`` product URLs matching ``query`` at or below ``max_price``."""
    if max_price < 0:
        raise ValueError("max_price must be non-negative")
    if limit <= 0:
        return []

    page.get_by_test_id(SEARCH_SELECTORS["query"]).fill(query)
    _wait_for_products_response(
        page, lambda: page.get_by_test_id(SEARCH_SELECTORS["submit"]).click()
    )

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

        _wait_for_products_response(page, next_page.click)

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
