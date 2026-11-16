
import os
import re

import pytest
from openpyxl import load_workbook
from playwright.sync_api import (
    Page,
    expect,
    TimeoutError as PlaywrightTimeoutError,
)

from pages.loginPage import LoginPage
from pages.profilesPage import ProfilesPage


@pytest.mark.ui
class TestProfilesPage:

    @pytest.fixture(autouse=True)
    def setup_profiles(self, page: Page, base_url: str):
        self.page = page

        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")

        assert email, "Please set TEST_EMAIL."
        assert password, "Please set TEST_PASSWORD."

        page.set_default_navigation_timeout(60000)

        self.login = LoginPage(page)

        try:
            self.login.open(base_url)
        except PlaywrightTimeoutError:
            expect(
                page.get_by_placeholder("Enter email address")
            ).to_be_visible(timeout=15000)

        self.login.enter_email(email)
        self.login.enter_password(password)
        self.login.click_login()

        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$"),
            timeout=45000
        )

        self.profiles = ProfilesPage(page)
        self.profiles.open_profiles()

    # ==========================================
    # 1. Profiles heading
    # ==========================================

    def test_profiles_heading(self):
        self.profiles.verify_heading()

    # ==========================================
    # 2. Description
    # ==========================================

    def test_profiles_description(self):
        self.profiles.verify_description()

    # ==========================================
    # 3. Search input
    # ==========================================

    def test_search_input_visible(self):
        self.profiles.verify_search_input()

    # ==========================================
    # 4. Search icon
    # ==========================================

    def test_search_icon_visible(self):
        self.profiles.verify_search_icon()

    # ==========================================
    # 5. Search placeholder
    # ==========================================

    def test_search_placeholder(self):
        self.profiles.verify_search_placeholder()

    # ==========================================
    # 6. Search accepts characters
    # ==========================================

    def test_search_accepts_characters(self):
        text = "Test123@"

        self.profiles.enter_search_text(text)

        expect(
            self.profiles.search_input
        ).to_have_value(text)

    # ==========================================
    # 7. Search by Client ID
    # ==========================================

    def test_search_by_client_id(self):
        client_id = self.profiles.get_first_row_value(0)

        print(f"Searching Client ID: {client_id}")

        self.profiles.perform_search(client_id)
        self.profiles.verify_search_results(
            0, client_id
        )

    # ==========================================
    # 8. Search by Name
    # ==========================================

    def test_search_by_name(self):
        name = self.profiles.get_first_row_value(1)

        print(f"Searching Name: {name}")

        self.profiles.perform_search(name)
        self.profiles.verify_search_results(
            1, name
        )

    # ==========================================
    # 9. Date picker visible
    # ==========================================

    def test_date_picker_visible(self):
        self.profiles.verify_date_picker()

    # ==========================================
    # 10. Date placeholders
    # ==========================================

    def test_date_placeholders(self):
        self.profiles.verify_date_placeholders()

    # ==========================================
    # 11. Calendar icon
    # ==========================================

    def test_calendar_icon_visible(self):
        self.profiles.verify_calendar_icon()

    # ==========================================
    # 12. Date selection
    # ==========================================

    def test_select_start_and_end_dates(self):
        start, end = self.profiles.select_date_range()

        print(f"Start Date: {start}")
        print(f"End Date: {end}")

        assert start, "Start Date is empty"
        assert end, "End Date is empty"

    # ==========================================
    # 13. Extract button
    # ==========================================

    def test_extract_button_visible(self):
        self.profiles.verify_extract_button()

    # ==========================================
    # 14. Extract icon
    # ==========================================

    def test_extract_down_arrow_icon(self):
        self.profiles.verify_extract_icon()

    # ==========================================
    # 15. Download Excel
    # ==========================================

    def test_extract_downloads_excel(self, tmp_path):
        self.profiles.select_my_files()

        saved_path = (
            self.profiles.download_profiles_excel(
                tmp_path
            )
        )

        print(f"Downloaded Excel: {saved_path.name}")

        assert saved_path.suffix.lower() == ".xlsx"

    # ==========================================
    # 16. Excel contains My Files records
    # ==========================================

    def test_excel_contains_my_files_records(self, tmp_path):
        self.profiles.select_my_files()
        expected = {r['client_id'] for r in self.profiles.get_current_page_records()}
        path = self.profiles.download_profiles_excel(tmp_path)
        workbook = load_workbook(path, read_only=True, data_only=True)
        try:
            sheet = workbook.active
            rows = sheet.iter_rows(values_only=True)
            headers = list(next(rows))
            assert 'Client ID' in headers
            idx = headers.index('Client ID')
            actual = {str(row[idx]).strip() for row in rows if row[idx] is not None}
            assert actual == expected, f'Missing: {expected - actual}; Extra: {actual - expected}'
        finally:
            workbook.close()

    def test_extract_exports_current_page_diagnostic(self, tmp_path):
        """Characterize the observed export scope without assuming it is correct."""
        self.profiles.select_my_files()
        all_records = self.profiles.get_all_records()
        visible_ids = set(self.profiles.current_client_ids())
        path = self.profiles.download_profiles_excel(tmp_path)
        workbook = load_workbook(path, read_only=True, data_only=True)
        try:
            exported_ids = set()
            for sheet in workbook.worksheets:
                rows = sheet.iter_rows(values_only=True)
                headers = next(rows, None)
                assert headers and "Client ID" in headers
                idx = list(headers).index("Client ID")
                for row in rows:
                    if len(row) > idx and row[idx]:
                        exported_ids.add(str(row[idx]).strip())
        finally:
            workbook.close()
        print("Total My Files:", len(all_records))
        print("Visible page IDs:", sorted(visible_ids))
        print("Exported IDs:", sorted(exported_ids))
        assert exported_ids == visible_ids, (
            "Export does not match the currently displayed page. "
            f"Missing: {sorted(visible_ids - exported_ids)}; "
            f"Extra: {sorted(exported_ids - visible_ids)}"
        )

    # ==========================================
    # 17. Client ID header
    # ==========================================

    def test_client_id_header(self):
        self.profiles.verify_header(
            1, "Client ID"
        )

    # ==========================================
    # 18. Client ID value
    # ==========================================

    def test_client_id_value(self):
        client_id = self.profiles.get_first_row_value(0)

        assert re.fullmatch(
            r"SENTINEL[A-Z0-9]+",
            client_id
        ), f"Invalid Client ID: {client_id}"

    # ==========================================
    # 19. Client ID navigation
    # ==========================================

    def test_client_id_redirects_to_verification(self):
        client_id = (
            self.profiles.click_first_client_id()
        )

        self.profiles.verify_verification_navigation(
            client_id
        )

        print(f"Clicked Client ID: {client_id}")
        print(f"Redirected URL: {self.page.url}")

    # ==========================================
    # 20. Name header
    # ==========================================

    def test_name_header(self):
        self.profiles.verify_header(2, "Name")

    # ==========================================
    # 21. Name value
    # ==========================================

    def test_name_value(self):
        name = self.profiles.get_first_row_value(1)

        assert name.strip(), "Name is empty"

    # ==========================================
    # 22. Type header
    # ==========================================

    def test_type_header(self):
        self.profiles.verify_header(3, "Type")

    # ==========================================
    # 23. Type value
    # ==========================================

    def test_type_value(self):
        record_type = self.profiles.get_first_row_value(2)

        assert record_type.casefold() in {
            "individual",
            "entity"
        }, f"Unexpected Type: {record_type}"

    # ==========================================
    # 24. Status header
    # ==========================================

    def test_status_header(self):
        self.profiles.verify_header(4, "Status")

    # ==========================================
    # 25. Status value
    # ==========================================

    def test_status_value(self):
        status = self.profiles.get_first_row_value(3)

        assert status.casefold() == "onboarded", (
            f"Unexpected Status: {status}"
        )

    # ==========================================
    # 26. Onboarded Date header
    # ==========================================

    def test_onboarded_date_header(self):
        self.profiles.verify_header(
            5, "Onboarded Date"
        )

    # ==========================================
    # 27. Onboarded Date value
    # ==========================================

    def test_onboarded_date_value(self):
        value = self.profiles.get_first_row_value(4)

        assert re.fullmatch(
            r"\d{2}-\d{2}-\d{4}",
            value
        ), f"Invalid Onboarded Date: {value}"

    # ==========================================
    # 28. Risk Rating header
    # ==========================================

    def test_risk_rating_header(self):
        self.profiles.verify_header(
            6, "Risk Rating"
        )

    # ==========================================
    # 29. Risk Rating value
    # ==========================================

    def test_risk_rating_value(self):
        rating = self.profiles.get_first_row_value(5)

        assert rating.casefold() in {
            "low",
            "medium",
            "high"
        }, f"Unexpected Risk Rating: {rating}"

    # ==========================================
    # 30. Onboarded By header
    # ==========================================

    def test_onboarded_by_header(self):
        self.profiles.verify_header(
            7, "Onboarded By"
        )

    # ==========================================
    # 31. Onboarded By value
    # ==========================================

    def test_onboarded_by_value(self):
        value = self.profiles.get_first_row_value(6)

        assert value.strip(), (
            "Onboarded By is empty"
        )

    # ==========================================
    # 32. My Files shows logged-in user's records
    # ==========================================

    def test_my_files_shows_logged_in_user_records(self):
        self.profiles.select_my_files()

        records = self.profiles.get_all_records()

        assert records, (
            "No records found under My Files"
        )

        # Obtain expected account name from authenticated header.
        # If the navbar DOM differs, provide TEST_DISPLAY_NAME explicitly.
        logged_in_user = os.getenv("TEST_DISPLAY_NAME")
        if not logged_in_user:
            pytest.skip("Set TEST_DISPLAY_NAME to verify My Files ownership without a hardcoded user")

        for record in records:
            actual_user = record["onboarded_by"]

            print(
                f"Onboarded By: {actual_user}"
            )

            assert (
                actual_user.casefold()
                == logged_in_user.casefold()
            ), (
                f"My Files contains a record onboarded "
                f"by '{actual_user}', expected "
                f"'{logged_in_user}'"
            )

    # ==========================================
    # 33. My Files folder icon
    # ==========================================

    def test_my_files_folder_icon(self):
        self.profiles.select_my_files()
        self.profiles.verify_my_files_icon()

    # ==========================================
    # 34. All Files shows My Files records too
    # ==========================================

    def test_all_files_shows_all_users_records(self):
        self.profiles.select_my_files()
        my_records = self.profiles.get_all_records()
        my_ids = {r["client_id"] for r in my_records}
        print("\n=== My Files ===")
        print("My Files count:", len(my_ids))
        self.profiles.debug_pagination()

        self.profiles.select_all_files()
        print("\n=== All Files (before pagination collection) ===")
        self.profiles.debug_pagination()
        all_records = self.profiles.get_all_records()
        all_ids = {r["client_id"] for r in all_records}
        missing_ids = sorted(my_ids - all_ids)
        print("All Files count:", len(all_ids))
        print("Missing IDs:", missing_ids)
        assert not missing_ids, (
            f"{len(missing_ids)} My Files records are missing from All Files: {missing_ids}"
        )

    # ==========================================
    # 35. All Files folder icon
    # ==========================================

    def test_all_files_folder_icon(self):
        self.profiles.select_all_files()
        self.profiles.verify_all_files_icon()


@pytest.mark.ui
class TestProfilesAdditionalRegression:
    @pytest.fixture(autouse=True)
    def setup_profiles(self, page: Page, base_url: str):
        email, password = os.getenv('TEST_EMAIL'), os.getenv('TEST_PASSWORD')
        assert email and password, 'Set TEST_EMAIL and TEST_PASSWORD'
        self.page = page
        login = LoginPage(page)
        login.open(base_url)
        login.enter_email(email)
        login.enter_password(password)
        login.click_login()
        expect(page).to_have_url(re.compile(r'.*/nolimit/app/home/?$'), timeout=45000)
        self.profiles = ProfilesPage(page)
        self.profiles.open_profiles()

    def test_search_clear_control(self):
        self.profiles.search_input.fill('SentinelExample')
        self.profiles.clear_search()

    def test_partial_client_id_search(self):
        self.profiles.select_all_files()
        ids = self.profiles.current_client_ids()
        if not ids:
            pytest.skip('No profile records available')
        query = ids[0][:min(12, len(ids[0]))]
        self.profiles.perform_search(query)
        self.profiles.wait_for_search_to_settle()
        results = self.profiles.assert_rows_match_search(query)
        assert results, 'Known partial Client ID returned no records'

    def test_partial_name_search(self):
        self.profiles.select_all_files()
        records = self.profiles.get_current_page_records(allow_empty=True)
        if not records:
            pytest.skip('No profile records available')
        name = records[0]['name']
        query = name[:max(1, min(4, len(name)))]
        self.profiles.perform_search(query)
        self.profiles.wait_for_search_to_settle()
        results = self.profiles.assert_rows_match_search(query)
        assert results, 'Known partial name returned no records'

    def test_negative_search_no_unrelated_results(self):
        self.profiles.perform_search('SENTINEL_NOT_A_REAL_CLIENT_987654321')
        self.profiles.wait_for_search_to_settle()
        self.profiles.assert_rows_match_search('SENTINEL_NOT_A_REAL_CLIENT_987654321')

    @pytest.mark.parametrize('query', ['<script>alert(1)</script>', '" OR 1=1 --', '@#$%^&*'])
    def test_negative_search_special_input_safe(self, query):
        self.profiles.perform_search(query)
        self.profiles.wait_for_search_to_settle()
        expect(self.profiles.heading).to_be_visible()
        # This checks DOM safety, not backend injection resistance.
        assert self.page.locator('script').filter(has_text='alert(1)').count() == 0

    def test_negative_profile_rows_have_valid_required_values(self):
        self.profiles.verify_table_row_integrity()

    def test_negative_duplicate_client_ids_on_current_page(self):
        ids = self.profiles.current_client_ids()
        assert len(ids) == len(set(ids)), 'Duplicate Client IDs on one page'

    def test_profile_link_matches_client_type_and_id(self):
        self.profiles.select_all_files()
        if self.profiles.rows.count() == 0:
            pytest.skip('No profile records available')
        kind, client_id, href = self.profiles.get_profile_link_info()
        assert kind in ('individual', 'entity')
        assert href is not None
        assert f'/profiles/{kind}/process?' in href, href
        from urllib.parse import urlparse, parse_qs
        params = parse_qs(urlparse(href).query)
        assert params.get('client') == [client_id], (client_id, href)
        assert params.get('step') == ['verification'], href

    def test_profile_link_navigates_to_correct_client(self):
        self.profiles.select_all_files()
        if self.profiles.rows.count() == 0:
            pytest.skip('No profile records available')
        kind, client_id, _ = self.profiles.get_profile_link_info()
        self.profiles.rows.first.locator('a.table-link').click()
        from urllib.parse import urlparse, parse_qs
        path = urlparse(self.page.url)
        assert path.path.endswith(f'/profiles/{kind}/process'), self.page.url
        params = parse_qs(path.query)
        assert params.get('client') == [client_id]
        assert params.get('step') == ['verification']
        expect(self.page.get_by_text(client_id, exact=True).first).to_be_visible(timeout=20000)

    def test_profile_page_survives_reload(self):
        self.page.reload(wait_until='domcontentloaded')
        expect(self.profiles.heading).to_be_visible(timeout=20000)
        expect(self.profiles.table).to_be_visible(timeout=20000)

    def test_negative_client_links_do_not_use_external_or_javascript_urls(self):
        for link in self.profiles.rows.locator('a.table-link').all():
            href = link.get_attribute('href') or ''
            assert href.startswith('/nolimit/app/profiles/'), href

    def test_my_files_all_files_tab_state(self):
        self.profiles.select_my_files()
        self.profiles.select_all_files()
        self.profiles.select_my_files()

    def test_negative_unauthenticated_profiles_redirects_to_login(self, browser, base_url):
        # New isolated browser context, no authentication state.
        context = browser.new_context()
        try:
            page = context.new_page()
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            page.goto(f'{parsed.scheme}://{parsed.netloc}/nolimit/app/profiles', wait_until='domcontentloaded')
            expect(page).to_have_url(re.compile(r'.*/nolimit/login/?(?:\?.*)?$'), timeout=20000)
        finally:
            context.close()



@pytest.mark.ui
class TestProfilesExtendedRegression:
    @pytest.fixture(autouse=True)
    def setup_profiles(self, page: Page, base_url: str):
        email, password = os.getenv('TEST_EMAIL'), os.getenv('TEST_PASSWORD')
        assert email and password, 'Set TEST_EMAIL and TEST_PASSWORD'
        self.page = page
        login = LoginPage(page)
        login.open(base_url)
        login.enter_email(email)
        login.enter_password(password)
        login.click_login()
        expect(page).to_have_url(re.compile(r'.*/nolimit/app/home/?$'), timeout=45000)
        self.profiles = ProfilesPage(page)
        self.profiles.open_profiles()

    def _records(self):
        self.profiles.select_all_files()
        return self.profiles.get_current_page_records()

    def _excel(self, tmp_path):
        from datetime import datetime
        path = self.profiles.download_profiles_excel(tmp_path)
        wb = load_workbook(path, read_only=True, data_only=True)
        try:
            rows = wb.active.iter_rows(values_only=True)
            headers = list(next(rows))
            data = [dict(zip(headers, row)) for row in rows]
            return headers, data
        finally:
            wb.close()

    def test_pagination_first_page_previous_disabled(self):
        self._records()
        assert self.profiles.active_page_number() == 1
        assert self.profiles.pagination_disabled('prev')

    def test_pagination_next_and_previous_records_change(self):
        first = {
            r["client_id"]
            for r in self._records()
        }

        if self.profiles.pagination_disabled("next"):
            pytest.skip("Dataset has only one page")

        # Page 1 -> Page 2
        second = set(self.profiles.navigate_page("next"))

        assert self.profiles.active_page_number() == 2

        assert first.isdisjoint(second), (
            "Same Client IDs found on pages 1 and 2"
        )

        # Page 2 -> Page 1
        self.profiles.navigate_page("prev")

        assert self.profiles.active_page_number() == 1

        # Wait until the original page 1 records are restored.
        returned = set()
        for _ in range(100):
            returned = set(self.profiles.current_client_ids())

            if returned == first:
                break

            self.page.wait_for_timeout(200)

        assert returned == first, (
            "Page 1 records changed after navigating "
            "to page 2 and returning to page 1. "
            f"Missing: {sorted(first - returned)}; "
            f"Extra: {sorted(returned - first)}"
        )

    def test_pagination_last_page_next_disabled(self):
        self._records()
        while not self.profiles.pagination_disabled('next'):
            self.profiles.navigate_page('next')
        assert self.profiles.pagination_disabled('next')
        assert self.profiles.current_client_ids()

    def test_pagination_all_pages_have_unique_client_ids(self):
        self._records()
        records = self.profiles.get_all_records()
        ids = [r['client_id'] for r in records]
        assert len(ids) == len(set(ids))

    def test_search_case_insensitive_client_id(self):
        client_id = self._records()[0]['client_id']
        self.profiles.perform_search(client_id.lower())
        records = self.profiles.wait_for_search_results(client_id.lower())
        assert any(r['client_id'] == client_id for r in records), 'Lowercase Client ID search did not match'

    def test_search_empty_query_keeps_records(self):
        initial = self._records()
        self.profiles.perform_search('')
        self.profiles.wait_for_table()
        assert self.profiles.get_current_page_records(), 'Empty search unexpectedly removed all records'

    def test_search_clear_restores_results(self):
        known = self._records()[0]['client_id']
        self.profiles.perform_search(known)
        assert self.profiles.wait_for_search_results(known)
        self.profiles.clear_search()
        self.profiles.wait_for_profile_records()
        assert self.profiles.get_current_page_records()

    def test_search_no_match_empty_state(self):
        self._records()
        self.profiles.perform_search('SENTINEL_NOMATCH_999999999999')
        self.profiles.wait_for_search_to_settle()
        expect(self.profiles.rows).to_have_count(0, timeout=20000)

    def test_search_long_unusual_input_safe(self):
        self._records()
        query = 'Z' * 256 + "'<>&"
        self.profiles.perform_search(query)
        self.profiles.wait_for_search_to_settle()
        expect(self.profiles.heading).to_be_visible()
        expect(self.profiles.rows).to_have_count(0, timeout=20000)

    def test_excel_headers_and_current_page_values(self, tmp_path):
        expected = self._records()
        headers, data = self._excel(tmp_path)
        assert headers == ['Serial No', 'Client ID', 'Name', 'Type', 'Status',
                           'Onboarded Date', 'Risk Rating', 'Onboarded By']
        assert len(data) == len(expected)
        by_id = {str(r['Client ID']).strip(): r for r in data}
        assert set(by_id) == {r['client_id'] for r in expected}
        for record in expected:
            exported = by_id[record['client_id']]
            for ui, excel in [('name', 'Name'), ('type', 'Type'),
                              ('risk_rating', 'Risk Rating'), ('onboarded_by', 'Onboarded By')]:
                assert str(exported[excel]).strip().casefold() == record[ui].strip().casefold(), (ui, record, exported)

    def test_excel_export_second_page(self, tmp_path):
        self._records()
        if self.profiles.pagination_disabled('next'):
            pytest.skip('Dataset has only one page')
        self.profiles.navigate_page('next')
        expected = set(self.profiles.current_client_ids())
        _, data = self._excel(tmp_path)
        assert {str(r['Client ID']).strip() for r in data} == expected

    def test_excel_export_last_page(self, tmp_path):
        self._records()
        while not self.profiles.pagination_disabled('next'):
            self.profiles.navigate_page('next')
        expected = set(self.profiles.current_client_ids())
        _, data = self._excel(tmp_path)
        assert {str(r['Client ID']).strip() for r in data} == expected

    def test_excel_export_after_client_id_search(self, tmp_path):
        known = self._records()[0]['client_id']
        self.profiles.perform_search(known)
        self.profiles.wait_for_search_results(known)
        expected = set(self.profiles.current_client_ids())
        assert known in expected
        _, data = self._excel(tmp_path)
        assert {str(r['Client ID']).strip() for r in data} == expected

    def test_date_range_same_day_selection(self):
        from datetime import datetime
        record = self._records()[0]
        day = datetime.strptime(record['onboarded_date'], '%d-%m-%Y').date()
        # Picker calendar clicks are more reliable than guessing input format.
        self.profiles.start_date.click()
        popup = self.page.locator('.ant-picker-dropdown:visible')
        expect(popup).to_be_visible()
        # Only run when the date is in the visible calendar; otherwise report a clear skip.
        cell = popup.locator(f'td.ant-picker-cell-in-view[title="{day.isoformat()}"]').first
        if cell.count() == 0:
            pytest.skip('Known record date is outside the currently visible calendar month')
        cell.click()
        cell = popup.locator(f'td.ant-picker-cell-in-view[title="{day.isoformat()}"]').first
        cell.click()
        expect(self.profiles.start_date).not_to_have_value('')
        expect(self.profiles.end_date).not_to_have_value('')

    def test_date_range_clear_control(self):
        self._records()
        self.profiles.select_date_range()
        self.profiles.clear_date_range()
        self.profiles.wait_for_profile_records()

    def test_date_range_records_within_selected_dates(self):
        from datetime import datetime
        self._records()
        start_text, end_text = self.profiles.select_date_range()
        # Date picker may display DD-MM-YYYY or YYYY-MM-DD; normalize both.
        def parse(value):
            for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d'):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    pass
            raise AssertionError(f'Unexpected date picker format: {value}')
        start, end = parse(start_text), parse(end_text)
        self.profiles.wait_for_table()
        records = self.profiles.get_current_page_records(allow_empty=True)
        for record in records:
            day = datetime.strptime(record['onboarded_date'], '%d-%m-%Y').date()
            assert start <= day <= end, f'Record outside date range: {record}'

    def test_switch_tabs_preserves_valid_table(self):
        self.profiles.select_my_files()
        assert self.profiles.get_current_page_records()
        self.profiles.select_all_files()
        assert self.profiles.get_current_page_records()
        self.profiles.select_my_files()
        assert self.profiles.get_current_page_records()
