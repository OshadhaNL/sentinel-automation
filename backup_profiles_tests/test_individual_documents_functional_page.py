
import os
import re
import base64
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.individualProfilePage import IndividualProfilePage


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

def open_individual_profile(
    page: Page,
    base_url: str,
    client_id: str,
):
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    assert email and password, (
        "Set TEST_EMAIL and TEST_PASSWORD environment variables"
    )

    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(email)
    login.enter_password(password)
    login.click_login()

    expect(page).to_have_url(
        re.compile(r".*/nolimit/app/home/?$")
    )

    page.get_by_role(
        "link", name="Profiles", exact=False
    ).click()

    expect(
        page.get_by_role(
            "heading", name="Profiles", exact=True
        )
    ).to_be_visible()

    all_files = page.locator(".tab-z-option").filter(
        has=page.locator(
            "label",
            has_text=re.compile(r"^\s*All Files\s*$"),
        )
    ).first

    all_files.click()

    search = page.get_by_placeholder(
        "Search by client ID or name"
    )

    search.fill(client_id)
    search.press("Enter")

    row = page.locator(
        "tbody.ant-table-tbody tr.ant-table-row"
    ).filter(
        has_text=client_id
    ).first

    expect(row).to_be_visible(timeout=15000)

    assert "individual" in row.inner_text().lower(), (
        f"Selected client is not an Individual: "
        f"{row.inner_text()}"
    )

    row.locator("a[href]").first.click()

    profile = IndividualProfilePage(page)

    expect(profile.heading).to_be_visible(timeout=15000)

    profile.open_document_subtab("Upload")

    return profile


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def readonly_profile(page: Page, base_url: str):
    client_id = os.getenv(
        "TEST_INDIVIDUAL_CLIENT_ID", ""
    ).strip()

    if not client_id:
        pytest.skip(
            "Set TEST_INDIVIDUAL_CLIENT_ID"
        )

    return open_individual_profile(
        page, base_url, client_id
    )


@pytest.fixture
def writable_profile(page: Page, base_url: str):
    allow_changes = os.getenv(
        "TEST_INDIVIDUAL_ALLOW_DOCUMENT_CHANGES"
    )

    if allow_changes != "1":
        pytest.skip(
            "Document changes disabled. "
            "Set TEST_INDIVIDUAL_ALLOW_DOCUMENT_CHANGES=1"
        )

    client_id = os.getenv(
        "TEST_INDIVIDUAL_WRITE_CLIENT_ID", ""
    ).strip()

    if not client_id:
        pytest.skip(
            "Set TEST_INDIVIDUAL_WRITE_CLIENT_ID"
        )

    readonly_id = os.getenv(
        "TEST_INDIVIDUAL_CLIENT_ID", ""
    ).strip()

    if readonly_id and readonly_id == client_id:
        pytest.fail(
            "Write client must differ from read-only client"
        )

    return open_individual_profile(
        page, base_url, client_id
    )


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

    def test_preview_opens_and_closes(
        self,
        readonly_profile,
    ):
        document_type = "Passport Copy"

        if uploaded_document(
            readonly_profile, document_type
        ).count() == 0:
            pytest.skip("No Passport Copy available")

        original_name = document_filename(
            readonly_profile, document_type
        ).inner_text().strip()

        document_action(
            readonly_profile,
            document_type,
            "View",
        ).click()

        modal = document_section(
            readonly_profile, document_type
        ).locator(
            ".document-preview-modal:visible"
        )

        expect(modal).to_be_visible()

        expect(
            modal.locator(".modal-z-title")
        ).to_contain_text(original_name)

        modal.locator(
            "button.modal-z-close"
        ).click()

        expect(modal).to_be_hidden()

        expect(
            document_filename(
                readonly_profile, document_type
            )
        ).to_have_text(original_name)

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
