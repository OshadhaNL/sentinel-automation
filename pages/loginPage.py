from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

        # Main login elements
        self.heading = page.get_by_role("heading", name="Log in")
        self.email = page.get_by_placeholder(
            "Enter email address", exact=True
        )
        self.password = page.get_by_placeholder(
            "Enter password", exact=True
        )
        self.login_button = page.get_by_role(
            "button", name="Login", exact=True
        )

        # Validation messages shown beside the fields
        self.email_required = page.locator(
            ".err-meg"
        ).filter(has_text="Email is required")

        self.password_required = page.locator(
            ".err-meg"
        ).filter(has_text="Password is required")

        # Popup notifications
        self.notification = page.get_by_role("alert")

        # Eye button inside the password input container
        self.password_visibility_button = page.locator(
            "button.input-after"
        )

    def open(self, url: str):
        self.page.goto(url)

    def enter_email(self, email: str):
        self.email.fill(email)

    def enter_password(self, password: str):
        self.password.fill(password)

    def click_login(self):
        self.login_button.click()

    def check_login_page(self):
        expect(self.heading).to_be_visible()
        expect(self.email).to_be_visible()
        expect(self.password).to_be_visible()
        expect(self.login_button).to_be_visible()
        expect(self.login_button).to_be_enabled()

    def check_email_required(self):
        expect(self.email_required).to_be_visible()

    def check_password_required(self):
        expect(self.password_required).to_be_visible()

    def check_notification(self, message: str):
        expect(self.notification).to_contain_text(message)

    def check_password_hidden(self):
        expect(self.password).to_have_attribute("type", "password")

    def check_password_visible(self):
        expect(self.password).to_have_attribute("type", "text")
