import allure
import pytest
from playwright.sync_api import Page, expect

from src.config.routes import URL_PATHS
from src.mapping.selectors import ERROR_MESSAGE_SELECTORS
from src.test_data.login_test_data import LOGIN_USERS
from src.utils.common_utils import endpoint
from src.utils.login_utils import login_user


@pytest.mark.page_path(URL_PATHS["login"])
@allure.epic("Practice Software Testing")
@allure.feature("Authentication")
class TestLoginUser:
    @allure.title("Valid customer can log in")
    def test_valid_registered_user_enters_user_space(self, page: Page) -> None:
        login_user(page, LOGIN_USERS["approved"])
        expect(page).to_have_url(endpoint(URL_PATHS["account"]))

    @allure.title("Invalid credentials display validation errors")
    def test_invalid_user_returns_errors(self, page: Page) -> None:
        login_user(page, LOGIN_USERS["unapproved"])
        expect(page).to_have_url(endpoint(URL_PATHS["login"]))
        expect(page.get_by_test_id(ERROR_MESSAGE_SELECTORS["email"])).to_be_visible()
        expect(page.get_by_test_id(ERROR_MESSAGE_SELECTORS["password"])).to_be_visible()

    @allure.title("Administrator is redirected to the admin dashboard")
    def test_admin_user_enters_dashboard(self, page: Page) -> None:
        login_user(page, LOGIN_USERS["admin"])
        expect(page).to_have_url(endpoint(URL_PATHS["admin_dashboard"]))
