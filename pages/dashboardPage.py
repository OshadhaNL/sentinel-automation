from playwright.sync_api import Page, expect

class DashboardPage:
    def __init__(self, page: Page):
        self.page = page

        # Dashboard page heading
        self.dashboard_heading = page.get_by_role(
            "heading", name="Dashboard", level=1, exact=True
        )

        # Dashboard card headings
        self.ongoing_onboarding = page.get_by_role(
            "heading", name="Ongoing Onboarding", exact=True
        )

        self.individuals = page.get_by_role(
            "heading", name="Individuals", exact=True
        )

        self.companies = page.get_by_role(
            "heading", name="Companies", exact=True
        )


        # Card containers
        self.ongoing_card = page.locator(
            ".dashboard-card.active"
        )

        self.individuals_card = page.locator(
            ".dashboard-card"
        ).filter(has=self.individuals)

        self.companies_card = page.locator(
            ".dashboard-card"
        ).filter(has=self.companies)

        # Card numbers
        self.ongoing_number = self.ongoing_card.locator("h3")
        self.individuals_number = self.individuals_card.locator("h3")
        self.companies_number = self.companies_card.locator("h3")

        # Card icons
        self.ongoing_icon = self.ongoing_card.locator(
            "i.fa-clipboard-list-check"
        )

        self.individuals_icon = self.individuals_card.locator(
            "i.fa-user-tie"
        )

        self.companies_icon = self.companies_card.locator(
            "i.fa-building"
        )


    def check_dashboard_heading(self):
        expect(self.dashboard_heading).to_be_visible()

    def check_ongoing_onboarding(self):
        expect(self.ongoing_onboarding).to_be_visible()

    def check_individuals(self):
        expect(self.individuals).to_be_visible()

    def check_companies(self):
        expect(self.companies).to_be_visible()

    def check_dashboard_card_numbers(self):
        expect(self.ongoing_number).to_have_text("26")
        expect(self.individuals_number).to_have_text("31")
        expect(self.companies_number).to_have_text("21")

    def check_dashboard_card_icons(self):
        expect(self.ongoing_icon).to_be_visible()
        expect(self.individuals_icon).to_be_visible()
        expect(self.companies_icon).to_be_visible()
