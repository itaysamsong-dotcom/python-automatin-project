from urllib.parse import urlparse

from playwright.sync_api import Page

from src.config.routes import BASE_URLS
from src.mapping.selectors import LOGIN_FIELD_SELECTORS, LOGIN_SELECTORS
from src.models.types import LoginDetails
from src.utils.common_utils import fill_text_fields


def fill_mail_and_password(page: Page, login_details: LoginDetails) -> None:
    fill_text_fields(page, login_details, LOGIN_FIELD_SELECTORS)


def login_user(page: Page, login_details: LoginDetails, wait_for_auth: bool = False) -> None:
    fill_mail_and_password(page, login_details)
    submit = page.get_by_test_id(LOGIN_SELECTORS["login_submit_btn"])

    if not wait_for_auth:
        submit.click()
        return

    api_url = urlparse(BASE_URLS["api"])

    def is_login_response(response) -> bool:
        response_url = urlparse(response.url)
        return (
            response.request.method == "POST"
            and (response_url.scheme, response_url.netloc) == (api_url.scheme, api_url.netloc)
            and response_url.path == "/users/login"
        )

    def is_current_user_response(response) -> bool:
        response_url = urlparse(response.url)
        return (
            response.request.method == "GET"
            and (response_url.scheme, response_url.netloc) == (api_url.scheme, api_url.netloc)
            and response_url.path == "/users/me"
            and response.ok
        )

    with page.expect_response(is_current_user_response, timeout=30_000) as user_response_info:
        with page.expect_response(is_login_response, timeout=10_000) as login_response_info:
            submit.click()

    login_response = login_response_info.value
    if not login_response.ok:
        raise RuntimeError(f"Login request failed with status {login_response.status}.")

    user_response = user_response_info.value
    if not user_response.ok:
        raise RuntimeError(f"Loading the logged-in user failed with status {user_response.status}.")


def extract_user_auth_token(page: Page) -> str:
    auth_token = page.evaluate("window.localStorage.getItem('auth-token')")
    if not auth_token:
        raise RuntimeError("The auth-token was not found in local storage. Make sure the user is logged in.")
    return auth_token
