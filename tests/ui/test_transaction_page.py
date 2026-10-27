
import os
import re
from datetime import date

import pytest
from playwright.sync_api import (
    Page,
    expect,
    TimeoutError as PlaywrightTimeoutError,
)

from pages.loginPage import LoginPage
from pages.transactionPage import TransactionPage


@pytest.mark.ui
class TestTransactionPage:

    @pytest.fixture(autouse=True)
    def setup_transaction(self, page: Page, base_url: str):
        self.page = page

        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")

        assert email, "Set TEST_EMAIL"
        assert password, "Set TEST_PASSWORD"

        page.set_default_navigation_timeout(60000)

        login = LoginPage(page)

        try:
            login.open(base_url)
        except PlaywrightTimeoutError:
            if "/nolimit/login" not in page.url:
                raise

        login.enter_email(email)
        login.enter_password(password)
        login.click_login()

        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$"),
            timeout=60000,
        )

        self.transaction = TransactionPage(page)
        self.transaction.open()

    # ==========================================
    # Main page
    # ==========================================

    def test_transaction_heading(self):
        expect(
            self.transaction.heading
        ).to_be_visible()

    def test_transaction_description(self):
        expect(
            self.transaction.description
        ).to_be_visible()

    # ==========================================
    # Search
    # ==========================================

    def test_search_input_visible(self):
        expect(
            self.transaction.search_input
        ).to_be_visible()

    def test_search_placeholder(self):
        expect(
            self.transaction.search_input
        ).to_have_attribute(
            "placeholder",
            "Search by ID, property, type, status…",
        )

    def test_search_accepts_any_characters(self):
        text = "Test123!@#"

        self.transaction.search_input.fill(text)

        expect(
            self.transaction.search_input
        ).to_have_value(text)

    def test_search_icon_visible(self):
        expect(
            self.transaction.search_icon
        ).to_be_visible()

    def test_search_button_visible(self):
        expect(
            self.transaction.search_button
        ).to_be_visible()

    def test_clear_icon_visible(self):
        self.transaction.search_input.fill("Example")

        expect(
            self.transaction.clear_icon
        ).to_be_visible()

    def test_clear_search(self):
        self.transaction.search_input.fill("Example")
        self.transaction.clear_search()

        expect(
            self.transaction.search_input
        ).to_have_value("")

    def test_search_by_transaction_id(self):
        transaction_id = (
            self.transaction.first_transaction_id()
        )

        self.transaction.search_for_record(
            transaction_id,
            column=0,
        )

        ids = [
            record["id"]
            for record in self.transaction.get_current_records()
        ]

        assert transaction_id in ids

    def test_search_by_property(self):
        records = self.transaction.get_current_records()
        assert records, "Transaction table is empty"

        address = records[0]["property"]
        assert address

        self.transaction.search_for_record(
            address,
            column=1,
        )

        found = self.transaction.get_current_records()

        assert any(
            address.casefold() in record["property"].casefold()
            for record in found
        )

    # ==========================================
    # Date filter
    # ==========================================

    def test_date_filter_visible(self):
        expect(
            self.transaction.date_range
        ).to_be_visible()

    def test_date_placeholders(self):
        expect(
            self.transaction.start_date
        ).to_have_attribute(
            "placeholder",
            "Start Date",
        )

        expect(
            self.transaction.end_date
        ).to_have_attribute(
            "placeholder",
            "End Date",
        )

    def test_date_calendar_icon(self):
        expect(
            self.transaction.date_range.locator(
                ".anticon-calendar"
            )
        ).to_be_visible()

    def test_date_filter_calendar_opens(self):
        self.transaction.start_date.click()

        expect(
            self.transaction.calendar_popup()
        ).to_be_visible()

    def test_start_and_end_date_selection(self):
        today = date.today()
        start = today.replace(day=1)

        self.transaction.select_date_range(
            start.isoformat(),
            today.isoformat(),
        )

        expect(
            self.transaction.start_date
        ).not_to_have_value("")

        expect(
            self.transaction.end_date
        ).not_to_have_value("")

    # ==========================================
    # Main buttons
    # ==========================================

    def test_add_transaction_button(self):
        expect(
            self.transaction.add_button
        ).to_be_visible()

    def test_add_transaction_plus_icon(self):
        expect(
            self.transaction.add_button.locator(
                "i.fa-plus"
            )
        ).to_be_visible()

    def test_export_button(self):
        expect(
            self.transaction.export_button
        ).to_be_visible()

    # ==========================================
    # Transaction table
    # ==========================================

    def test_table_visible(self):
        expect(
            self.transaction.table
        ).to_be_visible()

    @pytest.mark.parametrize(
        "position,header",
        list(enumerate(TransactionPage.HEADERS)),
    )
    def test_column_headers(self, position, header):
        expect(
            self.transaction.headers.nth(position)
        ).to_have_text(header)

    def test_transaction_id_value(self):
        record = self.transaction.get_current_records()[0]

        assert re.fullmatch(
            r"TR-\d+",
            record["id"],
        )

    def test_property_address_value(self):
        record = self.transaction.get_current_records()[0]

        assert record["property"], (
            "Property Address is empty"
        )

    def test_property_type_value(self):
        records = self.transaction.get_current_records()

        assert records[0]["property_type"] in (
            "Commercial",
            "Residential",
        )

    def test_buyer_name_column_value(self):
        self.transaction.require_records()

        expect(
            self.transaction.rows.first.locator("td").nth(2)
        ).to_be_visible()

    def test_vendor_seller_column_value(self):
        self.transaction.require_records()

        expect(
            self.transaction.rows.first.locator("td").nth(3)
        ).to_be_visible()

    def test_payment_column_value(self):
        record = self.transaction.get_current_records()[0]

        assert record["payment"] in (
            "Bank Transfer",
            "Cash",
        )

    def test_contract_sale_value_column(self):
        expect(
            self.transaction.rows.first.locator(
                "td"
            ).nth(5)
        ).to_be_visible()

    def test_date_column_value(self):
        record = self.transaction.get_current_records()[0]

        assert re.fullmatch(
            r"\d{2}-\d{2}-\d{4}",
            record["date"],
        )

    def test_date_sort_icons(self):
        expect(
            self.transaction.date_header.locator(
                ".ant-table-column-sorter-up"
            )
        ).to_be_visible()

        expect(
            self.transaction.date_header.locator(
                ".ant-table-column-sorter-down"
            )
        ).to_be_visible()

    def test_first_click_sorts_ascending(self):
        self.transaction.reset_date_sort()

        actual = self.transaction.click_date_sort()

        assert actual == "ascending"

    def test_second_click_sorts_descending(self):
        self.transaction.reset_date_sort()

        assert (
            self.transaction.click_date_sort()
            == "ascending"
        )

        assert (
            self.transaction.click_date_sort()
            == "descending"
        )

    def test_third_click_clears_sorting(self):
        self.transaction.reset_date_sort()

        self.transaction.click_date_sort()
        self.transaction.click_date_sort()

        assert (
            self.transaction.click_date_sort()
            == "none"
        )

    def test_dates_sorted_ascending(self):
        self.transaction.verify_sorted_dates(
            "ascending"
        )

    def test_dates_sorted_descending(self):
        self.transaction.verify_sorted_dates(
            "descending"
        )

    def test_pagination_visible(self):
        expect(
            self.transaction.pagination
        ).to_be_visible()

    def test_pagination_next_button(self):
        expect(
            self.transaction.pagination.locator(
                ".ant-pagination-next"
            )
        ).to_be_visible()

    def test_edit_button_visible(self):
        self.transaction.require_records()

        expect(
            self.transaction.rows.first.locator(
                'button[title="Edit"]'
            )
        ).to_be_visible()

    def test_edit_icon_visible(self):
        self.transaction.require_records()

        expect(
            self.transaction.rows.first.locator(
                'button[title="Edit"] i.fa-pen'
            )
        ).to_be_visible()

    # ==========================================
    # Edit Transaction modal
    # ==========================================

    def test_edit_transaction_opens(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.edit_modal
        ).to_be_visible()

    def test_edit_transaction_title(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.edit_modal.locator(
                ".modal-z-title h6"
            ).first
        ).to_have_text("Edit Transaction")

    def test_edit_close_icon(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.edit_modal.locator(
                ":scope > .modal-z-bg > .modal-z-card > "
                "button.modal-z-close i.fa-times-circle"
            ).first
        ).to_be_visible()

    def test_edit_close_button(self):
        self.transaction.open_edit_first()
        self.transaction.close_modal()

        expect(
            self.transaction.edit_modal
        ).to_be_hidden()

    def test_edit_cancel_button(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.edit_modal.locator(
                "button.modal-z-secondary-btn"
            )
        ).to_have_text("Cancel")

    def test_edit_cancel_closes_popup(self):
        self.transaction.open_edit_first()
        self.transaction.cancel_modal()

        expect(
            self.transaction.edit_modal
        ).to_be_hidden()

    def test_edit_save_changes_button(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.edit_modal.locator(
                "button.modal-z-primary-btn"
            )
        ).to_have_text("Save Changes")

    def test_edit_transaction_details_heading(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.edit_modal.get_by_text(
                "Transaction Details",
                exact=True,
            )
        ).to_be_visible()

    def test_edit_connected_party_heading(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.edit_modal.get_by_text(
                "Connected Party Details",
                exact=True,
            )
        ).to_be_visible()

    # ==========================================
    # Edit form labels and required fields
    # ==========================================

    @pytest.mark.parametrize(
        "field_id,label",
        list(TransactionPage.FORM_FIELDS.items()),
    )
    def test_edit_field_labels(self, field_id, label):
        self.transaction.open_edit_first()

        expect(
            self.transaction.field_label(field_id)
        ).to_contain_text(label)

    @pytest.mark.parametrize(
        "field_id",
        TransactionPage.REQUIRED_FIELDS,
    )
    def test_edit_required_fields(self, field_id):
        self.transaction.open_edit_first()
        self.transaction.verify_required(field_id)

    # ==========================================
    # Edit existing values
    # ==========================================

    def test_edit_previous_property_address(self):
        self.transaction.open_edit_first()

        assert self.transaction.field_value(
            "property"
        ).strip()

    def test_edit_property_address_editable(self):
        self.transaction.open_edit_first()

        self.transaction.fill_field(
            "property",
            "Temporary Edit Address",
        )

        self.transaction.cancel_modal()

    def test_edit_property_type_previous_value(self):
        self.transaction.open_edit_first()

        assert self.transaction.selected_option(
            "propertyType"
        ) in TransactionPage.PROPERTY_TYPES

    def test_edit_payment_method_previous_value(self):
        self.transaction.open_edit_first()

        assert self.transaction.selected_option(
            "paymentMethod"
        ) in TransactionPage.PAYMENT_METHODS

    def test_edit_currency_previous_value(self):
        self.transaction.open_edit_first()

        selected = self.transaction.selected_option(
            "currency"
        )

        assert selected[:3] in TransactionPage.CURRENCY_CODES

    @pytest.mark.parametrize(
        "field_id",
        ["propertyValue", "amount"],
    )
    def test_edit_amount_fields_editable(self, field_id):
        self.transaction.open_edit_first()

        self.transaction.fill_field(
            field_id,
            "5000",
        )

        self.transaction.cancel_modal()

    def test_edit_date_previous_value(self):
        self.transaction.open_edit_first()

        value = self.transaction.active_modal.locator(
            'input[placeholder="Select date and time"]'
        ).input_value()

        assert re.fullmatch(
            r"\d{2}-\d{2}-\d{4}",
            value,
        )

    def test_edit_calendar_icon(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.active_modal.locator(
                ".custom-datepicker .anticon-calendar"
            )
        ).to_be_visible()

    def test_edit_date_selectable(self):
        self.transaction.open_edit_first()

        self.transaction.select_form_date(
            date.today().isoformat()
        )

        self.transaction.cancel_modal()

    # ==========================================
    # Edit form dropdowns
    # ==========================================

    @pytest.mark.parametrize(
        "property_type",
        TransactionPage.PROPERTY_TYPES,
    )
    def test_edit_property_type_selectable(
        self, property_type
    ):
        self.transaction.open_edit_first()

        self.transaction.select_option(
            "propertyType",
            property_type,
        )

        self.transaction.cancel_modal()

    @pytest.mark.parametrize(
        "payment",
        TransactionPage.PAYMENT_METHODS,
    )
    def test_edit_payment_method_selectable(self, payment):
        self.transaction.open_edit_first()

        self.transaction.select_option(
            "paymentMethod",
            payment,
        )

        self.transaction.cancel_modal()

    @pytest.mark.parametrize(
        "currency",
        TransactionPage.CURRENCY_CODES,
    )
    def test_edit_currency_selectable(self, currency):
        self.transaction.open_edit_first()

        self.transaction.select_currency(currency)

        self.transaction.cancel_modal()

    # ==========================================
    # Edit connected parties
    # ==========================================

    def test_edit_vendor_dropdown_visible(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.party_dropdown("seller")
        ).to_be_visible()

    def test_edit_buyer_dropdown_visible(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.party_dropdown("buyer")
        ).to_be_visible()


    def test_edit_vendor_dropdown_enabled(self):
        self.transaction.open_edit_first()

        dropdown = self.transaction.party_dropdown("seller")

        expect(dropdown).to_be_visible()
        expect(dropdown).not_to_have_class(
            re.compile(r"\bant-select-disabled\b")
        )

        combobox = dropdown.get_by_role("combobox")
        expect(combobox).to_be_enabled()

    def test_edit_buyer_dropdown_enabled(self):
        self.transaction.open_edit_first()

        dropdown = self.transaction.party_dropdown("buyer")

        expect(dropdown).to_be_visible()
        expect(dropdown).not_to_have_class(
            re.compile(r"\bant-select-disabled\b")
        )

        combobox = dropdown.get_by_role("combobox")
        expect(combobox).to_be_enabled()


    def test_edit_vendor_dropdown_opens(self):
        self.transaction.open_edit_first()

        self.transaction.open_dropdown(
            "sellerClientIds"
        )

        expect(
            self.transaction.visible_options().first
        ).to_be_visible()

    def test_edit_buyer_dropdown_opens(self):
        self.transaction.open_edit_first()

        self.transaction.open_dropdown(
            "buyerClientIds"
        )

        expect(
            self.transaction.visible_options().first
        ).to_be_visible()

    def test_edit_seller_tab(self):
        self.transaction.open_edit_first()

        self.transaction.select_party_tab("Seller")

    def test_edit_buyer_tab(self):
        self.transaction.open_edit_first()

        self.transaction.select_party_tab("Buyer")

    def test_edit_connected_party_table_headers(self):
        self.transaction.open_edit_first()

        headers = self.transaction.party_table_headers()

        for text in (
            "Legal Name",
            "Client ID",
            "Role",
        ):
            expect(
                headers.get_by_text(text, exact=True)
            ).to_be_visible()

    def test_edit_buyer_selection(self):
        self.transaction.open_edit_first()

        buyer = os.getenv(
            "TEST_TRANSACTION_BUYER",
            "Donald J Trump",
        )

        before = self.transaction.party_tags(
            "buyer"
        ).count()

        existing = (
            self.transaction.party_tags("buyer")
            .all_inner_texts()
        )

        if not any(
            buyer.casefold() in name.casefold()
            for name in existing
        ):
            self.transaction.select_party(
                "buyer", buyer
            )

            assert (
                self.transaction.party_tags("buyer").count()
                == before + 1
            )

        self.transaction.cancel_modal()

    # ==========================================
    # Edit Transaction - Supporting Documents
    # ==========================================

    def test_edit_supporting_document_heading(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.edit_modal.get_by_text(
                "Supporting Document (if any)",
                exact=True,
            )
        ).to_be_visible()

    def test_edit_add_document_button(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.document_button()
        ).to_be_visible()

    def test_edit_add_document_plus_icon(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.document_button().locator(
                "i.fa-plus"
            )
        ).to_be_visible()

    def test_edit_add_document_row(self):
        self.transaction.open_edit_first()

        self.transaction.add_document_row()

        expect(
            self.transaction.document_uploaders().last
        ).to_be_visible()

    def test_edit_choose_file_button(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.edit_modal.get_by_role(
                "button",
                name="Choose File",
            ).first
        ).to_be_visible()

    def test_edit_document_file_types(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.edit_modal.get_by_text(
                re.compile(
                    r"PDF,\s*PNG,\s*JPG\s*or\s*JPEG"
                )
            ).first
        ).to_be_visible()

    def test_edit_document_max_size(self):
        self.transaction.open_edit_first()

        expect(
            self.transaction.edit_modal.get_by_text(
                re.compile(r"max\.\s*10MB")
            ).first
        ).to_be_visible()

    # ==========================================
    # Add Transaction - Modal
    # ==========================================

    def test_add_transaction_opens(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.add_modal
        ).to_be_visible()

    def test_add_transaction_title(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.add_modal.locator(
                ".modal-z-title h6"
            ).first
        ).to_have_text("Add Transaction")

    def test_add_close_icon(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.add_modal.locator(
                ":scope > .modal-z-bg > .modal-z-card > "
                "button.modal-z-close i.fa-times-circle"
            ).first
        ).to_be_visible()

    def test_add_close_button(self):
        self.transaction.open_add_modal()

        self.transaction.close_modal()

        expect(
            self.transaction.add_modal
        ).to_be_hidden()

    def test_add_cancel_button(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.add_modal.locator(
                "button.modal-z-secondary-btn"
            )
        ).to_have_text("Cancel")

    def test_add_cancel_closes_popup(self):
        self.transaction.open_add_modal()

        self.transaction.cancel_modal()

        expect(
            self.transaction.add_modal
        ).to_be_hidden()

    def test_add_submit_button(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.add_modal.locator(
                "button.modal-z-primary-btn"
            )
        ).to_have_text("Add Transaction")

    def test_add_transaction_details_heading(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.add_modal.get_by_text(
                "Transaction Details",
                exact=True,
            )
        ).to_be_visible()

    def test_add_connected_party_heading(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.add_modal.get_by_text(
                "Connected Party Details",
                exact=True,
            )
        ).to_be_visible()

    # ==========================================
    # Add Transaction - Form Labels
    # ==========================================

    @pytest.mark.parametrize(
        "field_id,label",
        list(TransactionPage.FORM_FIELDS.items()),
    )
    def test_add_field_labels(self, field_id, label):
        self.transaction.open_add_modal()

        expect(
            self.transaction.field_label(field_id)
        ).to_contain_text(label)

    # ==========================================
    # Add Transaction - Required Fields
    # ==========================================

    @pytest.mark.parametrize(
        "field_id",
        TransactionPage.REQUIRED_FIELDS,
    )
    def test_add_required_fields(self, field_id):
        self.transaction.open_add_modal()

        self.transaction.verify_required(field_id)

    # ==========================================
    # Add Transaction - Property Address
    # ==========================================

    def test_add_property_address_visible(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.input_for("property")
        ).to_be_visible()

    def test_add_property_address_placeholder(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.input_for("property")
        ).to_have_attribute(
            "placeholder",
            "Address, unit, plot",
        )

    def test_add_property_address_editable(self):
        self.transaction.open_add_modal()

        self.transaction.fill_field(
            "property",
            "Automation Test Address",
        )

        expect(
            self.transaction.input_for("property")
        ).to_have_value(
            "Automation Test Address"
        )

    # ==========================================
    # Add Transaction - Property Type
    # ==========================================

    def test_add_property_type_dropdown_visible(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.dropdown_for(
                "propertyType"
            )
        ).to_be_visible()

    def test_add_property_type_options_visible(self):
        self.transaction.open_add_modal()

        self.transaction.open_dropdown(
            "propertyType"
        )

        for property_type in TransactionPage.PROPERTY_TYPES:
            expect(
                self.transaction.visible_options().filter(
                    has_text=re.compile(
                        r"^\s*"
                        + re.escape(property_type)
                        + r"\s*$",
                        re.IGNORECASE,
                    )
                ).first
            ).to_be_visible()

    @pytest.mark.parametrize(
        "property_type",
        TransactionPage.PROPERTY_TYPES,
    )
    def test_add_property_type_selectable(
        self,
        property_type,
    ):
        self.transaction.open_add_modal()

        self.transaction.select_option(
            "propertyType",
            property_type,
        )

        assert (
            self.transaction.selected_option(
                "propertyType"
            ) == property_type
        )

    # ==========================================
    # Add Transaction - Payment Method
    # ==========================================

    def test_add_payment_method_dropdown_visible(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.dropdown_for(
                "paymentMethod"
            )
        ).to_be_visible()

    def test_add_payment_method_options_visible(self):
        self.transaction.open_add_modal()

        self.transaction.open_dropdown(
            "paymentMethod"
        )

        for payment in TransactionPage.PAYMENT_METHODS:
            expect(
                self.transaction.visible_options().filter(
                    has_text=re.compile(
                        r"^\s*"
                        + re.escape(payment)
                        + r"\s*$",
                        re.IGNORECASE,
                    )
                ).first
            ).to_be_visible()

    @pytest.mark.parametrize(
        "payment",
        TransactionPage.PAYMENT_METHODS,
    )
    def test_add_payment_method_selectable(
        self,
        payment,
    ):
        self.transaction.open_add_modal()

        self.transaction.select_option(
            "paymentMethod",
            payment,
        )

        assert (
            self.transaction.selected_option(
                "paymentMethod"
            ) == payment
        )

    # ==========================================
    # Add Transaction - Currency
    # ==========================================

    def test_add_currency_dropdown_visible(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.dropdown_for(
                "currency"
            )
        ).to_be_visible()

    def test_add_currency_default_value(self):
        self.transaction.open_add_modal()

        selected = self.transaction.selected_option(
            "currency"
        )

        assert selected.startswith("AUD"), (
            f"Expected AUD as default currency, "
            f"got {selected!r}"
        )

    def test_add_currency_options_visible(self):
        self.transaction.open_add_modal()

        self.transaction.open_dropdown(
            "currency"
        )

        options = self.transaction.visible_options()

        expect(
            options.first
        ).to_be_visible()

        option_text = " ".join(
            options.all_inner_texts()
        )

        assert "AUD" in option_text, (
            "AUD option not found"
        )

    @pytest.mark.parametrize(
        "currency",
        TransactionPage.CURRENCY_CODES,
    )
    def test_add_currency_selectable(self, currency):
        self.transaction.open_add_modal()

        self.transaction.select_currency(currency)

        selected = self.transaction.selected_option(
            "currency"
        )

        assert selected.startswith(currency), (
            f"Expected {currency}, got {selected!r}"
        )

    # ==========================================
    # Add Transaction - Amount Fields
    # ==========================================

    @pytest.mark.parametrize(
        "field_id",
        ["propertyValue", "amount"],
    )
    def test_add_amount_fields_visible(self, field_id):
        self.transaction.open_add_modal()

        expect(
            self.transaction.input_for(field_id)
        ).to_be_visible()

    @pytest.mark.parametrize(
        "field_id",
        ["propertyValue", "amount"],
    )
    def test_add_amount_fields_editable(self, field_id):
        self.transaction.open_add_modal()

        self.transaction.fill_field(
            field_id,
            "5000",
        )

        expect(
            self.transaction.input_for(field_id)
        ).to_have_value("5000")

    # ==========================================
    # Add Transaction - Date
    # ==========================================

    def test_add_date_input_visible(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.active_modal.locator(
                'input[placeholder="Select date and time"]'
            )
        ).to_be_visible()

    def test_add_date_placeholder(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.active_modal.locator(
                'input[placeholder="Select date and time"]'
            )
        ).to_have_attribute(
            "placeholder",
            "Select date and time",
        )

    def test_add_calendar_icon(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.active_modal.locator(
                ".custom-datepicker .anticon-calendar"
            )
        ).to_be_visible()

    def test_add_date_calendar_opens(self):
        self.transaction.open_add_modal()

        self.transaction.active_modal.locator(
            'input[placeholder="Select date and time"]'
        ).click()

        expect(
            self.transaction.calendar_popup()
        ).to_be_visible()

    def test_add_date_selectable(self):
        self.transaction.open_add_modal()

        self.transaction.select_form_date(
            date.today().isoformat()
        )

        expect(
            self.transaction.active_modal.locator(
                'input[placeholder="Select date and time"]'
            )
        ).not_to_have_value("")

    # ==========================================
    # Add Transaction - Connected Parties
    # ==========================================

    def test_add_vendor_dropdown_visible(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.party_dropdown("seller")
        ).to_be_visible()

    def test_add_buyer_dropdown_visible(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.party_dropdown("buyer")
        ).to_be_visible()

    def test_add_vendor_options_visible(self):
        self.transaction.open_add_modal()

        self.transaction.open_dropdown(
            "sellerClientIds"
        )

        expect(
            self.transaction.visible_options().first
        ).to_be_visible(timeout=15000)

    def test_add_buyer_options_visible(self):
        self.transaction.open_add_modal()

        self.transaction.open_dropdown(
            "buyerClientIds"
        )

        expect(
            self.transaction.visible_options().first
        ).to_be_visible(timeout=15000)

    def test_add_seller_selectable(self):
        self.transaction.open_add_modal()

        seller = os.getenv(
            "TEST_TRANSACTION_SELLER",
            "Mia Perera",
        )

        self.transaction.select_party(
            "seller",
            seller,
        )

        expect(
            self.transaction.party_tags("seller")
        ).to_contain_text(seller)

    def test_add_buyer_selectable(self):
        self.transaction.open_add_modal()

        buyer = os.getenv(
            "TEST_TRANSACTION_BUYER",
            "Donald J Trump",
        )

        self.transaction.select_party(
            "buyer",
            buyer,
        )

        expect(
            self.transaction.party_tags("buyer")
        ).to_contain_text(buyer)

    def test_add_seller_removable(self):
        self.transaction.open_add_modal()

        seller = os.getenv(
            "TEST_TRANSACTION_SELLER",
            "Mia Perera",
        )

        self.transaction.select_party(
            "seller",
            seller,
        )

        before = self.transaction.party_tags(
            "seller"
        ).count()

        assert before > 0

        self.transaction.remove_last_party("seller")

        expect(
            self.transaction.party_tags("seller")
        ).to_have_count(before - 1)

    def test_add_buyer_removable(self):
        self.transaction.open_add_modal()

        buyer = os.getenv(
            "TEST_TRANSACTION_BUYER",
            "Donald J Trump",
        )

        self.transaction.select_party(
            "buyer",
            buyer,
        )

        before = self.transaction.party_tags(
            "buyer"
        ).count()

        assert before > 0

        self.transaction.remove_last_party("buyer")

        expect(
            self.transaction.party_tags("buyer")
        ).to_have_count(before - 1)

    # ==========================================
    # Add Transaction - Party Details
    # ==========================================

    def test_add_seller_tab(self):
        self.transaction.open_add_modal()

        seller = os.getenv(
            "TEST_TRANSACTION_SELLER",
            "Mia Perera",
        )

        self.transaction.select_party(
            "seller",
            seller,
        )

        self.transaction.select_party_tab("Seller")

    def test_add_buyer_tab(self):
        self.transaction.open_add_modal()

        buyer = os.getenv(
            "TEST_TRANSACTION_BUYER",
            "Donald J Trump",
        )

        self.transaction.select_party(
            "buyer",
            buyer,
        )

        self.transaction.select_party_tab("Buyer")

    def test_add_party_table_headers(self):
        self.transaction.open_add_modal()

        buyer = os.getenv(
            "TEST_TRANSACTION_BUYER",
            "Donald J Trump",
        )

        self.transaction.select_party(
            "buyer",
            buyer,
        )

        headers = self.transaction.party_table_headers()

        for header in (
            "Legal Name",
            "Client ID",
            "Role",
        ):
            expect(
                headers.get_by_text(
                    header,
                    exact=True,
                )
            ).to_be_visible()

    # ==========================================
    # Add Transaction - Supporting Documents
    # ==========================================

    def test_add_supporting_document_heading(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.add_modal.get_by_text(
                "Supporting Document (if any)",
                exact=True,
            )
        ).to_be_visible()

    def test_add_document_button_visible(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.document_button()
        ).to_be_visible()

    def test_add_document_plus_icon(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.document_button().locator(
                "i.fa-plus"
            )
        ).to_be_visible()

    def test_add_document_row(self):
        self.transaction.open_add_modal()

        self.transaction.add_document_row()

        expect(
            self.transaction.document_uploaders().last
        ).to_be_visible()

    def test_add_choose_file_button(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.add_modal.get_by_role(
                "button",
                name="Choose File",
            ).first
        ).to_be_visible()

    def test_add_document_file_types(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.add_modal.get_by_text(
                re.compile(
                    r"PDF,\s*PNG,\s*JPG\s*or\s*JPEG"
                )
            ).first
        ).to_be_visible()

    def test_add_document_max_size(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.add_modal.get_by_text(
                re.compile(r"max\.\s*10MB")
            ).first
        ).to_be_visible()

    def test_add_document_multiple_rows(self):
        self.transaction.open_add_modal()

        initial = (
            self.transaction.document_uploaders().count()
        )

        self.transaction.add_document_row()
        self.transaction.add_document_row()

        expect(
            self.transaction.document_uploaders()
        ).to_have_count(initial + 2)

    # ==========================================
    # Add Transaction - Form Validation
    # ==========================================

    def test_add_property_address_empty_initially(self):
        self.transaction.open_add_modal()

        expect(
            self.transaction.input_for("property")
        ).to_have_value("")

    def test_add_property_address_accepts_text(self):
        self.transaction.open_add_modal()

        address = "Automation Property Test 123"

        self.transaction.fill_field(
            "property",
            address,
        )

        expect(
            self.transaction.input_for("property")
        ).to_have_value(address)

    def test_add_sale_value_accepts_numbers(self):
        self.transaction.open_add_modal()

        self.transaction.fill_field(
            "propertyValue",
            "100000",
        )

        expect(
            self.transaction.input_for("propertyValue")
        ).to_have_value("100000")

    def test_add_deposit_amount_accepts_numbers(self):
        self.transaction.open_add_modal()

        self.transaction.fill_field(
            "amount",
            "25000",
        )

        expect(
            self.transaction.input_for("amount")
        ).to_have_value("25000")

    def test_add_property_type_required(self):
        self.transaction.open_add_modal()

        self.transaction.verify_required(
            "propertyType"
        )

    def test_add_payment_method_required(self):
        self.transaction.open_add_modal()

        self.transaction.verify_required(
            "paymentMethod"
        )

    def test_add_currency_required(self):
        self.transaction.open_add_modal()

        self.transaction.verify_required(
            "currency"
        )

    def test_add_date_required(self):
        self.transaction.open_add_modal()

        self.transaction.verify_required(
            "date"
        )

    # ==========================================
    # Final UI Verification
    # ==========================================

    def test_add_modal_remains_open_when_editing(self):
        self.transaction.open_add_modal()

        self.transaction.fill_field(
            "property",
            "Temporary Automation Address",
        )

        expect(
            self.transaction.add_modal
        ).to_be_visible()

    def test_add_cancel_discards_unsaved_changes(self):
        self.transaction.open_add_modal()

        self.transaction.fill_field(
            "property",
            "Unsaved Automation Address",
        )

        self.transaction.cancel_modal()

        self.transaction.open_add_modal()

        expect(
            self.transaction.input_for("property")
        ).to_have_value("")

    def test_edit_cancel_discards_unsaved_changes(self):
        self.transaction.open_edit_first()

        original = self.transaction.field_value(
            "property"
        )

        self.transaction.fill_field(
            "property",
            "Unsaved Edited Address",
        )

        self.transaction.cancel_modal()

        self.transaction.open_edit_first()

        expect(
            self.transaction.input_for("property")
        ).to_have_value(original)
