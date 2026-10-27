
import re
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import (
    Page,
    expect,
    TimeoutError as PlaywrightTimeoutError,
)


class ProfilesPage:

    HEADERS = [
        "Client ID",
        "Name",
        "Type",
        "Status",
        "Onboarded Date",
        "Risk Rating",
        "Onboarded By",
    ]

    def __init__(self, page: Page):
        self.page = page

        # Page information
        self.heading = page.get_by_role(
            "heading", name="Profiles", exact=True
        )
        self.description = page.get_by_text(
            "View and manage profiles of existing clients.",
            exact=True
        )

        # Search
        self.search_input = page.get_by_placeholder(
            "Search by client ID or name"
        )
        self.search_button = page.locator("button.search-btn")
        self.search_icon = self.search_button.locator(
            "i.fa-search"
        )
        self.clear_button = page.locator("button.clear-btn")

        # Date picker
        self.date_picker = page.locator(".ant-picker-range")
        self.start_date = page.get_by_placeholder("Start Date")
        self.end_date = page.get_by_placeholder("End Date")
        self.calendar_icon = self.date_picker.locator(
            ".anticon-calendar"
        )

        # Extract
        self.extract_button = page.locator(
            "button.primary-btn"
        ).filter(has_text="Extract")
        self.extract_icon = self.extract_button.locator(
            "i.fa-arrow-to-bottom"
        )

        # My Files / All Files
        self.my_files_tab = page.locator(
            ".tab-z-option"
        ).filter(has_text="My Files")

        self.all_files_tab = page.locator(
            ".tab-z-option"
        ).filter(has_text="All Files")

        self.my_files_icon = self.my_files_tab.locator(
            "i.fa-folder"
        )
        self.all_files_icon = self.all_files_tab.locator(
            "i.fa-folders"
        )

        # Profiles table
        self.table_wrapper = page.locator(
            ".table-scroll-wrapper .ant-table-wrapper"
        )
        self.table = self.table_wrapper.locator(
            ".ant-table"
        )
        self.headers = self.table.locator(
            "thead.ant-table-thead th"
        )
        self.rows = self.table.locator(
            "tbody.ant-table-tbody tr.ant-table-row"
        )
        self.pagination = self.table_wrapper.locator(
            "ul.ant-table-pagination"
        )

    # ==========================================
    # Navigation
    # ==========================================

    def open_profiles(self):
        self.page.get_by_role(
            "link", name=re.compile("Profiles", re.I)
        ).click()

        expect(self.heading).to_be_visible(timeout=20000)
        expect(self.table).to_be_visible(timeout=20000)

    def verify_heading(self):
        expect(self.heading).to_be_visible()

    def verify_description(self):
        expect(self.description).to_be_visible()

    # ==========================================
    # Search
    # ==========================================

    def verify_search_input(self):
        expect(self.search_input).to_be_visible()

    def verify_search_icon(self):
        expect(self.search_icon).to_be_visible()

    def verify_search_placeholder(self):
        expect(self.search_input).to_have_attribute(
            "placeholder",
            "Search by client ID or name"
        )

    def enter_search_text(self, text):
        self.search_input.fill(text)
        expect(self.search_input).to_have_value(text)

    def perform_search(self, text):
        self.search_input.fill(text)
        self.search_button.click()

        expect(self.search_input).to_have_value(text)

    def verify_search_results(self, column_index, search_text):
        expected = search_text.casefold()

        self.page.wait_for_function(
            """
            ({columnIndex, searchText}) => {
                const rows = Array.from(
                    document.querySelectorAll(
                        ".table-scroll-wrapper " +
                        "tbody.ant-table-tbody tr.ant-table-row"
                    )
                );

                if (!rows.length) return false;

                return rows.every(row => {
                    const cells = row.querySelectorAll("td");
                    const value = (
                        cells[columnIndex]?.innerText || ""
                    ).trim().toLowerCase();

                    return value.includes(searchText);
                });
            }
            """,
            arg={
                "columnIndex": column_index,
                "searchText": expected,
            },
            timeout=20000,
        )

        records = self.get_current_page_records()

        field = (
            "client_id"
            if column_index == 0
            else "name"
        )

        assert records, "No search results found"

        for record in records:
            assert expected in record[field].casefold(), (
                f"Search result mismatch: {record[field]}"
            )

    # ==========================================
    # Date picker
    # ==========================================

    def verify_date_picker(self):
        expect(self.date_picker).to_be_visible()
        expect(self.start_date).to_be_visible()
        expect(self.end_date).to_be_visible()

    def verify_date_placeholders(self):
        expect(self.start_date).to_have_attribute(
            "placeholder", "Start Date"
        )
        expect(self.end_date).to_have_attribute(
            "placeholder", "End Date"
        )

    def verify_calendar_icon(self):
        expect(self.calendar_icon).to_be_visible()

    def select_date_range(self):
        today = date.today()
        start = today.replace(day=1)
        end = min(
            today,
            start + timedelta(days=6)
        )

        self.start_date.click()

        popup = self.page.locator(
            ".ant-picker-dropdown:visible"
        )
        expect(popup).to_be_visible(timeout=10000)

        for selected_date in (start, end):
            value = selected_date.strftime("%Y-%m-%d")

            cell = popup.locator(
                f'td.ant-picker-cell-in-view[title="{value}"]'
            ).first

            expect(cell).to_be_visible(timeout=10000)
            cell.click()

        expect(self.start_date).not_to_have_value("")
        expect(self.end_date).not_to_have_value("")

        return (
            self.start_date.input_value(),
            self.end_date.input_value()
        )

    # ==========================================
    # Extract / Excel download
    # ==========================================

    def verify_extract_button(self):
        expect(self.extract_button).to_be_visible()

    def verify_extract_icon(self):
        expect(self.extract_icon).to_be_visible()

    def download_profiles_excel(self, directory):
        """
        Click Extract and save the actual browser download.

        Waits for table records before exporting and retries
        once if the application does not start a download.
        """

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        self.select_my_files()

        expect(self.table).to_be_visible(timeout=20000)
        expect(self.rows.first).to_be_visible(timeout=20000)
        expect(self.extract_button).to_be_visible(timeout=20000)
        expect(self.extract_button).to_be_enabled(timeout=20000)

        last_error = None

        for attempt in range(1, 3):
            print(f"Excel export attempt {attempt}")

            try:
                with self.page.expect_download(
                    timeout=20000
                ) as download_info:
                    self.extract_button.click()

                download = download_info.value

                filename = download.suggested_filename

                assert re.fullmatch(
                    r"profiles_my-files_\d{8}_\d{4}\.xlsx",
                    filename,
                    re.IGNORECASE
                ), (
                    f"Unexpected downloaded filename: {filename}"
                )

                saved_path = directory / filename
                download.save_as(str(saved_path))

                failure = download.failure()
                assert failure is None, (
                    f"Browser download failed: {failure}"
                )

                assert saved_path.exists(), (
                    "Downloaded file does not exist"
                )
                assert saved_path.stat().st_size > 0, (
                    "Downloaded Excel file is empty"
                )

                print(f"Downloaded: {saved_path}")

                return saved_path

            except PlaywrightTimeoutError as error:
                last_error = error
                print(
                    f"No download detected on attempt {attempt}"
                )

                # Collect application error messages.
                notifications = self.page.locator(
                    ".ant-notification-notice, "
                    ".ant-message-notice, "
                    "[role='alert']"
                )

                for index in range(notifications.count()):
                    message = notifications.nth(
                        index
                    ).inner_text().strip()

                    if message:
                        print(
                            f"Application notification: {message}"
                        )

                if attempt == 1:
                    self.page.reload(
                        wait_until="domcontentloaded",
                        timeout=60000
                    )

                    expect(self.heading).to_be_visible(
                        timeout=20000
                    )

                    self.select_my_files()

                    expect(self.rows.first).to_be_visible(
                        timeout=20000
                    )

        raise AssertionError(
            "Extract was clicked twice, but the browser "
            "did not receive an Excel download. "
            "The export request or application behavior "
            "needs further investigation."
        ) from last_error

    # ==========================================
    # Tabs
    # ==========================================

    def select_my_files(self):
        self.my_files_tab.click()

        expect(self.my_files_tab).to_have_class(
            re.compile(r"\bactive\b")
        )

    def select_all_files(self):
        self.all_files_tab.click()

        expect(self.all_files_tab).to_have_class(
            re.compile(r"\bactive\b")
        )

    def verify_my_files_icon(self):
        expect(self.my_files_icon).to_be_visible()

    def verify_all_files_icon(self):
        expect(self.all_files_icon).to_be_visible()

    # ==========================================
    # Table
    # ==========================================

    def verify_table_visible(self):
        expect(self.table).to_be_visible()

    def verify_header(self, position, expected):
        expect(
            self.headers.nth(position - 1)
        ).to_have_text(expected)

    def get_first_row_cells(self):
        expect(self.rows.first).to_be_visible(
            timeout=20000
        )

        return [
            cell.inner_text().strip()
            for cell in self.rows.first.locator(
                "td"
            ).all()
        ]

    def get_first_row_value(self, column_index):
        return self.get_first_row_cells()[column_index]

    def normalize_onboarded_by(self, text):
        """
        Remove avatar initials from Onboarded By text.

        Example:
            OW Oshadha Weerakon
            -> Oshadha Weerakon
        """
        text = " ".join(text.split())

        parts = text.split(" ", 1)

        if (
            len(parts) == 2
            and re.fullmatch(r"[A-Z]{1,3}", parts[0])
        ):
            return parts[1].strip()

        return text

    def get_current_page_records(self, allow_empty=False):
        expect(self.table).to_be_visible()

        if not allow_empty:
            expect(self.rows.first).to_be_visible(
                timeout=20000
            )

        records = []

        for index in range(self.rows.count()):
            cells = self.rows.nth(index).locator("td")

            if cells.count() < 7:
                continue

            onboarded_by_raw = (
                cells.nth(6).inner_text().strip()
            )

            records.append({
                "client_id": cells.nth(0).inner_text().strip(),
                "name": cells.nth(1).inner_text().strip(),
                "type": cells.nth(2).inner_text().strip(),
                "status": cells.nth(3).inner_text().strip(),
                "onboarded_date": cells.nth(4).inner_text().strip(),
                "risk_rating": cells.nth(5).inner_text().strip(),
                "onboarded_by": self.normalize_onboarded_by(
                    onboarded_by_raw
                ),
            })

        return records

    def get_all_records(self):
        """
        Collect records from every pagination page.

        Wait for both the active page number and table
        records to update before collecting the next page.
        """

        records = []
        visited_pages = set()

        expect(self.table).to_be_visible(timeout=20000)

        while True:
            # Wait until the table is ready.
            expect(self.rows.first).to_be_visible(timeout=20000)

            if self.pagination.count() == 0:
                active_page = "1"
            else:
                active_page = self.pagination.locator(
                    ".ant-pagination-item-active"
                ).inner_text().strip()

            assert active_page not in visited_pages, (
                f"Pagination repeated page {active_page}"
            )

            visited_pages.add(active_page)

            # Read the current page.
            page_records = self.get_current_page_records()

            assert page_records, (
                f"No records found on page {active_page}"
            )

            records.extend(page_records)

            print(
                f"Profiles page {active_page}: "
                f"{len(page_records)} records"
            )

            # Stop if pagination is absent.
            if self.pagination.count() == 0:
                break

            next_button = self.pagination.locator(
                ".ant-pagination-next"
            )

            disabled = (
                    next_button.get_attribute("aria-disabled") == "true"
                    or "ant-pagination-disabled" in (
                            next_button.get_attribute("class") or ""
                    )
            )

            if disabled:
                break

            # Capture current Client IDs before navigating.
            previous_ids = [
                record["client_id"]
                for record in page_records
            ]

            previous_page = active_page

            # Click Next.
            next_button.click()

            # Wait for page number to change.
            expect(
                self.pagination.locator(
                    ".ant-pagination-item-active"
                )
            ).not_to_have_text(
                previous_page,
                timeout=20000
            )

            # IMPORTANT: Wait for table records to change.
            self.page.wait_for_function(
                """
                (previousIds) => {
                    const rows = Array.from(
                        document.querySelectorAll(
                            ".table-scroll-wrapper "
                            + "tbody.ant-table-tbody "
                            + "tr.ant-table-row"
                        )
                    );

                    if (rows.length === 0) {
                        return false;
                    }

                    const currentIds = rows.map(row => {
                        const firstCell = row.querySelector(
                            "td:first-child"
                        );

                        return firstCell
                            ? firstCell.innerText.trim()
                            : "";
                    });

                    return JSON.stringify(currentIds)
                        !== JSON.stringify(previousIds);
                }
                """,
                arg=previous_ids,
                timeout=20000
            )

        # Validate Client IDs after collecting all pages.
        client_ids = [
            record["client_id"]
            for record in records
        ]

        assert len(client_ids) == len(set(client_ids)), (
            "Duplicate Client IDs found across Profiles pages"
        )

        print(
            f"Total Profiles records: {len(records)}"
        )

        return records

    # ==========================================
    # Client ID navigation
    # ==========================================

    def click_first_client_id(self):
        expect(self.rows.first).to_be_visible(
            timeout=20000
        )

        link = self.rows.first.locator(
            "td"
        ).first.locator("a")

        expect(link).to_be_visible()

        client_id = link.inner_text().strip()
        link.click()

        return client_id

    def verify_screening_navigation(self, client_id):
        expect(self.page).to_have_url(
            re.compile(
                r"/nolimit/app/profiles/"
                r"(individual|entity)/process"
                r"\?step=verification&client="
                + re.escape(client_id)
                + r"(?:&.*)?$"
            ),
            timeout=20000
        )
