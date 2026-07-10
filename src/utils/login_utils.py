from playwright.sync_api import Page

from src.mapping.selectors import LOGIN_FIELD_SELECTORS, LOGIN_SELECTORS
from src.models.types import LoginDetails
from src.utils.common_utils import fill_text_fields


def fill_mail_and_password(page: Page, login_details: LoginDetails) -> None:
    fill_text_fields(page, login_details, LOGIN_FIELD_SELECTORS)


def login_user(page: Page, login_details: LoginDetails) -> None:
    fill_mail_and_password(page, login_details)
    page.get_by_test_id(LOGIN_SELECTORS["login_submit_btn"]).dblclick()


def extract_user_auth_token(page: Page) -> str:
    auth_token = page.evaluate("window.localStorage.getItem('auth-token')")
    if not auth_token:
        raise RuntimeError("The auth-token was not found in local storage. Make sure the user is logged in.")
    return auth_token

