import allure
import pytest
from playwright.sync_api import Page, expect

from src.config.routes import URL_PATHS
from src.mapping.selectors import LOGIN_SELECTORS
from src.test_data.register_test_data import REGISTER_USERS
from src.utils.common_utils import endpoint
from src.utils.login_utils import fill_mail_and_password
from src.utils.register_utils import fill_register_details


@pytest.mark.page_path(URL_PATHS["register"])
@allure.epic("Practice Software Testing")
@allure.feature("Registration")
@allure.title("Customer can register with valid details")
def test_correct_details_create_a_user(page: Page) -> None:
    user = REGISTER_USERS["correct_user_field"]
    fill_register_details(page, user)
    expect(page).to_have_url(endpoint(URL_PATHS["login"]))
    fill_mail_and_password(page, user)
    page.get_by_test_id(LOGIN_SELECTORS["login_submit_btn"]).click()
    expect(page).to_have_url(endpoint(URL_PATHS["account"]))
