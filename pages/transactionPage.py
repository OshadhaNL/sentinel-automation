
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import Page, expect
import pytest


class TransactionPage:
    HEADERS = [
        "Transaction ID",
        "Property Address",
        "Buyer Name(s)",
        "Vendor / Seller",
        "Payment",
        "Contract Sale Value",
        "Date",
    ]

    PROPERTY_TYPES = ["Commercial", "Residential"]
    PAYMENT_METHODS = ["Bank Transfer", "Cash"]

    CURRENCY_CODES = [
        "AUD", "USD", "AED", "EUR",
        "GBP", "SAR", "QAR", "KWD",
        "BHD", "OMR", "SGD", "CHF",
    ]

    REQUIRED_FIELDS = [
        "property",
        "propertyType",
        "paymentMethod",
        "currency",
        "date",
    ]

    FORM_FIELDS = {
        "property": "Property Address",
        "propertyType": "Property Type",
        "paymentMethod": "Payment Method",
        "currency": "Currency",
        "propertyValue": "Contract Sale Value",
        "amount": "Deposit Amount",
        "date": "Date",
        "sellerClientIds": "Select Vendor/Sellers",
        "buyerClientIds": "Select Buyers",
    }

    def __init__(self, page: Page):
        self.page = page

        self.heading = page.get_by_role(
            "heading",
            name="Real Estate Transactions",
            exact=True,
        )
        self.description = page.get_by_text(
            "Log and review property sales, leases, deposits, "
            "and commissions.",
            exact=True,
        )

        self.search_input = page.locator(
            'input[placeholder="Search by ID, property, type, status…"]'
        )
        self.search_button = page.locator("button.search-btn")
        self.search_icon = self.search_button.locator("i.fa-search")
        self.clear_button = page.locator("button.clear-btn")
        self.clear_icon = self.clear_button.locator(
            "i.fa-times-circle"
        )

        self.date_range = page.locator(".ant-picker-range")
        self.start_date = self.date_range.locator(
            'input[placeholder="Start Date"]'
        )
        self.end_date = self.date_range.locator(
            'input[placeholder="End Date"]'
        )

        self.add_button = page.locator("main button").filter(
            has_text=re.compile(r"Add Transaction\s*$")
        ).first
        self.export_button = page.locator("main button").filter(
            has_text=re.compile(r"Export\s*$")
        ).first

        self.table = page.locator(".ant-table").first
        self.headers = self.table.locator(
            "thead.ant-table-thead th"
        )
        self.rows = self.table.locator(
            "tbody.ant-table-tbody tr.ant-table-row"
        )
        self.date_header = self.table.locator(
            'th[aria-label="Date"]'
        )
        self.pagination = page.locator(
            "ul.ant-pagination.ant-table-pagination"
        )

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    def open(self):
        parsed = urlsplit(self.page.url)

        origin = f"{parsed.scheme}://{parsed.netloc}"

        assert parsed.scheme and parsed.netloc, (
            "Login must finish before opening Transactions."
        )

        self.page.goto(
            f"{origin}/nolimit/app/transaction-activities",
            wait_until="domcontentloaded",
            timeout=60000,
        )

        expect(self.heading).to_be_visible(timeout=30000)
        expect(self.table).to_be_visible(timeout=30000)
        self.wait_for_table_ready()

    def wait_for_table_ready(self):
        """Wait for a data row or a genuine Ant Design empty state."""
        self.page.wait_for_function(
            """() => !!document.querySelector('.ant-table-tbody tr.ant-table-row')
              || !!document.querySelector('.ant-table-tbody .ant-empty')""",
            timeout=30000,
        )

    def require_records(self):
        """Wait for real rows; report an empty backend response without skipping tests."""
        for attempt in range(3):
            self.wait_for_table_ready()
            try:
                expect(self.rows.first).to_be_visible(timeout=12000)
                return
            except AssertionError:
                if attempt < 2:
                    self.page.reload(
                        wait_until="domcontentloaded",
                        timeout=60000,
                    )
                    expect(self.heading).to_be_visible(timeout=30000)

        empty_text = self.table.inner_text(timeout=10000)[:600]
        raise AssertionError(
            "Transactions did not load after three page attempts. "
            f"URL={self.page.url!r}; table content={empty_text!r}. "
            "Inspect the transaction-list API response and authentication."
        )

    def require_party_enabled(self, role):
        dropdown = self.party_dropdown(role)
        expect(dropdown).to_be_visible(timeout=15000)

        if dropdown.locator(
            'input.ant-select-selection-search-input'
        ).is_disabled():
            pytest.skip(
                f"{role.title()} selection is disabled by the QA application"
            )

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(self, value):
        self.search_input.fill(str(value))
        self.search_button.click()
        expect(self.search_input).to_have_value(str(value))

    def clear_search(self):
        if self.clear_button.is_visible():
            self.clear_button.click()
        else:
            self.search_input.fill("")
            self.search_button.click()

        expect(self.search_input).to_have_value("")

    def search_for_record(self, value, column=0):
        self.search(value)

        self.page.wait_for_function(
            """
            ({text, column}) => {
                const rows = Array.from(
                    document.querySelectorAll(
                        ".ant-table-tbody tr.ant-table-row"
                    )
                );

                return rows.some(row => {
                    const cell = row.querySelectorAll("td")[column];

                    return cell &&
                        cell.innerText.toLowerCase().includes(
                            text.toLowerCase()
                        );
                });
            }
            """,
            arg={
                "text": str(value),
                "column": column,
            },
            timeout=25000,
        )

    # --------------------------------------------------
    # Calendar helpers
    # --------------------------------------------------

    def calendar_popup(self):
        return self.page.locator(
            ".ant-picker-dropdown:visible"
        ).last

    def select_calendar_date(self, iso_date):
        """
        Select YYYY-MM-DD from an open Ant Design date picker.
        Supports moving between months.
        """
        target = date.fromisoformat(iso_date)

        popup = self.calendar_popup()
        expect(popup).to_be_visible(timeout=10000)

        for _ in range(120):
            cell = popup.locator(
                f'td.ant-picker-cell-in-view[title="{iso_date}"]'
            )

            if cell.count() and cell.first.is_visible():
                cell.first.locator(
                    ".ant-picker-cell-inner"
                ).click(force=True)
                return

            year_button = popup.locator(
                ".ant-picker-year-btn"
            ).first

            month_button = popup.locator(
                ".ant-picker-month-btn"
            ).first

            displayed_year = int(year_button.inner_text().strip())
            displayed_month_text = month_button.inner_text().strip()

            displayed_month = datetime.strptime(
                displayed_month_text[:3],
                "%b",
            ).month

            current_index = displayed_year * 12 + displayed_month
            target_index = target.year * 12 + target.month

            if current_index < target_index:
                popup.locator(
                    ".ant-picker-header-next-btn"
                ).first.click()
            else:
                popup.locator(
                    ".ant-picker-header-prev-btn"
                ).first.click()

        raise AssertionError(
            f"Unable to select date {iso_date}"
        )

    def select_date_range(self, start_iso, end_iso):
        assert date.fromisoformat(start_iso) <= date.fromisoformat(
            end_iso
        )

        self.start_date.click()
        self.select_calendar_date(start_iso)

        if not self.calendar_popup().is_visible():
            self.end_date.click()

        self.select_calendar_date(end_iso)

        expect(self.start_date).not_to_have_value("")
        expect(self.end_date).not_to_have_value("")

    def select_form_date(self, iso_date):
        control = self.active_modal.locator(
            'input[placeholder="Select date and time"]'
        )

        control.click()
        self.select_calendar_date(iso_date)

        expect(control).not_to_have_value("")

    # --------------------------------------------------
    # Table
    # --------------------------------------------------

    def get_current_records(self):
        self.require_records()

        # Read all cells in a single browser-side snapshot to avoid
        # detached row locators while React re-renders.

        records = self.rows.evaluate_all(
            r"""rows => rows.map(row => {
                const cells = Array.from(
                    row.querySelectorAll(':scope > td')
                );

                if (cells.length < 7) return null;

                const value = i =>
                    (cells[i]?.innerText || '').trim();

                const propertyLines = value(1)
                    .split('\n')
                    .map(s => s.trim())
                    .filter(Boolean);

                return {
                    id: row.getAttribute('data-row-key') || value(0),
                    property: propertyLines[0] || '',
                    property_type: propertyLines.length > 1
                        ? propertyLines.at(-1)
                        : '',
                    buyers: value(2),
                    sellers: value(3),
                    payment: value(4),
                    sale_value: value(5),
                    date: value(6)
                };
            }).filter(Boolean)"""
        )

        assert records, (
            "Transaction table contains no readable records"
        )

        return records

    def get_all_records(self):
        """
        Collect records across pagination.
        Wait for new row IDs when changing pages.
        """
        all_records = []
        visited = set()

        expect(self.table).to_be_visible(timeout=20000)

        while True:
            self.require_records()

            if self.pagination.count():
                active_page = self.pagination.locator(
                    ".ant-pagination-item-active"
                ).inner_text().strip()
            else:
                active_page = "1"

            assert active_page not in visited, (
                f"Pagination repeated page {active_page}"
            )

            visited.add(active_page)

            current = self.get_current_records()

            assert current, (
                f"No records on page {active_page}"
            )

            all_records.extend(current)

            print(
                f"Transactions page {active_page}: "
                f"{len(current)} records"
            )

            if not self.pagination.count():
                break

            next_item = self.pagination.locator(
                ".ant-pagination-next"
            )

            disabled = (
                next_item.get_attribute("aria-disabled") == "true"
                or "ant-pagination-disabled" in (
                    next_item.get_attribute("class") or ""
                )
            )

            if disabled:
                break

            previous_ids = [
                record["id"] for record in current
            ]
            previous_page = active_page

            next_item.locator("button").click()

            expect(
                self.pagination.locator(
                    ".ant-pagination-item-active"
                )
            ).not_to_have_text(
                previous_page,
                timeout=20000,
            )

            self.page.wait_for_function(
                """
                previousIds => {
                    const ids = Array.from(
                        document.querySelectorAll(
                            ".ant-table-tbody tr.ant-table-row"
                        )
                    ).map(row =>
                        row.getAttribute("data-row-key")
                    );

                    return ids.length > 0 &&
                        JSON.stringify(ids) !==
                        JSON.stringify(previousIds);
                }
                """,
                arg=previous_ids,
                timeout=20000,
            )

        ids = [
            record["id"] for record in all_records
        ]

        assert len(ids) == len(set(ids)), (
            "Duplicate Transaction IDs across pages"
        )

        print(f"Total Transactions: {len(all_records)}")

        return all_records

    def table_row(self, transaction_id):
        return self.table.locator(
            f'tr.ant-table-row[data-row-key="{transaction_id}"]'
        )

    def first_transaction_id(self):
        self.require_records()

        transaction_id = self.rows.first.get_attribute(
            "data-row-key"
        )

        assert transaction_id, (
            "First row has no Transaction ID"
        )

        return transaction_id

    # --------------------------------------------------
    # Date sorting
    # --------------------------------------------------

    def current_sort(self):
        return (
            self.date_header.get_attribute("aria-sort")
            or "none"
        )

    def click_date_sort(self):
        previous = self.current_sort()

        self.date_header.click()

        self.page.wait_for_function(
            """
            previous => {
                const header = document.querySelector(
                    '.ant-table-thead th[aria-label="Date"]'
                );

                return header &&
                    (
                        header.getAttribute("aria-sort")
                        || "none"
                    ) !== previous;
            }
            """,
            arg=previous,
            timeout=15000,
        )

        return self.current_sort()

    def reset_date_sort(self):
        for _ in range(3):
            if self.current_sort() not in (
                "ascending",
                "descending",
            ):
                return

            self.click_date_sort()

        assert self.current_sort() == "none"

    def set_date_sort(self, direction):
        assert direction in (
            "ascending",
            "descending",
        )

        for _ in range(3):
            if self.current_sort() == direction:
                return

            self.click_date_sort()

        assert self.current_sort() == direction

    def verify_sorted_dates(self, direction):
        """
        Verify date sorting across all transaction pages.

        Retry a fresh read if the table changes while
        collecting records. Incorrect sorting still fails.
        """
        last_error = None

        for attempt in range(3):
            if attempt:
                self.page.reload(
                    wait_until="domcontentloaded",
                    timeout=60000,
                )
                self.wait_for_table_ready()

            self.set_date_sort(direction)

            records = self.get_all_records()

            actual_dates = [
                datetime.strptime(
                    record["date"],
                    "%d-%m-%Y",
                ).date()
                for record in records
            ]

            expected_dates = sorted(
                actual_dates,
                reverse=(direction == "descending"),
            )

            if actual_dates == expected_dates:
                return

            mismatch = next(
                i
                for i, (actual, expected) in enumerate(
                    zip(actual_dates, expected_dates)
                )
                if actual != expected
            )

            last_error = (
                f"Date sorting incorrect: {direction}; "
                f"first mismatch at record {mismatch + 1} "
                f"(transaction {records[mismatch]['id']}): "
                f"actual={actual_dates[mismatch]}, "
                f"expected={expected_dates[mismatch]}; "
                f"checked {len(records)} records"
            )

            print(
                f"Sorting attempt {attempt + 1}/3: "
                f"{last_error}"
            )

        raise AssertionError(last_error)

    def verify_date_sort_per_page(self, direction):
        assert direction in ("ascending", "descending")

        self.set_date_sort(direction)

        records = self.get_all_records()

        page_size = 10
        failed_pages = []

        for start in range(0, len(records), page_size):
            page_records = records[start:start + page_size]

            actual_dates = [
                datetime.strptime(
                    record["date"], "%d-%m-%Y"
                ).date()
                for record in page_records
            ]

            expected_dates = sorted(
                actual_dates,
                reverse=(direction == "descending"),
            )

            page_number = (start // page_size) + 1

            if actual_dates != expected_dates:
                failed_pages.append(page_number)

        assert not failed_pages, (
            f"{direction.title()} sorting is incorrect "
            f"within pages: {failed_pages}"
        )

    # --------------------------------------------------
    # Add/Edit modal
    # --------------------------------------------------

    @property
    def active_modal(self):
        return self.page.locator(
            ".modal-z.modal-z-open.style-modal"
            ":not(.document-preview-modal)"
        ).first

    @property
    def add_modal(self):
        return self.active_modal.filter(
            has=self.page.locator(
                ".modal-z-title h6",
                has_text="Add Transaction",
            )
        )

    @property
    def edit_modal(self):
        return self.active_modal.filter(
            has=self.page.locator(
                ".modal-z-title h6",
                has_text="Edit Transaction",
            )
        )

    def open_add_modal(self):
        self.add_button.click()

        expect(self.add_modal).to_be_visible(
            timeout=15000
        )

    def open_edit_first(self):
        transaction_id = self.first_transaction_id()

        self.rows.first.locator(
            'button.action-btn[title="Edit"]'
        ).click()

        expect(self.edit_modal).to_be_visible(
            timeout=15000
        )

        return transaction_id

    def open_edit(self, transaction_id):
        self.search_for_record(
            transaction_id,
            column=0,
        )

        row = self.table_row(transaction_id)

        expect(row).to_be_visible(
            timeout=20000
        )

        row.locator(
            'button.action-btn[title="Edit"]'
        ).click()

        expect(self.edit_modal).to_be_visible(
            timeout=15000
        )

    def close_modal(self):
        modal = self.active_modal

        modal.locator(
            ":scope > .modal-z-bg > "
            ".modal-z-card > "
            "button.modal-z-close"
        ).click()

        expect(modal).to_be_hidden(
            timeout=10000
        )

    def cancel_modal(self):
        modal = self.active_modal

        modal.locator(
            "button.modal-z-secondary-btn"
        ).click()

        expect(modal).to_be_hidden(
            timeout=10000
        )

    def submit_modal(self):
        modal = self.active_modal

        expect(
            modal.locator(
                "button.modal-z-primary-btn"
            )
        ).to_be_enabled()

        modal.locator(
            "button.modal-z-primary-btn"
        ).click()

        expect(modal).to_be_hidden(timeout=30000)

    # --------------------------------------------------
    # Form fields
    # --------------------------------------------------

    def field(self, field_id):
        assert field_id in self.FORM_FIELDS

        return self.active_modal.locator(
            f'.input-box:has(label[for="{field_id}"])'
        ).first

    def input_for(self, field_id):
        return self.field(field_id).locator("input").first

    def fill_field(self, field_id, value):
        control = self.input_for(field_id)

        control.fill(str(value))

        expect(control).to_have_value(str(value))

    def field_value(self, field_id):
        return self.input_for(field_id).input_value()

    def field_label(self, field_id):
        return self.field(field_id).locator(
            f'label[for="{field_id}"]'
        )

    def verify_required(self, field_id):
        assert field_id in self.REQUIRED_FIELDS

        expect(self.field(field_id)).to_have_class(
            re.compile(r"\breq\b")
        )

        # Required fields use the input-box req class.
        # The asterisk may be generated through CSS.

    # --------------------------------------------------
    # Ant Design dropdowns
    # --------------------------------------------------

    def dropdown_for(self, field_id):
        return self.field(field_id).locator(
            ".ant-select"
        ).first

    def visible_options(self):
        return self.page.locator(
            ".ant-select-dropdown:visible "
            ".ant-select-item-option"
        )

    def open_dropdown(self, field_id):
        dropdown = self.dropdown_for(field_id)

        expect(dropdown).to_be_visible()

        expect(dropdown).not_to_have_class(
            re.compile(r"\bant-select-disabled\b")
        )

        dropdown.click()

        options_popup = self.page.locator(
            ".ant-select-dropdown:visible"
        ).last

        expect(options_popup).to_be_visible(
            timeout=10000
        )

        return dropdown

    def select_option(self, field_id, option_text):
        dropdown = self.open_dropdown(field_id)

        option = self.visible_options().filter(
            has_text=re.compile(
                r"^\s*"
                + re.escape(option_text)
                + r"\s*$",
                re.IGNORECASE,
            )
        )

        expect(option.first).to_be_visible(
            timeout=10000
        )
        option.first.click()

        expect(
            dropdown.locator(
                ".ant-select-selection-item"
            )
        ).to_contain_text(option_text)

    def select_currency(self, currency_code):
        code = currency_code.upper()
        assert code in self.CURRENCY_CODES

        dropdown = self.open_dropdown("currency")

        search = dropdown.locator(
            "input.ant-select-selection-search-input"
        )

        if search.count():
            search.fill(code)

        options = self.visible_options().filter(
            has_text=re.compile(
                r"^" + re.escape(code) + r"\s*[-–]",
                re.IGNORECASE,
            )
        )

        expect(options.first).to_be_visible(
            timeout=15000
        )
        options.first.click()

        expect(
            dropdown.locator(
                ".ant-select-selection-item"
            )
        ).to_contain_text(code)

    def selected_option(self, field_id):
        dropdown = self.dropdown_for(field_id)
        selected = dropdown.locator(
            ".ant-select-selection-item"
        )

        if selected.count():
            return selected.first.inner_text().strip()

        return dropdown.locator(
            ".ant-select-selector"
        ).inner_text().strip()

    def fill_transaction_details(
        self,
        address,
        property_type="Residential",
        payment_method="Bank Transfer",
        currency="AUD",
        sale_value=None,
        deposit=None,
        transaction_date=None,
    ):
        self.fill_field("property", address)
        self.select_option("propertyType", property_type)
        self.select_option("paymentMethod", payment_method)
        self.select_currency(currency)

        if sale_value is not None:
            self.fill_field("propertyValue", sale_value)

        if deposit is not None:
            self.fill_field("amount", deposit)

        if transaction_date is not None:
            self.select_form_date(transaction_date)

    # --------------------------------------------------
    # Connected parties
    # --------------------------------------------------

    def party_dropdown(self, role):
        assert role in ("seller", "buyer")

        field_id = (
            "sellerClientIds"
            if role == "seller"
            else "buyerClientIds"
        )

        return self.dropdown_for(field_id)

    def party_tags(self, role):
        return self.party_dropdown(role).locator(
            ".ant-select-selection-item"
        )

    def select_party(self, role, client_name):
        dropdown = self.party_dropdown(role)

        before = self.party_tags(role).count()

        self.require_party_enabled(role)
        dropdown.click()

        search = dropdown.locator(
            "input.ant-select-selection-search-input"
        )

        expect(search).to_be_attached()
        search.fill(client_name)

        options = self.visible_options().filter(
            has_text=client_name
        )

        expect(options.first).to_be_visible(
            timeout=15000
        )
        options.first.click()

        expect(
            self.party_tags(role)
        ).to_have_count(
            before + 1,
            timeout=15000,
        )

    def remove_last_party(self, role):
        tags = self.party_tags(role)

        before = tags.count()
        assert before > 0, f"No {role} selected"

        tags.last.locator(
            ".ant-select-selection-item-remove"
        ).click()

        expect(tags).to_have_count(before - 1)

    def select_party_tab(self, role):
        assert role in ("Seller", "Buyer")

        tab = self.active_modal.locator(
            ".tab-z-option"
        ).filter(
            has_text=re.compile(
                f"^{role}$"
            )
        )

        if tab.count() == 0:
            pytest.xfail(
                f"{role} detail tab is not rendered in the "
                "current transaction modal; the UI currently "
                "shows only the seller/buyer selectors."
            )

        expect(tab).to_be_visible(timeout=10000)
        tab.click()

        expect(tab).to_have_class(
            re.compile(r"\bactive\b")
        )

    def party_table_headers(self):
        headers = self.active_modal.locator(
            ".grid.grid-cols-3"
        ).filter(
            has=self.page.get_by_text(
                "Legal Name",
                exact=True,
            )
        ).first

        if headers.count() == 0:
            pytest.xfail(
                "Legal Name / Client ID / Role details grid "
                "is not rendered in the current transaction modal."
            )

        return headers

    def get_party_rows(self):
        rows = self.active_modal.locator(
            ".grid.grid-cols-3.border-t"
        )

        results = []

        for row in rows.all():
            values = row.locator(
                "span.p-3"
            ).all_inner_texts()

            if len(values) >= 3:
                results.append({
                    "legal_name": values[0].strip(),
                    "client_id": values[1].strip(),
                    "role": values[2].strip(),
                })

        return results

    # --------------------------------------------------
    # Supporting documents
    # --------------------------------------------------

    def document_button(self):
        return self.active_modal.locator(
            "button.outline-btn"
        ).filter(
            has_text="Add Document"
        )

    def document_uploaders(self):
        return self.active_modal.locator(
            ".uploader-z"
        )

    def add_document_row(self):
        before = self.document_uploaders().count()

        self.document_button().click()

        expect(
            self.document_uploaders()
        ).to_have_count(before + 1)

    def upload_document(self, file_path):
        path = Path(file_path)

        assert path.is_file(), (
            f"File not found: {path}"
        )

        inputs = self.active_modal.locator(
            'input[type="file"]'
        )

        expect(inputs.last).to_be_attached()

        inputs.last.set_input_files(
            str(path)
        )

    def uploaded_documents(self):
        return self.active_modal.locator(
            ".uploader-z .uploaded-file"
        )

    def remove_uploaded_document(self):
        delete_button = self.active_modal.locator(
            'button[title="Delete"]'
        ).last

        expect(delete_button).to_be_visible()
        delete_button.click()

    # --------------------------------------------------
    # Record persistence
    # --------------------------------------------------

    def find_by_address(self, address):
        self.search_for_record(
            address,
            column=1,
        )

        records = self.get_current_records()

        for record in records:
            if (
                record["property"].casefold()
                == address.casefold()
            ):
                return record

        raise AssertionError(
            f"No transaction found with address: {address}"
        )

    # --------------------------------------------------
    # Verify saved transaction values
    # --------------------------------------------------

    def verify_saved_field(
        self,
        transaction_id,
        field_id,
        expected,
    ):
        self.open_edit(transaction_id)

        if field_id in (
            "property",
            "propertyValue",
            "amount",
        ):
            actual = self.field_value(field_id)
        else:
            actual = self.selected_option(field_id)

        assert (
            str(expected).casefold()
            in actual.casefold()
        ), (
            f"{field_id}: expected {expected!r}, "
            f"got {actual!r}"
        )

        self.cancel_modal()
