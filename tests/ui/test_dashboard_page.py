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
            re.compile(r".*/nolimit/app/home/?$"),
            timeout=30000
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
        actual_counts = self.get_actual_dashboard_counts()

        self.dashboard.open_dashboard()

        expected = actual_counts["ongoing"]

        expect(self.dashboard.ongoing_card.locator("h3")).to_have_text(
            f"{expected:,}",
            timeout=30000
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
        actual_counts = self.get_actual_dashboard_counts()

        # Return to Dashboard
        self.dashboard.open_dashboard()

        expected_count = actual_counts["individuals"]

        # Wait for the Dashboard to show the final count
        expect(
            self.dashboard.individual_card.locator("h3")
        ).to_have_text(
            f"{expected_count:,}",
            timeout=30000
        )

        print(f"Dashboard Individuals: {expected_count}")
        print(f"Expected Individuals: {expected_count}")

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
        actual_counts = self.get_actual_dashboard_counts()

        # Return to Dashboard
        self.dashboard.open_dashboard()

        expected_count = actual_counts["companies"]

        # Wait for the Dashboard to show the final count
        expect(
            self.dashboard.company_card.locator("h3")
        ).to_have_text(
            f"{expected_count:,}",
            timeout=30000
        )

        print(f"Dashboard Companies: {expected_count}")
        print(f"Expected Companies: {expected_count}")

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


    # =====================================
    # Additional live, read-only Dashboard tests
    # =====================================

    def test_negative_dashboard_url_does_not_expose_password(self):
        password = os.getenv("TEST_PASSWORD")
        assert password and password not in self.page.url

    def test_negative_dashboard_card_counts_not_invalid(self):
        self.dashboard.verify_no_invalid_card_numbers()

    def test_negative_ongoing_count_not_negative(self):
        assert self.dashboard.get_ongoing_count() >= 0

    def test_negative_individual_count_not_negative(self):
        assert self.dashboard.get_individual_count() >= 0

    def test_negative_company_count_not_negative(self):
        assert self.dashboard.get_company_count() >= 0

    def test_dashboard_counts_are_integers(self):
        for getter in (
            self.dashboard.get_ongoing_count,
            self.dashboard.get_individual_count,
            self.dashboard.get_company_count,
        ):
            assert isinstance(getter(), int)

    def test_dashboard_refresh_keeps_heading_and_cards(self):
        self.page.reload(wait_until="domcontentloaded")
        self.dashboard.verify_dashboard_heading()
        self.dashboard.verify_ongoing_card_visible()
        self.dashboard.verify_individual_card_visible()
        self.dashboard.verify_company_card_visible()

    def test_dashboard_refresh_keeps_charts(self):
        self.page.reload(wait_until="domcontentloaded")
        self.dashboard.verify_risk_chart_visible()
        self.dashboard.verify_onboarding_chart_visible()

    def test_dashboard_charts_have_nonzero_canvas_dimensions(self):
        self.dashboard.verify_canvases_have_pixels()

    def test_client_risk_chart_horizontal_scroll(self):
        self.dashboard.verify_risk_chart_scrollable()

    def test_dashboard_chart_headings_are_visible(self):
        self.dashboard.verify_chart_accessible_names()

    def test_documents_table_is_visible(self):
        self.dashboard.verify_documents_table_visible()

    def test_documents_table_has_exactly_five_columns(self):
        self.dashboard.verify_document_table_headers()

    def test_documents_table_has_records(self):
        expect(self.dashboard.document_rows().first).to_be_visible(timeout=20000)

    def test_negative_documents_client_links_match_ids(self):
        self.dashboard.verify_document_links_match_ids()

    def test_negative_documents_have_valid_uploaded_and_expiry_dates(self):
        self.dashboard.verify_document_dates()

    def test_negative_documents_have_filenames_and_matching_icons(self):
        self.dashboard.verify_document_names_and_icons()

    def test_negative_documents_status_not_missing(self):
        self.dashboard.verify_document_statuses()

    def test_documents_allow_multiple_files_for_same_client(self):
        # Duplicated Client IDs are valid when the document names differ.
        records = self.dashboard.document_data()
        assert len(records) >= 1
        for record in records:
            assert record["client_id"] and record["document"]

    def test_documents_view_all_button_visible(self):
        expect(self.dashboard.get_view_all_button()).to_be_visible()

    def test_documents_view_all_button_enabled(self):
        expect(self.dashboard.get_view_all_button()).to_be_enabled()

    def test_documents_view_all_navigates_away_from_dashboard(self):
        self.dashboard.get_view_all_button().click()
        expect(self.page).not_to_have_url(
            re.compile(r".*/nolimit/app/dashboard/?$")
        )
        assert "/nolimit/app/" in self.page.url, (
            f"Unexpected View All destination: {self.page.url}"
        )

    @pytest.mark.parametrize("client_type", ["individual", "entity"])
    def test_document_client_type_links_are_valid(self, client_type):
        from urllib.parse import urlsplit, parse_qs
        records = [r for r in self.dashboard.document_data()
                   if f"/{client_type}/process" in r["href"]]
        if not records:
            pytest.skip(f"No {client_type} document rows in current QA data")
        for record in records:
            parsed = urlsplit(record["href"])
            assert parsed.path.endswith(f"/{client_type}/process")
            assert parse_qs(parsed.query).get("client") == [record["client_id"]]

    @pytest.mark.parametrize("viewport", [(1280, 800), (768, 1024), (390, 844)],
                             ids=["desktop", "tablet", "mobile"])
    def test_dashboard_responsive_core_content(self, viewport):
        self.page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
        self.dashboard.verify_dashboard_heading()
        self.dashboard.verify_ongoing_card_visible()
        self.dashboard.verify_individual_card_visible()
        self.dashboard.verify_company_card_visible()

    def test_dashboard_document_links_have_accessible_text(self):
        for link in self.dashboard.client_id_links.all():
            assert link.inner_text().strip()


    # Extended, non-destructive regression tests
    def test_dashboard_card_count_display_format(self):
        self.dashboard.verify_card_count_format()

    def test_negative_dashboard_cards_are_not_duplicated(self):
        self.dashboard.verify_no_duplicate_dashboard_cards()

    def test_negative_dashboard_document_links_do_not_leave_origin(self):
        self.dashboard.verify_document_links_stay_on_same_origin()

    def test_dashboard_client_links_keyboard_focusable(self):
        self.dashboard.focus_first_client_link_by_keyboard()

    def test_dashboard_sidebar_home_and_return(self):
        self.dashboard.navigate_home_from_dashboard()
        self.dashboard.verify_dashboard_after_return()

    def test_negative_dashboard_document_status_values_not_empty(self):
        statuses = self.dashboard.document_status_values()
        assert statuses, "No document statuses were loaded"
        assert all(isinstance(s, str) and s.strip() for s in statuses)

    def test_dashboard_count_cards_have_accessible_headings(self):
        for title in ("Ongoing Onboarding", "Individuals", "Companies"):
            expect(self.dashboard.get_card(title).get_by_role(
                "heading", name=title, exact=True
            )).to_be_visible()

    def test_negative_dashboard_documents_no_broken_client_hrefs(self):
        for record in self.dashboard.document_data():
            assert record["href"].startswith("/nolimit/app/onboarding/"), record
            assert "client=" in record["href"], record


@pytest.mark.ui
class TestDashboardUnauthenticated:
    @pytest.fixture(autouse=True)
    def setup_unauthenticated(self, browser, base_url):
        from urllib.parse import urlsplit
        parsed = urlsplit(base_url)
        self.dashboard_url = f"{parsed.scheme}://{parsed.netloc}/nolimit/app/dashboard"
        self.context = browser.new_context()
        self.page = self.context.new_page()
        yield
        self.context.close()

    def test_negative_dashboard_requires_login(self):
        self.page.goto(self.dashboard_url, wait_until="domcontentloaded")
        expect(self.page).to_have_url(re.compile(r".*/nolimit/login/?$"), timeout=20000)
        expect(self.page.locator(".dashboard-page")).to_have_count(0)

    def test_negative_dashboard_refresh_without_login(self):
        self.page.goto(self.dashboard_url, wait_until="domcontentloaded")
        expect(self.page).to_have_url(re.compile(r".*/nolimit/login/?$"), timeout=20000)
        self.page.reload(wait_until="domcontentloaded")
        expect(self.page).to_have_url(re.compile(r".*/nolimit/login/?$"), timeout=20000)
        expect(self.page.locator(".dashboard-page")).to_have_count(0)


@pytest.mark.ui
class TestDashboardSession:
    @pytest.fixture(autouse=True)
    def setup_session(self, page: Page, base_url: str):
        from pages.homePage import HomePage

        self.page = page

        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")

        assert email, "Please set TEST_EMAIL"
        assert password, "Please set TEST_PASSWORD"

        # Initialize LoginPage
        self.login_page = LoginPage(page)

        # Perform login
        self.login_page.open(base_url)
        self.login_page.enter_email(email)
        self.login_page.enter_password(password)
        self.login_page.click_login()

        # Wait for successful login
        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$"),
            timeout=30000
        )

        # Verify successful login
        expect(
            page.get_by_role(
                "link",
                name=re.compile("Dashboard", re.I)
            )
        ).to_be_visible(timeout=15000)

        # Initialize page objects
        self.home = HomePage(page)
        self.dashboard = DashboardPage(page)

        # Navigate to Dashboard
        self.dashboard.open_dashboard()

        expect(
            page.get_by_role(
                "heading",
                name="Dashboard",
                exact=True
            )
        ).to_be_visible(timeout=15000)

        self.dashboard_url = self.dashboard.dashboard_url()

    def test_negative_dashboard_not_accessible_after_logout(self):
        dashboard_url = self.page.url
        self.home.logout()

        expect(self.page).to_have_url(
            re.compile(r".*/nolimit/login/?$"), timeout=30000
        )
        print("After logout URL:", self.page.url)
        print("After logout cookie names:",
              [c["name"] for c in self.page.context.cookies()])
        print("After logout localStorage keys:",
              self.page.evaluate("Object.keys(localStorage)"))
        print("After logout sessionStorage keys:",
              self.page.evaluate("Object.keys(sessionStorage)"))

        # Navigate back without clearing storage: this tests the real logout.
        self.page.goto(dashboard_url, wait_until="domcontentloaded")
        print("After reopening URL:", self.page.url)
        print("After reopening cookie names:",
              [c["name"] for c in self.page.context.cookies()])
        print("After reopening localStorage keys:",
              self.page.evaluate("Object.keys(localStorage)"))
        print("After reopening sessionStorage keys:",
              self.page.evaluate("Object.keys(sessionStorage)"))

        # Check the actual protected content as well as the redirect.
        # Neither assertion is relaxed: a persistent Dashboard is a failure.
        try:
            expect(self.page).to_have_url(
                re.compile(r".*/nolimit/login/?$"), timeout=30000
            )
        finally:
            print("Final URL:", self.page.url)
            print("Dashboard heading visible:",
                  self.page.get_by_role(
                      "heading", name="Dashboard", exact=True
                  ).is_visible())
            print("Session-expired notice visible:",
                  self.page.get_by_text(
                      "Your session has expired. Please log in again.",
                      exact=False
                  ).is_visible())

        expect(self.page.get_by_role(
            "heading", name="Dashboard", exact=True
        )).not_to_be_visible(timeout=10000)

        new_tab = self.page.context.new_page()
        try:
            new_tab.goto(dashboard_url, wait_until="domcontentloaded")
            expect(new_tab).to_have_url(
                re.compile(r".*/nolimit/login/?$"), timeout=30000
            )
            expect(new_tab.get_by_role(
                "heading", name="Dashboard", exact=True
            )).not_to_be_visible(timeout=10000)
        finally:
            new_tab.close()

    def test_negative_browser_back_after_dashboard_logout(self):
        self.home.logout()
        self.page.go_back(wait_until="domcontentloaded")
        expect(self.page).to_have_url(re.compile(r".*/nolimit/login/?$"), timeout=20000)
        expect(self.page.locator(".dashboard-page")).to_have_count(0)


@pytest.mark.ui
class TestDashboardFaultInjection:
    """Opt-in tests: configure the real dashboard API route and expected UI behavior.

    The app's exact API endpoint and error/empty-state contract have not been
    provided. These tests deliberately skip rather than guess an endpoint or
    treat any arbitrary text as a passing empty/error state.
    """

    @pytest.fixture(autouse=True)
    def setup_fault_injection(self, page: Page, base_url: str):
        self.page = page
        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")
        assert email and password, "Set TEST_EMAIL and TEST_PASSWORD"
        login = LoginPage(page)
        login.open(base_url)
        login.enter_email(email)
        login.enter_password(password)
        login.click_login()
        expect(page).to_have_url(re.compile(r".*/nolimit/app/home/?$"), timeout=30000)
        self.dashboard = DashboardPage(page)

    def _route_and_open(self, status, payload):
        import json
        pattern = os.getenv("DASHBOARD_DOCUMENTS_API_PATTERN")
        if not pattern:
            pytest.skip("Set DASHBOARD_DOCUMENTS_API_PATTERN to the verified Documents API URL glob")
        hits = []
        def mock(route):
            hits.append(route.request.url)
            route.fulfill(status=status, content_type="application/json", body=json.dumps(payload))
        self.page.route(pattern, mock)
        self.dashboard.open_dashboard()
        expect(self.dashboard.documents_card).to_be_visible(timeout=15000)
        # Wait for a matching request; avoid falsely passing a test where mocking never happened.
        self.page.wait_for_timeout(1500)
        assert hits, f"No request matched API pattern {pattern!r}; verify the endpoint"

    def test_negative_documents_empty_state_with_mock_api(self):
        import json
        payload_json = os.getenv("DASHBOARD_DOCUMENTS_EMPTY_JSON")
        expected = os.getenv("DASHBOARD_DOCUMENTS_EMPTY_TEXT")
        if not payload_json or not expected:
            pytest.skip("Configure DASHBOARD_DOCUMENTS_EMPTY_JSON and DASHBOARD_DOCUMENTS_EMPTY_TEXT from app contract")
        self._route_and_open(200, json.loads(payload_json))
        expect(self.dashboard.documents_card.get_by_text(expected, exact=False)).to_be_visible(timeout=15000)
        expect(self.dashboard.document_rows()).to_have_count(0, timeout=15000)

    def test_negative_documents_api_error_shows_expected_feedback(self):
        expected = os.getenv("DASHBOARD_DOCUMENTS_ERROR_TEXT")
        if not expected:
            pytest.skip("Configure DASHBOARD_DOCUMENTS_ERROR_TEXT from verified app contract")
        self._route_and_open(500, {"message": "Injected QA test failure"})
        expect(self.page.get_by_text(expected, exact=False)).to_be_visible(timeout=15000)


@pytest.mark.ui
class TestDashboardAdditionalRegression:
    """Additional non-destructive checks; uses the existing Page Object Model."""

    @pytest.fixture(autouse=True)
    def setup_dashboard(self, page: Page, base_url: str):
        self.page = page
        email = os.getenv('TEST_EMAIL')
        password = os.getenv('TEST_PASSWORD')
        assert email and password, 'Set TEST_EMAIL and TEST_PASSWORD'
        login = LoginPage(page)
        login.open(base_url)
        login.enter_email(email)
        login.enter_password(password)
        login.click_login()
        expect(page).to_have_url(
            re.compile(r'.*/nolimit/app/home/?$'), timeout=30000
        )
        self.dashboard = DashboardPage(page)
        self.dashboard.open_dashboard()
        self.dashboard.verify_dashboard_heading()

    def test_dashboard_documents_loading_completes(self):
        self.dashboard.wait_for_documents_settled()
        expect(self.dashboard.documents_headers).to_have_count(5)

    def test_dashboard_charts_have_visible_text_context(self):
        self.dashboard.verify_chart_has_text_context()

    def test_negative_dashboard_document_links_do_not_use_javascript_urls(self):
        self.dashboard.wait_for_documents_settled()
        links = self.dashboard.client_id_links
        for index in range(links.count()):
            href = links.nth(index).get_attribute('href') or ''
            assert not re.match(r'^\s*(?:javascript|data):', href, re.I), href

    def test_negative_dashboard_cards_do_not_display_nonfinite_numbers(self):
        self.dashboard.verify_no_invalid_card_numbers()

    def test_negative_dashboard_document_links_do_not_contain_credentials(self):
        self.dashboard.wait_for_documents_settled()
        password = os.getenv('TEST_PASSWORD')
        assert password
        for link in self.dashboard.client_id_links.all():
            href = link.get_attribute('href') or ''
            assert password not in href, 'Password exposed in client link'

    def test_dashboard_chart_remains_visible_after_reload(self):
        self.page.reload(wait_until='domcontentloaded')
        self.dashboard.verify_dashboard_heading()
        self.dashboard.verify_risk_chart_visible()
        self.dashboard.verify_onboarding_chart_visible()
