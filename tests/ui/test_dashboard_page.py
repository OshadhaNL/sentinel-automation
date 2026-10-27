
import os
import re

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.dashboardPage import DashboardPage


@pytest.mark.ui
class TestDashboardPage:

    @pytest.fixture(autouse=True)
    def setup_dashboard(self, page: Page, base_url: str):
        self.page = page

        test_email = os.getenv("TEST_EMAIL")
        test_password = os.getenv("TEST_PASSWORD")

        assert test_email, "Please set TEST_EMAIL."
        assert test_password, "Please set TEST_PASSWORD."

        # Login
        self.login_page = LoginPage(page)
        self.login_page.open(base_url)
        self.login_page.enter_email(test_email)
        self.login_page.enter_password(test_password)
        self.login_page.click_login()

        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$")
        )

        self.dashboard = DashboardPage(page)
        self.dashboard.open_dashboard()

    # =====================================
    # Combined Dashboard count helper
    # =====================================

    def get_actual_dashboard_counts(self):
        """
        Expected Dashboard counts:

        Ongoing = Pending Ongoing

        Individuals = Pending Individuals
                    + Onboarded Profile Individuals

        Companies = Pending Entities
                  + Onboarded Profile Entities
        """

        # Pending Onboarding
        self.dashboard.open_pending_onboarding()
        pending = self.dashboard.get_pending_onboarding_counts()

        print("\n===== Pending Onboarding =====")
        print(f"Ongoing: {pending['ongoing']}")
        print(f"Individuals: {pending['individuals']}")
        print(f"Entities: {pending['companies']}")

        # Profiles -> All Files
        self.dashboard.open_profiles_all_files()
        profiles = self.dashboard.get_profiles_counts()

        print("\n===== Profiles - All Files =====")
        print(f"Onboarded Individuals: {profiles['individuals']}")
        print(f"Onboarded Entities: {profiles['companies']}")

        counts = {
            "ongoing": pending["ongoing"],
            "individuals": (
                pending["individuals"]
                + profiles["individuals"]
            ),
            "companies": (
                pending["companies"]
                + profiles["companies"]
            )
        }

        print("\n===== Expected Dashboard Counts =====")
        print(f"Ongoing: {counts['ongoing']}")
        print(f"Individuals: {counts['individuals']}")
        print(f"Companies: {counts['companies']}")
        print("=====================================\n")

        return counts

    # =====================================
    # 1. Dashboard heading
    # =====================================

    def test_dashboard_heading(self):
        self.dashboard.verify_dashboard_heading()

    # =====================================
    # 2. Ongoing card
    # =====================================

    def test_ongoing_onboarding_card_visible(self):
        self.dashboard.verify_ongoing_card_visible()

    # =====================================
    # 3. Ongoing count
    # =====================================

    def test_ongoing_onboarding_count(self):
        dashboard_count = self.dashboard.get_ongoing_count()
        actual_counts = self.get_actual_dashboard_counts()

        print(f"Dashboard Ongoing: {dashboard_count}")
        print(f"Expected Ongoing: {actual_counts['ongoing']}")

        assert dashboard_count == actual_counts["ongoing"], (
            f"Ongoing mismatch: Dashboard={dashboard_count}, "
            f"Expected={actual_counts['ongoing']}"
        )

    # =====================================
    # 4. Ongoing icon
    # =====================================

    def test_ongoing_checklist_icon(self):
        self.dashboard.verify_ongoing_icon()

    # =====================================
    # 5. Individuals card
    # =====================================

    def test_individuals_card_visible(self):
        self.dashboard.verify_individual_card_visible()

    # =====================================
    # 6. Individuals count
    # =====================================

    def test_individuals_count(self):
        dashboard_count = self.dashboard.get_individual_count()
        actual_counts = self.get_actual_dashboard_counts()

        print(f"Dashboard Individuals: {dashboard_count}")
        print(f"Expected Individuals: {actual_counts['individuals']}")

        assert dashboard_count == actual_counts["individuals"], (
            f"Individuals mismatch: Dashboard={dashboard_count}, "
            f"Expected={actual_counts['individuals']}"
        )

    # =====================================
    # 7. Individual icon
    # =====================================

    def test_individual_user_tie_icon(self):
        self.dashboard.verify_individual_icon()

    # =====================================
    # 8. Companies card
    # =====================================

    def test_companies_card_visible(self):
        self.dashboard.verify_company_card_visible()

    # =====================================
    # 9. Companies count
    # =====================================

    def test_companies_count(self):
        dashboard_count = self.dashboard.get_company_count()
        actual_counts = self.get_actual_dashboard_counts()

        print(f"Dashboard Companies: {dashboard_count}")
        print(f"Expected Companies: {actual_counts['companies']}")

        assert dashboard_count == actual_counts["companies"], (
            f"Companies mismatch: Dashboard={dashboard_count}, "
            f"Expected={actual_counts['companies']}"
        )

    # =====================================
    # 10. Company icon
    # =====================================

    def test_company_building_icon(self):
        self.dashboard.verify_company_icon()

    # =====================================
    # 11. Risk chart
    # =====================================

    def test_client_risk_breakdown_chart(self):
        self.dashboard.verify_risk_chart_visible()

    # =====================================
    # 12. Onboarding pie chart
    # =====================================

    def test_onboarding_pie_chart(self):
        self.dashboard.verify_onboarding_chart_visible()

    # =====================================
    # 13. In Progress pink
    # =====================================

    def test_in_progress_pie_chart_pink(self):
        self.dashboard.verify_in_progress_pink()

    # =====================================
    # 14. Closed purple
    # =====================================

    def test_closed_pie_chart_purple(self):
        self.dashboard.verify_closed_purple()

    # =====================================
    # 15. Documents heading
    # =====================================

    def test_documents_heading(self):
        self.dashboard.verify_documents_heading()

    # =====================================
    # 16. Client ID column
    # =====================================

    def test_client_id_first_column(self):
        self.dashboard.verify_documents_table_visible()
        self.dashboard.verify_document_header(1, "Client ID")

    # =====================================
    # 17. Document column
    # =====================================

    def test_document_second_column(self):
        self.dashboard.verify_document_header(2, "Document")

    # =====================================
    # 18. Status column
    # =====================================

    def test_status_third_column(self):
        self.dashboard.verify_document_header(3, "Status")

    # =====================================
    # 19. Uploaded Date column
    # =====================================

    def test_uploaded_date_fourth_column(self):
        self.dashboard.verify_document_header(4, "Uploaded Date")

    # =====================================
    # 20. Date of Expiry column
    # =====================================

    def test_date_of_expiry_fifth_column(self):
        self.dashboard.verify_document_header(
            5, "Date of Expiry"
        )

    # =====================================
    # 21. Client ID navigation
    # =====================================

    def test_client_id_redirects_to_kyc_form(self):
        self.dashboard.verify_documents_table_visible()

        client_id = self.dashboard.click_first_client_id()

        print(f"Clicked Client ID: {client_id}")

        self.dashboard.verify_client_kyc_navigation(client_id)

        print(f"Navigated to: {self.page.url}")
