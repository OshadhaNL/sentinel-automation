
import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage


# SAMPLE TEST DATA — replace with your approved test account
VALID_EMAIL = "oshadha@northlark.com"
VALID_PASSWORD = "5e11Piwu"

Invalid_Email_Format = "InvalidEmail"
INVALID_EMAIL = "InvalidEmail@gmail.com"
INVALID_PASSWORD = "WrongPassword123!"

# SAMPLE URL — replace with your actual home page URL
HOME_URL = "https://sentinel-austrac-qa.northlark.com/nolimit/app/home"


# TEST 1: Login heading is displayed
@pytest.mark.ui
@pytest.mark.smoke
def test_login_heading_displayed(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    expect(login.heading).to_be_visible()


# TEST 2: Email Address label is displayed
@pytest.mark.ui
def test_email_label_displayed(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    expect(page.get_by_text("Email Address", exact=True)).to_be_visible()


# TEST 3: Password label is displayed
@pytest.mark.ui
def test_password_label_displayed(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    expect(page.get_by_text("Password", exact=True)).to_be_visible()


# TEST 4: Login button is displayed correctly
@pytest.mark.ui
def test_login_button_displayed(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    expect(login.login_button).to_be_visible()
    expect(login.login_button).to_be_enabled()


# TEST 5: Blank email and password show required messages
@pytest.mark.ui
@pytest.mark.negative
def test_both_fields_are_mandatory(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    login.enter_email("")
    login.enter_password("")
    login.click_login()

    login.check_email_required()
    login.check_password_required()


# TEST 6: Email input is visible
@pytest.mark.ui
def test_email_input_visible(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    expect(login.email).to_be_visible()


# TEST 7: Password input is visible
@pytest.mark.ui
def test_password_input_visible(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    expect(login.password).to_be_visible()


# TEST 8: Blank email + invalid password
# Expected: Email is required; remain on login page
@pytest.mark.ui
@pytest.mark.negative
def test_blank_email_invalid_password(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    login.enter_email("")
    login.enter_password(INVALID_PASSWORD)
    login.click_login()

    login.check_email_required()
    expect(login.heading).to_be_visible()


# TEST 9: Blank email + valid password
# Expected: Email is required; remain on login page
@pytest.mark.ui
@pytest.mark.negative
def test_blank_email_valid_password(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    login.enter_email("")
    login.enter_password(VALID_PASSWORD)
    login.click_login()

    login.check_email_required()
    expect(login.heading).to_be_visible()


# TEST 10: Invalid email + blank password
# Expected: Password is required; remain on login page
@pytest.mark.ui
@pytest.mark.negative
def test_invalid_email_blank_password(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    login.enter_email(INVALID_EMAIL)
    login.enter_password("")
    login.click_login()

    login.check_password_required()
    expect(login.heading).to_be_visible()


# TEST 11: Valid email + blank password
# Expected: Password is required; remain on login page
@pytest.mark.ui
@pytest.mark.negative
def test_valid_email_blank_password(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    login.enter_email(VALID_EMAIL)
    login.enter_password("")
    login.click_login()

    login.check_password_required()
    expect(login.heading).to_be_visible()


# TEST 12: Invalid email + invalid password
# Expected: Invalid email popup; remain on login page
@pytest.mark.ui
@pytest.mark.negative
def test_invalid_email_invalid_password(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    login.enter_email(INVALID_EMAIL)
    login.enter_password(INVALID_PASSWORD)
    login.click_login()

    login.check_notification("Invalid email address")
    expect(login.heading).to_be_visible()


# TEST 13: Invalid email + valid password
# Expected: Invalid email popup; remain on login page
@pytest.mark.ui
@pytest.mark.negative
def test_invalid_email_valid_password(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    login.enter_email(INVALID_EMAIL)
    login.enter_password(VALID_PASSWORD)
    login.click_login()

    login.check_notification("Invalid email")
    expect(login.heading).to_be_visible()


# TEST 14: Valid email + invalid password
# Expected: Invalid password popup; remain on login page
@pytest.mark.ui
@pytest.mark.negative
def test_valid_email_invalid_password(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    login.enter_email(VALID_EMAIL)
    login.enter_password(INVALID_PASSWORD)
    login.click_login()

    login.check_notification("Invalid password")
    expect(login.heading).to_be_visible()


# TEST 15: Valid email + valid password
# Expected: Navigate to home page
@pytest.mark.ui
@pytest.mark.smoke
def test_valid_login_navigates_to_home(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    login.enter_email(VALID_EMAIL)
    login.enter_password(VALID_PASSWORD)
    login.click_login()

    expect(page).to_have_url(HOME_URL)


# TEST 16: Password can be shown and hidden
@pytest.mark.ui
def test_password_show_and_hide(page: Page, base_url: str):
    login = LoginPage(page)
    login.open(base_url)

    login.enter_password(VALID_PASSWORD)

    # Initially, password characters should be hidden
    login.check_password_hidden()

    # Click eye icon to show the password
    login.password_visibility_button.click()
    login.check_password_visible()

    # Click again to hide the password
    login.password_visibility_button.click()
    login.check_password_hidden()
