
import os

import pytest
from playwright.sync_api import Page

from pages.loginPage import LoginPage


@pytest.mark.ui
class TestLoginPage:

    @pytest.fixture(autouse=True)
    def setup_login(self, page: Page, base_url: str):
        self.page = page
        self.login_page = LoginPage(page)
        self.login_page.open(base_url)

    # --------------------------------
    # Login screen UI tests
    # --------------------------------

    def test_login_heading(self):
        self.login_page.verify_login_heading()

    def test_email_label(self):
        self.login_page.verify_email_label()

    def test_email_required_asterisk_red(self):
        self.login_page.verify_email_asterisk_red()

    def test_email_input_visible(self):
        self.login_page.verify_email_input()

    def test_email_placeholder(self):
        self.login_page.verify_email_placeholder()

    def test_invalid_email_alert(self):
        self.login_page.login("invalidemail@gmail.com", "Password123")
        self.login_page.verify_invalid_email_alert()

    def test_invalid_email_inline_message(self):
        self.login_page.enter_email("invalidemail")
        self.login_page.email_input.blur()

        self.login_page.verify_invalid_email_inline_message()

    def test_password_label(self):
        self.login_page.verify_password_label()

    def test_password_required_asterisk_red(self):
        self.login_page.verify_password_asterisk_red()

    def test_password_input_visible(self):
        self.login_page.verify_password_input()

    def test_password_placeholder(self):
        self.login_page.verify_password_placeholder()

    # --------------------------------
    # Password length tests
    # --------------------------------

    def test_password_five_characters(self):
        self.login_page.login("test@example.com", "12345")
        self.login_page.verify_password_length_alert()

    def test_password_six_characters(self):
        self.login_page.login("test@example.com", "123456")
        self.login_page.verify_no_password_length_alert()

    def test_password_seven_characters(self):
        self.login_page.login("test@example.com", "1234567")
        self.login_page.verify_no_password_length_alert()

    # --------------------------------
    # Password visibility tests
    # --------------------------------

    def test_password_characters_masked(self):
        self.login_page.enter_password("Password123")
        self.login_page.verify_password_masked()

    def test_password_eye_icon_visible(self):
        self.login_page.verify_eye_icon_visible()

    def test_password_eye_shows_characters(self):
        self.login_page.enter_password("Password123")
        self.login_page.click_password_eye()
        self.login_page.verify_password_visible()

    def test_password_eye_toggle_twice(self):
        self.login_page.enter_password("Password123")

        self.login_page.click_password_eye()
        self.login_page.verify_password_visible()

        self.login_page.click_password_eye()
        self.login_page.verify_password_hidden()

    # --------------------------------
    # Login button and branding
    # --------------------------------

    def test_login_button_visible_and_pink(self):
        self.login_page.verify_login_button()
        self.login_page.verify_login_button_pink()

    def test_login_button_clickable(self):
        self.login_page.verify_login_button_clickable()

    def test_software_version_visible(self):
        self.login_page.verify_software_version_visible()

    def test_logo_visible(self):
        self.login_page.verify_logo_visible()

    # --------------------------------
    # Credential combination tests
    # --------------------------------

    def test_blank_email_blank_password(self):
        self.login_page.click_login()
        self.login_page.verify_email_required()
        self.login_page.verify_password_required()
        self.login_page.verify_still_on_login_page()

    def test_blank_email_invalid_password(self):
        self.login_page.login("", "12345")
        self.login_page.verify_email_required()
        self.login_page.verify_still_on_login_page()

    def test_blank_email_valid_password(self):
        self.login_page.login("", "Password123")
        self.login_page.verify_email_required()
        self.login_page.verify_still_on_login_page()

    def test_invalid_email_blank_password(self):
        self.login_page.login("invalidemail", "")
        self.login_page.verify_password_required()
        self.login_page.verify_still_on_login_page()

    def test_invalid_email_invalid_password(self):
        self.login_page.login("invalidemail", "12345")
        self.login_page.verify_still_on_login_page()

    def test_invalid_email_valid_password(self):
        self.login_page.login("invalidemail", "Password123")

        self.login_page.verify_invalid_email_inline_message()
        self.login_page.verify_still_on_login_page()

    def test_valid_email_blank_password(self):
        email = os.getenv("TEST_EMAIL")
        assert email, "Set TEST_EMAIL before running this test."

        self.login_page.login(email, "")
        self.login_page.verify_password_required()
        self.login_page.verify_still_on_login_page()

    def test_valid_email_invalid_password(self):
        email = os.getenv("TEST_EMAIL")
        assert email, "Set TEST_EMAIL before running this test."

        self.login_page.login(email, "12345")
        self.login_page.verify_still_on_login_page()

    def test_valid_email_valid_password(self):
        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")

        assert email, "Set TEST_EMAIL before running this test."
        assert password, "Set TEST_PASSWORD before running this test."

        self.login_page.login(email, password)
        self.login_page.verify_login_successful()
