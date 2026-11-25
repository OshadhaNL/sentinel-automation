
import re
from playwright.sync_api import Page, expect


class IndividualActivitiesPage:
    HEADERS = [
        "Transaction ID",
        "Property Address",
        "Type",
        "Client ID",
        "Payment",
        "Risk Rating",
        "Date",
    ]

    def __init__(self, page: Page):
        self.page = page

    @property
    def heading(self):
        return self.page.get_by_role(
            "heading", name="Transaction History", exact=True
        )

    @property
    def search_input(self):
        return self.page.locator(
            'input[placeholder="Search by ID, property, type, status…"]'
        )

    @property
    def search_box(self):
        return self.page.locator(".search-box-z").filter(
            has=self.search_input
        )

    @property
    def table(self):
        return self.page.locator(".ant-table").filter(
            has=self.page.locator(
                "thead th", has_text="Transaction ID"
            )
        )

    @property
    def add_modal(self):
        return self.page.locator(".modal-z.style-modal").filter(
            has=self.page.locator(
                ":scope > .modal-z-bg > .modal-z-card > .modal-z-title h6",
                has_text=re.compile(r"^Add Transaction$")
            )
        )

    @property
    def export_modal(self):
        return self.page.locator(".modal-z").filter(
            has=self.page.locator(
                ".modal-z-title h6",
                has_text=re.compile(r"^Export Transactions$")
            )
        )

    def open(self):
        tab = self.page.locator(".tab-z-option").filter(
            has_text=re.compile(r"^\s*Activities\s*$")
        )

        expect(tab).to_be_visible(timeout=15000)
        tab.click()

        expect(tab).to_have_class(
            re.compile(r"\bactive\b"),
            timeout=10000
        )

        expect(self.heading).to_be_visible(timeout=15000)

        print("Individual Activities tab opened successfully.")

    def add_transaction_button(self):
        return self.page.locator("button.primary-btn").filter(
            has_text=re.compile(r"Add Transaction\s*$")
        )

    def open_add_modal(self):
        button = self.add_transaction_button()
        expect(button).to_be_visible(timeout=10000)
        expect(button).to_be_enabled(timeout=10000)

        button.click()
        expect(self.add_modal).to_be_visible(timeout=10000)

    def open_export_modal(self):
        button = self.export_button()

        expect(button).to_be_visible(timeout=10000)
        expect(button).to_be_enabled(timeout=10000)

        button.click()

        expect(self.export_modal).to_be_visible(timeout=10000)

    def close_add_modal(self):
        self.add_modal.locator(
            ".modal-z-secondary-btn", has_text="Cancel"
        ).click()
        expect(self.add_modal).not_to_be_visible()

    def close_add_modal_with_x(self):
        close_button = self.add_modal.locator(
            ":scope > .modal-z-bg > .modal-z-card > .modal-z-close"
        )

        expect(close_button).to_be_visible()
        close_button.click()

        expect(self.add_modal).not_to_be_visible()

    def close_export_modal(self):
        self.export_modal.locator(".modal-z-close").click()
        expect(self.export_modal).not_to_be_visible()

    def assert_table_headers(self):
        for header in self.HEADERS:
            expect(
                self.table.locator("thead th").filter(
                    has_text=re.compile(
                        rf"^\s*{re.escape(header)}\s*$"
                    )
                )
            ).to_have_count(1)

    def assert_empty_state(self):
        expect(
            self.table.locator(".ant-empty-description")
        ).to_have_text("No data")

    def search(self, value):
        self.search_input.fill(value)
        self.search_box.locator(".search-btn").click()

    def clear_search(self):
        self.search_box.locator(".clear-btn").click()
        expect(self.search_input).to_be_empty()

    def modal_field(self, name):
        return self.add_modal.locator(
            f'input[name="{name}"]'
        )

    def modal_select(self, field_id):
        return self.add_modal.locator(
            f'.input-box:has(label[for="{field_id}"]) .ant-select'
        )

    def selected_value(self, field_id):
        return self.modal_select(field_id).locator(
            ".ant-select-selection-item"
        )

    def select_party_tab(self, name):
        tab = self.add_modal.locator(
            ".tab-z-option"
        ).filter(
            has=self.page.locator(
                "label", has_text=re.compile(
                    rf"^{re.escape(name)}$"
                )
            )
        )
        tab.click()
        expect(tab).to_have_class(re.compile(r"\bactive\b"))

    def submit_empty_form(self):
        self.add_modal.locator(
            ".modal-z-primary-btn",
            has_text="Add Transaction"
        ).click()

    def assert_required_fields(self):
        for field in (
            "property",
            "propertyType",
            "paymentMethod",
            "currency",
            "date",
        ):
            expect(
                self.add_modal.locator(
                    f'label[for="{field}"]'
                ).locator("xpath=..")
            ).to_have_class(re.compile(r"\breq\b"))

    def assert_transaction_form(self):
        expect(self.modal_field("property")).to_be_visible()
        expect(self.modal_field("propertyValue")).to_be_visible()
        expect(self.modal_field("amount")).to_be_visible()

        expect(
            self.add_modal.get_by_placeholder(
                "Select date and time"
            )
        ).to_be_visible()

        for field in (
            "propertyType",
            "paymentMethod",
            "currency",
            "sellerClientIds",
            "buyerClientIds",
        ):
            expect(self.modal_select(field)).to_be_visible()

        self.assert_required_fields()

    # Extended reusable locators/actions. Existing working methods above are unchanged.
    @property
    def start_date(self):
        return self.page.get_by_placeholder("Start Date")

    @property
    def end_date(self):
        return self.page.get_by_placeholder("End Date")

    @property
    def search_button(self):
        return self.search_box.locator(".search-btn")

    @property
    def clear_button(self):
        return self.search_box.locator(".clear-btn")

    @property
    def table_rows(self):
        return self.table.locator("tbody tr.ant-table-row")

    @property
    def date_sort_header(self):
        return self.table.locator("thead th.ant-table-column-has-sorters")

    @property
    def add_submit(self):
        return self.add_modal.locator(".modal-z-primary-btn", has_text="Add Transaction")

    @property
    def add_cancel(self):
        return self.add_modal.locator(".modal-z-secondary-btn", has_text="Cancel")

    @property
    def document_input(self):
        return self.add_modal.locator('input[type="file"]')

    @property
    def transaction_date(self):
        return self.add_modal.get_by_placeholder("Select date and time")

    def select_dropdown_option(self, field_id, option_text):
        """Ant Design options normally render in a portal outside the modal."""
        self.modal_select(field_id).click()
        option = self.page.locator(".ant-select-dropdown:visible .ant-select-item-option").filter(
            has_text=re.compile(rf"^\s*{re.escape(option_text)}\s*$")
        )
        expect(option).to_be_visible(timeout=5000)
        option.click()

    def dropdown_options(self, field_id):
        self.modal_select(field_id).click()
        options = self.page.locator(".ant-select-dropdown:visible .ant-select-item-option:not(.ant-select-item-option-disabled)")
        expect(options.first).to_be_visible(timeout=10000)
        return options

    def export_action_buttons(self):
        return self.export_modal.locator("button:visible")

    def current_table_values(self, column_index):
        return [x.strip() for x in self.table_rows.locator(
            f"td:nth-child({column_index})"
        ).all_text_contents()]

    def export_button(self):
        """The page toolbar Export button (not the modal action)."""
        return self.page.locator("button.outline-btn").filter(
            has_text=re.compile(r"^\s*Export\s*$")
        )

    def export_submit_button(self):
        """Export action inside the Export Transactions dialog."""
        return self.export_modal.locator(
            ":scope > .modal-z-bg > .modal-z-card > .modal-z-body button.primary-btn"
        ).filter(has_text=re.compile(r"^\s*Export\s*$"))

    def select_export_scope(self, scope):
        if scope not in ("Current page only", "All data"):
            raise ValueError(f"Unsupported export scope: {scope!r}")
        option = self.export_modal.locator(
            ":scope > .modal-z-bg > .modal-z-card > .modal-z-body label"
        ).filter(has_text=re.compile(rf"^\s*{re.escape(scope)}\s*$"))
        expect(option).to_be_visible()
        option.click()

    def download_transactions(self, scope):
        """Click export and return the completed Playwright Download object."""
        self.open_export_modal()
        self.select_export_scope(scope)
        button = self.export_submit_button()
        expect(button).to_be_visible()
        expect(button).to_be_enabled()
        with self.page.expect_download(timeout=30000) as download_info:
            button.click()
        return download_info.value

    # Additional reusable actions for the comprehensive suite.
    def dropdown_labels(self, field_id):
        options = self.dropdown_options(field_id)
        expect(options.first).to_be_visible(timeout=10000)
        return [s.strip() for s in options.all_text_contents() if s.strip()]

    def choose_first_dropdown_option(self, field_id):
        """Select an Ant Design option without relying on an unstable portal click."""
        control = self.modal_select(field_id)
        # The dropdown may already have a value; opening it again can close it.
        selected = self.selected_value(field_id)
        if selected.count() and selected.first.is_visible():
            existing = selected.first.inner_text().strip()
            if existing:
                return existing

        control.click()
        options = self.page.locator(
            ".ant-select-dropdown:visible "
            ".ant-select-item-option:not(.ant-select-item-option-disabled)"
        )
        expect(options.first).to_be_visible(timeout=10000)
        label = options.first.inner_text().strip()
        assert label, f"No labeled option available for {field_id}"

        # Ant Design can animate or re-render the portal between discovery and
        # a pointer click. Dispatching the click directly avoids stability waits
        # while still firing the application's normal click handler.
        options.first.dispatch_event("click", timeout=5000)
        expect(self.selected_value(field_id)).to_contain_text(label, timeout=10000)
        return label

    def selected_export_scope(self):
        return self.export_modal.locator('input[type="radio"]:checked')

    def date_filter_inputs(self):
        return self.start_date, self.end_date

    def add_modal_direct_close(self):
        return self.add_modal.locator(':scope > .modal-z-bg > .modal-z-card > .modal-z-close')

    def table_snapshot(self):
        return [row.strip() for row in self.table_rows.all_text_contents()]

    def export_excel(self, scope, directory):
        from pathlib import Path
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        download = self.download_transactions(scope)
        destination = directory / download.suggested_filename
        download.save_as(destination)
        return destination

    def fill_transaction_datetime(self, value=None):
        from datetime import datetime
        from playwright.sync_api import expect

        field = self.add_modal.get_by_placeholder(
            "Select date and time"
        )

        expect(field).to_be_visible(timeout=10000)

        # Open the calendar through the actual input.
        field.click()

        calendar = self.page.locator(
            ".ant-picker-dropdown:visible "
            ".ant-picker-panel-container"
        )

        expect(calendar).to_be_visible(timeout=10000)

        # Select today's date using the calendar's
        # actual date cell, rather than typing.
        today = calendar.locator(
            "td.ant-picker-cell-today"
            ":not(.ant-picker-cell-disabled) "
            ".ant-picker-cell-inner"
        )

        if today.count() > 0:
            today.click()
        else:
            # Fallback: click the Today control supplied
            # by this application's date picker.
            today_button = calendar.locator(
                ".ant-picker-now-btn"
            )

            expect(today_button).to_be_visible(timeout=10000)
            today_button.click()

        # Verify the picker actually updated the input.
        expect(field).not_to_be_empty(timeout=10000)

        selected = field.input_value().strip()

        # Verify that the required-field validation
        # is no longer displayed.
        date_error = self.add_modal.get_by_text(
            "Date is required",
            exact=True,
        )

        expect(date_error).to_have_count(0, timeout=10000)

        print(f"Transaction date selected: {selected}")

        return selected

    def choose_party_client(self, field_id):
        """Choose an available party without waiting for an animated portal click.

        Do not reopen an already expanded select: clicking the control a second
        time can close the dropdown between option lookup and selection.
        """
        control = self.modal_select(field_id)
        expect(control).to_be_visible(timeout=10000)

        selected = self.selected_value(field_id)
        if selected.count():
            existing = selected.first.inner_text().strip()
            if existing:
                return existing

        dropdown = self.page.locator(
            ".ant-select-dropdown:visible"
        )
        if dropdown.count() == 0:
            control.click()

        options = self.page.locator(
            ".ant-select-dropdown:visible "
            ".ant-select-item-option:not(.ant-select-item-option-disabled)"
        )
        try:
            expect(options.first).to_be_visible(timeout=5000)
        except AssertionError:
            # Some clients have no available connected parties.
            return None

        label = options.first.inner_text().strip()
        if not label:
            raise AssertionError(f"Blank party option in {field_id}")

        # Ant Design may close or reposition the dropdown during its animation.
        # Dispatch an actual DOM click without Playwright's stability wait.
        options.first.dispatch_event("click", timeout=5000)

        # A selected tag/value must be rendered; merely dispatching is not proof.
        expect(self.selected_value(field_id).first).to_contain_text(
            label, timeout=10000
        )
        return label

    def create_test_transaction(self, address, property_value="250000", amount="25000"):
        """Create a QA transaction and verify the saved address in the table."""
        import os
        self.open_add_modal()
        self.modal_field("property").fill(address)
        self.modal_field("propertyValue").fill(property_value)
        self.modal_field("amount").fill(amount)
        chosen = {}
        for field in ("propertyType", "paymentMethod", "currency"):
            override = os.getenv("ACTIVITIES_" + field.upper(), "").strip()
            if override:
                self.select_dropdown_option(field, override)
                chosen[field] = override
            else:
                chosen[field] = self.choose_first_dropdown_option(field)

        chosen["transactionDate"] = self.fill_transaction_datetime(
            os.getenv("ACTIVITIES_TRANSACTION_DATETIME") or None
        )
        for field in ("sellerClientIds", "buyerClientIds"):
            chosen[field] = self.choose_party_client(field)

        self.add_submit.click()
        try:
            expect(self.add_modal).not_to_be_visible(timeout=20000)
        except AssertionError as exc:
            errors = self.add_modal.locator(
                ".ant-form-item-explain-error, [role=alert], .error, .err-meg"
            ).all_text_contents()
            raise AssertionError(
                f"Transaction creation rejected: {errors!r}; selections={chosen!r}"
            ) from exc

        self.search(address)
        expect(self.table_rows).not_to_have_count(0, timeout=20000)
        assert any(
            address.lower() in value.lower()
            for value in self.current_table_values(2)
        ), f"Created transaction {address!r} not found in table"
        return chosen
