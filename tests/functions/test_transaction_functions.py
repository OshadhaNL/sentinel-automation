
import base64
import os
import re
import uuid
from datetime import date, datetime
from decimal import Decimal

import pytest
from playwright.sync_api import (
    Page,
    expect,
    TimeoutError as PlaywrightTimeoutError,
)

from pages.loginPage import LoginPage
from pages.transactionPage import TransactionPage


@pytest.mark.functional
class TestTransactionFunctions:

    @pytest.fixture(autouse=True)
    def setup_transaction(self, page: Page, base_url: str):
        self.page = page

        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")

        assert email, "Set TEST_EMAIL"
        assert password, "Set TEST_PASSWORD"

        page.set_default_navigation_timeout(60000)
        page.set_viewport_size({"width": 1440, "height": 1000})

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

        self.seller = os.getenv(
            "TEST_TRANSACTION_SELLER",
            "Senith Client",
        )
        self.buyer = os.getenv(
            "TEST_TRANSACTION_BUYER",
            "Donald J Trump",
        )

    # ==========================================
    # Test data and reusable helpers
    # ==========================================

    def unique_address(self):
        return (
            "QA Automation Property "
            + uuid.uuid4().hex[:12]
        )

    def create_transaction(
        self,
        address=None,
        document_path=None,
    ):
        address = address or self.unique_address()

        self.transaction.open_add_modal()

        self.transaction.fill_transaction_details(
            address=address,
            property_type="Residential",
            payment_method="Bank Transfer",
            currency="AUD",
            sale_value="100000",
            deposit="5000",
            transaction_date=None,
        )

        self.select_functional_date(
            date.today().isoformat()
        )

        self.transaction.select_party(
            "seller",
            self.seller,
        )
        self.transaction.select_party(
            "buyer",
            self.buyer,
        )

        if document_path is not None:
            self.transaction.upload_document(document_path)

            expect(
                self.transaction.uploaded_documents().first
            ).to_be_visible(timeout=20000)

        self.transaction.submit_modal()

        record = self.transaction.find_by_address(address)

        assert re.fullmatch(
            r"TR-\d+",
            record["id"],
        ), (
            f"Invalid new Transaction ID: {record['id']}"
        )

        print(f"Created {record['id']} | {address}")

        return record["id"], address

    def select_functional_date(self, iso_date):
        """
        Select a transaction date without force-clicking
        a calendar cell outside the viewport.

        This helper is local to functional tests.
        """

        target = date.fromisoformat(iso_date)

        control = self.transaction.active_modal.locator(
            'input[placeholder="Select date and time"]'
        )

        control.click()

        popup = self.transaction.calendar_popup()

        expect(popup).to_be_visible(timeout=10000)

        for _ in range(120):
            day = popup.locator(
                f'td.ant-picker-cell-in-view[title="{iso_date}"] '
                '.ant-picker-cell-inner'
            )

            if day.count() and day.first.is_visible():
                day.first.evaluate(
                    "element => element.click()"
                )
                break

            year_text = popup.locator(
                ".ant-picker-year-btn"
            ).first.inner_text().strip()

            month_text = popup.locator(
                ".ant-picker-month-btn"
            ).first.inner_text().strip()

            shown_year = int(year_text)

            shown_month = datetime.strptime(
                month_text[:3],
                "%b",
            ).month

            shown_index = shown_year * 12 + shown_month
            target_index = target.year * 12 + target.month

            if shown_index < target_index:
                popup.locator(
                    ".ant-picker-header-next-btn"
                ).first.click()
            else:
                popup.locator(
                    ".ant-picker-header-prev-btn"
                ).first.click()

        else:
            raise AssertionError(
                f"Could not find date {iso_date}"
            )

        expect(control).not_to_have_value(
            "",
            timeout=10000,
        )

    def create_test_png(self, tmp_path):
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB"
            "CAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/lXc"
            "AAAAASUVORK5CYII="
        )

        path = tmp_path / (
            "qa_transaction_document_"
            + uuid.uuid4().hex[:8]
            + ".png"
        )

        path.write_bytes(png)

        return path

    def saved_transaction_record(self, transaction_id):
        """
        Find a saved transaction in the table using
        the existing TransactionPage methods.
        """

        self.transaction.search_for_record(
            transaction_id,
            column=0,
        )

        records = self.transaction.get_current_records()

        record = next(
            (
                item
                for item in records
                if item["id"] == transaction_id
            ),
            None,
        )

        assert record is not None, (
            f"Transaction {transaction_id} not found"
        )

        return record

    # ==========================================
    # Add Transaction Tests
    # ==========================================

    def test_add_transaction_saves_new_record(self):
        transaction_id, address = self.create_transaction()

        self.transaction.open_edit(transaction_id)

        expect(
            self.transaction.input_for("property")
        ).to_have_value(address)

        self.transaction.cancel_modal()

    def test_new_transaction_has_correct_values(self):
        transaction_id, address = self.create_transaction()

        self.transaction.open_edit(transaction_id)

        assert (
            self.transaction.field_value("property")
            == address
        )

        self.transaction.cancel_modal()

        record = self.saved_transaction_record(transaction_id)

        assert (
            record["property_type"].strip()
            == "Residential"
        )

        assert (
            record["payment"].strip()
            == "Bank Transfer"
        )

        assert (
            record["sale_value"].strip().startswith("AUD")
        )

    def test_new_transaction_saves_buyer_and_seller(self):
        transaction_id, _ = self.create_transaction()

        self.transaction.open_edit(transaction_id)

        assert (
            self.transaction.party_tags("seller").count()
            >= 1
        )

        assert (
            self.transaction.party_tags("buyer").count()
            >= 1
        )

        self.transaction.select_party_tab("Seller")

        seller_rows = self.transaction.get_party_rows()

        assert seller_rows, (
            "Saved Seller details are missing"
        )

        assert all(
            row["role"].casefold() == "seller"
            for row in seller_rows
        )

        self.transaction.select_party_tab("Buyer")

        buyer_rows = self.transaction.get_party_rows()

        assert buyer_rows, (
            "Saved Buyer details are missing"
        )

        assert all(
            row["role"].casefold() == "buyer"
            for row in buyer_rows
        )

        self.transaction.cancel_modal()

    # ==========================================
    # Edit Transaction Tests
    # ==========================================

    def test_edit_property_address_is_saved(self):
        transaction_id, original = self.create_transaction()

        updated_address = original + " Updated"

        self.transaction.open_edit(transaction_id)

        self.transaction.fill_field(
            "property",
            updated_address,
        )

        self.transaction.submit_modal()

        record = self.saved_transaction_record(transaction_id)

        assert record["property"] == updated_address, (
            f"Expected {updated_address!r}, "
            f"got {record['property']!r}"
        )

    def test_edit_property_type_is_saved(self):
        transaction_id, _ = self.create_transaction()

        self.transaction.open_edit(transaction_id)

        self.transaction.select_option(
            "propertyType",
            "Commercial",
        )

        self.transaction.submit_modal()

        record = self.saved_transaction_record(transaction_id)

        assert (
            record["property_type"].strip()
            == "Commercial"
        ), (
            "Property Type was not saved. "
            f"Expected 'Commercial', "
            f"got {record['property_type']!r}"
        )

    def test_edit_payment_method_is_saved(self):
        transaction_id, _ = self.create_transaction()

        self.transaction.open_edit(transaction_id)

        self.transaction.select_option(
            "paymentMethod",
            "Cash",
        )

        self.transaction.submit_modal()

        record = self.saved_transaction_record(
            transaction_id
        )

        assert record["payment"].strip() == "Cash", (
            "Payment Method was not saved. "
            f"Expected 'Cash', got {record['payment']!r}"
        )

    def test_edit_currency_is_saved(self):
        transaction_id, _ = self.create_transaction()

        self.transaction.open_edit(transaction_id)

        self.transaction.select_currency("USD")

        self.transaction.submit_modal()

        record = self.saved_transaction_record(transaction_id)

        assert (
            record["sale_value"].strip().startswith("USD")
        ), (
            "Currency was not saved. "
            f"Expected USD, got {record['sale_value']!r}"
        )

    def test_edit_contract_sale_value_is_saved(self):
        transaction_id, _ = self.create_transaction()

        self.transaction.open_edit(transaction_id)

        self.transaction.fill_field(
            "propertyValue",
            "120000",
        )

        self.transaction.submit_modal()

        record = self.saved_transaction_record(
            transaction_id
        )

        saved_value = record["sale_value"]

        match = re.search(
            r"[\d,]+(?:\.\d+)?",
            saved_value,
        )

        assert match is not None, (
            f"No numeric sale value found: {saved_value!r}"
        )

        actual = Decimal(
            match.group().replace(",", "")
        )

        assert actual == Decimal("120000"), (
            "Contract Sale Value was not saved. "
            f"Expected 120000, got {saved_value!r}"
        )

    def test_edit_deposit_amount_is_saved(self):
        transaction_id, _ = self.create_transaction()

        self.transaction.open_edit(transaction_id)

        self.transaction.fill_field(
            "amount",
            "7500",
        )

        self.transaction.submit_modal()

        self.transaction.verify_saved_field(
            transaction_id,
            "amount",
            "7500",
        )

    def test_edit_transaction_date_is_saved(self):
        transaction_id, _ = self.create_transaction()

        selected_date = date.today().replace(day=1)

        self.transaction.open_edit(transaction_id)

        self.select_functional_date(
            selected_date.isoformat()
        )

        self.transaction.submit_modal()

        record = self.saved_transaction_record(transaction_id)

        expected_date = selected_date.strftime(
            "%d-%m-%Y"
        )

        assert record["date"] == expected_date, (
            f"Expected date {expected_date!r}, "
            f"got {record['date']!r}"
        )

    # ==========================================
    # Cancel Operations
    # ==========================================

    def test_cancel_edit_does_not_save(self):
        transaction_id, original = self.create_transaction()

        self.transaction.open_edit(transaction_id)

        self.transaction.fill_field(
            "property",
            "Temporary Unsaved Address",
        )

        self.transaction.cancel_modal()

        record = self.saved_transaction_record(transaction_id)

        assert record["property"] == original, (
            "Cancel Edit incorrectly saved the changes. "
            f"Expected {original!r}, "
            f"got {record['property']!r}"
        )

    def test_cancel_add_does_not_create_record(self):
        address = self.unique_address()

        self.transaction.open_add_modal()

        self.transaction.fill_field(
            "property",
            address,
        )

        self.transaction.cancel_modal()

        self.transaction.search(address)

        expect(
            self.transaction.rows
        ).to_have_count(0, timeout=20000)

    # ==========================================
    # Buyer and Seller Selection
    # ==========================================

    def test_buyer_can_be_removed_before_saving(self):
        self.transaction.open_add_modal()

        self.transaction.select_party(
            "buyer",
            self.buyer,
        )

        assert (
            self.transaction.party_tags("buyer").count()
            == 1
        )

        self.transaction.remove_last_party("buyer")

        expect(
            self.transaction.party_tags("buyer")
        ).to_have_count(0)

        self.transaction.cancel_modal()

    def test_seller_can_be_removed_before_saving(self):
        self.transaction.open_add_modal()

        self.transaction.select_party(
            "seller",
            self.seller,
        )

        assert (
            self.transaction.party_tags("seller").count()
            == 1
        )

        self.transaction.remove_last_party("seller")

        expect(
            self.transaction.party_tags("seller")
        ).to_have_count(0)

        self.transaction.cancel_modal()

    # ==========================================
    # Required Field Validation
    # ==========================================

    def test_empty_add_form_cannot_be_saved(self):
        self.transaction.open_add_modal()

        self.transaction.active_modal.locator(
            "button.modal-z-primary-btn"
        ).click()

        expect(
            self.transaction.add_modal
        ).to_be_visible(timeout=10000)

        self.transaction.cancel_modal()

    # ==========================================
    # Supporting Documents
    # ==========================================

    @pytest.mark.skip(
        reason="Document upload issue - temporarily skipped"
    )
    def test_document_can_be_uploaded(self, tmp_path):
        document = self.create_test_png(tmp_path)

        self.transaction.open_add_modal()

        self.transaction.upload_document(document)

        expect(
            self.transaction.uploaded_documents().first
        ).to_be_visible(timeout=20000)

        self.transaction.cancel_modal()

    def test_document_is_saved_with_transaction(
        self,
        tmp_path,
    ):
        document = self.create_test_png(tmp_path)

        transaction_id, _ = self.create_transaction(
            document_path=document
        )

        self.transaction.open_edit(transaction_id)

        expect(
            self.transaction.uploaded_documents().first
        ).to_be_visible(timeout=20000)

        self.transaction.cancel_modal()

    def test_existing_document_controls(
        self,
        tmp_path,
    ):
        document = self.create_test_png(tmp_path)

        transaction_id, _ = self.create_transaction(
            document_path=document
        )

        self.transaction.open_edit(transaction_id)

        for title in (
            "Reupload",
            "View",
            "Download",
            "Delete",
        ):
            expect(
                self.transaction.active_modal.locator(
                    f'button[title="{title}"]'
                ).first
            ).to_be_visible()

        self.transaction.cancel_modal()
