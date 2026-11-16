
"""Initial READ-ONLY Individual Profile regression tests.

Run from repository root. Credentials: TEST_EMAIL, TEST_PASSWORD.
Optional: TEST_INDIVIDUAL_CLIENT_ID to target a specific row on Profiles > All Files.
No uploads, saves, deletes, screening runs, or transaction creation.
"""
import os
import re

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.profiles.individual.individualProfilePage import IndividualProfilePage
from pages.profiles.profileNavigation import open_client_profile


@pytest.mark.ui
class TestIndividualProfileReadOnly:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        target_id = os.getenv("TEST_INDIVIDUAL_CLIENT_ID", "").strip() or None
        open_client_profile(page, base_url, "individual", target_id)
        self.profile = IndividualProfilePage(page)
        expect(self.profile.heading).to_be_visible(timeout=15000)
        self.page = page

    def test_page_shell_and_six_tabs(self):
        self.profile.verify_shell()

    @pytest.mark.parametrize("name", IndividualProfilePage.TABS)
    def test_each_main_tab_opens(self, name):
        self.profile.open_tab(name)

    def test_verification_labels(self):
        self.profile.open_tab("Verification")

        for label in self.profile.VERIFICATION_LABELS:
            if label == "Driver Licence Number":
                item = self.page.locator(
                    ".verification-report-item"
                ).filter(
                    has=self.page.locator(
                        ".label",
                        has_text=re.compile(
                            r"^\s*(Driver|Driving) Licence Number\s*$",
                            re.I
                        )
                    )
                )
            else:
                item = self.profile.verification_item(label)

            expect(item).to_be_visible()

    def test_verification_values_have_badges(self):
        self.profile.open_tab("Verification")

        for label in self.profile.VERIFICATION_LABELS:
            if label == "Driver Licence Number":
                item = self.page.locator(
                    ".verification-report-item"
                ).filter(
                    has=self.page.locator(
                        ".label",
                        has_text=re.compile(
                            r"^\s*(Driver|Driving) Licence Number\s*$",
                            re.I
                        )
                    )
                )
            else:
                item = self.profile.verification_item(label)

            expect(item.locator(".custom-badge")).to_have_count(1)

    def test_verification_images_if_present_are_loaded(self):
        self.profile.open_tab("Verification")

        images = self.page.locator(".document-img img")

        image_count = images.count()

        print(f"\nVerification images found: {image_count}")

        if image_count == 0:
            pytest.skip("No verification images available for this client")

        for i in range(image_count):
            image = images.nth(i)

            expect(image).to_be_visible(timeout=15000)

            src = image.get_attribute("src")

            print(f"\nChecking verification image {i + 1}")
            print(f"Image URL present: {bool(src)}")

            assert src, f"Verification image {i + 1} has no source URL"

            try:
                expect(image).to_have_js_property(
                    "complete", True, timeout=20000
                )

                # Wait for actual image decoding, not just completion.
                expect(image).not_to_have_js_property(
                    "naturalWidth", 0, timeout=20000
                )

                print(f"Verification image {i + 1} loaded successfully")

            except AssertionError:
                status = image.evaluate(
                    """img => ({
                        complete: img.complete,
                        naturalWidth: img.naturalWidth,
                        naturalHeight: img.naturalHeight
                    })"""
                )

                print(f"Image loading state: {status}")

                raise AssertionError(
                    f"Verification image {i + 1} failed to load. "
                    f"Image state: {status}"
                )

    @pytest.mark.parametrize("name", ["Upload", "Verify", "Cabinets"])
    def test_documents_subtabs(self, name):
        self.profile.open_document_subtab(name)

    def test_screening_results_tabs_and_empty_state(self):
        self.profile.open_tab("Screening")
        for name in ("Unresolved Hits", "Positive Hits", "False Hits", "Possible Hits"):
            expect(self.page.locator(".tab-z-option").filter(has_text=name).first).to_be_visible()
        table = self.page.locator(".ant-table-wrapper").first
        expect(table).to_be_visible()
        # Empty state is valid, but populated results must also be accepted.
        assert table.locator("tbody tr.ant-table-row").count() > 0 or table.locator(
            "tbody tr.ant-table-placeholder"
        ).count() > 0

    def test_screening_back_to_single_screening(self):
        self.profile.screening_back_to_form()

    def test_kyc_form_heading_and_save(self):
        self.profile.open_tab("KYC Form")
        expect(self.page.get_by_text("KNOW YOUR CUSTOMER (KYC) FORM - INDIVIDUAL")).to_be_visible()
        expect(self.page.get_by_role("button", name="Save", exact=True)).to_be_visible()

    def test_risk_sections_and_update_button(self):
        self.profile.open_tab("Risk Assessment")
        for heading in self.profile.RISK_HEADINGS:
            expect(self.page.get_by_text(heading, exact=True).first).to_be_visible()
        expect(self.page.get_by_role("button", name="Update Changes")).to_be_visible()

    def test_activities_heading_and_columns(self):
        self.profile.open_tab("Activities")
        expect(self.page.get_by_role("heading", name="Transaction History")).to_be_visible()
        table = self.profile.activities_table()
        expect(table).to_be_visible()
        for heading in ("Transaction ID", "Property Address", "Type", "Client ID", "Payment", "Risk Rating", "Date"):
            expect(table.locator("thead th", has_text=heading).first).to_be_visible()

    def test_activities_empty_search_and_clear(self):
        self.profile.open_tab("Activities")
        search = self.profile.activity_search()
        expect(search).to_be_visible()
        search.fill("UNLIKELY-TRANSACTION-ID-99999999")
        search.press("Enter")
        expect(search).to_have_value("UNLIKELY-TRANSACTION-ID-99999999")
        search.locator("xpath=..").locator("button.clear-btn").click()
        expect(search).to_have_value("")

    def test_activities_export_modal_options(self):
        self.profile.open_tab("Activities")
        export_button = self.page.locator("button").filter(
            has_text=re.compile(r"^\s*Export\s*$", re.I)
        ).first

        expect(export_button).to_be_visible(timeout=10000)
        export_button.click()
        modal = self.page.locator(".modal-z:visible").filter(has_text="Export Transactions")
        expect(modal).to_be_visible()
        expect(modal.get_by_text("Current page only")).to_be_visible()
        expect(modal.get_by_text("All data")).to_be_visible()
        # Close without exporting.
        modal.locator("button.modal-z-close").click()
        expect(modal).to_be_hidden()

    def test_add_transaction_modal_cancel(self):
        self.profile.open_tab("Activities")
        add_transaction_button = self.page.locator("button").filter(
            has_text=re.compile(r"Add\s*Transaction", re.I)
        ).first

        expect(add_transaction_button).to_be_visible(timeout=10000)
        add_transaction_button.click()
        modal = self.page.locator(".modal-z:visible").filter(
            has=self.page.locator(".modal-z-title", has_text="Add Transaction")
        )
        expect(modal).to_be_visible()
        for field in ("Property Address", "Property Type", "Payment Method", "Currency", "Date"):
            expect(modal.get_by_text(field, exact=True).first).to_be_visible()
        modal.get_by_role("button", name="Cancel", exact=True).click()
        expect(modal).to_be_hidden()



@pytest.mark.ui
class TestIndividualDocumentsReadOnly:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        target_id = os.getenv("TEST_INDIVIDUAL_CLIENT_ID", "").strip() or None
        open_client_profile(page, base_url, "individual", target_id)
        self.profile = IndividualProfilePage(page)
        expect(self.profile.heading).to_be_visible(timeout=15000)
        self.page = page
    @pytest.mark.parametrize(
        "document_type",
        IndividualProfilePage.DOCUMENT_TYPES,
    )
    def test_document_section_visible(self, document_type):
        self.profile.open_documents_upload()

        section = self.profile.document_section(document_type)

        expect(section).to_be_visible()
        expect(
            section.locator("label.document-label")
        ).to_be_visible()

    @pytest.mark.parametrize(
        "name",
        ["Passport Copy", "Driver Licence", "Proof of Age Card", "Others"]
    )
    def test_document_upload_input_accept_types(self, name):
        self.profile.open_document_subtab("Upload")

        section = self.profile.document_section(name)
        expect(section).to_be_visible()

        file_input = section.locator('input[type="file"]')

        # A section with existing uploaded documents may
        # intentionally hide its upload input.
        if file_input.count() == 0:
            uploaded_files = section.locator(
                "h6"
            ).filter(
                has_text=re.compile(
                    r"\.(pdf|png|jpg|jpeg)$", re.I
                )
            )

            assert uploaded_files.count() > 0, (
                f"{name}: neither an upload input "
                "nor an uploaded document was found"
            )

            print(
                f"{name}: existing uploaded document found"
            )
            return

        expect(file_input.first).to_have_attribute(
            "accept",
            "application/pdf,image/png,image/jpeg,image/jpg"
        )

    @pytest.mark.parametrize(
        "document_type",
        IndividualProfilePage.DOCUMENT_TYPES,
    )
    def test_document_upload_size_information(self, document_type):
        self.profile.open_documents_upload()

        uploader = self.profile.document_uploader(document_type)

        expect(
            uploader.get_by_text(
                "PDF, PNG, JPG or JPEG (max. 10MB)"
            )
        ).to_be_attached()

    @pytest.mark.parametrize(
        "document_type",
        IndividualProfilePage.DOCUMENT_TYPES,
    )
    def test_document_action_buttons_match_state(self, document_type):
        self.profile.open_documents_upload()

        uploader = self.profile.document_uploader(document_type)

        if self.profile.document_has_uploaded_file(document_type):
            filename = self.profile.document_filename(document_type)

            assert filename, (
                f"{document_type} shows an uploaded file "
                "but has no filename"
            )

            expect(
                self.profile.document_action(
                    document_type, "View"
                )
            ).to_be_visible()

            expect(
                self.profile.document_action(
                    document_type, "Download"
                )
            ).to_be_visible()

        else:
            expect(
                uploader.locator(".upload-wrapper")
            ).to_be_visible()

    def test_passport_uploaded_file_details(self):
        self.profile.open_documents_upload()

        if not self.profile.document_has_uploaded_file(
            "Passport Copy"
        ):
            pytest.skip("Passport Copy has no uploaded file")

        filename = self.profile.document_filename(
            "Passport Copy"
        )

        assert filename, "Uploaded passport filename is empty"

        uploader = self.profile.document_uploader(
            "Passport Copy"
        )

        expect(
            uploader.locator(".uploaded-file")
        ).to_be_visible()

    def test_next_button_visible(self):
        self.profile.open_documents_upload()

        next_button = self.page.locator(
            "button.primary-btn"
        ).filter(
            has_text=re.compile(r"^\s*Next\s*$")
        )

        expect(next_button).to_be_visible()
