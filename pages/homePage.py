import re
from playwright.sync_api import Page, expect


class HomePage:
    def __init__(self, page: Page):
        self.page = page
        self.home_page = page.locator('.home-page')
        self.welcome_heading = page.get_by_role('heading', name='Welcome', level=1)
        self.username = page.locator('.home-content h2')
        self.description = page.locator('.home-content p')
        self.logo = page.locator('img.home-logo')
        self.navbar = page.locator('nav.navbar')
        self.nav_account_email = page.locator('.nav-avatar p')
        self.nav_account_name = page.locator('.nav-avatar h6')
        self.logout_button = page.locator('nav.navbar button[title="Logout"]')
        # Logout confirmation dialog
        self.logout_dialog = page.get_by_role(
            "dialog", name="Confirm Logout"
        )

        self.confirm_logout_button = self.logout_dialog.get_by_role(
            "button", name="Yes, Logout"
        )

        self.cancel_logout_button = self.logout_dialog.get_by_role(
            "button", name="Cancel"
        )

    def verify_welcome_heading(self):
        expect(self.welcome_heading).to_be_visible()
        expect(self.welcome_heading).to_have_text('Welcome')

    def verify_username(self):
        expect(self.username).to_be_visible()
        expect(self.username).not_to_be_empty()

    def verify_description(self):
        expect(self.description).to_be_visible()
        expect(self.description).to_have_text(
            'A complete solution to support secure, efficient, '
            'and streamlined customer onboarding'
        )

    def verify_logo(self):
        expect(self.logo).to_be_visible()
        expect(self.logo).to_have_attribute('alt', 'SENTINEL')

    def verify_home_visible(self):
        expect(self.home_page).to_be_visible()
        self.verify_welcome_heading()

    def verify_account_email(self, expected_email: str):
        expect(self.nav_account_email).to_be_visible()
        expect(self.nav_account_email).to_have_text(expected_email)

    def verify_no_password_in_url(self, password: str):
        assert password not in self.page.url, 'Password is exposed in the page URL'

    def click_logout(self):
        self.logout_button.click()

    def verify_login_page(self):
        expect(self.page).to_have_url(re.compile(r'.*/nolimit/login/?$'), timeout=15000)

    def verify_protected_home_not_accessible(self):
        # Allow the application's asynchronous auth check to finish.
        expect(self.page).to_have_url(
            re.compile(r".*/nolimit/login/?$"),
            timeout=30000
        )

        # Protected content must no longer be present.
        expect(self.home_page).to_have_count(0)

    def confirm_logout(self):
        expect(self.logout_dialog).to_be_visible()
        self.confirm_logout_button.click()

    def cancel_logout(self):
        expect(self.logout_dialog).to_be_visible()
        self.cancel_logout_button.click()
        expect(self.logout_dialog).to_be_hidden()

    def logout(self):
        self.click_logout()
        self.confirm_logout()
        self.verify_login_page()