
import os
import re
import base64
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from pages.profiles.individual.individualDocumentsPage import IndividualDocumentsPage
from pages.profiles.profileNavigation import open_client_profile


READONLY_DOCUMENT_CLIENT_ID = "SENTINELE7CE963CAACEA23"

DOCUMENT_CATEGORIES = {
    "Consent Letter": 1,
    "Passport Copy": 1,
    "Risk Assessment": 1,
    "Verification": 2,
}

DOCUMENT_TYPES = (
    "Passport Copy",
    "Driver Licence",
    "Proof of Age Card",
    "Others",
)

SUPPORTED_FORMATS = ("pdf", "png", "jpg", "jpeg")
MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================
# LOGIN AND PROFILE NAVIGATION
# ============================================================

def open_individual_profile(page: Page, base_url: str, client_id: str | None = None):
    open_client_profile(page, base_url, "individual", client_id)
    profile = IndividualDocumentsPage(page)
    expect(profile.heading).to_be_visible(timeout=15000)
    profile.open_document_subtab("Upload")
    return profile


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def readonly_profile(page: Page, base_url: str):
    client_id = (
        os.getenv("TEST_INDIVIDUAL_DOCUMENT_CLIENT_ID", "").strip()
        or READONLY_DOCUMENT_CLIENT_ID
    )
    return open_individual_profile(page, base_url, client_id)


@pytest.fixture
def writable_profile(page: Page, base_url: str):
    if os.getenv("TEST_INDIVIDUAL_ALLOW_DOCUMENT_CHANGES") != "1":
        pytest.skip("Set TEST_INDIVIDUAL_ALLOW_DOCUMENT_CHANGES=1 to enable writes")

    client_id = os.getenv("TEST_INDIVIDUAL_WRITE_CLIENT_ID", "").strip()
    if not client_id:
        pytest.skip("Set TEST_INDIVIDUAL_WRITE_CLIENT_ID for a disposable client")

    readonly_ids = {
        READONLY_DOCUMENT_CLIENT_ID.upper(),
        os.getenv("TEST_INDIVIDUAL_DOCUMENT_CLIENT_ID", "").strip().upper(),
        os.getenv("TEST_INDIVIDUAL_CLIENT_ID", "").strip().upper(),
    }
    if client_id.upper() in readonly_ids:
        pytest.fail("Write client must differ from every protected read-only client")

    return open_individual_profile(page, base_url, client_id)


@pytest.fixture
def documents_page(readonly_profile):
    profile = readonly_profile
    profile.open_documents_upload()
    expected_id = (
        os.getenv("TEST_INDIVIDUAL_DOCUMENT_CLIENT_ID", "").strip()
        or READONLY_DOCUMENT_CLIENT_ID
    )
    expect(profile.document_reference()).to_contain_text(expected_id)
    return profile


# ============================================================
# DOCUMENT LOCATORS
# ============================================================

def document_section(profile, document_type):
    return profile.page.locator(
        ".custom-form > div"
    ).filter(
        has=profile.page.locator(
            "label.document-label",
            has_text=re.compile(
                rf"^\s*{re.escape(document_type)}\s*$"
            ),
        )
    ).first


def document_uploader(profile, document_type):
    return document_section(
        profile, document_type
    ).locator(".uploader-z").first


def document_input(profile, document_type):
    # The HTML contains repeated id="dealCsv".
    # Always scope the input to the document section.
    return document_uploader(
        profile, document_type
    ).locator('input[type="file"]')


def uploaded_document(profile, document_type):
    return document_uploader(
        profile, document_type
    ).locator(".uploaded.show-file")


def document_filename(profile, document_type):
    return uploaded_document(
        profile, document_type
    ).locator(".uploaded-file h6")


def document_action(profile, document_type, action):
    return document_uploader(
        profile, document_type
    ).locator(f'button[title="{action}"]')


def visible_delete_modal(profile):
    return profile.page.locator(
        ".modal-z:visible"
    ).filter(
        has=profile.page.locator(
            ".modal-z-title",
            has_text="Delete document",
        )
    ).first


# ============================================================
# TEST FILE GENERATION
# ============================================================

def create_test_file(
    tmp_path: Path,
    extension: str,
    size: int | None = None,
):
    filename = f"qa-test-{os.getpid()}.{extension}"
    path = tmp_path / filename

    if extension == "pdf":
        # Minimal PDF for upload validation.
        payload = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog>>endobj\n"
            b"%%EOF\n"
        )

    elif extension == "png":
        payload = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB"
            "CAQAAAC1HAwCAAAAC0lEQVR42mP8/x8A"
            "AwMCAO+/WZkAAAAASUVORK5CYII="
        )

    elif extension in ("jpg", "jpeg"):
        payload = base64.b64decode(
            "/9j/4AAQSkZJRgABAQAAAQABAAD/"
            "2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsL"
            "DBkSEw8UHRofHh0aHBwgJC4nICIsIxwc"
            "KDcpLDAxNDQ0Hyc5PTgyPC4zNDL/"
            "2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIy"
            "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy"
            "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy"
            "MjL/wAARCAACAAIDASIAAhEBAxEB/"
            "8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECA"
            "wQFBgcICQoL/8QAtRAAAgEDAwIEAwUF"
            "BAQAAAF9AQIDAAQRBRIhMUEGE1FhByJx"
            "FDKBkaEII0KxwRVS0fAkM2JyggkKFhc"
            "YGRolJicoKSo0NTY3ODk6Q0RFRkdISU"
            "pTVFVWV1hZWmNkZWZnaGlqc3R1dnd4"
            "eXqDhIWGh4iJipKTlJWWl5iZmqKjpKW"
            "mp6ipqrKztLW2t7i5usLDxMXGx8jJ"
            "ytLT1NXW19jZ2uHi4+Tl5ufo6erx8"
            "vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEB"
            "AQAAAAAAAAECAwQFBgcICQoL/8QAtR"
            "EAAgECBAQDBAcFBAQAAQJ3AAECAxEEB"
            "SExBhJBUQdhcRMiMoEIFEKRobHBCSMz"
            "UvAVYnLRChYkNOEl8RcYGRomJygpKj"
            "U2Nzg5OkNERUZHSElKU1RVVldYWVpjZ"
            "GVmZ2hpanN0dXZ3eHl6goOEhYaHiImK"
            "kpOUlZaXmJmaoqOkpaanqKmqsrO0tba"
            "3uLm6wsPExcbHyMnK0tPU1dbX2Nna4"
            "uPk5ebn6Onq8vP09fb3+Pn6/9oADAM"
            "BAAIRAxEAPwD3+iiigD//2Q=="
        )

    else:
        payload = b"QA invalid file content\n"

    with path.open("wb") as file:
        file.write(payload)

        if size is not None:
            file.truncate(size)

    return path


# ============================================================
# SAFE DOCUMENT HELPERS
# ============================================================

def require_empty_slot(profile):
    document_type = "Others"

    expect(
        document_section(profile, document_type)
    ).to_be_visible()

    if uploaded_document(
        profile, document_type
    ).count() > 0:
        pytest.skip(
            "Others already contains a document. "
            "Refusing to overwrite an existing file."
        )

    return document_type


def delete_test_document(
    profile,
    document_type,
    expected_filename,
):
    expect(
        uploaded_document(profile, document_type)
    ).to_be_visible(timeout=20000)

    expect(
        document_filename(profile, document_type)
    ).to_have_text(expected_filename)

    document_action(
        profile, document_type, "Delete"
    ).click()

    modal = visible_delete_modal(profile)

    expect(modal).to_be_visible()

    modal.locator(
        "button.modal-z-primary-btn"
    ).click()

    expect(
        uploaded_document(profile, document_type)
    ).to_have_count(0, timeout=20000)


def cleanup_test_document(
    profile,
    document_type,
    expected_filename,
):
    # Only remove a file created by this test.
    # Never delete an unrelated client document.
    profile.page.reload()
    profile.open_document_subtab("Upload")

    if uploaded_document(
        profile, document_type
    ).count() == 0:
        return

    actual_name = document_filename(
        profile, document_type
    ).inner_text().strip()

    if actual_name == expected_filename:
        delete_test_document(
            profile,
            document_type,
            expected_filename,
        )


def assert_verify_preview_opens_and_closes(documents_page, category):
    """Verify and close either the Ant Design image viewer or the PDF modal."""
    documents_page.open_verify()
    modal = documents_page.verify_preview(category)
    expect(modal).to_be_visible(timeout=10000)

    # Ant Design image preview uses an accessible dialog with an image filename.
    image_viewer = documents_page.page.get_by_role("dialog").filter(
        has=documents_page.page.get_by_role(
            "img", name=re.compile(r"\.(?:jpg|jpeg|png)$", re.I)
        )
    )
    if image_viewer.is_visible():
        expect(image_viewer.get_by_role("img")).to_be_visible()
        documents_page.page.get_by_role(
            "button", name="close", exact=True
        ).click()
        expect(image_viewer).to_be_hidden(timeout=10000)
    else:
        # PDF preview is rendered by the application's document modal.
        expect(modal.locator(".modal-z-title")).to_be_visible()
        modal.locator("button.modal-z-close").click()
        expect(modal).to_be_hidden(timeout=10000)


# ============================================================
# READ-ONLY FUNCTIONAL TESTS
# ============================================================

@pytest.mark.ui
class TestIndividualDocumentReadOnlyFunctional:

    @pytest.mark.parametrize(
        "document_type",
        DOCUMENT_TYPES,
    )
    def test_upload_controls_have_supported_types(
        self,
        readonly_profile,
        document_type,
    ):
        control = document_input(
            readonly_profile, document_type
        )

        expect(control).to_have_count(1)

        accept = control.get_attribute("accept") or ""

        actual_types = {
            item.strip()
            for item in accept.split(",")
        }

        expected_types = {
            "application/pdf",
            "image/png",
            "image/jpeg",
            "image/jpg",
        }

        assert actual_types == expected_types

    @pytest.mark.parametrize(
        "document_type",
        DOCUMENT_TYPES,
    )
    def test_document_file_state_is_consistent(
        self,
        readonly_profile,
        document_type,
    ):
        uploader = document_uploader(
            readonly_profile, document_type
        )

        expect(uploader).to_be_visible()

        if uploaded_document(
            readonly_profile, document_type
        ).count() > 0:

            expect(
                document_filename(
                    readonly_profile, document_type
                )
            ).not_to_be_empty()

            expect(
                document_action(
                    readonly_profile,
                    document_type,
                    "View",
                )
            ).to_be_visible()

            expect(
                document_action(
                    readonly_profile,
                    document_type,
                    "Download",
                )
            ).to_be_visible()

        else:
            expect(
                uploader.locator(".upload-wrapper")
            ).to_be_visible()

    @pytest.mark.parametrize("category", list(DOCUMENT_CATEGORIES))
    def test_preview_opens_and_closes(self, documents_page, category):
        assert_verify_preview_opens_and_closes(documents_page, category)

    def test_download_existing_document(
        self,
        readonly_profile,
    ):
        document_type = "Passport Copy"

        if uploaded_document(
            readonly_profile, document_type
        ).count() == 0:
            pytest.skip("No Passport Copy available")

        page = readonly_profile.page

        with page.expect_download(timeout=15000) as info:
            document_action(
                readonly_profile,
                document_type,
                "Download",
            ).click()

        download = info.value

        assert download.suggested_filename
        assert not download.failure(), (
            f"Download failed: {download.failure()}"
        )


# ============================================================
# WRITE TESTS - DISPOSABLE CLIENT ONLY
# ============================================================

@pytest.mark.ui
@pytest.mark.document_write
class TestIndividualDocumentWrites:

    @pytest.mark.parametrize(
        "extension",
        SUPPORTED_FORMATS,
    )
    def test_valid_upload_persists_and_cleanup(
        self,
        writable_profile,
        tmp_path,
        extension,
    ):
        profile = writable_profile
        document_type = require_empty_slot(profile)

        path = create_test_file(
            tmp_path, extension
        )

        try:
            document_input(
                profile, document_type
            ).set_input_files(str(path))

            expect(
                uploaded_document(
                    profile, document_type
                )
            ).to_be_visible(timeout=20000)

            expect(
                document_filename(
                    profile, document_type
                )
            ).to_have_text(path.name)

            profile.page.reload()
            profile.open_document_subtab("Upload")

            expect(
                document_filename(
                    profile, document_type
                )
            ).to_have_text(
                path.name,
                timeout=20000,
            )

        finally:
            cleanup_test_document(
                profile,
                document_type,
                path.name,
            )

    def test_delete_cancel_preserves_document(
        self,
        writable_profile,
        tmp_path,
    ):
        profile = writable_profile
        document_type = require_empty_slot(profile)

        path = create_test_file(
            tmp_path, "png"
        )

        try:
            document_input(
                profile, document_type
            ).set_input_files(str(path))

            expect(
                document_filename(
                    profile, document_type
                )
            ).to_have_text(
                path.name,
                timeout=20000,
            )

            document_action(
                profile,
                document_type,
                "Delete",
            ).click()

            modal = visible_delete_modal(profile)

            expect(modal).to_be_visible()

            modal.locator(
                "button.modal-z-secondary-btn"
            ).click()

            expect(modal).to_be_hidden()

            expect(
                document_filename(
                    profile, document_type
                )
            ).to_have_text(path.name)

            profile.page.reload()
            profile.open_document_subtab("Upload")

            expect(
                document_filename(
                    profile, document_type
                )
            ).to_have_text(
                path.name,
                timeout=20000,
            )

        finally:
            cleanup_test_document(
                profile,
                document_type,
                path.name,
            )

    @pytest.mark.parametrize(
        "extension,size",
        [
            ("txt", None),
            ("pdf", 0),
            ("pdf", MAX_FILE_SIZE + 1),
        ],
        ids=[
            "unsupported-txt",
            "zero-byte-pdf",
            "oversized-pdf",
        ],
    )
    def test_invalid_file_does_not_persist(
        self,
        writable_profile,
        tmp_path,
        extension,
        size,
    ):
        profile = writable_profile
        document_type = require_empty_slot(profile)

        path = create_test_file(
            tmp_path,
            extension,
            size,
        )

        try:
            document_input(
                profile, document_type
            ).set_input_files(str(path))

            # Reload checks whether the invalid file
            # has persisted on the server.
            # A more detailed validation-message check
            # can be added after observing the UI.
            profile.page.reload()
            profile.open_document_subtab("Upload")

            assert uploaded_document(
                profile, document_type
            ).count() == 0, (
                f"Invalid file persisted: {path.name}"
            )

        finally:
            cleanup_test_document(
                profile,
                document_type,
                path.name,
            )


# ============================================================
# DOCUMENTS: UPLOAD, VERIFY, CABINETS, LISTING (READ ONLY)
# ============================================================

@pytest.mark.ui
class TestIndividualDocumentsUpload:
    def test_reference_and_name_visible(self, documents_page):
        expect(documents_page.document_reference()).to_be_visible()
        expect(documents_page.document_client_name()).to_be_visible()

    def test_passport_filename_and_size(self, documents_page):
        uploader = documents_page.document_uploader("Passport Copy")
        expect(uploader.locator(".uploaded-file h6")).to_have_text("doc-front.jpg")
        expect(uploader.locator(".uploaded.show-file")).to_contain_text(
            re.compile(r"\d+(?:\.\d+)?\s*KB")
        )

    @pytest.mark.parametrize("action", ("View", "Download"))
    def test_passport_actions_visible(self, documents_page, action):
        expect(documents_page.document_action("Passport Copy", action)).to_be_visible()

    @pytest.mark.parametrize("document_type", ("Driver Licence", "Proof of Age Card", "Others"))
    def test_empty_upload_slots(self, documents_page, document_type):
        uploader = documents_page.document_uploader(document_type)
        expect(uploader.locator(".uploaded.show-file")).to_have_count(0)
        expect(uploader.locator(".upload-wrapper")).to_be_visible()

    def test_next_button_visible(self, documents_page):
        expect(documents_page.page.get_by_role("button", name="Next", exact=True)).to_be_visible()


@pytest.mark.ui
class TestIndividualDocumentsVerify:
    @pytest.mark.parametrize("category,count", list(DOCUMENT_CATEGORIES.items()))
    def test_category_document_counts(self, documents_page, category, count):
        documents_page.open_verify()
        expect(documents_page.verify_category(category)).to_be_visible()
        expect(documents_page.verify_files(category)).to_have_count(count)

    @pytest.mark.parametrize("category", list(DOCUMENT_CATEGORIES))
    def test_document_actions_visible(self, documents_page, category):
        documents_page.open_verify()
        for index in range(DOCUMENT_CATEGORIES[category]):
            for action in ("Reupload", "View", "Download", "Delete", "Modify"):
                expect(documents_page.verify_file_action(category, action, index)).to_be_visible()

    @pytest.mark.parametrize("category", list(DOCUMENT_CATEGORIES))
    def test_preview_opens_and_closes(self, documents_page, category):
        assert_verify_preview_opens_and_closes(documents_page, category)


@pytest.mark.ui
class TestIndividualDocumentsCabinets:
    def test_cabinet_headers(self, documents_page):
        documents_page.open_cabinets()
        expect(documents_page.cabinets_table().locator("thead th")).to_have_text([
            "Cabinet", "Status", "Uploaded Date", "Date of Expiry", "Uploaded By"
        ])

    def test_cabinet_row_count(self, documents_page):
        documents_page.open_cabinets()
        expect(documents_page.cabinet_rows()).to_have_count(4)

    @pytest.mark.parametrize("category,count", list(DOCUMENT_CATEGORIES.items()))
    def test_cabinet_document_count(self, documents_page, category, count):
        documents_page.open_cabinets()
        expect(documents_page.cabinet_row(category)).to_have_count(1)
        expect(documents_page.cabinet_row(category)).to_contain_text(f"{category} ({count})")

    @pytest.mark.parametrize("category,count", list(DOCUMENT_CATEGORIES.items()))
    def test_cabinet_opens_listing(self, documents_page, category, count):
        documents_page.open_cabinets()
        documents_page.open_cabinet(category)
        expect(documents_page.page).to_have_url(re.compile(r"/nolimit/app/documents/"))
        expect(documents_page.listing_table()).to_be_visible()
        expect(documents_page.listing_rows()).to_have_count(count)


@pytest.mark.ui
class TestIndividualDocumentsListing:
    @pytest.fixture(autouse=True)
    def setup_listing(self, documents_page):
        self.documents = documents_page
        documents_page.open_cabinets()
        documents_page.open_cabinet("Consent Letter")
        expect(documents_page.listing_table()).to_be_visible()

    def test_listing_headers(self):
        expect(self.documents.listing_table().locator("thead th")).to_have_text([
            "Document", "Status", "Uploaded Date", "Date of Expiry", "Uploaded By", "Action"
        ])

    def test_filename_and_status(self):
        row = self.documents.listing_rows().first
        expect(row).to_contain_text("Active")
        expect(row).to_contain_text("consent-letter-")

    def test_search_controls(self):
        expect(self.documents.listing_search()).to_be_visible()
        expect(self.documents.listing_search_button()).to_be_visible()

    def test_search_existing_document(self):
        self.documents.listing_search().fill("consent-letter")
        self.documents.listing_search_button().click()
        expect(self.documents.listing_rows()).to_have_count(1)

    def test_negative_search_nonexistent_document(self):
        self.documents.listing_search().fill("qa-nonexistent-document-987654")
        self.documents.listing_search_button().click()
        expect(self.documents.listing_rows()).to_have_count(0)

    def test_search_clear_restores_documents(self):
        search = self.documents.listing_search()
        search.fill("qa-nonexistent-document-987654")
        self.documents.listing_search_button().click()
        expect(self.documents.listing_rows()).to_have_count(0)
        self.documents.listing_clear_button().click()
        expect(search).to_be_empty()
        self.documents.listing_search_button().click()
        expect(self.documents.listing_rows()).to_have_count(1)

    def test_date_filter_fields(self):
        expect(self.documents.page.get_by_placeholder("Start Date")).to_be_visible()
        expect(self.documents.page.get_by_placeholder("End Date")).to_be_visible()

    def test_pagination_controls(self):
        pagination = self.documents.page.locator("ul.ant-pagination")
        expect(pagination).to_be_visible()
        expect(pagination.locator(".ant-pagination-item-active")).to_contain_text("1")

    def test_listing_action_buttons(self):
        row = self.documents.listing_rows().first
        for action in ("View Document", "Download", "Delete Document"):
            expect(row.locator(f'button[title="{action}"]')).to_be_visible()

    def test_back_navigation(self):
        self.documents.listing_back().click()
        expect(self.documents.page.get_by_role(
            "heading", name="Profile - Individual", exact=True
        )).to_be_visible()
