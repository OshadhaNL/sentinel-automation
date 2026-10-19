from playwright.sync_api import Page, expect


class HomePage:
    def __init__(self, page: Page):
        self.page = page

        # Home page locators
        self.welcome_heading = page.get_by_role(
            "heading", name="Welcome", exact=True
        )

        self.user_name = page.get_by_role(
            "heading",
            name="Oshadha Weerakon",
            level=2,
            exact=True
        )

        self.welcome_description = page.get_by_text(
            "A complete solution to support secure, efficient, "
            "and streamlined customer onboarding",
            exact=True
        )

    def check_welcome_heading(self):
        expect(self.welcome_heading).to_be_visible()

    def check_user_name(self):
        expect(self.user_name).to_be_visible()

    def check_welcome_description(self):
        expect(self.welcome_description).to_be_visible()

    def check_home_page(self):
        self.check_welcome_heading()
        self.check_user_name()
        self.check_welcome_description()
