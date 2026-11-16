import re
from playwright.sync_api import expect


class IndividualScreeningPage:
    """Read-only locators and navigation for Individual Profile Screening."""

    HIT_CATEGORIES = ('Unresolved Hits', 'Positive Hits', 'False Hits', 'Possible Hits')
    HIT_HEADERS = ('Name', 'Match Strength', 'Type', 'Gender', 'Date of Birth', 'Citizenship', 'Resolution')
    DAILY_HEADERS = ('Name', 'Profile ID', 'Mandatory Actions', 'Resolved Hits', 'Total Hits', 'Review Required', 'Last Modified By', 'Created Date', 'Last Screened Date')

    def __init__(self, page):
        self.page = page

    @property
    def heading(self):
        return self.page.get_by_role('heading', name='Profile - Individual', exact=True)

    def tab(self, name: str):
        pattern = re.compile(
            rf"^\s*{re.escape(name)}(?:\s*\(\d+\))?\s*$"
        )

        return self.page.locator(".tab-z-option").filter(
            has=self.page.locator(
                "label",
                has_text=pattern,
            )
        ).first

    def _screening_view(self):
        """
        Identify the currently visible Screening view.
        """
        if self.name_input().is_visible():
            return "single"

        if self.daily_search().is_visible():
            return "daily"

        if (
                self.back_to_screening().is_visible()
                and self.tab("Unresolved Hits").is_visible()
        ):
            return "hits"

        return "unknown"

    def _wait_for_screening_view(self, expected, timeout=20000):
        """
        Wait for the requested view, including after React rerenders.
        """
        self.page.wait_for_function(
            """(expected) => {
                const visible = (element) =>
                    !!element &&
                    element.getClientRects().length > 0;

                const single = [...document.querySelectorAll(
                    'input[placeholder="Enter individual name"]'
                )].some(visible);

                const daily = [...document.querySelectorAll(
                    'input[placeholder="Search here..."]'
                )].some(visible);

                const back = [...document.querySelectorAll("button")]
                    .some(el => visible(el) &&
                        el.textContent.includes("Back to Screening"));

                const hits = [...document.querySelectorAll(
                    ".tab-z-option label"
                )].some(el => visible(el) &&
                    el.textContent.includes("Unresolved Hits"));

                if (expected === "single") return single;
                if (expected === "daily") return daily;
                if (expected === "hits") return back && hits;

                return false;
            }""",
            arg=expected,
            timeout=timeout,
        )

    def _click_screening_tab(self, name):
        """
        Click a tab and wait for its destination.
        """
        destination = {
            "Single Screening": "single",
            "Daily Screening": "daily",
        }[name]

        tab = self.tab(name)
        expect(tab).to_be_visible(timeout=15000)
        tab.click(timeout=15000)

        self._wait_for_screening_view(destination)

    def open_hits(self):
        """
        Open Screening Hits and verify the correct view.
        """
        if self._screening_view() == "hits":
            return

        self.tab("Screening").click(timeout=15000)

        self._wait_for_screening_view("hits")
        expect(self.hit_table()).to_be_visible(timeout=15000)

    def open_single(self):
        """
        Navigate reliably to Single Screening.
        """
        current = self._screening_view()

        if current == "single":
            return

        if current == "daily":
            self._click_screening_tab("Single Screening")

        elif current == "hits":
            back = self.back_to_screening()
            expect(back).to_be_visible(timeout=15000)
            back.click(timeout=15000)
            self._wait_for_screening_view("single")

        else:
            self.tab("Screening").click(timeout=15000)

            self.page.wait_for_function(
                """() => {
                    const name = document.querySelector(
                        'input[placeholder="Enter individual name"]'
                    );
                    const back = [...document.querySelectorAll("button")]
                        .find(el => el.textContent.includes(
                            "Back to Screening"
                        ));
                    return Boolean(name || back);
                }""",
                timeout=15000,
            )

            self.open_single()
            return

        expect(self.name_input()).to_be_visible(timeout=15000)

    def open_daily(self):
        """
        Navigate reliably to Daily Screening.
        """
        if self._screening_view() == "daily":
            return

        self.open_single()
        self._click_screening_tab("Daily Screening")

        expect(self.daily_search()).to_be_visible(timeout=15000)

    def require_hits(self):
        """
        Ensure Screening Hits is displayed.
        """
        self.open_hits()

        expect(
            self.tab("Unresolved Hits")
        ).to_be_visible(timeout=15000)

        expect(self.hit_table()).to_be_visible(timeout=15000)

    def hit_table(self):
        return self.page.locator('.ant-table-wrapper table').first

    def hit_rows(self):
        return self.hit_table().locator('tbody tr:not(.ant-table-placeholder):not(.ant-table-measure-row)')

    def name_input(self):
        return self.page.get_by_placeholder('Enter individual name')

    def gender(self, value):
        return self.page.locator(f'input[name="gender"][value="{value}"]')

    def client_type(self, value):
        return self.page.locator(f'input[name="entityType"][value="{value}"]')

    def date_of_birth(self):
        return self.page.get_by_placeholder('Pick date of birth')

    def select_field(self, label):
        return self.page.locator('.input-box').filter(
            has=self.page.locator('label', has_text=re.compile(r'^\s*' + re.escape(label) + r'\s*$'))
        ).locator('.ant-select').first

    def connected_parties(self):
        return self.page.locator('.screen-history-card')

    def daily_search(self):
        return self.page.get_by_placeholder('Search here...')

    def daily_search_button(self):
        return self.page.locator('.search-box-z .search-btn')

    def daily_clear_button(self):
        return self.page.locator('.search-box-z .clear-btn')

    def daily_table(self):
        return self.page.locator('.ant-table-wrapper table').first

    def daily_rows(self):
        return self.daily_table().locator('tbody tr:not(.ant-table-placeholder):not(.ant-table-measure-row)')

    def daily_result_count(self):
        return self.page.locator('.table-description')

    # Extended functional-test locators and actions.
    def analyze_button(self):
        return self.page.locator('button.primary-btn').filter(has_text='Analyze').first

    def ongoing_checkbox(self):
        return self.page.locator('input#ongoing')

    def gender_group(self):
        return self.page.locator('input[name="gender"]')

    def country_combobox(self, label):
        return self.select_field(label).locator(
            'input[role="combobox"]'
        ).first

    def back_to_screening(self):
        return self.page.get_by_role('button', name='Back to Screening')

    def bulk_action_button(self):
        return self.page.get_by_role('button', name='Bulk Action', exact=True)

    def remove_button(self):
        return self.page.locator('button.primary-btn').filter(has_text='Remove').first

    def bulk_remove_dialog(self):
        return self.page.locator('.modal-z').filter(has=self.page.get_by_text('Bulk Remove', exact=True)).first

    def csv_file_input(self):
        return self.page.locator('input#excel-file[accept=".csv"]')

    def selected_hit_category(self):
        return self.page.locator('.tab-z-option.active').filter(
            has=self.page.locator('label', has_text=re.compile('Hits'))
        ).first

    def selected_screening_mode(self):
        return self.page.locator('.tab-z-option.active').filter(
            has=self.page.locator('label', has_text=re.compile('Screening'))
        ).first

    def select_gender(self, value):
        self.open_single()

        radio = self.gender(value)

        expect(radio).to_be_attached(timeout=15000)

        radio.check(timeout=15000)

        expect(radio).to_be_checked(timeout=15000)

    def search_daily(self, query):
        self.open_daily()
        self.daily_search().fill(query)
        self.daily_search_button().click()

    def clear_daily_search(self):
        self.daily_clear_button().click()
        expect(self.daily_search()).to_be_empty()

    def daily_row_by_profile_id(self, profile_id):
        return self.daily_rows().filter(
            has_text=profile_id
        ).first

    def select_daily_record(self, profile_id):
        self.open_daily()

        row = self.daily_row_by_profile_id(profile_id)

        expect(row).to_be_visible(timeout=15000)

        checkbox = row.get_by_role("checkbox")
        checkbox.check()

        expect(checkbox).to_be_checked()

    def remove_selected_daily_record(self):
        """Remove selected ongoing screenings and confirm server success."""
        selected_rows = self.daily_rows().filter(
            has=self.page.locator('input[type="checkbox"]:checked')
        )
        expect(selected_rows).not_to_have_count(0, timeout=10000)

        remove = self.remove_button()
        expect(remove).to_be_visible(timeout=15000)
        expect(remove).to_be_enabled(timeout=15000)
        remove.click()

        # The application leaves the row visible until the page is refreshed.
        # Confirm the server acknowledged removal before refreshing.
        expect(
            self.page.get_by_text(
                "Ongoing screenings removed", exact=True
            )
        ).to_be_visible(timeout=15000)

    def refresh_daily_screening(self):
        """Reload the profile and return to the Daily Screening table."""
        self.page.reload(wait_until="domcontentloaded")
        expect(self.heading).to_be_visible(timeout=20000)
        self.open_daily()
        expect(self.daily_table()).to_be_visible(timeout=20000)

    def return_to_daily_after_analysis(self):
        """
        Navigate from Screening Hits to Daily Screening.
        """
        # Analyze opens the Screening Hits page.
        expect(
            self.back_to_screening()
        ).to_be_visible(timeout=20000)

        # Return to the Single Screening form.
        self.back_to_screening().click()

        expect(
            self.name_input()
        ).to_be_visible(timeout=20000)

        # Open Daily Screening.
        self.open_daily()

        expect(
            self.daily_search()
        ).to_be_visible(timeout=20000)

        expect(
            self.daily_table()
        ).to_be_visible(timeout=20000)

    def daily_row_by_name(self, name):
        """
        Find a Daily Screening row by its Name column.
        """
        return self.daily_rows().filter(
            has=self.page.get_by_role(
                "cell",
                name=name,
                exact=True,
            )
        ).first

    def select_daily_record_by_name(self, name):
        """
        Select the Daily Screening record checkbox.
        """
        self.open_daily()

        row = self.daily_row_by_name(name)
        expect(row).to_be_visible(timeout=20000)

        checkbox = row.get_by_role("checkbox")
        checkbox.check()

        expect(checkbox).to_be_checked()

