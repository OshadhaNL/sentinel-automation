import os
import re

import pytest
from playwright.sync_api import expect

from pages.profiles.individual.individualActivitiesPage import (
    IndividualActivitiesPage,
)

from config.screening_test_data import READ_ONLY_CLIENT_ID, WRITE_CLIENT_ID
from pages.profiles.profileNavigation import open_client_profile


_SEEDED_WORKERS = set()


def _needs_transaction(node):
    name = node.name
    return (
        name.startswith("test_positive_create_transaction_end_to_end")
        or name.startswith("test_search_by_existing_")
        or name.startswith("test_positive_search_matches_existing_")
        or name.startswith("test_positive_transaction_")
        or name in {
            "test_transaction_rows_have_expected_column_count",
            "test_transaction_ids_are_nonempty",
            "test_property_addresses_are_nonempty",
            "test_transaction_client_ids_match_profile",
            "test_date_sort_changes_direction",
            "test_no_duplicate_transaction_ids_on_current_page",
            "test_positive_sort_does_not_change_transaction_id_set",
        }
    )


@pytest.fixture
def activities(page, base_url, request):
    needs_rows = _needs_transaction(request.node)
    read_id = os.getenv("ACTIVITIES_TEST_CLIENT_ID", READ_ONLY_CLIENT_ID).strip()
    write_id = os.getenv("ACTIVITIES_WRITE_CLIENT_ID", WRITE_CLIENT_ID).strip()
    write_enabled = os.getenv("ACTIVITIES_ALLOW_WRITES") == "1"
    if needs_rows and write_enabled:
        if not write_id:
            pytest.skip("Transaction creation requires a configured approved disposable WRITE_CLIENT_ID; set ACTIVITIES_WRITE_CLIENT_ID or config/screening_test_data.py")
        assert write_id != read_id, "Writable client must differ from read-only client"
        client_id = write_id
    else:
        client_id = read_id
    assert client_id, "Configure Screening client IDs or ACTIVITIES_*_CLIENT_ID"
    open_client_profile(page, base_url, "individual", client_id)
    view = IndividualActivitiesPage(page)
    view.open()
    view.test_client_id = client_id
    if needs_rows and write_enabled and not request.node.name.startswith("test_positive_create_transaction_end_to_end") and os.getenv("ACTIVITIES_AUTO_SEED") == "1":
        worker = os.getenv("PYTEST_XDIST_WORKER", "master")
        key = (worker, client_id)
        if view.table_rows.count() == 0 and key not in _SEEDED_WORKERS:
            address = "QA-ACTIVITIES-" + uuid.uuid4().hex[:12].upper()
            view.create_test_transaction(address)
            view.clear_search()
            _SEEDED_WORKERS.add(key)
    return view


@pytest.mark.ui
class TestIndividualActivitiesUI:

    def test_activities_heading_visible(self, activities):
        expect(activities.heading).to_be_visible()

    def test_transaction_description_visible(self, activities):
        expect(
            activities.page.get_by_text(
                re.compile(
                    r"All transactions involving .*"
                    r"Flag entries as suspicious"
                )
            )
        ).to_be_visible()

    def test_search_input_visible(self, activities):
        expect(activities.search_input).to_be_visible()

    def test_search_placeholder(self, activities):
        expect(activities.search_input).to_have_attribute(
            "placeholder",
            "Search by ID, property, type, status…"
        )

    def test_search_button_visible(self, activities):
        expect(
            activities.search_box.locator(".search-btn")
        ).to_be_visible()

    def test_search_accepts_text(self, activities):
        activities.search_input.fill("TEST123")
        expect(activities.search_input).to_have_value(
            "TEST123"
        )

    def test_clear_search(self, activities):
        activities.search_input.fill("TEST123")
        activities.clear_search()

    def test_search_button_clickable(self, activities):
        activities.search("NONEXISTENT_TEST_TRANSACTION")

    def test_date_range_inputs_visible(self, activities):
        expect(
            activities.page.get_by_placeholder("Start Date")
        ).to_be_visible()
        expect(
            activities.page.get_by_placeholder("End Date")
        ).to_be_visible()

    def test_add_transaction_button_visible(self, activities):
        expect(
            activities.add_transaction_button()
        ).to_be_visible()

    def test_export_button_visible(self, activities):
        expect(
            activities.page.get_by_role(
                "button",
                name=re.compile(r"Export\s*$")
            )
        ).to_be_visible()

    def test_transaction_table_headers(self, activities):
        activities.assert_table_headers()

    def test_date_sort_control_visible(self, activities):
        expect(
            activities.table.locator(
                "thead th.ant-table-column-has-sorters"
            )
        ).to_be_visible()


@pytest.mark.ui
class TestIndividualActivitiesModal:

    def test_add_transaction_modal_opens(self, activities):
        activities.open_add_modal()

    def test_add_transaction_modal_closes_with_cancel(
        self, activities
    ):
        activities.open_add_modal()
        activities.close_add_modal()

    def test_add_transaction_modal_closes_with_x(
        self, activities
    ):
        activities.open_add_modal()
        activities.close_add_modal_with_x()

    def test_transaction_form_fields_visible(self, activities):
        activities.open_add_modal()
        activities.assert_transaction_form()

    def test_required_fields_marked(self, activities):
        activities.open_add_modal()
        activities.assert_required_fields()

    def test_property_address_accepts_text(self, activities):
        activities.open_add_modal()
        activities.modal_field("property").fill(
            "123 Test Street"
        )
        expect(
            activities.modal_field("property")
        ).to_have_value("123 Test Street")

    def test_contract_sale_value_accepts_number(
        self, activities
    ):
        activities.open_add_modal()
        activities.modal_field("propertyValue").fill("250000")
        expect(
            activities.modal_field("propertyValue")
        ).to_have_value("250000")

    def test_deposit_amount_accepts_number(self, activities):
        activities.open_add_modal()
        activities.modal_field("amount").fill("25000")
        expect(
            activities.modal_field("amount")
        ).to_have_value("25000")

    def test_seller_tab_visible(self, activities):
        activities.open_add_modal()
        activities.select_party_tab("Seller")

    def test_buyer_tab_clickable(self, activities):
        activities.open_add_modal()
        activities.select_party_tab("Buyer")

    def test_connected_party_table_headers(self, activities):
        activities.open_add_modal()
        for header in ("Legal Name", "Client ID", "Role"):
            expect(
                activities.add_modal.get_by_text(
                    header, exact=True
                )
            ).to_be_visible()

    def test_supporting_document_section_visible(
        self, activities
    ):
        activities.open_add_modal()
        expect(
            activities.add_modal.get_by_text(
                "Supporting Document (if any)"
            )
        ).to_be_visible()

    def test_add_document_button_visible(self, activities):
        activities.open_add_modal()
        expect(
            activities.add_modal.get_by_role(
                "button", name="Add Document"
            )
        ).to_be_visible()

    def test_document_file_input_accept_types(
        self, activities
    ):
        activities.open_add_modal()
        expect(
            activities.add_modal.locator('input[type="file"]')
        ).to_have_attribute(
            "accept",
            "application/pdf,image/png,image/jpeg,image/jpg"
        )

    def test_negative_empty_form_does_not_close_modal(
        self, activities
    ):
        activities.open_add_modal()
        activities.submit_empty_form()
        expect(activities.add_modal).to_be_visible()

    def test_negative_cancel_does_not_create_transaction(
        self, activities
    ):
        activities.open_add_modal()
        activities.modal_field("property").fill(
            "CANCEL TEST PROPERTY"
        )
        activities.close_add_modal()
        expect(
            activities.add_modal
        ).not_to_be_visible()


@pytest.mark.ui
class TestIndividualActivitiesExport:

    def test_export_modal_opens(self, activities):
        activities.open_export_modal()

    def test_export_options_visible(self, activities):
        activities.open_export_modal()
        expect(
            activities.export_modal.get_by_text(
                "Current page only"
            )
        ).to_be_visible()
        expect(
            activities.export_modal.get_by_text(
                "All data", exact=True
            )
        ).to_be_visible()

    def test_export_modal_closes(self, activities):
        activities.open_export_modal()
        activities.close_export_modal()


# -------------------- EXTENDED ACTIVITIES COVERAGE --------------------
# All original 32 tests are retained above. Tests below are deliberately
# independent, and use a fresh authenticated page via the activities fixture.
# Write operations are opt-in: ACTIVITIES_ALLOW_WRITES=1, disposable client only.
# Tests requiring existing transactions skip with an explicit reason when absent.

from pathlib import Path
from datetime import datetime
import uuid
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def _rows_or_skip(view):
    if view.table_rows.count() == 0:
        pytest.skip("No existing transaction: enable ACTIVITIES_ALLOW_WRITES=1 for automatic disposable data creation")
    return view.table_rows


def _nonempty_dropdown_or_skip(view, field):
    options = view.dropdown_options(field)
    if options.count() == 0:
        pytest.skip(f"No selectable {field} options in current QA data")
    return options


def _writable_client_or_skip():
    if os.getenv("ACTIVITIES_ALLOW_WRITES") != "1":
        pytest.skip("Writes disabled: ACTIVITIES_ALLOW_WRITES=1 is required")
    write_id = os.getenv("ACTIVITIES_WRITE_CLIENT_ID", WRITE_CLIENT_ID).strip()
    read_id = os.getenv("ACTIVITIES_TEST_CLIENT_ID", READ_ONLY_CLIENT_ID).strip()
    assert write_id, "Set WRITE_CLIENT_ID in config/screening_test_data.py"
    assert write_id != read_id, "Disposable write client must differ from read-only client"


@pytest.mark.ui
class TestActivitiesExtendedPageUI:
    def test_active_tab_after_navigation(self, activities):
        tab = activities.page.locator(".tab-z-option").filter(has_text=re.compile(r"^\s*Activities\s*$"))
        expect(tab).to_have_class(re.compile(r"\bactive\b"))

    def test_search_field_enabled(self, activities):
        expect(activities.search_input).to_be_enabled()

    def test_search_button_enabled(self, activities):
        expect(activities.search_button).to_be_enabled()

    def test_negative_clear_button_hidden_for_empty_search(self, activities):
        expect(activities.search_input).to_be_empty()
        expect(activities.clear_button).not_to_be_visible()

    def test_clear_button_appears_after_typing(self, activities):
        activities.search_input.fill("ABC")
        expect(activities.clear_button).to_be_visible()

    def test_clear_button_disappears_after_clearing(self, activities):
        activities.search_input.fill("ABC")
        activities.clear_search()
        expect(activities.clear_button).not_to_be_visible()

    def test_start_and_end_date_are_distinct(self, activities):
        expect(activities.start_date).to_have_count(1)
        expect(activities.end_date).to_have_count(1)

    def test_add_button_enabled(self, activities):
        expect(activities.add_transaction_button()).to_be_enabled()

    def test_export_button_enabled(self, activities):
        expect(activities.page.get_by_role("button", name=re.compile(r"Export\s*$"))).to_be_enabled()

    def test_table_has_one_header_row(self, activities):
        expect(activities.table.locator("thead tr")).to_have_count(1)

    def test_table_empty_or_has_rows(self, activities):
        assert activities.table_rows.count() > 0 or activities.table.locator(".ant-empty-description").count() > 0

    def test_negative_no_add_modal_initially(self, activities):
        expect(activities.add_modal).not_to_be_visible()

    def test_negative_no_export_modal_initially(self, activities):
        expect(activities.export_modal).not_to_be_visible()

    def test_table_header_order(self, activities):
        headers = [h.strip() for h in activities.table.locator("thead th").all_text_contents()]
        assert headers[:len(activities.HEADERS)] == activities.HEADERS

    def test_sort_control_is_interactive(self, activities):
        expect(activities.date_sort_header).to_be_visible()
        activities.date_sort_header.click()
        expect(activities.table).to_be_visible()


@pytest.mark.ui
class TestActivitiesExtendedSearch:
    @pytest.mark.parametrize("term", ["TEST123", "Property", "sale", "abc123", "A B C", "1234567890"])
    def test_search_accepts_various_terms(self, activities, term):
        activities.search_input.fill(term)
        expect(activities.search_input).to_have_value(term)

    @pytest.mark.parametrize("term", ["NO_MATCH_" + "Z" * 32, "unlikely-transaction-987654321"])
    def test_negative_search_nonexistent_returns_no_rows(self, activities, term):
        activities.search(term)
        expect(activities.table.locator(".ant-empty-description")).to_be_visible(timeout=10000)
        expect(activities.table_rows).to_have_count(0)

    @pytest.mark.parametrize("term", ["   ", "!@#$%^&*()", "' OR 1=1 --", "<script>alert(1)</script>", "x" * 255])
    def test_negative_search_input_is_handled_safely(self, activities, term):
        activities.search(term)
        expect(activities.table).to_be_visible()
        # Must never cause a JavaScript alert, page crash, or disappearance of the table.
        assert not activities.page.is_closed()

    def test_search_clearing_restores_unfiltered_state(self, activities):
        before = activities.table_rows.count()
        activities.search("NO_MATCH_" + uuid.uuid4().hex)
        expect(activities.table_rows).to_have_count(0)
        activities.clear_search()
        expect(activities.search_input).to_be_empty()
        expect(activities.table_rows).to_have_count(before, timeout=10000)

    def test_search_enter_key_keeps_page_functional(self, activities):
        activities.search_input.fill("TEST")
        activities.search_input.press("Enter")
        expect(activities.table).to_be_visible()

    def test_search_by_existing_transaction_id(self, activities):
        _rows_or_skip(activities)
        transaction_id = activities.current_table_values(1)[0]
        if not transaction_id:
            pytest.skip("First row has no transaction ID")
        activities.search(transaction_id)
        expect(activities.table_rows).not_to_have_count(0, timeout=10000)
        assert any(transaction_id in v for v in activities.current_table_values(1))

    def test_search_by_existing_property_address(self, activities):
        _rows_or_skip(activities)
        address = activities.current_table_values(2)[0]
        if not address:
            pytest.skip("First row has no property address")
        activities.search(address)
        expect(activities.table_rows).not_to_have_count(0, timeout=10000)
        assert any(address.lower() in v.lower() for v in activities.current_table_values(2))

    def test_search_by_existing_transaction_type(self, activities):
        _rows_or_skip(activities)
        value = activities.current_table_values(3)[0]
        if not value:
            pytest.skip("First row has no transaction type")
        activities.search(value)
        expect(activities.table_rows).not_to_have_count(0, timeout=10000)


@pytest.mark.ui
class TestActivitiesExtendedModal:
    def test_modal_title_visible(self, activities):
        activities.open_add_modal()
        expect(activities.add_modal.locator(
            ":scope > .modal-z-bg > .modal-z-card .modal-z-title h6"
        ).first).to_have_text("Add Transaction")

    def test_cancel_button_visible_and_enabled(self, activities):
        activities.open_add_modal()
        expect(activities.add_cancel).to_be_visible()
        expect(activities.add_cancel).to_be_enabled()

    def test_submit_button_visible(self, activities):
        activities.open_add_modal()
        expect(activities.add_submit).to_be_visible()

    @pytest.mark.parametrize("field", ["property", "propertyValue", "amount"])
    def test_text_field_initially_empty(self, activities, field):
        activities.open_add_modal()
        expect(activities.modal_field(field)).to_be_empty()

    @pytest.mark.parametrize("field", ["propertyType", "paymentMethod", "currency", "sellerClientIds", "buyerClientIds"])
    def test_select_control_visible_and_enabled(self, activities, field):
        activities.open_add_modal()
        expect(activities.modal_select(field)).to_be_visible()
        expect(activities.modal_select(field)).not_to_have_class(re.compile(r"\bant-select-disabled\b"))

    @pytest.mark.parametrize("field", ["propertyType", "paymentMethod", "currency"])
    def test_dropdown_has_options(self, activities, field):
        activities.open_add_modal()
        opts = _nonempty_dropdown_or_skip(activities, field)
        assert opts.count() >= 1

    @pytest.mark.parametrize("field", ["propertyType", "paymentMethod", "currency"])
    def test_dropdown_option_can_be_selected(self, activities, field):
        activities.open_add_modal()
        opts = _nonempty_dropdown_or_skip(activities, field)
        label = opts.first.inner_text().strip()
        opts.first.click()
        expect(activities.selected_value(field)).to_contain_text(label)

    @pytest.mark.parametrize("field", ["property", "propertyValue", "amount"])
    def test_form_values_not_saved_after_cancel(self, activities, field):
        activities.open_add_modal()
        value = "Temporary address" if field == "property" else "1234"
        activities.modal_field(field).fill(value)
        activities.close_add_modal()
        activities.open_add_modal()
        expect(activities.modal_field(field)).to_be_empty()

    def test_buyer_and_seller_tab_switching(self, activities):
        activities.open_add_modal()
        for name in ("Buyer", "Seller", "Buyer"):
            activities.select_party_tab(name)

    def test_date_picker_visible_and_enabled(self, activities):
        activities.open_add_modal()
        expect(activities.transaction_date).to_be_visible()
        expect(activities.transaction_date).to_be_enabled()

    def test_file_size_hint_visible(self, activities):
        activities.open_add_modal()
        expect(activities.add_modal.get_by_text(re.compile(r"max\.\s*10\s*MB", re.I))).to_be_visible()

    def test_file_upload_is_single_file(self, activities):
        activities.open_add_modal()
        assert activities.document_input.get_attribute("multiple") is None

    def test_file_input_is_present(self, activities):
        activities.open_add_modal()
        expect(activities.document_input).to_have_count(1)

    def test_negative_required_property_missing_blocks_submission(self, activities):
        activities.open_add_modal()
        activities.submit_empty_form()
        expect(activities.add_modal).to_be_visible()

    @pytest.mark.parametrize("text", ["   ", "<script>alert(1)</script>", "' OR 1=1 --", "A" * 256])
    def test_negative_property_input_validation(self, activities, text):
        activities.open_add_modal()
        activities.modal_field("property").fill(text)
        expect(activities.modal_field("property")).to_have_value(text)
        # Input acceptance is not validation; assert safe, stable UI without inventing a max length.
        expect(activities.add_modal).to_be_visible()

    @pytest.mark.parametrize("field", ["propertyValue", "amount"])
    @pytest.mark.parametrize("value", ["0", "-1", "0.01", "123.45", "999999999.99"])
    def test_amount_field_boundary_input(self, activities, field, value):
        activities.open_add_modal()
        input_el = activities.modal_field(field)
        input_el.fill(value)
        assert input_el.input_value() != ""  # browser may normalize numeric input
        expect(activities.add_modal).to_be_visible()

    @pytest.mark.parametrize("field", ["propertyValue", "amount"])
    @pytest.mark.parametrize("value", ["abc", "1e1000", "--5"])
    def test_negative_amount_rejects_or_normalizes_invalid_input(self, activities, field, value):
        activities.open_add_modal()
        input_el = activities.modal_field(field)
        try:
            input_el.fill(value)
        except Exception as exc:
            # Playwright fill rejects nonnumeric values on native number inputs.
            assert "Cannot type text into input[type=number]" in str(exc) or "Input of type" in str(exc) or "Malformed value" in str(exc)
            return
        assert input_el.input_value() != value or input_el.evaluate("el => el.validity.valid") is False, (
            f"Invalid numeric input {value!r} accepted as valid in {field}"
        )

    def test_negative_cancel_after_typing_keeps_table_unchanged(self, activities):
        before = activities.table_rows.count()
        activities.open_add_modal()
        activities.modal_field("property").fill("CANCEL_" + uuid.uuid4().hex)
        activities.close_add_modal()
        expect(activities.table_rows).to_have_count(before)

    def test_negative_close_x_after_typing_keeps_table_unchanged(self, activities):
        before = activities.table_rows.count()
        activities.open_add_modal()
        activities.modal_field("property").fill("CLOSE_" + uuid.uuid4().hex)
        activities.close_add_modal_with_x()
        expect(activities.table_rows).to_have_count(before)

    def test_document_file_input_accepts_pdf_png_jpg(self, activities):
        activities.open_add_modal()
        accept = activities.document_input.get_attribute("accept") or ""
        for mime in ("application/pdf", "image/png", "image/jpeg"):
            assert mime in accept

    def test_document_upload_valid_small_pdf(self, activities):
        activities.open_add_modal()
        # A minimal in-memory PDF is enough to test the input and upload preview UI.
        pdf = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\n%%EOF\n"
        activities.document_input.set_input_files({"name": "activities-test.pdf", "mimeType": "application/pdf", "buffer": pdf})
        expect(activities.add_modal).to_be_visible()

    @pytest.mark.parametrize("name,mime,data", [
        ("activities-test.png", "image/png", b"\x89PNG\r\n\x1a\n"),
        ("activities-test.jpg", "image/jpeg", b"\xff\xd8\xff\xd9"),
    ])
    def test_document_upload_image_file_input(self, activities, name, mime, data):
        activities.open_add_modal()
        activities.document_input.set_input_files({"name": name, "mimeType": mime, "buffer": data})
        expect(activities.add_modal).to_be_visible()

    def test_negative_unsupported_file_type_not_advertised(self, activities):
        activities.open_add_modal()
        assert ".exe" not in (activities.document_input.get_attribute("accept") or "")


@pytest.mark.ui
class TestActivitiesExtendedTable:
    def test_empty_state_when_no_transactions(self, activities):
        if activities.table_rows.count() > 0:
            pytest.skip("Client has transactions; empty-state case requires an empty client")
        activities.assert_empty_state()

    def test_transaction_rows_have_expected_column_count(self, activities):
        rows = _rows_or_skip(activities)
        for i in range(min(rows.count(), 10)):
            assert rows.nth(i).locator("td").count() >= len(activities.HEADERS)

    def test_transaction_ids_are_nonempty(self, activities):
        _rows_or_skip(activities)
        assert all(v for v in activities.current_table_values(1))

    def test_property_addresses_are_nonempty(self, activities):
        _rows_or_skip(activities)
        assert all(v for v in activities.current_table_values(2))

    def test_transaction_client_ids_match_profile(self, activities):
        _rows_or_skip(activities)
        expected = activities.test_client_id
        assert all(expected in v for v in activities.current_table_values(4))

    def test_date_sort_changes_direction(self, activities):
        _rows_or_skip(activities)
        header = activities.date_sort_header
        header.click()
        first_state = header.get_attribute("aria-sort") or header.get_attribute("class")
        header.click()
        second_state = header.get_attribute("aria-sort") or header.get_attribute("class")
        assert first_state != second_state, "Sort direction did not change"

    def test_no_duplicate_transaction_ids_on_current_page(self, activities):
        _rows_or_skip(activities)
        ids = activities.current_table_values(1)
        assert len(ids) == len(set(ids))


@pytest.mark.ui
class TestActivitiesExtendedExport:
    def test_export_modal_title(self, activities):
        activities.open_export_modal()
        expect(activities.export_modal.locator(".modal-z-title h6")).to_have_text("Export Transactions")

    @pytest.mark.parametrize("scope", ["Current page only", "All data"])
    def test_export_scope_selectable(self, activities, scope):
        activities.open_export_modal()
        activities.select_export_scope(scope)
        expect(activities.export_modal).to_be_visible()

    def test_negative_export_modal_closed_initially(self, activities):
        expect(activities.export_modal).not_to_be_visible()

    def test_export_modal_reopens(self, activities):
        activities.open_export_modal()
        activities.close_export_modal()
        activities.open_export_modal()
        expect(activities.export_modal).to_be_visible()

    def test_export_does_not_hide_table(self, activities):
        activities.open_export_modal()
        activities.close_export_modal()
        expect(activities.table).to_be_visible()


@pytest.mark.ui
class TestActivitiesOptInIntegration:
    """High-impact scenarios require verified QA fixtures and explicit opt-in."""

    def test_positive_create_transaction_end_to_end(self, activities):
        """Create a new transaction and verify the specific saved record."""
        _writable_client_or_skip()
        address = "QA-ACTIVITIES-" + uuid.uuid4().hex[:12].upper()
        activities.create_test_transaction(
            address=address,
            property_value="250000",
            amount="25000",
        )
        activities.clear_search()
        activities.search(address)
        expect(activities.table_rows).not_to_have_count(0, timeout=20000)
        assert any(
            address.lower() in value.lower()
            for value in activities.current_table_values(2)
        ), f"Created transaction {address!r} was not found in Transaction History"

    @pytest.mark.parametrize("scope", ["Current page only", "All data"])
    def test_positive_export_download(self, activities, scope):
        """Check real browser download for both available export scopes."""
        download = activities.download_transactions(scope)
        assert download.suggested_filename.lower().endswith((".xlsx", ".xls")), (
            f"Expected Excel export, got {download.suggested_filename!r}"
        )
        assert download.failure() is None


# ---------------- COMPREHENSIVE ADDITIONAL COVERAGE ----------------
# Read-only by default. Data-dependent cases skip explicitly when no records exist.
# These tests assert observed behavior rather than treating an open modal as proof
# of successful business validation.

@pytest.mark.ui
class TestActivitiesComprehensiveSearch:
    @pytest.mark.parametrize('term', [
        'A', 'a', '123', '123.45', 'Property Street', ' 123 ',
        'UPPER lower', 'a-b_c', 'a/b', 'éàñ', '中文', '🏠',
        '"quoted"', 'back\\slash', 'a.b@example.com',
    ])
    def test_positive_search_accepts_text_variations(self, activities, term):
        activities.search_input.fill(term)
        expect(activities.search_input).to_have_value(term)
        expect(activities.search_button).to_be_enabled()

    @pytest.mark.parametrize('term', [
        'NO_MATCH_' + 'Q' * 48, 'not-a-real-property-000999',
        '000000000000000000000000',
    ])
    def test_negative_search_no_matching_transactions(self, activities, term):
        activities.search(term)
        expect(activities.table_rows).to_have_count(0, timeout=15000)
        expect(activities.table.locator('.ant-empty-description')).to_be_visible()

    def test_positive_repeated_search_and_clear(self, activities):
        for term in ('FIRST_NO_MATCH_12345', 'SECOND_NO_MATCH_67890'):
            activities.search(term)
            expect(activities.table_rows).to_have_count(0, timeout=15000)
            activities.clear_search()
            expect(activities.search_input).to_be_empty()

    def test_positive_search_input_remains_after_submit(self, activities):
        activities.search('NO_MATCH_' + uuid.uuid4().hex)
        expect(activities.search_input).not_to_be_empty()

    def test_positive_search_can_be_edited_after_submit(self, activities):
        activities.search('FIRST_' + uuid.uuid4().hex)
        activities.search_input.fill('SECOND_' + uuid.uuid4().hex)
        expect(activities.search_input).to_have_value(re.compile('^SECOND_'))

    def test_negative_clear_button_not_visible_before_input(self, activities):
        expect(activities.clear_button).not_to_be_visible()

    def test_positive_clear_button_resets_multiple_searches(self, activities):
        for term in ('AAA', 'BBB', 'CCC'):
            activities.search_input.fill(term)
            expect(activities.clear_button).to_be_visible()
            activities.clear_search()
            expect(activities.clear_button).not_to_be_visible()

    def test_positive_search_does_not_open_add_modal(self, activities):
        activities.search('TEST')
        expect(activities.add_modal).not_to_be_visible()

    def test_positive_search_does_not_open_export_modal(self, activities):
        activities.search('TEST')
        expect(activities.export_modal).not_to_be_visible()


@pytest.mark.ui
class TestActivitiesComprehensiveForm:
    @pytest.mark.parametrize('field', ['property', 'propertyValue', 'amount'])
    def test_positive_form_field_can_be_replaced(self, activities, field):
        activities.open_add_modal()
        control = activities.modal_field(field)
        first = 'Address One' if field == 'property' else '100'
        second = 'Address Two' if field == 'property' else '200'
        control.fill(first)
        control.fill(second)
        expect(control).to_have_value(second)

    @pytest.mark.parametrize('field', ['property', 'propertyValue', 'amount'])
    def test_positive_form_field_can_be_cleared(self, activities, field):
        activities.open_add_modal()
        control = activities.modal_field(field)
        control.fill('Test property' if field == 'property' else '100')
        control.clear()
        expect(control).to_be_empty()

    @pytest.mark.parametrize('field', ['propertyType', 'paymentMethod', 'currency'])
    def test_positive_dropdown_selected_value_survives_tab_switch(self, activities, field):
        activities.open_add_modal()
        chosen = activities.choose_first_dropdown_option(field)
        activities.select_party_tab('Buyer')
        activities.select_party_tab('Seller')
        expect(activities.selected_value(field)).to_contain_text(chosen)

    @pytest.mark.parametrize('field', ['propertyType', 'paymentMethod', 'currency'])
    def test_positive_dropdown_selection_resets_after_cancel(self, activities, field):
        activities.open_add_modal()
        activities.choose_first_dropdown_option(field)
        activities.close_add_modal()
        activities.open_add_modal()
        # Reopened form should not preserve a manually selected value from a cancelled draft.
        assert activities.selected_value(field).count() == 0 or not activities.selected_value(field).first.is_visible(), (
            f'Cancelled draft retained {field}'
        )

    @pytest.mark.parametrize('field', ['property', 'propertyValue', 'amount'])
    def test_negative_close_x_discards_draft_field(self, activities, field):
        activities.open_add_modal()
        activities.modal_field(field).fill('Temporary' if field == 'property' else '42')
        activities.close_add_modal_with_x()
        activities.open_add_modal()
        expect(activities.modal_field(field)).to_be_empty()

    def test_positive_modal_buttons_are_distinct(self, activities):
        activities.open_add_modal()
        expect(activities.add_submit).to_have_count(1)
        expect(activities.add_cancel).to_have_count(1)
        expect(activities.add_modal_direct_close()).to_have_count(1)

    def test_positive_add_modal_keeps_background_table_intact(self, activities):
        before = activities.table_snapshot()
        activities.open_add_modal()
        activities.close_add_modal()
        assert activities.table_snapshot() == before

    def test_positive_buyer_seller_tabs_do_not_clear_property(self, activities):
        activities.open_add_modal()
        activities.modal_field('property').fill('Persistent draft property')
        for name in ('Buyer', 'Seller', 'Buyer', 'Seller'):
            activities.select_party_tab(name)
        expect(activities.modal_field('property')).to_have_value('Persistent draft property')

    def test_negative_empty_submit_keeps_table_unchanged(self, activities):
        before = activities.table_snapshot()
        activities.open_add_modal()
        activities.submit_empty_form()
        expect(activities.add_modal).to_be_visible()
        assert activities.table_snapshot() == before

    @pytest.mark.parametrize('field', ['propertyType', 'paymentMethod', 'currency'])
    def test_positive_dropdown_has_no_blank_option_labels(self, activities, field):
        activities.open_add_modal()
        labels = activities.dropdown_labels(field)
        assert labels and all(label.strip() for label in labels)

    def test_positive_supporting_document_is_optional_label(self, activities):
        activities.open_add_modal()
        expect(activities.add_modal.get_by_text(re.compile('Supporting Document.*if any', re.I))).to_be_visible()

    def test_negative_document_input_does_not_allow_multiple_files(self, activities):
        activities.open_add_modal()
        assert activities.document_input.get_attribute('multiple') is None

    @pytest.mark.parametrize('extension,mime', [
        ('pdf', 'application/pdf'), ('png', 'image/png'),
        ('jpg', 'image/jpeg'), ('jpeg', 'image/jpeg'),
    ])
    def test_positive_document_picker_accepts_supported_file(self, activities, extension, mime):
        activities.open_add_modal()
        activities.document_input.set_input_files({
            'name': f'qa-document.{extension}', 'mimeType': mime,
            'buffer': b'QA file picker test only',
        })
        expect(activities.add_modal).to_be_visible()


@pytest.mark.ui
class TestActivitiesComprehensiveTable:
    @pytest.mark.parametrize('column', range(1, 8))
    def test_positive_transaction_cells_not_blank(self, activities, column):
        _rows_or_skip(activities)
        values = activities.current_table_values(column)
        assert values and all(v.strip() for v in values), f'Blank column {column}'

    def test_positive_transaction_rows_have_consistent_columns(self, activities):
        rows = _rows_or_skip(activities)
        widths = [rows.nth(i).locator('td').count() for i in range(rows.count())]
        assert len(set(widths)) == 1
        assert widths[0] >= len(activities.HEADERS)

    def test_positive_search_matches_existing_transaction_id_case_exact(self, activities):
        _rows_or_skip(activities)
        value = activities.current_table_values(1)[0]
        activities.search(value)
        expect(activities.table_rows).not_to_have_count(0, timeout=15000)
        assert value in activities.current_table_values(1)

    def test_positive_search_matches_existing_address_partial(self, activities):
        _rows_or_skip(activities)
        address = activities.current_table_values(2)[0]
        token = address[:min(5, len(address))].strip()
        if not token:
            pytest.skip('No searchable address token')
        activities.search(token)
        expect(activities.table_rows).not_to_have_count(0, timeout=15000)

    def test_positive_table_unchanged_after_export_modal_cancel(self, activities):
        before = activities.table_snapshot()
        activities.open_export_modal()
        activities.close_export_modal()
        assert activities.table_snapshot() == before

    def test_positive_sort_does_not_change_transaction_id_set(self, activities):
        _rows_or_skip(activities)
        before = activities.current_table_values(1)
        activities.date_sort_header.click()
        after = activities.current_table_values(1)
        assert sorted(before) == sorted(after)


@pytest.mark.ui
class TestActivitiesComprehensiveExport:
    @pytest.mark.parametrize('scope', ['Current page only', 'All data'])
    def test_positive_export_button_enabled_for_scope(self, activities, scope):
        activities.open_export_modal()
        activities.select_export_scope(scope)
        expect(activities.export_submit_button()).to_be_enabled()

    @pytest.mark.parametrize('scope', ['Current page only', 'All data'])
    def test_positive_export_saved_file_is_nonempty(self, activities, scope, tmp_path):
        destination = activities.export_excel(scope, tmp_path)
        assert destination.exists()
        assert destination.stat().st_size > 0
        assert destination.suffix.lower() in ('.xls', '.xlsx')

    def test_positive_export_scope_can_be_changed_before_export(self, activities):
        activities.open_export_modal()
        for scope in ('Current page only', 'All data', 'Current page only'):
            activities.select_export_scope(scope)
            expect(activities.export_submit_button()).to_be_enabled()

    def test_negative_export_invalid_scope_rejected_by_page_object(self, activities):
        activities.open_export_modal()
        with pytest.raises(ValueError, match='Unsupported export scope'):
            activities.select_export_scope('Unknown scope')

    def test_positive_export_does_not_mutate_transaction_table(self, activities):
        before = activities.table_snapshot()
        activities.download_transactions('Current page only')
        assert activities.table_snapshot() == before

    def test_positive_export_xlsx_can_be_opened(self, activities, tmp_path):
        destination = activities.export_excel('All data', tmp_path)
        if destination.suffix.lower() != '.xlsx':
            pytest.skip('Application produced legacy .xls; xlsx workbook check not applicable')
        from openpyxl import load_workbook
        workbook = load_workbook(destination, read_only=True, data_only=True)
        try:
            assert workbook.sheetnames
            sheet = workbook.active
            assert sheet.max_row >= 1
            assert sheet.max_column >= 1
        finally:
            workbook.close()
