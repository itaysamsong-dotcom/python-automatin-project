from playwright.sync_api import Playwright

from src.config.routes import BASE_URLS, URL_PATHS


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
