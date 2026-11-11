import os
import re

import pytest
from playwright.sync_api import Page, expect
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

    def test_negative_invalid_email_alert(self):
        self.login_page.login("invalidemail@gmail.com", "Password123")
        self.login_page.verify_invalid_email_alert()

    def test_negative_invalid_email_inline_message(self):
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

    def test_negative_password_five_characters(self):
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

    def test_negative_blank_email_blank_password(self):
        self.login_page.click_login()
        self.login_page.verify_email_required()
        self.login_page.verify_password_required()
        self.login_page.verify_still_on_login_page()

    def test_negative_blank_email_invalid_password(self):
        self.login_page.login("", "12345")
        self.login_page.verify_email_required()
        self.login_page.verify_still_on_login_page()

    def test_negative_blank_email_valid_password(self):
        self.login_page.login("", "Password123")
        self.login_page.verify_email_required()
        self.login_page.verify_still_on_login_page()

    def test_negative_invalid_email_blank_password(self):
        self.login_page.login("invalidemail", "")
        self.login_page.verify_password_required()
        self.login_page.verify_still_on_login_page()

    def test_negative_invalid_email_invalid_password(self):
        self.login_page.login("invalidemail", "12345")
        self.login_page.verify_still_on_login_page()

    def test_negative_invalid_email_valid_password(self):
        self.login_page.login("invalidemail", "Password123")

        self.login_page.verify_invalid_email_inline_message()
        self.login_page.verify_still_on_login_page()

    def test_negative_valid_email_blank_password(self):
        email = os.getenv("TEST_EMAIL")
        assert email, "Set TEST_EMAIL before running this test."

        self.login_page.login(email, "")
        self.login_page.verify_password_required()
        self.login_page.verify_still_on_login_page()

    def test_negative_valid_email_invalid_password(self):
        email = os.getenv("TEST_EMAIL")
        assert email, "Set TEST_EMAIL before running this test."

        self.login_page.login(email, "DefinitelyWrongPassword987!")
        self.login_page.verify_authentication_rejected()

    def test_valid_email_valid_password(self):
        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")

        assert email, "Set TEST_EMAIL before running this test."
        assert password, "Set TEST_PASSWORD before running this test."

        self.login_page.login(email, password)
        self.login_page.verify_login_successful()


# ---------------------------------------------------------------------------
# Additional negative scenarios. These tests do not modify account data.
# Keep P1 authentication/security cases separate from optional policy tests.
# ---------------------------------------------------------------------------
@pytest.mark.ui
class TestLoginNegative:
    @pytest.fixture(autouse=True)
    def setup_login(self, page: Page, base_url: str):
        self.page = page
        self.login_page = LoginPage(page)
        self.login_page.open(base_url)

    @pytest.mark.parametrize('email', [
        'plainaddress', 'name@', '@example.com', 'name example@example.com',
        'name@@example.com', 'name@example..com',
    ], ids=['missing-at', 'missing-domain', 'missing-local-part',
            'embedded-space', 'double-at', 'double-dot'])
    def test_negative_invalid_email_formats(self, email):
        self.login_page.login(email, 'ValidLength123!')
        self.login_page.verify_email_format_rejected()

    def test_negative_unregistered_email(self):
        # Use a reserved example domain, not a real person's mailbox.
        self.login_page.login('not-registered-user-92837@example.com', 'ValidLength123!')
        self.login_page.verify_authentication_rejected()

    def test_negative_correct_email_wrong_password(self):
        email = os.getenv('TEST_EMAIL')
        if not email:
            pytest.skip('Set TEST_EMAIL to test an existing account')
        self.login_page.login(email, 'DefinitelyWrongPassword987!')
        self.login_page.verify_authentication_rejected()

    @pytest.mark.parametrize('password', [' ', '     ', '12345'],
                             ids=['one-space', 'five-spaces', 'five-characters'])
    def test_negative_short_or_whitespace_password(self, password):
        self.login_page.login('qa@example.com', password)
        self.login_page.verify_still_on_login_page()
        self.login_page.verify_no_authenticated_home()

    def test_negative_very_long_email(self):
        self.login_page.login('a' * 300 + '@example.com', 'ValidLength123!')
        self.login_page.verify_still_on_login_page()
        self.login_page.verify_login_fields_usable()

    def test_negative_very_long_password(self):
        self.login_page.login('qa@example.com', 'x' * 4096)
        self.login_page.verify_still_on_login_page()
        self.login_page.verify_login_fields_usable()

    @pytest.mark.parametrize('payload', [
        "' OR '1'='1", "admin'--", '<script>alert(1)</script>'
    ], ids=['sql-boolean', 'sql-comment', 'html-script'])
    def test_negative_email_injection_input(self, payload):
        self.login_page.login(payload, 'ValidLength123!')
        self.login_page.verify_still_on_login_page()
        self.login_page.verify_no_authenticated_home()

    def test_negative_password_html_injection(self):
        marker = 'sentinel-login-test-marker'
        payload = f'<img data-login-xss-marker="{marker}" src=x onerror=alert(1)>'
        self.login_page.login('qa@example.com', payload)
        self.login_page.verify_still_on_login_page()
        self.login_page.verify_no_executable_markup(marker)
        self.login_page.verify_password_not_in_url(payload)

    def test_negative_password_not_in_url(self):
        password = 'WrongPasswordNeverInURL123!'
        self.login_page.login('qa@example.com', password)
        self.login_page.verify_password_not_in_url(password)

    def test_negative_direct_home_access_without_login(self):
        from urllib.parse import urlsplit
        url = self.page.url
        parsed = urlsplit(url)
        home = f'{parsed.scheme}://{parsed.netloc}/nolimit/app/home'
        self.page.goto(home, wait_until='domcontentloaded')
        # An unauthenticated browser must not remain on the protected page.
        expect(self.page).to_have_url(re.compile(r'.*/nolimit/login/?$'), timeout=15000)

    def test_negative_enter_key_does_not_submit_login(self):
        # Enter a valid-format email
        self.login_page.enter_email("qa@example.com")

        # Leave password empty
        self.login_page.enter_password("")

        # Focus password field and press Enter
        self.login_page.password_input.focus()
        self.login_page.password_input.press("Enter")

        # Verify that Enter did not trigger validation
        expect(
            self.login_page.password_required_message
        ).to_have_count(0)

        # Verify user remains on login page
        self.login_page.verify_still_on_login_page()


    def test_negative_recovery_after_invalid_email(self):
        self.login_page.login('invalidemail', 'ValidLength123!')
        self.login_page.verify_still_on_login_page()
        self.login_page.clear_credentials()
        self.login_page.enter_email('qa@example.com')
        self.login_page.enter_password('ValidLength123!')
        self.login_page.verify_login_fields_usable()

    @pytest.mark.parametrize('email', [' qa@example.com', 'qa@example.com '],
                             ids=['leading-space', 'trailing-space'])
    def test_negative_email_whitespace_handling(self, email):
        # The specification may permit trimming. Only require no unexpected login.
        self.login_page.login(email, 'WrongPassword123!')
        self.login_page.verify_still_on_login_page()

    def test_negative_repeated_failed_attempts_policy(self):
        if os.getenv('TEST_LOGIN_RATE_LIMIT') != '1':
            pytest.skip('Opt in with TEST_LOGIN_RATE_LIMIT=1; may lock test account')
        email = os.getenv('TEST_RATE_LIMIT_EMAIL')
        if not email:
            pytest.skip('Set TEST_RATE_LIMIT_EMAIL to an approved disposable account')
        for _ in range(5):
            self.login_page.login(email, 'DefinitelyWrongPassword987!')
            self.login_page.verify_still_on_login_page()
        # Policy-specific lockout or 429 assertion must be added once defined.
        self.login_page.verify_no_authenticated_home()

    def test_negative_empty_password_click_login_shows_required_error(self):
        # Enter a valid-format email
        self.login_page.enter_email("qa@example.com")

        # Leave password empty
        self.login_page.enter_password("")

        # Click Login button
        self.login_page.click_login()

        # Verify password-required validation
        self.login_page.verify_password_required()

        # Verify user remains on login page
        self.login_page.verify_still_on_login_page()


