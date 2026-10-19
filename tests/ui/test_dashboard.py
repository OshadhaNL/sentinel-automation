
import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.dashboardPage import DashboardPage


@pytest.mark.ui
@pytest.mark.smoke
class TestDashboard:

    @pytest.fixture(autouse=True)
    def setup_dashboard(
        self,
        page: Page,
        base_url: str,
    ):
        """
        Log in first, then open Dashboard using the sidebar.
        """
        self.page = page

        # Login
        self.login_page = LoginPage(page)
        self.login_page.open(base_url)

        self.login_page.enter_email("Oshadha@northlark.com")
        self.login_page.enter_password("5e11Piwu")
        self.login_page.click_login()

        expect(page).to_have_url(
            __import__("re").compile(r".*/nolimit/app/home/?$")
        )

        # Navigate to Dashboard from the sidebar.
        page.get_by_role(
            "link", name="Dashboard", exact=False
        ).click()

        expect(page).to_have_url(
            __import__("re").compile(r".*/nolimit/app/dashboard/?$")
        )

        self.dashboard = DashboardPage(page)

    def test_dashboard_heading_is_displayed(self):
        self.dashboard.check_dashboard_heading()

    def test_ongoing_onboarding_card_is_displayed(self):
        self.dashboard.check_ongoing_onboarding()

    def test_individuals_card_is_displayed(self):
        self.dashboard.check_individuals()

    def test_companies_card_is_displayed(self):
        self.dashboard.check_companies()

    def test_dashboard_card_numbers_are_displayed(self):
        self.dashboard.check_dashboard_card_numbers()

    def test_dashboard_card_icons_are_displayed(self):
        self.dashboard.check_dashboard_card_icons()

    def test_client_risk_breakdown_heading_and_chart_are_displayed(self):
        self.dashboard.check_client_risk_breakdown()

    def test_onboarding_heading_and_chart_are_displayed(self):
        self.dashboard.check_onboarding_chart()

    def test_documents_section_is_displayed(self):
        self.dashboard.check_documents_section()

    def test_documents_table_headers_are_displayed(self):
        self.dashboard.check_documents_table_headers()

    def test_documents_table_contains_rows(self):
        self.dashboard.check_documents_table_has_rows()

    def test_first_client_id_link_is_displayed_with_expected_url(self):
        self.dashboard.check_first_client_id_link()

    def test_document_details_are_displayed(self):
        self.dashboard.check_document_details_displayed()

    def test_first_client_id_link_redirects_to_entity_page(self):
        self.dashboard.click_first_client_id_link()

        # Verify navigation to the onboarding entity/process page.
        expect(self.page).to_have_url(
            __import__("re").compile(
                r".*/nolimit/app/onboarding/entity/process\?.*"
            )
        )
