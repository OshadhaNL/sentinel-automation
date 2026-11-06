"""Entity Documents Phase 2: read-only actions and opt-in write scenarios.

Uses the existing Sentinel LoginPage + pytest-playwright fixtures.  No test
pays a verification fee or completes onboarding.  Tests that may persist data
require a dedicated entity and TEST_ENTITY_ALLOW_WRITES=1.
"""

import os
import re
import struct
import uuid
import zlib
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.entityDocumentsPage import EntityDocumentsPage


def _enabled(name: str) -> bool:
    return os.getenv(name, "").strip() == "1"


def _qa_pdf(path: Path, label: str) -> Path:
    """Generate a small, valid single-page PDF using only Python stdlib."""
    label = re.sub(r"[^A-Za-z0-9 _-]", "", label)[:70]
    content = f"BT /F1 12 Tf 55 750 Td ({label}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n"
        + content + b"\nendstream",
    ]
    data = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for idx, body in enumerate(objects, start=1):
        offsets.append(len(data))
        data += f"{idx} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(data)
    data += f"xref\n0 {len(offsets)}\n".encode()
    data += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        data += f"{offset:010d} 00000 n \n".encode()
    data += (f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
             f"startxref\n{xref}\n%%EOF\n").encode()
    path.write_bytes(data)
    return path


def _qa_png(path: Path) -> Path:
    """Generate a valid 1x1 RGB PNG without Pillow."""
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + kind + payload
                + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(b"\x00\x00\x80\xff"))
           + chunk(b"IEND", b""))
    path.write_bytes(png)
    return path


def _new_name(extension: str) -> str:
    return f"qa-auto-{uuid.uuid4().hex[:12]}.{extension}"


class _EntityDocumentsSetup:
    WRITE = False

    @pytest.fixture(autouse=True)
    def open_entity(
            self,
            page: Page,
            base_url: str,
            request: pytest.FixtureRequest
    ):
        test_name = request.node.name.split("[", 1)[0]

        if self.WRITE:

            if not _enabled("TEST_ENTITY_ALLOW_WRITES"):
                pytest.skip(
                    "Set TEST_ENTITY_ALLOW_WRITES=1 to run write tests"
                )

            if os.getenv("PYTEST_XDIST_WORKER"):
                pytest.fail(
                    "Run write tests with -n 0, not parallel workers"
                )

            # Skip optional scenarios BEFORE logging in.
            if test_name == "test_upload_all_reaches_review_without_paying":
                if not _enabled("TEST_ENTITY_ALLOW_SUBMIT"):
                    pytest.skip(
                        "Set TEST_ENTITY_ALLOW_SUBMIT=1 to click Upload All"
                    )

            if test_name == "test_delete_only_a_named_qa_automation_file":
                if not _enabled("TEST_ENTITY_ALLOW_DELETE"):
                    pytest.skip(
                        "Set TEST_ENTITY_ALLOW_DELETE=1 to test deletion"
                    )

            if test_name == "test_delete_cancel_preserves_named_qa_file":
                if not _enabled("TEST_ENTITY_ALLOW_DELETE_CANCEL"):
                    pytest.skip(
                        "Set TEST_ENTITY_ALLOW_DELETE_CANCEL=1"
                    )

            if test_name in {
                "test_delete_only_a_named_qa_automation_file",
                "test_delete_cancel_preserves_named_qa_file",
            }:
                filename = os.getenv(
                    "TEST_ENTITY_DELETE_FILENAME", ""
                ).strip()

                if not re.fullmatch(
                        r"qa-auto-[A-Za-z0-9_-]+\.pdf",
                        filename,
                        re.I
                ):
                    pytest.fail(
                        "Set TEST_ENTITY_DELETE_FILENAME to "
                        "an existing qa-auto-*.pdf"
                    )

            client_id = os.getenv(
                "TEST_ENTITY_WRITE_CLIENT_ID", ""
            ).strip()

            readonly_id = os.getenv(
                "TEST_ENTITY_CLIENT_ID", ""
            ).strip()

            if not readonly_id:
                pytest.fail(
                    "Set TEST_ENTITY_CLIENT_ID for safety"
                )

            if not client_id:
                pytest.skip(
                    "Set TEST_ENTITY_WRITE_CLIENT_ID to "
                    "a real disposable QA entity ID"
                )

            if not re.fullmatch(
                    r"SENTINEL[A-Za-z0-9_-]+",
                    client_id
            ):
                pytest.fail(
                    "Invalid entity ID. Do not use a placeholder."
                )

            if client_id == readonly_id:
                pytest.fail(
                    "Read-only and write entity IDs must be different"
                )

        else:

            if test_name == "test_verify_download_existing_consent_letter":
                if not _enabled("TEST_ENTITY_ENABLE_DOWNLOAD"):
                    pytest.skip(
                        "Set TEST_ENTITY_ENABLE_DOWNLOAD=1"
                    )

            client_id = os.getenv(
                "TEST_ENTITY_CLIENT_ID", ""
            ).strip()

            if not client_id:
                pytest.skip(
                    "Set TEST_ENTITY_CLIENT_ID"
                )

        # Login
        email = os.getenv("TEST_EMAIL", "").strip()
        password = os.getenv("TEST_PASSWORD", "")

        assert email, "TEST_EMAIL is required"
        assert password, "TEST_PASSWORD is required"

        login = LoginPage(page)

        login.open(base_url)
        login.enter_email(email)
        login.enter_password(password)
        login.click_login()

        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$"),
            timeout=45000
        )

        # Navigate to the requested entity.
        base = urlsplit(base_url)
        origin = f"{base.scheme}://{base.netloc}"

        entity_url = (
            f"{origin}/nolimit/app/onboarding/entity/process"
            f"?step=documents&client={quote(client_id, safe='')}"
        )

        page.goto(
            entity_url,
            wait_until="domcontentloaded"
        )

        self.page = page
        self.client_id = client_id
        self.documents = EntityDocumentsPage(page)

        self.documents.verify_page_loaded()

        # Confirm that the correct entity actually loaded.
        expect(
            self.documents.reference_id
        ).to_have_text(
            client_id,
            timeout=15000
        )

    def _handle_owned_file_delete(
            self,
            file_card,
            *,
            confirm: bool
    ):
        """
        Handle a browser confirmation or a custom Delete modal.

        Only use for automation-owned files on a disposable QA entity.
        """

        dialog_types = []

        def on_dialog(dialog):

            dialog_types.append(dialog.type)

            if dialog.type != "confirm":
                dialog.dismiss()
                return

            if confirm:
                dialog.accept()
            else:
                dialog.dismiss()

        self.page.on("dialog", on_dialog)

        try:
            delete_button = file_card.locator(
                'button[title="Delete"]'
            )

            expect(delete_button).to_be_visible()

            delete_button.click()

            if dialog_types:

                assert dialog_types == ["confirm"], (
                    f"Unexpected browser dialog: {dialog_types}"
                )

            else:

                modal = self.documents.visible_named_modal(
                    "Delete document"
                )

                expect(modal).to_be_visible(
                    timeout=5000
                )

                button_name = (
                    "Delete" if confirm else "Cancel"
                )

                modal.get_by_role(
                    "button",
                    name=button_name,
                    exact=True
                ).click()

                expect(modal).not_to_be_visible()

        finally:

            self.page.remove_listener(
                "dialog",
                on_dialog
            )

@pytest.mark.ui
class TestEntityDocumentsReadOnlyActions(_EntityDocumentsSetup):
    """Safe on the existing QA entity with a Consent Letter document."""

    def test_consent_letter_cabinet_navigation(self):
        row = self.documents.wait_for_consent_letter_cabinet()
        link = row.locator("a.table-link")
        expect(link).to_be_visible()
        href = link.get_attribute("href")
        assert href is not None
        assert urlsplit(href).path.startswith("/nolimit/app/documents/consent-letter/")
        assert parse_qs(urlsplit(href).query).get("clientRefId") == [self.client_id]
        link.click()
        expect(self.page).to_have_url(
            re.compile(r"/nolimit/app/documents/consent-letter/"), timeout=15000
        )

    def test_verify_consent_letter_preview_opens_and_closes(self):
        self.documents.open_document_tab("Verify")
        self.documents.click_verify_file_action("Consent Letter", "View")
        modal = self.documents.visible_preview_modal()
        expect(modal).to_be_visible(timeout=15000)
        expect(modal.locator(".document-view iframe")).to_have_count(1)
        modal.locator("button.modal-z-close").click()
        expect(modal).not_to_be_visible()

    def test_verify_delete_button_is_visible_without_clicking(self):
        self.documents.open_document_tab("Verify")

        file_card = self.documents.verify_uploaded_file(
            "Consent Letter"
        )

        expect(file_card).to_be_visible(
            timeout=15000
        )

        delete_button = file_card.locator(
            'button[title="Delete"]'
        )

        expect(delete_button).to_be_visible()

    def test_verify_modify_cancel_preserves_consent_letter(self):
        self.documents.open_document_tab("Verify")
        file_card = self.documents.verify_uploaded_file("Consent Letter")
        expect(file_card).to_be_visible(timeout=15000)
        file_card.locator('button[title="Modify"]').click()
        modal = self.documents.visible_modify_modal()
        expect(modal).to_be_visible()
        modal.get_by_role("button", name="Cancel", exact=True).click()
        expect(modal).not_to_be_visible()
        expect(file_card).to_be_visible()

    def test_verify_reupload_opens_file_chooser_without_selecting(self):
        self.documents.open_document_tab("Verify")
        file_card = self.documents.verify_uploaded_file("Consent Letter")
        expect(file_card).to_be_visible(timeout=15000)
        # We do NOT call file_chooser.set_files(), so the existing document is safe.
        with self.page.expect_file_chooser(timeout=10000):
            file_card.locator('button[title="Reupload"]').click()

    def test_verify_download_existing_consent_letter(self, tmp_path: Path):
        if not _enabled("TEST_ENTITY_ENABLE_DOWNLOAD"):
            pytest.skip("Set TEST_ENTITY_ENABLE_DOWNLOAD=1 to test browser downloads")
        self.documents.open_document_tab("Verify")
        file_card = self.documents.verify_uploaded_file("Consent Letter")
        expect(file_card).to_be_visible(timeout=15000)
        with self.page.expect_download(timeout=30000) as download_info:
            file_card.locator('button[title="Download"]').click()
        download = download_info.value
        saved_path = tmp_path / download.suggested_filename
        download.save_as(str(saved_path))
        assert saved_path.is_file() and saved_path.stat().st_size > 0


@pytest.mark.ui
class TestEntityDocumentsWrite(_EntityDocumentsSetup):
    """Opt-in tests. Run with -n 0 against a dedicated disposable entity."""
    WRITE = True

    def test_bulk_valid_pdf_enables_upload_all(self, tmp_path: Path):
        pdf = _qa_pdf(tmp_path / _new_name("pdf"), "QA Entity bulk upload")
        self.documents.upload_bulk_file(pdf)
        expect(self.documents.upload_all_button).to_be_enabled(timeout=15000)
        # Do not click Upload All: this test only checks staging.

    def test_bulk_multiple_valid_files_enable_upload_all(self, tmp_path: Path):
        pdf = _qa_pdf(tmp_path / _new_name("pdf"), "QA Entity multiple files")
        png = _qa_png(tmp_path / _new_name("png"))
        self.documents.open_document_tab("Upload")
        self.documents.bulk_upload_input.set_input_files([str(pdf), str(png)])
        expect(self.documents.upload_all_button).to_be_enabled(timeout=15000)

    def test_bulk_rejects_unsupported_extension(self, tmp_path: Path):
        txt = tmp_path / _new_name("txt")
        txt.write_text("unsupported extension test", encoding="utf-8")
        self.documents.open_document_tab("Upload")
        expect(self.documents.upload_all_button).to_be_disabled()
        self.documents.bulk_upload_input.set_input_files(str(txt))
        # Requirement: only PDF/PNG/JPG/JPEG may be staged for upload.
        expect(self.documents.upload_all_button).to_be_disabled(timeout=10000)

    def test_bulk_rejects_file_larger_than_10mb(self, tmp_path: Path):
        pdf = _qa_pdf(tmp_path / _new_name("pdf"), "Oversize QA test")
        # The extra bytes are a PDF comment, keeping a valid PDF prefix.
        with pdf.open("ab") as f:
            f.write(b"\n%" + b"A" * (10 * 1024 * 1024 + 1))
        assert pdf.stat().st_size > 10 * 1024 * 1024
        self.documents.open_document_tab("Upload")
        expect(self.documents.upload_all_button).to_be_disabled()
        self.documents.bulk_upload_input.set_input_files(str(pdf))
        expect(self.documents.upload_all_button).to_be_disabled(timeout=10000)

    def test_category_upload_others_accepts_pdf(self, tmp_path: Path):
        # Category inputs may upload immediately. Only run on disposable entity.
        pdf = _qa_pdf(tmp_path / _new_name("pdf"), "QA Entity category upload")
        self.documents.open_document_tab("Upload")
        card = self.documents.category_card("Others")
        expect(card).to_be_visible()
        before = card.inner_text()
        self.documents.category_file_input("Others").set_input_files(str(pdf))
        # The app may stage the file OR upload immediately. Require a visible
        # change in the card or an enabled Upload All button, not just input.files.
        self.page.wait_for_function(
            """({before, name}) => {
                const cards = [...document.querySelectorAll(
                    '.bulk-documents-wrapper > .grid > div')];
                const card = cards.find(c => [...c.querySelectorAll('button')]
                    .some(b => b.textContent.trim() === 'Others'));
                const uploadAll = [...document.querySelectorAll('button')]
                    .find(b => b.textContent.includes('Upload All'));
                return !!card && (card.innerText !== before ||
                    card.innerText.includes(name) || (uploadAll && !uploadAll.disabled));
            }""",
            arg={"before": before, "name": pdf.name},
            timeout=20000,
        )

    def test_upload_all_reaches_review_without_paying(self, tmp_path: Path):
        if not _enabled("TEST_ENTITY_ALLOW_SUBMIT"):
            pytest.skip("Set TEST_ENTITY_ALLOW_SUBMIT=1 to click Upload All")
        pdf = _qa_pdf(tmp_path / _new_name("pdf"), "QA Entity upload all")
        self.documents.upload_bulk_file(pdf)
        expect(self.documents.upload_all_button).to_be_enabled(timeout=15000)
        self.documents.upload_all_button.click()
        payment = self.page.locator(".modal-z.payment-modal:visible")
        success = self.page.get_by_text("Submission Successful", exact=True)
        # The captured DOM contains both possible dialogs; which appears after
        # upload is a live-app behavior to verify. Never click Pay & Confirm.
        expect(payment.or_(success).first).to_be_visible(timeout=30000)
        if payment.is_visible():
            expect(payment.get_by_role("button", name="Pay & Confirm")).to_be_visible()
            payment.get_by_role("button", name="Cancel", exact=True).click()

    def test_delete_only_a_named_qa_automation_file(self):

        filename = os.getenv(
            "TEST_ENTITY_DELETE_FILENAME", ""
        ).strip()

        group = os.getenv(
            "TEST_ENTITY_DELETE_GROUP", "Others"
        ).strip()

        self.documents.open_document_tab("Verify")

        file_card = self.documents.verify_uploaded_file(
            group,
            filename
        )

        expect(file_card).to_be_visible(
            timeout=15000
        )

        # Explicitly confirmed deletion.
        self._handle_owned_file_delete(
            file_card,
            confirm=True
        )

        expect(file_card).to_have_count(
            0,
            timeout=15000
        )

        # Verify deletion persists after refresh.
        self.page.reload(
            wait_until="domcontentloaded"
        )

        self.documents.verify_page_loaded()

        self.documents.open_document_tab("Verify")

        expect(
            self.documents.verify_uploaded_file(
                group,
                filename
            )
        ).to_have_count(0)

    def test_delete_cancel_preserves_named_qa_file(self):

        filename = os.getenv(
            "TEST_ENTITY_DELETE_FILENAME", ""
        ).strip()

        group = os.getenv(
            "TEST_ENTITY_DELETE_GROUP", "Others"
        ).strip()

        self.documents.open_document_tab("Verify")

        file_card = self.documents.verify_uploaded_file(
            group,
            filename
        )

        expect(file_card).to_be_visible(
            timeout=15000
        )

        # Cancel the deletion.
        self._handle_owned_file_delete(
            file_card,
            confirm=False
        )

        expect(file_card).to_be_visible(
            timeout=15000
        )

        # Reload and confirm the file still exists.
        self.page.reload(
            wait_until="domcontentloaded"
        )

        self.documents.verify_page_loaded()

        self.documents.open_document_tab("Verify")

        expect(
            self.documents.verify_uploaded_file(
                group,
                filename
            )
        ).to_be_visible(
            timeout=15000
        )
