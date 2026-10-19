
import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.homePage import HomePage


# Replace these with your real test account credentials
VALID_EMAIL = "oshadha@northlark.com"
VALID_PASSWORD = "5e11Piwu"

# Replace with your actual Home page URL
HOME_URL = "https://sentinel-austrac-qa.northlark.com/nolimit/app/home"


@pytest.mark.ui
@pytest.mark.smoke
def test_welcome_heading_displayed(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(VALID_EMAIL)
    login.enter_password(VALID_PASSWORD)
    login.click_login()

    expect(page).to_have_url(HOME_URL)

    home = HomePage(page)
    home.check_welcome_heading()


@pytest.mark.ui
def test_user_name_displayed(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(VALID_EMAIL)
    login.enter_password(VALID_PASSWORD)
    login.click_login()

    expect(page).to_have_url(HOME_URL)

    home = HomePage(page)
    home.check_user_name()


@pytest.mark.ui
def test_welcome_description_displayed(
    page: Page, base_url: str
):
    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(VALID_EMAIL)
    login.enter_password(VALID_PASSWORD)
    login.click_login()

    expect(page).to_have_url(HOME_URL)

    home = HomePage(page)
    home.check_welcome_description()

