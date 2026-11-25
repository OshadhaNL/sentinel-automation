import re
import uuid

from playwright.sync_api import Page, expect

from pages.screeningPage import ScreeningPage
from pages.screeningResultsPage import ScreeningResultsPage


class ScreeningDailyPage(ScreeningPage):

    DAILY_COLUMNS = (
        "Name",
        "Profile ID",
        "Mandatory Actions",
        "Resolved Hits",
        "Total Hits",
        "Review Required",
        "Last Modified By",
        "Created Date",
        "Last Screened Date",
    )

    QA_PREFIX = "QA Automation Screening "

    def __init__(self, page: Page):
        super().__init__(page)

    # ==================================================
    # TEST DATA
    # ==================================================

    @staticmethod
    def unique_name():
        suffix = "".join(
            chr(97 + int(character, 16))
            for character in uuid.uuid4().hex[:10]
        )

        return f"QA Automation Screening {suffix}"

    # ==================================================
    # SINGLE SCREENING LOCATORS
    # ==================================================

    @property
    def individual_option(self):
        return self.page.locator(
            'input[name="entityType"][value="P"]'
        )

    @property
    def organization_option(self):
        return self.page.locator(
            'input[name="entityType"][value="O"]'
        )

    @property
    def screening_name(self):
        return self.page.locator('input[name="name"]')

    @property
    def ongoing_checkbox(self):
        return self.page.locator('input[name="ongoing"]')

    @property
    def analyze_action(self):
        return self.page.locator("main").get_by_role(
            "button",
            name=re.compile(r"\bAnalyze\s*$", re.I),
        )

    @property
    def back_to_screening_button(self):
        return ScreeningResultsPage(self.page).back

    # ==================================================
    # SINGLE SCREENING ACTIONS
    # ==================================================

    def choose_individual(self):
        self.switch_single()

        self.individual_option.check()

        expect(self.individual_option).to_be_checked()
        expect(self.organization_option).not_to_be_checked()

    def choose_organization(self):
        self.switch_single()

        self.organization_option.check()

        expect(self.organization_option).to_be_checked()
        expect(self.individual_option).not_to_be_checked()

        expect(
            self.organization_name_input
        ).to_be_visible(timeout=30000)

    def set_ongoing(self, enabled=True):
        expect(self.ongoing_checkbox).to_be_visible()
        expect(self.ongoing_checkbox).to_be_enabled()

        self.ongoing_checkbox.set_checked(enabled)

        if enabled:
            expect(self.ongoing_checkbox).to_be_checked()
        else:
            expect(self.ongoing_checkbox).not_to_be_checked()

    def analyze_screening(
        self,
        name,
        ongoing=False,
        organization=False,
    ):
        if organization:
            self.choose_organization()
        else:
            self.choose_individual()

        self.screening_name.fill(name)

        expect(self.screening_name).to_have_value(name)

        self.set_ongoing(ongoing)

        expect(self.analyze_action).to_be_enabled()

        self.analyze_action.click()

        expect(
            self.back_to_screening_button
        ).to_be_visible(timeout=90000)

        results = ScreeningResultsPage(self.page)

        results.assert_loaded(name)
        results.wait_for_counts()

        print("Screening completed:", name)

        return results

    def return_to_screening(self):
        self.back_to_screening_button.click()

        expect(
            self.page.get_by_role(
                "heading",
                name="Screening",
                exact=True,
            )
        ).to_be_visible(timeout=30000)

        expect(
            self.page.get_by_text(
                "Single Screening",
                exact=True,
            )
        ).to_be_visible(timeout=30000)

    # ==================================================
    # DAILY SCREENING LOCATORS
    # ==================================================

    @property
    def daily_search_input(self):
        return self.page.get_by_placeholder(
            "Search here...",
            exact=True,
        )

    @property
    def daily_search_action(self):
        return self.daily_search_input.locator(
            "xpath=.."
        ).locator("button.search-btn")

    @property
    def daily_clear_action(self):
        return self.daily_search_input.locator(
            "xpath=.."
        ).locator("button.clear-btn")

    @property
    def daily_results_table(self):
        return self.page.locator(
            "main table:visible"
        ).filter(
            has=self.page.get_by_role(
                "columnheader",
                name="Profile ID",
                exact=True,
            )
        )

    @property
    def daily_record_rows(self):
        # Exclude hidden Ant Design measurement rows.

        return self.daily_results_table.locator(
            "tbody tr.ant-table-row[data-row-key]:visible"
        )

    @property
    def daily_result_count(self):
        return self.page.locator(
            "main p.table-description"
        ).filter(
            has_text=re.compile(
                r"Showing\s+[\d,]+\s+results?",
                re.I,
            )
        )

    @property
    def daily_loading_spinner(self):
        return self.page.locator(
            "main .ant-spin-spinning:visible"
        )

    @property
    def daily_select_all(self):
        return self.daily_results_table.get_by_role(
            "checkbox",
            name="Select all",
            exact=True,
        )

    @property
    def daily_next_page(self):
        return self.page.locator(
            "main .ant-pagination:visible .ant-pagination-next"
        )

    @property
    def remove_action(self):
        return self.page.locator("main").get_by_role(
            "button",
            name=re.compile(r"\bRemove\s*$", re.I),
        )

    @property
    def remove_notification(self):
        return self.page.get_by_text(
            "Ongoing screenings removed",
            exact=True,
        ).filter(visible=True)

    # ==================================================
    # DAILY SCREENING NAVIGATION
    # ==================================================

    def wait_daily_loading(self):
        expect(
            self.daily_loading_spinner
        ).to_have_count(0, timeout=60000)

    def open_daily(self):
        self.switch_daily()

        expect(
            self.daily_search_input
        ).to_be_visible(timeout=30000)

        expect(
            self.daily_results_table
        ).to_be_visible(timeout=30000)

        expect(
            self.daily_result_count
        ).to_be_visible(timeout=30000)

        self.wait_daily_loading()

    def refresh_daily(self):
        # Reopen the page to reset search and selection.

        self.open(self.page.url)
        self.open_daily()

        expect(
            self.daily_search_input
        ).to_have_value("")

        self.wait_daily_loading()

    def result_count(self):
        expect(self.daily_result_count).to_be_visible()

        text = self.daily_result_count.inner_text()

        match = re.search(
            r"Showing\s+([\d,]+)\s+results?",
            text,
            re.I,
        )

        assert match, (
            f"Invalid Daily Screening count: {text}"
        )

        return int(match.group(1).replace(",", ""))

    def assert_result_count(self, expected):
        expect(
            self.daily_result_count
        ).to_have_text(
            re.compile(
                rf"^\s*Showing\s+"
                rf"(?:{expected}|{expected:,})"
                rf"\s+results?\s*$",
                re.I,
            ),
            timeout=30000,
        )

    def assert_daily_headers(self):
        for header in self.DAILY_COLUMNS:

            expect(
                self.daily_results_table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible(timeout=30000)

    # ==================================================
    # DAILY SCREENING SEARCH
    # ==================================================

    def search_daily_records(self, value):
        expect(self.daily_search_input).to_be_visible()

        self.wait_daily_loading()

        self.daily_search_input.fill(value)

        expect(
            self.daily_search_input
        ).to_have_value(value)

        expect(
            self.daily_search_action
        ).to_be_visible()

        expect(
            self.daily_search_action
        ).to_be_enabled()

        self.daily_search_action.click()

        self.wait_daily_loading()

        print("Daily Screening search:", value)

    def clear_daily_search(self):
        if self.daily_search_input.input_value():

            expect(
                self.daily_clear_action
            ).to_be_visible()

            self.daily_clear_action.click()

        expect(
            self.daily_search_input
        ).to_have_value("")

        self.wait_daily_loading()

    def daily_row_by_name(self, name):
        return self.daily_record_rows.filter(
            has=self.page.locator(
                "td:nth-child(2)",
                has_text=re.compile(
                    rf"^\s*{re.escape(name)}\s*$",
                    re.I,
                ),
            )
        )

    def daily_row_by_id(self, profile_id):
        return self.daily_record_rows.filter(
            has=self.page.locator(
                "td:nth-child(3)",
                has_text=re.compile(
                    rf"^\s*{re.escape(profile_id)}\s*$"
                ),
            )
        )

    def get_daily_profile_id(self, row):
        expect(row).to_be_visible()

        profile_id = (
            row.locator("td")
            .nth(2)
            .inner_text()
            .strip()
        )

        assert profile_id, (
            "Daily Screening profile ID is empty"
        )

        return profile_id

    def visible_profile_ids(self):
        return [
            self.get_daily_profile_id(row)
            for row in self.daily_record_rows.all()
        ]

    def visible_record_names(self):
        return [
            row.locator("td").nth(1).inner_text().strip()
            for row in self.daily_record_rows.all()
        ]

    def assert_filtered_record(self, record):
        # Validate the actual table contents first.
        # This distinguishes filtering failures from
        # incorrect result count failures.

        try:
            expect(
                self.daily_record_rows
            ).to_have_count(1, timeout=30000)

        except AssertionError as error:

            raise AssertionError(
                "Daily Screening search did not return "
                "exactly one matching record.\n"
                f"Expected name: {record['name']}\n"
                f"Expected profile ID: {record['profile_id']}\n"
                f"Visible names: {self.visible_record_names()}\n"
                f"Visible IDs: {self.visible_profile_ids()}\n"
                f"Displayed count: {self.result_count()}"
            ) from error

        row = self.daily_record_rows.first

        expect(row).to_be_visible()

        expect(
            row.locator("td").nth(1)
        ).to_have_text(record["name"])

        expect(
            row.locator("td").nth(2)
        ).to_have_text(record["profile_id"])

        # Independently verify the displayed result count.

        self.assert_result_count(1)

        print("Filtered record:", record["name"])
        print("Filtered profile ID:", record["profile_id"])
        print("Displayed result count:", self.result_count())

    # ==================================================
    # UNFILTERED RECORD LOOKUP
    # ==================================================

    def wait_for_daily_records(self):
        self.wait_daily_loading()

        count = self.result_count()

        if count > 0:

            expect(
                self.daily_record_rows.first
            ).to_be_visible(timeout=30000)

        else:

            expect(
                self.daily_record_rows
            ).to_have_count(0, timeout=30000)

    def has_next_daily_page(self):
        if self.daily_next_page.count() == 0:
            return False

        if not self.daily_next_page.is_visible():
            return False

        classes = (
            self.daily_next_page.get_attribute("class")
            or ""
        )

        disabled = self.daily_next_page.get_attribute(
            "aria-disabled"
        )

        return (
            "ant-pagination-disabled" not in classes
            and disabled != "true"
        )

    def go_to_next_daily_page(self):
        assert self.has_next_daily_page()

        first_id = self.get_daily_profile_id(
            self.daily_record_rows.first
        )

        self.daily_next_page.click()

        expect(
            self.daily_record_rows.first.locator("td").nth(2)
        ).not_to_have_text(
            first_id,
            timeout=30000,
        )

        self.wait_daily_loading()

    def collect_daily_records(self):
        # Read the complete unfiltered table.
        # Do not depend on the search functionality
        # when validating creation or removal.

        self.refresh_daily()
        self.wait_for_daily_records()

        expected_count = self.result_count()

        records = {}
        visited_pages = set()

        while True:

            page_ids = tuple(self.visible_profile_ids())

            assert page_ids not in visited_pages, (
                "Repeated Daily Screening page detected"
            )

            visited_pages.add(page_ids)

            for row in self.daily_record_rows.all():

                profile_id = self.get_daily_profile_id(row)

                name = (
                    row.locator("td")
                    .nth(1)
                    .inner_text()
                    .strip()
                )

                assert profile_id not in records, (
                    f"Duplicate profile ID: {profile_id}"
                )

                records[profile_id] = name

            if not self.has_next_daily_page():
                break

            self.go_to_next_daily_page()

        assert len(records) == expected_count, (
            "Unable to inspect the complete Daily Screening "
            f"table. Expected {expected_count} records, "
            f"inspected {len(records)}."
        )

        return records

    def find_daily_record(self, name):
        # Locate the generated record independently
        # of the potentially defective search feature.

        self.refresh_daily()
        self.wait_for_daily_records()

        visited_pages = set()

        while True:

            row = self.daily_row_by_name(name)

            if row.count() > 0:

                expect(row).to_have_count(1)
                expect(row).to_be_visible()

                return row

            page_ids = tuple(self.visible_profile_ids())

            assert page_ids not in visited_pages, (
                "Repeated Daily Screening page detected"
            )

            visited_pages.add(page_ids)

            if not self.has_next_daily_page():
                break

            self.go_to_next_daily_page()

        raise AssertionError(
            f"Daily Screening record not found: {name}"
        )

    def assert_daily_record_absent(self, name):
        records = self.collect_daily_records()

        matching_names = [
            value
            for value in records.values()
            if value.casefold() == name.casefold()
        ]

        assert not matching_names, (
            f"Unexpected Daily Screening record: {name}"
        )

        print("Confirmed record absent:", name)

    # ==================================================
    # CREATE ONGOING SCREENING
    # ==================================================

    def create_ongoing_record(
        self,
        name=None,
        organization=False,
    ):
        name = name or self.unique_name()

        self.analyze_screening(
            name=name,
            ongoing=True,
            organization=organization,
        )

        self.return_to_screening()
        self.open_daily()

        row = self.find_daily_record(name)

        profile_id = self.get_daily_profile_id(row)

        print("Created ongoing screening:", name)
        print("Profile ID:", profile_id)

        return {
            "name": name,
            "profile_id": profile_id,
        }

    # ==================================================
    # DAILY SCREENING RECORD VALIDATION
    # ==================================================

    def assert_daily_record_values(self, row):
        expect(row).to_be_visible()

        cells = row.locator("td")

        assert cells.count() >= 10, (
            "Daily Screening row has missing columns"
        )

        name = cells.nth(1).inner_text().strip()

        profile_id = cells.nth(2).inner_text().strip()

        assert name
        assert profile_id

        mandatory_actions = (
            cells.nth(3)
            .inner_text()
            .strip()
            .replace(",", "")
        )

        resolved_hits = (
            cells.nth(4)
            .inner_text()
            .strip()
            .replace(",", "")
        )

        total_hits = (
            cells.nth(5)
            .inner_text()
            .strip()
            .replace(",", "")
        )

        assert mandatory_actions.isdigit(), (
            f"Invalid mandatory actions: {mandatory_actions}"
        )

        assert resolved_hits.isdigit(), (
            f"Invalid resolved hits: {resolved_hits}"
        )

        assert total_hits.isdigit(), (
            f"Invalid total hits: {total_hits}"
        )

        assert int(resolved_hits) <= int(total_hits), (
            "Resolved hits exceed total hits"
        )

        return {
            "name": name,
            "profile_id": profile_id,
            "mandatory_actions": int(mandatory_actions),
            "resolved_hits": int(resolved_hits),
            "total_hits": int(total_hits),
        }

    def open_daily_record(self, record):
        row = self.find_daily_record(record["name"])

        assert self.get_daily_profile_id(row) == (
            record["profile_id"]
        )

        row.locator("td").nth(1).get_by_text(
            record["name"],
            exact=True,
        ).click()

        results = ScreeningResultsPage(self.page)

        results.assert_loaded(record["name"])
        results.wait_for_counts()

        return results

    # ==================================================
    # DAILY SCREENING SELECTION
    # ==================================================

    def daily_checkbox(self, index=0):
        return self.daily_record_rows.nth(index).locator(
            'td.ant-table-selection-column '
            'input[type="checkbox"]'
        )

    def select_daily_row(self, index=0):
        checkbox = self.daily_checkbox(index)

        expect(checkbox).to_be_visible()
        expect(checkbox).to_be_enabled()

        checkbox.check()

        expect(checkbox).to_be_checked()

    def deselect_daily_row(self, index=0):
        checkbox = self.daily_checkbox(index)

        expect(checkbox).to_be_visible()

        checkbox.uncheck()

        expect(checkbox).not_to_be_checked()

    def selected_daily_count(self):
        return self.daily_record_rows.locator(
            'input[type="checkbox"]:checked'
        ).count()

    def assert_selected_daily_count(self, expected):
        expect(
            self.daily_record_rows.locator(
                'input[type="checkbox"]:checked'
            )
        ).to_have_count(expected)

    def select_all_daily_rows(self):
        expect(self.daily_record_rows.first).to_be_visible()

        expect(self.daily_select_all).to_be_visible()
        expect(self.daily_select_all).to_be_enabled()

        self.daily_select_all.check()

        expect(self.daily_select_all).to_be_checked()

        for row in self.daily_record_rows.all():

            expect(
                row.locator('input[type="checkbox"]')
            ).to_be_checked()

    def clear_all_daily_rows(self):
        if self.daily_select_all.is_checked():
            self.daily_select_all.uncheck()

        # Use first repeatedly because checked locators
        # change when a checkbox becomes unchecked.

        checked = self.daily_record_rows.locator(
            'input[type="checkbox"]:checked'
        )

        while checked.count() > 0:

            previous_count = checked.count()

            checked.first.uncheck()

            expect(checked).to_have_count(
                previous_count - 1
            )

        expect(self.daily_select_all).not_to_be_checked()

        self.assert_selected_daily_count(0)

    # ==================================================
    # REMOVE ONGOING SCREENING
    # ==================================================

    def remove_ongoing_records(self, records):
        assert records, "No disposable records supplied"

        expected_ids = {
            record["profile_id"]
            for record in records
        }

        assert len(expected_ids) == len(records)

        for record in records:

            assert record["name"].startswith(
                self.QA_PREFIX
            ), "Refusing to remove a non-QA record"

        # Obtain a complete snapshot before deletion.

        before = self.collect_daily_records()

        for record in records:

            assert before.get(record["profile_id"]) == (
                record["name"]
            ), "Disposable record identity mismatch"

        # Fresh navigation resets existing selections.

        self.refresh_daily()
        self.wait_for_daily_records()

        visited_pages = set()

        # For bulk removal, require all target records
        # to be present on the same table page.

        while True:

            visible_ids = set(self.visible_profile_ids())

            if expected_ids.issubset(visible_ids):
                break

            page_ids = tuple(self.visible_profile_ids())

            assert page_ids not in visited_pages

            visited_pages.add(page_ids)

            assert self.has_next_daily_page(), (
                "Target records are not on the same page. "
                "Bulk removal aborted for safety."
            )

            self.go_to_next_daily_page()

        self.clear_all_daily_rows()

        for record in records:

            row = self.daily_row_by_id(
                record["profile_id"]
            )

            expect(row).to_have_count(1)

            expect(
                row.locator("td").nth(1)
            ).to_have_text(record["name"])

            checkbox = row.locator(
                'input[type="checkbox"]'
            )

            checkbox.check()

            expect(checkbox).to_be_checked()

        selected_ids = set()

        for row in self.daily_record_rows.all():

            checkbox = row.locator(
                'input[type="checkbox"]'
            )

            if checkbox.is_checked():

                selected_ids.add(
                    self.get_daily_profile_id(row)
                )

        assert selected_ids == expected_ids, (
            "Unexpected records selected. Removal aborted."
        )

        self.assert_selected_daily_count(len(records))

        expect(self.remove_action).to_be_enabled()

        self.remove_action.click()

        expect(
            self.remove_notification
        ).to_be_visible(timeout=30000)

        print(
            "Removal notification:",
            self.remove_notification.inner_text(),
        )

        self.wait_daily_loading()

        # Verify removal against the complete table.

        after = self.collect_daily_records()

        expected_remaining = {
            profile_id: name
            for profile_id, name in before.items()
            if profile_id not in expected_ids
        }

        assert after == expected_remaining, (
            "Daily Screening records after removal "
            "do not match the expected remaining records."
        )

        for record in records:

            assert record["profile_id"] not in after

            print(
                "Removed QA record:",
                record["name"],
                record["profile_id"],
            )

    def cleanup_ongoing_record(self, record):
        # Cleanup must not depend on the search feature.

        assert record["name"].startswith(self.QA_PREFIX)

        records = self.collect_daily_records()

        profile_id = record["profile_id"]

        if profile_id not in records:

            print(
                "QA record already absent:",
                record["name"],
            )

            return

        assert records[profile_id] == record["name"], (
            "Cleanup record identity mismatch"
        )

        self.remove_ongoing_records([record])

    def cleanup_ongoing_name(self, name):
        # Recover a generated record if creation succeeded
        # but the test failed before returning its ID.

        assert name.startswith(self.QA_PREFIX)

        records = self.collect_daily_records()

        matches = [
            {
                "name": record_name,
                "profile_id": profile_id,
            }
            for profile_id, record_name in records.items()
            if record_name == name
        ]

        assert len(matches) <= 1, (
            "Multiple records found for a generated QA name"
        )

        if matches:
            self.cleanup_ongoing_record(matches[0])

    # ==================================================
    # ORGANIZATION SCREENING
    # ==================================================

    @property
    def organization_name_input(self):
        return self.page.get_by_placeholder(
            "Enter organisation name",
            exact=True,
        )

    @property
    def registered_country_select(self):
        return self.page.locator(
            "main .ant-select:visible"
        )

    @property
    def country_options(self):
        return self.page.locator(
            ".ant-select-dropdown:visible "
            ".ant-select-item-option"
        )

    def choose_registered_country(self, country):
        self.choose_organization()

        expect(
            self.registered_country_select
        ).to_have_count(1, timeout=30000)

        expect(
            self.registered_country_select
        ).to_be_visible()

        self.registered_country_select.click()

        search = self.registered_country_select.locator(
            'input[role="combobox"]'
        )

        if search.count() == 1 and search.is_editable():
            search.fill(country)

        option = self.country_options.filter(
            has_text=re.compile(
                rf"^\s*{re.escape(country)}\s*$",
                re.I,
            )
        )

        expect(option).to_have_count(1, timeout=30000)
        expect(option).to_be_visible()

        option.click()

        expect(
            self.registered_country_select.locator(
                ".ant-select-selection-item"
            )
        ).to_have_text(country)

        print("Registered country selected:", country)

    def assert_organization_fields(self):
        self.choose_organization()

        expect(
            self.organization_name_input
        ).to_be_visible()

        expect(
            self.registered_country_select
        ).to_have_count(1)

        expect(
            self.registered_country_select
        ).to_be_visible()

        expect(self.ongoing_checkbox).to_be_visible()
        expect(self.analyze_action).to_be_visible()

        expect(
            self.page.locator(
                'input[name="gender"]:visible'
            )
        ).to_have_count(0)

        expect(
            self.page.get_by_placeholder(
                "Pick date of birth"
            )
        ).to_have_count(0)

        expect(
            self.page.get_by_placeholder(
                "Enter citizenship"
            )
        ).to_have_count(0)