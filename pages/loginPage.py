
import re

from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

        # Heading
        self.login_heading = page.get_by_role(
            "heading", name="Log in", exact=True
        )

        # Email
        self.email_label = page.locator('label[for="email"]')
        self.email_input = page.locator('input[name="email"]')
        self.email_required_message = page.locator(
            'label[for="email"] .err-meg'
        )

        # Password
        self.password_label = page.locator('label[for="password"]')
        self.password_input = page.locator('input[name="password"]')
        self.password_required_message = page.locator(
            'label[for="password"] .err-meg'
        )
        self.password_visibility_button = page.locator(
            ".input-password button.input-after"
        )
        self.password_eye_icon = page.locator(
            ".input-password button.input-after i"
        )

        # Login button
        self.login_button = page.get_by_role(
            "button", name="Login", exact=True
        )

        # Notifications
        self.error_notification = page.locator(
            ".ant-notification-notice-error"
        )
        self.invalid_email_alert = self.error_notification.locator(
            ".ant-notification-notice-message"
        ).filter(has_text="Invalid email address")

        self.password_length_alert = self.error_notification.locator(
            ".ant-notification-notice-message"
        ).filter(
            has_text='"password" length must be at least 6 characters long'
        )

        # Logo and version
        self.logo = page.locator('img.logo[alt="SENTINEL"]')
        self.software_version = page.locator(
            "div.absolute.bottom-4 p"
        )

    # ------------------------------
    # Reusable actions
    # ------------------------------

    def open(self, url: str):
        self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        expect(self.login_heading).to_be_visible(
            timeout=15000
        )

    def enter_email(self, email: str):
        self.email_input.fill(email)

    def enter_password(self, password: str):
        self.password_input.fill(password)

    def click_login(self):
        self.login_button.click()

    def click_password_eye(self):
        self.password_visibility_button.click()

    def login(self, email: str, password: str):
        self.enter_email(email)
        self.enter_password(password)
        self.click_login()

    # ------------------------------
    # Basic UI verifications
    # ------------------------------

    def verify_login_heading(self):
        expect(self.login_heading).to_be_visible()

    def verify_email_label(self):
        expect(self.email_label).to_contain_text("Email Address")

    def verify_password_label(self):
        expect(self.password_label).to_contain_text("Password")

    def verify_email_input(self):
        expect(self.email_input).to_be_visible()
        expect(self.email_input).to_have_attribute("type", "email")

    def verify_password_input(self):
        expect(self.password_input).to_be_visible()
        expect(self.password_input).to_have_attribute("type", "password")

    def verify_email_placeholder(self):
        expect(self.email_input).to_have_attribute(
            "placeholder", "Enter email address"
        )

    def verify_password_placeholder(self):
        expect(self.password_input).to_have_attribute(
            "placeholder", "Enter password"
        )

    def verify_login_button(self):
        expect(self.login_button).to_be_visible()

    def verify_login_button_clickable(self):
        expect(self.login_button).to_be_enabled()

    def verify_login_button_pink(self):
        expect(self.login_button).to_have_css(
            "background-color", "rgb(202, 53, 128)"
        )

    def verify_logo_visible(self):
        expect(self.logo).to_be_visible()

    def verify_software_version_visible(self):
        expect(self.software_version).to_be_visible()
        expect(self.software_version).to_contain_text(
            re.compile(r"Version\s+\d+\.\d+\.\d+\+\d+")
        )

    # ------------------------------
    # Required asterisk verification
    # ------------------------------

    def verify_required_asterisk(self, label):
        expect(label).to_be_visible()

        result = label.evaluate(
            """element => {
                const style = getComputedStyle(element, '::after');
                return {
                    content: style.content,
                    color: style.color
                };
            }"""
        )

        assert "*" in result["content"], (
            "Required asterisk is missing"
        )

        # Colour observed in DevTools, subject to
        # confirmation of the exact CSS 'color' property.
        assert result["color"] == "rgb(235, 87, 87)", (
            f"Expected red asterisk, got {result['color']}"
        )

    def verify_email_asterisk_red(self):
        self.verify_required_asterisk(self.email_label)

    def verify_password_asterisk_red(self):
        self.verify_required_asterisk(self.password_label)

    # ------------------------------
    # Password visibility
    # ------------------------------

    def verify_password_masked(self):
        expect(self.password_input).to_have_attribute(
            "type", "password"
        )

    def verify_eye_icon_visible(self):
        expect(self.password_visibility_button).to_be_visible()
        expect(self.password_eye_icon).to_be_visible()

    def verify_password_visible(self):
        expect(self.password_input).to_have_attribute(
            "type", "text"
        )

    def verify_password_hidden(self):
        expect(self.password_input).to_have_attribute(
            "type", "password"
        )

    # ------------------------------
    # Validation messages
    # ------------------------------

    def verify_email_required(self):
        expect(self.email_required_message).to_have_text(
            "Email is required"
        )
        expect(self.email_required_message).to_be_visible()

    def verify_password_required(self):
        expect(self.password_required_message).to_have_text(
            "Password is required"
        )
        expect(self.password_required_message).to_be_visible()

    def verify_invalid_email_inline_message(self):
        expect(self.email_required_message).to_contain_text(
            re.compile(
                r"(Please enter a valid email address\.|Enter valid email address)"
            )
        )

    def verify_invalid_email_alert(self):
        expect(self.invalid_email_alert).to_be_visible()

    def verify_password_length_alert(self):
        expect(self.password_length_alert).to_be_visible()

    def verify_no_password_length_alert(self):
        expect(self.password_length_alert).to_have_count(0)

    # ------------------------------
    # Navigation
    # ------------------------------

    def verify_still_on_login_page(self):
        expect(self.page).to_have_url(
            re.compile(r".*/nolimit/login/?$")
        )

    def verify_login_successful(self):
        expect(self.page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$")
        )
