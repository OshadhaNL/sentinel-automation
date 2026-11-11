import os
import re
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Page, Browser, expect

from pages.loginPage import LoginPage
from pages.homePage import HomePage


@pytest.mark.ui
class TestHomePage:
    @pytest.fixture(autouse=True)
    def setup_home(self, page: Page, base_url: str):
        self.page = page
        self.email = os.getenv('TEST_EMAIL')
        self.password = os.getenv('TEST_PASSWORD')
        assert self.email, 'Please set TEST_EMAIL.'
        assert self.password, 'Please set TEST_PASSWORD.'

        self.login_page = LoginPage(page)
        self.login_page.open(base_url)
        self.login_page.enter_email(self.email)
        self.login_page.enter_password(self.password)
        self.login_page.click_login()
        expect(page).to_have_url(re.compile(r'.*/nolimit/app/home/?$'))
        self.home_page = HomePage(page)

    def test_welcome_heading(self):
        self.home_page.verify_welcome_heading()

    def test_username_visible(self):
        self.home_page.verify_username()

    def test_description_visible(self):
        self.home_page.verify_description()

    def test_home_logo_visible(self):
        self.home_page.verify_logo()

    def test_negative_home_must_show_logged_in_account_email(self):
        # Prevent accidentally showing a different user's account information.
        self.home_page.verify_account_email(self.email)

    def test_negative_password_must_not_appear_in_home_url(self):
        self.home_page.verify_no_password_in_url(self.password)

    def test_negative_logout_prevents_home_access(self):
        from urllib.parse import urlsplit

        parts = urlsplit(self.page.url)
        home_url = f"{parts.scheme}://{parts.netloc}/nolimit/app/home"

        # Perform logout
        self.home_page.logout()

        print("\n=== AFTER LOGOUT ===")
        print("URL:", self.page.url)

        # Capture storage metadata without printing token values
        storage = self.page.evaluate("""
                                     () => ({
                                         localKeys: Object.keys(localStorage),
                                         sessionKeys: Object.keys(sessionStorage)
                                     })
                                     """)

        print("Local storage key names:", storage["localKeys"])
        print("Session storage key names:", storage["sessionKeys"])

        # Check whether a fresh tab in the same browser context
        # can access the protected page.
        new_page = self.page.context.new_page()

        try:
            new_page.goto(
                home_url,
                wait_until="domcontentloaded"
            )

            expect(new_page).to_have_url(
                re.compile(r".*/nolimit/login/?$"),
                timeout=15000
            )

            print("Fresh tab: protected route blocked")

        finally:
            new_page.close()

        # Check the original tab
        self.page.goto(
            home_url,
            wait_until="domcontentloaded"
        )

        self.home_page.verify_protected_home_not_accessible()

    def test_negative_browser_back_after_logout_does_not_show_home(self):
        # Perform complete logout
        self.home_page.logout()

        # Navigate backward in browser history
        self.page.go_back(wait_until="domcontentloaded")

        # Verify protected Home page is not accessible
        self.home_page.verify_login_page()

    def _home_url(self):
        parts = urlsplit(self.page.url)
        return f'{parts.scheme}://{parts.netloc}/nolimit/app/home'

    def test_negative_cancel_logout_keeps_user_logged_in(self):
        self.home_page.click_logout()
        self.home_page.cancel_logout()

        expect(self.page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$")
        )

        self.home_page.verify_welcome_heading()

@pytest.mark.ui
class TestHomePageUnauthenticated:
    # Do not use the login fixture here: these tests require a fresh session.
    @pytest.fixture(autouse=True)
    def setup_unauthenticated(self, browser: Browser, base_url: str):
        self.context = browser.new_context()
        self.page = self.context.new_page()
        self.base_url = base_url
        yield
        self.context.close()

    @pytest.mark.parametrize('route', [
        pytest.param('/nolimit/app/home', id='home'),
        pytest.param('/nolimit/app/dashboard', id='dashboard'),
    ])
    def test_negative_protected_routes_require_login(self, route):
        parts = urlsplit(self.base_url)
        target = f'{parts.scheme}://{parts.netloc}{route}'
        self.page.goto(target, wait_until='domcontentloaded')
        home_page = HomePage(self.page)
        home_page.verify_login_page()
        expect(home_page.home_page).to_have_count(0)

    def test_negative_unauthenticated_home_reload_stays_protected(self):
        parts = urlsplit(self.base_url)
        target = f'{parts.scheme}://{parts.netloc}/nolimit/app/home'
        self.page.goto(target, wait_until='domcontentloaded')
        self.page.reload(wait_until='domcontentloaded')
        HomePage(self.page).verify_protected_home_not_accessible()

