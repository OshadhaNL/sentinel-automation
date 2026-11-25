
import re

from playwright.sync_api import Page, expect


class ScreeningResultsPage:

    CATEGORIES = (
        "Unresolved Hits",
        "Positive Hits",
        "False Hits",
        "Possible Hits",
    )

    HEADERS = (
        "Name",
        "Match Strength",
        "Type",
        "Gender",
        "Date of Birth",
        "Citizenship",
        "Resolution",
    )

    def __init__(self, page: Page):
        self.page = page

    # ==================================================
    # PAGE LOCATORS
    # ==================================================

    @property
    def back(self):
        return self.page.locator(
            "main .wc-page-header button.back-link"
        )

    @property
    def summary(self):
        return self.page.locator(
            "main .wc-page-header p"
        )

    @property
    def tabs(self):
        return self.page.locator(
            "main .tab-z-labels .tab-z-option"
        )

    @property
    def active_tab(self):
        return self.page.locator(
            "main .tab-z-labels .tab-z-option.active"
        )

    @property
    def results_table(self):
        return self.page.locator(
            "main .table-scroll-wrapper "
            ".ant-table-content table:visible"
        ).last

    @property
    def rows(self):
        return self.results_table.locator(
            "tbody tr.ant-table-row[data-row-key]:visible"
        )

    @property
    def empty_message(self):
        return self.results_table.locator(
            "tr.ant-table-placeholder "
            ".ant-empty-description"
        )

    @property
    def loading_spinner(self):
        return self.page.locator(
            "main .ant-spin-spinning:visible"
        )

    # ==================================================
    # LOADING VALIDATION
    # ==================================================

    def wait_for_loading(self):

        expect(self.loading_spinner).to_have_count(
            0,
            timeout=60000,
        )

    def assert_loaded(self, name=None):

        expect(self.back).to_be_visible(
            timeout=60000
        )

        expect(self.summary).to_have_text(
            re.compile(
                r"Showing\s+[\d,]+\s+matches\s+for",
                re.I,
            ),
            timeout=60000,
        )

        if name:
            expect(self.summary).to_contain_text(
                name,
                timeout=60000,
            )

        expect(self.tabs).to_have_count(
            4,
            timeout=60000,
        )

        expect(self.results_table).to_be_visible(
            timeout=60000
        )

        self.wait_for_loading()

    # ==================================================
    # TOTAL MATCH COUNT
    # ==================================================

    def count(self):

        text = self.summary.inner_text()

        match = re.search(
            r"Showing\s+([\d,]+)\s+matches",
            text,
            re.I,
        )

        assert match, (
            f"Cannot identify total matches: {text}"
        )

        return int(
            match.group(1).replace(",", "")
        )

    # ==================================================
    # CATEGORY LOCATORS
    # ==================================================

    def category(self, name):

        assert name in self.CATEGORIES, (
            f"Invalid category: {name}"
        )

        return self.tabs.filter(
            has_text=re.compile(
                rf"^\s*{re.escape(name)}"
                rf"\s*\([\d,]+\)\s*$",
                re.I,
            )
        )

    def category_count(self, name):

        tab = self.category(name)

        expect(tab).to_be_visible(
            timeout=30000
        )

        text = tab.inner_text()

        match = re.search(
            r"\(([\d,]+)\)",
            text,
        )

        assert match, (
            f"Cannot identify count for {name}: {text}"
        )

        return int(
            match.group(1).replace(",", "")
        )

    def get_category_counts(self):

        return {
            category: self.category_count(category)
            for category in self.CATEGORIES
        }

    # ==================================================
    # WAIT FOR CATEGORY COUNTS TO RECONCILE
    # ==================================================

    def wait_for_counts(self, timeout=90000):

        self.wait_for_loading()

        # Wait until the four displayed category counts
        # reconcile with the displayed total matches.
        self.page.wait_for_function(
            """
            () => {
                const summary = document.querySelector(
                    'main .wc-page-header p'
                );

                const tabs = Array.from(
                    document.querySelectorAll(
                        'main .tab-z-labels .tab-z-option'
                    )
                );

                if (!summary || tabs.length !== 4) {
                    return false;
                }

                const totalMatch = summary.innerText.match(
                    /Showing\\s+([\\d,]+)\\s+matches/i
                );

                if (!totalMatch) {
                    return false;
                }

                const total = Number(
                    totalMatch[1].replace(/,/g, '')
                );

                const counts = tabs.map(tab => {
                    const match = tab.innerText.match(
                        /\\(([\\d,]+)\\)/
                    );

                    return match
                        ? Number(match[1].replace(/,/g, ''))
                        : NaN;
                });

                if (counts.some(Number.isNaN)) {
                    return false;
                }

                return counts.reduce(
                    (sum, value) => sum + value, 0
                ) === total;
            }
            """,
            timeout=timeout,
        )

        return self.get_category_counts()

    # ==================================================
    # CATEGORY SWITCHING
    # ==================================================

    def choose_category(self, name):

        self.wait_for_loading()

        tab = self.category(name)

        expect(tab).to_be_visible(
            timeout=30000
        )

        # Click the actual parent category container,
        # rather than its nested label.
        tab.click()

        # Confirm that the selected tab is active.
        expect(tab).to_have_class(
            re.compile(r"\bactive\b"),
            timeout=30000,
        )

        expect(self.active_tab).to_have_count(1)

        expect(self.active_tab).to_contain_text(
            name
        )

        self.wait_for_loading()

        expect(self.results_table).to_be_visible(
            timeout=30000
        )

        print(f"Active category: {name}")

    # ==================================================
    # TABLE HEADER VALIDATION
    # ==================================================

    def assert_headers(self):

        for header in self.HEADERS:

            expect(
                self.results_table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True,
                )
            ).to_be_visible()

    # ==================================================
    # EMPTY CATEGORY VALIDATION
    # ==================================================

    def assert_empty(self):

        expect(self.empty_message).to_be_visible(
            timeout=30000
        )

        expect(self.empty_message).to_have_text(
            re.compile(
                r"^(No data|No screening hits found)$",
                re.I,
            )
        )

        expect(self.rows).to_have_count(
            0,
            timeout=30000,
        )

    # ==================================================
    # CATEGORY RESOLUTION VALIDATION
    # ==================================================

    def assert_category_rows(self, category):

        count = self.category_count(category)

        if count == 0:

            self.assert_empty()

            return 0

        expected_resolution = {
            "Unresolved Hits": "Unresolved",
            "Positive Hits": "Positive Hit",
            "False Hits": "False Hit",
            "Possible Hits": "Possible Hit",
        }[category]

        pattern = re.compile(
            rf"^{re.escape(expected_resolution)}s?$",
            re.I,
        )

        expect(self.rows.first).to_be_visible(
            timeout=30000
        )

        # Wait for the table to contain the correct
        # resolution rather than the previous tab's rows.
        expect(
            self.rows.first.locator(
                "td:last-child .tag-z p"
            )
        ).to_have_text(
            pattern,
            timeout=30000,
        )

        for row in self.rows.all():

            expect(
                row.locator(
                    "td:last-child .tag-z p"
                )
            ).to_have_text(
                pattern,
                timeout=30000,
            )

        visible_count = self.rows.count()

        assert 0 < visible_count <= count, (
            f"{category}: "
            f"Visible rows={visible_count}, "
            f"Category count={count}"
        )

        print(
            f"{category}: "
            f"{visible_count} visible rows, "
            f"{count} reported matches"
        )

        return visible_count

    # ==================================================
    # FIND MATCHING NAMES
    # ==================================================

    def matching_rows(self, name):

        return self.rows.filter(
            has=self.page.locator(
                "button.table-link",
                has_text=re.compile(
                    re.escape(name),
                    re.I,
                ),
            )
        )

    # ==================================================
    # OPEN MATCH DETAILS
    # ==================================================

    def open_match(self, row):

        name_button = row.locator(
            "button.table-link"
        )

        expect(name_button).to_be_visible(
            timeout=30000
        )

        name = name_button.inner_text().strip()

        profile_id = row.get_attribute(
            "data-row-key"
        )

        assert profile_id, (
            "Selected row has no profile ID"
        )

        name_button.click()

        report = self.page.locator(
            "#wc-report"
        )

        expect(report).to_be_visible(
            timeout=60000
        )

        expect(
            report.locator(
                ".wc-report-profile h6"
            )
        ).to_have_text(
            name,
            timeout=30000,
        )

        expect(
            report.locator(
                ".wc-report-profile p"
            ).first
        ).to_have_text(
            profile_id,
            timeout=30000,
        )

        expect(
            report.get_by_role(
                "heading",
                name="PERSONAL DETAILS",
                exact=True,
            )
        ).to_be_visible()

        print(f"Verified profile name: {name}")
        print(f"Verified profile ID: {profile_id}")

        return name, profile_id

    def open_first_match(self):

        name, profile_id = self.open_match(
            self.rows.first
        )

        return name

    # ==================================================
    # RETURN TO MATCHES
    # ==================================================

    def back_to_matches(self, name=None):

        self.page.get_by_role(
            "button",
            name=re.compile(
                "Back to Matches",
                re.I,
            ),
        ).click()

        self.assert_loaded(name)

        self.wait_for_counts()
