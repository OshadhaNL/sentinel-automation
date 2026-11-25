
import re
import math

from playwright.sync_api import Page, expect

from pages.screeningResultsPage import ScreeningResultsPage


class ScreeningFunctionalPage(ScreeningResultsPage):

    RESOLUTIONS = (
        "Positive Hits",
        "False Hits",
        "Possible Hits",
    )

    REPORT_SECTIONS = (
        "PERSONAL DETAILS",
        "BIOGRAPHY",
        "PEP ROLE DETAILS",
        "Further Information",
        "Linked Individuals",
        "Education",
        "Linked Companies",
        "Sources",
    )

    PERSONAL_FIELDS = (
        "Name",
        "Record Date",
        "Category",
        "Gender",
        "Date of Birth",
        "Place of Birth",
        "Citizenship",
        "Location Details",
        "Address",
        "Special Interest Categories",
        "Identification Numbers",
        "Alias",
        "PEP Type",
    )

    def __init__(self, page: Page):

        super().__init__(page)

    # ==================================================
    # RESULT TABLE SELECTION
    # ==================================================

    def row_checkbox(self, index=0):

        return self.rows.nth(index).locator(
            'input[type="checkbox"]'
        )

    def select_row(self, index=0):

        checkbox = self.row_checkbox(index)

        expect(checkbox).to_be_visible()

        checkbox.check()

        expect(checkbox).to_be_checked()

    def selected_count(self):

        return self.page.locator("main").get_by_text(
            re.compile(
                r"^\s*\d+\s+hit\(s\)\s+selected\s*$",
                re.I,
            )
        )

    def assert_selected_count(self, count):

        expect(self.selected_count()).to_have_text(
            re.compile(
                rf"^\s*{count}\s+hit\(s\)\s+selected\s*$",
                re.I,
            )
        )

    @property
    def bulk_resolution(self):

        return self.page.locator(
            "main .ant-select:visible"
        ).filter(
            has=self.page.locator(
                ".ant-select-selection-placeholder",
                has_text="Select any",
            )
        )

    @property
    def apply_button(self):

        return self.page.get_by_role(
            "button",
            name="Apply",
            exact=True,
        )

    @property
    def clear_button(self):

        return self.page.get_by_role(
            "button",
            name="Clear",
            exact=True,
        )

    @property
    def dropdown_options(self):

        return self.page.locator(
            ".ant-select-dropdown:visible "
            ".ant-select-item-option"
        )

    def open_bulk_resolution(self):

        expect(self.bulk_resolution).to_be_visible()

        self.bulk_resolution.click()

        expect(
            self.dropdown_options.first
        ).to_be_visible()

    def assert_resolution_options(self):

        self.open_bulk_resolution()

        expect(
            self.dropdown_options
        ).to_have_count(3)

        for resolution in self.RESOLUTIONS:

            expect(
                self.dropdown_options.filter(
                    has_text=re.compile(
                        rf"^{re.escape(resolution)}$"
                    )
                )
            ).to_be_visible()

        self.page.keyboard.press("Escape")

    def choose_bulk_resolution(self, resolution):

        assert resolution in self.RESOLUTIONS

        self.open_bulk_resolution()

        self.dropdown_options.filter(
            has_text=re.compile(
                rf"^{re.escape(resolution)}$"
            )
        ).click()

        expect(self.apply_button).to_be_enabled()

    def clear_selection(self):

        self.clear_button.click()

        expect(
            self.selected_count()
        ).to_have_count(0)

        expect(
            self.rows.locator(
                'input[type="checkbox"]:checked'
            )
        ).to_have_count(0)

    # ==================================================
    # PROFILE IDENTIFICATION
    # ==================================================

    def row_id(self, index=0):

        row = self.rows.nth(index)

        expect(row).to_be_visible()

        profile_id = row.get_attribute(
            "data-row-key"
        )

        assert profile_id, "Missing profile ID"

        return profile_id

    def visible_profile_ids(self):

        return [
            row.get_attribute("data-row-key")
            for row in self.rows.all()
        ]

    def row_by_id(self, profile_id):

        return self.rows.and_(
            self.page.locator(
                f'tr[data-row-key="{profile_id}"]'
            )
        )

    # ==================================================
    # RESOLUTION UPDATE
    # ==================================================

    def assert_update_notification(self):

        notification = self.page.get_by_text(
            re.compile(
                r"Resolution updated",
                re.I,
            )
        ).filter(visible=True)

        expect(notification.first).to_be_visible(
            timeout=30000
        )

        print(
            "Update notification:",
            notification.first.inner_text(),
        )

    def assert_resolution_counts(
        self,
        before,
        source,
        destination,
        quantity,
        total_before,
    ):

        expected = before.copy()

        expected[source] -= quantity
        expected[destination] += quantity

        for category, count in expected.items():

            expect(
                self.category(category)
            ).to_have_text(
                re.compile(
                    rf"^\s*{re.escape(category)}"
                    rf"\s*\({count:,}\)\s*$|"
                    rf"^\s*{re.escape(category)}"
                    rf"\s*\({count}\)\s*$",
                    re.I,
                ),
                timeout=60000,
            )

        actual = self.wait_for_counts()

        assert actual == expected, (
            f"Expected counts: {expected}; "
            f"Actual counts: {actual}"
        )

        assert self.count() == total_before

        print("Before update:", before)
        print("After update:", actual)

    def update_selected_records(
        self,
        source,
        destination,
        quantity=1,
    ):

        assert source != destination

        self.choose_category(source)

        before = self.wait_for_counts()

        total_before = self.count()

        assert before[source] >= quantity

        expect(self.rows.nth(quantity - 1)).to_be_visible()

        profile_ids = [
            self.row_id(index)
            for index in range(quantity)
        ]

        for index in range(quantity):

            self.select_row(index)

        self.assert_selected_count(quantity)

        self.choose_bulk_resolution(destination)

        self.apply_button.click()

        self.assert_update_notification()

        self.assert_resolution_counts(
            before,
            source,
            destination,
            quantity,
            total_before,
        )

        # Verify updated records are no longer
        # in the original category.
        self.choose_category(source)

        for profile_id in profile_ids:

            assert not self.find_profile_across_pages(
                profile_id
            ), (
                f"{profile_id} remains in {source}"
            )

        # Verify the same records appear in
        # the destination category.
        self.choose_category(destination)

        for profile_id in profile_ids:

            assert self.find_profile_across_pages(
                profile_id
            ), (
                f"{profile_id} missing from {destination}"
            )

            row = self.row_by_id(profile_id)

            resolution = destination.removesuffix("s")

            expect(
                row.locator("td").last
            ).to_have_text(
                re.compile(
                    rf"^{re.escape(resolution)}s?$",
                    re.I,
                )
            )

        return profile_ids

    # ==================================================
    # PAGINATION LOCATORS
    # ==================================================

    @property
    def pagination(self):

        return self.page.locator(
            "main .ant-pagination:visible"
        ).last

    @property
    def previous_page(self):

        return self.pagination.locator(
            ".ant-pagination-prev"
        )

    @property
    def next_page(self):

        return self.pagination.locator(
            ".ant-pagination-next"
        )

    @property
    def active_page(self):

        return self.pagination.locator(
            ".ant-pagination-item-active"
        )

    @property
    def page_size_selector(self):

        return self.pagination.locator(
            ".ant-pagination-options-size-changer"
        )

    def current_page(self):

        return int(
            self.active_page.inner_text().strip()
        )

    def page_size(self):

        text = self.page_size_selector.inner_text()

        match = re.search(r"\d+", text)

        assert match, (
            f"Cannot identify page size: {text}"
        )

        return int(match.group())

    def assert_page_loaded(
        self,
        page_number,
        old_ids=None,
    ):

        expect(self.active_page).to_have_text(
            str(page_number),
            timeout=30000,
        )

        self.wait_for_loading()

        expect(self.rows.first).to_be_visible()

        if old_ids:

            self.page.wait_for_function(
                """
                oldIds => {
                    const rows = Array.from(
                        document.querySelectorAll(
                            'main tr.ant-table-row[data-row-key]'
                        )
                    ).filter(
                        row => row.getClientRects().length > 0
                    );

                    const ids = rows.map(
                        row => row.getAttribute('data-row-key')
                    );

                    return ids.length > 0 &&
                        ids.every(id => !oldIds.includes(id));
                }
                """,
                arg=old_ids,
                timeout=30000,
            )

    def go_next_page(self):

        current = self.current_page()

        old_ids = self.visible_profile_ids()

        expect(self.next_page).not_to_have_class(
            re.compile(r"\bant-pagination-disabled\b")
        )

        self.next_page.click()

        self.assert_page_loaded(
            current + 1,
            old_ids,
        )

    def go_previous_page(self):

        current = self.current_page()

        old_ids = self.visible_profile_ids()

        expect(self.previous_page).not_to_have_class(
            re.compile(r"\bant-pagination-disabled\b")
        )

        self.previous_page.click()

        self.assert_page_loaded(
            current - 1,
            old_ids,
        )

    def go_to_page(self, number):

        if self.current_page() == number:
            return

        old_ids = self.visible_profile_ids()

        item = self.pagination.locator(
            f'.ant-pagination-item[title="{number}"]'
        )

        expect(item).to_be_visible()

        item.click()

        self.assert_page_loaded(
            number,
            old_ids,
        )

    def go_first_page(self):

        if not self.pagination.is_visible():
            return

        while self.current_page() > 1:

            self.go_previous_page()

    def go_last_page(self, category):

        count = self.category_count(category)

        size = self.page_size()

        last = math.ceil(count / size)

        while self.current_page() < last:

            self.go_next_page()

        return last

    def find_profile_across_pages(self, profile_id):

        self.go_first_page()

        while True:

            if self.row_by_id(profile_id).count() > 0:

                return True

            if not self.pagination.is_visible():

                return False

            classes = (
                self.next_page.get_attribute("class")
                or ""
            )

            if "ant-pagination-disabled" in classes:

                return False

            self.go_next_page()

    # ==================================================
    # MATCH DETAILS LOCATORS
    # ==================================================

    @property
    def report(self):

        return self.page.locator("#wc-report")

    @property
    def profile_name(self):

        return self.report.locator(
            ".wc-report-profile h6"
        )

    @property
    def profile_id(self):

        return self.report.locator(
            ".wc-report-profile p"
        ).first

    @property
    def previous_match(self):

        return self.page.locator(
            'button[title="Previous"]'
        )

    @property
    def next_match(self):

        return self.page.locator(
            'button[title="Next"]'
        )

    @property
    def match_position(self):

        return self.page.get_by_text(
            re.compile(
                r"Showing\s+\d+\s+of\s+\d+\s+Matches",
                re.I,
            )
        )

    @property
    def detail_resolution(self):

        return self.page.locator(
            ".listing-toolbar-actions .ant-select"
        )

    @property
    def update_button(self):

        return self.page.get_by_role(
            "button",
            name="Update",
            exact=True,
        )

    @property
    def pdf_button(self):

        return self.page.locator(
            ".listing-toolbar-actions button.outline-btn"
        )

    def assert_details_loaded(self):

        expect(self.report).to_be_visible(
            timeout=60000
        )

        expect(self.profile_name).not_to_be_empty()

        expect(self.profile_id).not_to_be_empty()

        expect(self.match_position).to_be_visible()

    def position(self):

        text = self.match_position.inner_text()

        match = re.search(
            r"Showing\s+(\d+)\s+of\s+(\d+)\s+Matches",
            text,
            re.I,
        )

        assert match, (
            f"Invalid position text: {text}"
        )

        return (
            int(match.group(1)),
            int(match.group(2)),
        )

    # ==================================================
    # MATCH DETAILS NAVIGATION
    # ==================================================

    def navigate_match(self, direction):

        assert direction in ("next", "previous")

        old_id = self.profile_id.inner_text().strip()

        old_position, total = self.position()

        button = (
            self.next_match
            if direction == "next"
            else self.previous_match
        )

        expect(button).to_be_enabled()

        button.click()

        expected_position = (
            old_position + 1
            if direction == "next"
            else old_position - 1
        )

        expect(self.match_position).to_have_text(
            re.compile(
                rf"Showing\s+0*{expected_position}"
                rf"\s+of\s+0*{total}\s+Matches",
                re.I,
            ),
            timeout=30000,
        )

        expect(self.profile_id).not_to_have_text(
            old_id,
            timeout=30000,
        )

        self.assert_details_loaded()

        return self.profile_id.inner_text().strip()

    # ==================================================
    # MATCH DETAILS RESOLUTION
    # ==================================================

    def choose_detail_resolution(self, resolution):

        assert resolution in self.RESOLUTIONS

        self.detail_resolution.click()

        self.dropdown_options.filter(
            has_text=re.compile(
                rf"^{re.escape(resolution)}$"
            )
        ).click()

        expect(
            self.detail_resolution.locator(
                ".ant-select-selection-item"
            )
        ).to_have_text(resolution)

    # ==================================================
    # REPORT SECTION VALIDATION
    # ==================================================

    def section(self, name):

        return self.report.get_by_role(
            "heading",
            name=name,
            exact=True,
        )

    def personal_field(self, label):

        return self.report.locator(
            "table.wc-report-body tbody tr"
        ).filter(
            has=self.page.locator(
                "td:first-child b",
                has_text=re.compile(
                    rf"^{re.escape(label)}$"
                ),
            )
        )

    def assert_personal_fields(self):

        for field in self.PERSONAL_FIELDS:

            expect(
                self.personal_field(field)
            ).to_be_visible()

        name_value = self.personal_field(
            "Name"
        ).locator("td").nth(1)

        expect(name_value).to_have_text(
            self.profile_name.inner_text().strip()
        )

    def assert_section(self, section):

        expect(
            self.section(section)
        ).to_be_visible()

    def section_table(self, section):

        return self.section(section).locator(
            "xpath=ancestor::div"
            "[contains(@class,'wc-report-title')][1]"
            "/following-sibling::table[1]"
        )

    def assert_section_headers(self, section, headers):

        table = self.section_table(section)

        for header in headers:

            expect(
                table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

    def assert_badge_navigation(
        self,
        badge_name,
        anchor,
    ):

        badge = self.report.locator(
            f'a[href="#{anchor}"]'
        ).filter(
            has_text=re.compile(
                rf"^{re.escape(badge_name)}$",
                re.I,
            )
        )

        expect(badge).to_be_visible()

        badge.click()

        expect(
            self.report.locator(f"#{anchor}")
        ).to_be_in_viewport(
            timeout=10000
        )

    # ==================================================
    # PDF DOWNLOAD
    # ==================================================

    def download_report(self, destination):

        expect(self.pdf_button).to_be_visible()

        expect(self.pdf_button).to_be_enabled()

        with self.page.expect_download(
            timeout=120000
        ) as download_info:

            self.pdf_button.click()

        download = download_info.value

        filename = download.suggested_filename

        path = destination / filename

        download.save_as(str(path))

        assert download.failure() is None

        assert path.exists()

        assert path.stat().st_size > 0

        print("Downloaded PDF:", filename)

        print(
            "PDF size:",
            path.stat().st_size,
            "bytes",
        )

        return path
