from playwright.sync_api import Page, expect
import re

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

        # Client Risk Breakdown section
        self.client_risk_heading = page.get_by_role(
            "heading",
            name="Client Risk Breakdown",
            exact=True
        )

        self.client_risk_card = page.locator(
            ".dashboard-card"
        ).filter(has=self.client_risk_heading)

        self.client_risk_chart = self.client_risk_card.locator(
            "canvas"
        )

        # Onboarding section
        self.onboarding_heading = page.get_by_role(
            "heading",
            name="Onboarding",
            exact=True
        )

        self.onboarding_card = page.locator(
            ".dashboard-card"
        ).filter(has=self.onboarding_heading)

        self.onboarding_chart = self.onboarding_card.locator(
            "canvas"
        )

        # Documents section
        self.documents_heading = self.page.get_by_role(
            "heading", name="Documents", exact=True
        )

        self.documents_view_all_button = self.page.get_by_role(
            "button", name="View All", exact=True
        )

        # Documents table
        self.documents_table = self.page.locator(".ant-table")

        self.documents_table_rows = self.page.locator(
            ".ant-table-tbody tr"
        )

        # Table headers
        self.client_id_header = self.page.get_by_role(
            "columnheader", name="Client ID", exact=True
        )

        self.document_header = self.page.get_by_role(
            "columnheader", name="Document", exact=True
        )

        self.status_header = self.page.get_by_role(
            "columnheader", name="Status", exact=True
        )

        self.uploaded_date_header = self.page.get_by_role(
            "columnheader", name="Uploaded Date", exact=True
        )

        self.expiry_date_header = self.page.get_by_role(
            "columnheader", name="Date of Expiry", exact=True
        )


        # First Client ID link in the Documents table
        self.first_client_id_link = self.documents_table.locator(
            "tbody tr"
        ).first.locator("a.table-link")

        # Document names
        self.document_names = self.documents_table.locator(
            ".doc-cell .doc-text"
        )

        # Status cells
        self.document_statuses = self.documents_table.locator(
            "tbody tr td:nth-child(3)"
        )

        # Uploaded dates
        self.uploaded_dates = self.documents_table.locator(
            "tbody tr td:nth-child(4)"
        )

        # Expiry dates
        self.expiry_dates = self.documents_table.locator(
            "tbody tr td:nth-child(5)"
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
        expect(self.ongoing_number).to_have_text("25")
        expect(self.individuals_number).to_have_text("31")
        expect(self.companies_number).to_have_text("21")

    def check_dashboard_card_icons(self):
        expect(self.ongoing_icon).to_be_visible()
        expect(self.individuals_icon).to_be_visible()
        expect(self.companies_icon).to_be_visible()

    def check_client_risk_breakdown(self):
        expect(self.client_risk_heading).to_be_visible()
        expect(self.client_risk_chart).to_be_visible()

    def check_onboarding_chart(self):
        expect(self.onboarding_heading).to_be_visible()
        expect(self.onboarding_chart).to_be_visible()

    def check_documents_section(self):
        expect(self.documents_heading).to_be_visible()
        expect(self.documents_view_all_button).to_be_visible()
        expect(self.documents_table).to_be_visible()

    def check_documents_table_headers(self):
        expect(self.client_id_header).to_be_visible()
        expect(self.document_header).to_be_visible()
        expect(self.status_header).to_be_visible()
        expect(self.uploaded_date_header).to_be_visible()
        expect(self.expiry_date_header).to_be_visible()

    def check_documents_table_has_rows(self):
        expect(self.documents_table_rows.first).to_be_visible()


    def check_first_client_id_link(self):
        expect(self.first_client_id_link).to_be_visible()
        expect(self.first_client_id_link).to_have_attribute(
            "href",
            __import__("re").compile(
                r"^/nolimit/app/onboarding/entity/process\?"
            )
        )

    def click_first_client_id_link(self):
        self.first_client_id_link.click()

    def check_document_details_displayed(self):
        expect(self.document_names.first).to_be_visible()
        expect(self.document_statuses.first).to_be_visible()
        expect(self.uploaded_dates.first).to_be_visible()
        expect(self.expiry_dates.first).to_be_visible()

