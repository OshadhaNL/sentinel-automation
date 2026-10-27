
from playwright.sync_api import Page, expect


class HomePage:
    def __init__(self, page: Page):
        self.page = page

        # Home screen container
        self.home_page = page.locator(".home-page")

        # Welcome heading
        self.welcome_heading = page.get_by_role(
            "heading", name="Welcome", level=1
        )

        # Username
        self.username = page.locator(".home-content h2")

        # Description
        self.description = page.locator(".home-content p")

        # Home logo
        self.logo = page.locator("img.home-logo")

    def verify_welcome_heading(self):
        expect(self.welcome_heading).to_be_visible()
        expect(self.welcome_heading).to_have_text("Welcome")

    def verify_username(self):
        expect(self.username).to_be_visible()
        expect(self.username).not_to_be_empty()

    def verify_description(self):
        expect(self.description).to_be_visible()
        expect(self.description).to_have_text(
            "A complete solution to support secure, efficient, "
            "and streamlined customer onboarding"
        )

    def verify_logo(self):
        expect(self.logo).to_be_visible()
        expect(self.logo).to_have_attribute(
            "alt", "SENTINEL"
        )
