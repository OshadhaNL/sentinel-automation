
import os
import re

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.homePage import HomePage


@pytest.mark.ui
class TestHomePage:

    @pytest.fixture(autouse=True)
    def setup_home(self, page: Page, base_url: str):
        self.page = page

        # Read credentials
        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")

        assert email, "Please set TEST_EMAIL."
        assert password, "Please set TEST_PASSWORD."

        # Login
        self.login_page = LoginPage(page)
        self.login_page.open(base_url)
        self.login_page.enter_email(email)
        self.login_page.enter_password(password)
        self.login_page.click_login()

        # Verify successful navigation
        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$")
        )

        # Initialize Home page
        self.home_page = HomePage(page)

    def test_welcome_heading(self):
        self.home_page.verify_welcome_heading()

    def test_username_visible(self):
        self.home_page.verify_username()

    def test_description_visible(self):
        self.home_page.verify_description()

    def test_home_logo_visible(self):
        self.home_page.verify_logo()
