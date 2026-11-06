"""Read-only Entity Documents smoke tests.

Setup: a pre-existing QA entity must be supplied via TEST_ENTITY_CLIENT_ID.
No tests upload, delete, move, verify, or complete entity records.
"""

import os
import re
from urllib.parse import parse_qs, quote, urlsplit

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.entityDocumentsPage import EntityDocumentsPage


@pytest.mark.ui
class TestEntityDocuments:
    @pytest.fixture(autouse=True)
    def setup_entity_documents(self, page: Page, base_url: str):
        client_id = os.getenv("TEST_ENTITY_CLIENT_ID", "").strip()
        if not client_id:
            pytest.skip("Set TEST_ENTITY_CLIENT_ID to an existing QA entity Reference ID")

        email = os.getenv("TEST_EMAIL", "").strip()
        password = os.getenv("TEST_PASSWORD", "")
        assert email, "TEST_EMAIL environment variable is required"
        assert password, "TEST_PASSWORD environment variable is required"

        login = LoginPage(page)
        login.open(base_url)
        login.enter_email(email)
        login.enter_password(password)
        login.click_login()
        expect(page).to_have_url(re.compile(r".*/nolimit/app/home/?$"), timeout=45000)

        parsed = urlsplit(base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        entity_url = (
            f"{origin}/nolimit/app/onboarding/entity/process"
            f"?step=documents&client={quote(client_id, safe='')}"
        )
        page.goto(entity_url, wait_until="domcontentloaded")
        self.documents = EntityDocumentsPage(page)
        self.documents.verify_page_loaded()
        self.client_id = client_id

    def test_entity_main_navigation_and_icons(self):
        self.documents.verify_main_navigation()
        expect(self.documents.main_tab("Documents")).to_have_class(
            re.compile(r"(?:^|\s)active(?:\s|$)")
        )

    def test_entity_document_reference_id(self):
        expect(self.documents.reference_id).to_have_text(self.client_id)
        expect(self.documents.client_name).not_to_be_empty()

    def test_entity_document_subnavigation_and_icons(self):
        self.documents.verify_document_navigation()

    @pytest.mark.parametrize("tab_name", ["Upload", "Verify", "Cabinets"])
    def test_document_tab_can_be_selected(self, tab_name):
        self.documents.open_document_tab(tab_name)
        expect(self.documents.document_tab(tab_name)).to_have_class(
            re.compile(r"(?:^|\s)active(?:\s|$)")
        )

    def test_upload_section_structure_and_accepted_file_types(self):
        self.documents.verify_upload_section()

    @pytest.mark.parametrize("category", EntityDocumentsPage.DOCUMENT_CATEGORIES)
    def test_document_category_is_visible(self, category):
        self.documents.open_document_tab("Upload")
        self.documents.verify_category(category)

    def test_verify_tab_has_consent_letter_section(self):
        self.documents.open_document_tab("Verify")
        expect(self.documents.verify_group("Consent Letter")).to_be_visible()

    def test_verify_consent_letter_file_actions_if_uploaded(self):
        self.documents.open_document_tab("Verify")
        group = self.documents.verify_group("Consent Letter")
        expect(group).to_be_visible()
        if group.locator(".uploaded.show-file").count() == 0:
            pytest.skip("This QA entity has no uploaded consent letter")
        for title in ("Reupload", "View", "Download", "Delete", "Modify"):
            expect(self.documents.verify_file_action("Consent Letter", title)).to_be_visible()

    def test_cabinets_table_headers(self):
        self.documents.open_document_tab("Cabinets")
        expect(self.documents.cabinets_table).to_be_visible()
        for heading in (
            "Cabinet", "Status", "Uploaded Date", "Date of Expiry", "Uploaded By"
        ):
            expect(
                self.documents.cabinets_table.get_by_role(
                    "columnheader", name=heading, exact=True
                )
            ).to_be_visible()

    def test_consent_letter_cabinet_link_if_present(self):
        # This fixture entity is expected to have a Consent Letter cabinet.
        # Wait for async table rows rather than skipping on an immediate count().
        row = self.documents.wait_for_consent_letter_cabinet(timeout=15000)
        link = row.locator("a.table-link")
        expect(link).to_be_visible()
        expect(link).to_contain_text("Consent Letter")
        href = link.get_attribute("href")
        assert href is not None
        assert urlsplit(href).path.startswith("/nolimit/app/documents/consent-letter/")
        assert parse_qs(urlsplit(href).query).get("clientRefId") == [self.client_id]
