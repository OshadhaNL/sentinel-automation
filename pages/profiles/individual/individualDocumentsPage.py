import re
from playwright.sync_api import expect
from pages.profiles.baseProfilePage import BaseProfilePage


class IndividualDocumentsPage(BaseProfilePage):
    """Document-specific locators and actions. Reused by IndividualProfilePage."""
    TABS = ("Verification", "Documents", "Screening", "KYC Form", "Risk Assessment", "Activities")

    def open_document_subtab(self, name: str):
        self.open_tab("Documents")
        tab = self.page.locator(".tab-z-option").filter(
            has=self.page.locator("label", has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))
        ).first
        tab.click()
        expect(tab).to_have_class(re.compile(r"\bactive\b"))

    DOCUMENT_TYPES = (
        "Passport Copy",
        "Driver Licence",
        "Proof of Age Card",
        "Others",
    )

    @property
    def heading(self):
        return self.page.get_by_role(
            "heading",
            name="Profile - Individual",
            exact=True,
        )

    def open_documents_upload(self):
        self.open_document_subtab("Upload")

    def document_section(self, document_type: str):
        if document_type not in self.DOCUMENT_TYPES:
            raise ValueError(f"Unknown document type: {document_type}")

        return self.page.locator(
            ".custom-form > div"
        ).filter(
            has=self.page.locator(
                "label.document-label",
                has_text=re.compile(
                    rf"^\s*{re.escape(document_type)}\s*$"
                ),
            )
        ).first

    def document_uploader(self, document_type: str):
        return self.document_section(document_type).locator(
            ".uploader-z"
        ).first

    def document_file_input(self, document_type: str):
        return self.document_uploader(document_type).locator(
            'input[type="file"]'
        )

    def document_has_uploaded_file(self, document_type: str):
        return self.document_uploader(document_type).locator(
            ".uploaded.show-file"
        ).count() > 0

    def document_filename(self, document_type: str):
        return self.document_uploader(document_type).locator(
            ".uploaded.show-file .uploaded-file h6"
        ).inner_text().strip()

    def document_action(self, document_type: str, action: str):
        return self.document_uploader(document_type).locator(
            f'button[title="{action}"]'
        )

    def upload_document(self, document_type: str, file_path: str):
        self.document_file_input(document_type).set_input_files(
            file_path
        )

    def open_document_preview(self, document_type: str):
        self.document_action(document_type, "View").click()

        modal = self.page.locator(
            ".document-preview-modal:visible"
        )

        expect(modal).to_be_visible()
        return modal

    def delete_document(self, document_type: str):
        self.document_action(document_type, "Delete").click()

        modal = self.page.locator(
            ".modal-z:visible"
        ).filter(
            has=self.page.locator(
                ".modal-z-title",
                has_text="Delete document",
            )
        )

        expect(modal).to_be_visible()
        return modal



    # --------------------------------------------------------
    # Read-only Documents helpers
    # --------------------------------------------------------

    def document_reference(self):
        return self.page.locator(
            "h4.secondary-title"
        ).filter(has_text="Ref ID:")

    def document_client_name(self):
        return self.page.locator(
            "h4.secondary-title"
        ).filter(has_text="Client Name:")

    def open_verify(self):
        self.open_document_subtab("Verify")

    def open_cabinets(self):
        self.open_document_subtab("Cabinets")

    def verify_category(self, name: str):
        return self.page.locator(
            ".border-box"
        ).filter(
            has=self.page.locator(
                "label.border-box-label",
                has_text=re.compile(
                    rf"^\s*{re.escape(name)}\s*$"
                )
            )
        )

    def verify_files(self, name: str):
        return self.verify_category(name).locator(
            ".uploaded.show-file"
        )

    def verify_file_action(
        self,
        category: str,
        action: str,
        index: int = 0,
    ):
        return self.verify_files(category).nth(index).locator(
            f'button[title="{action}"]'
        )

    def verify_preview(self, category: str, index: int = 0):
        self.verify_file_action(
            category, "View", index
        ).click()

        # Image files open in a separate image viewer.
        image_viewer = self.page.get_by_role("dialog").filter(
            has=self.page.get_by_role("img", name=re.compile(r"\.(jpg|jpeg|png)$", re.I))
        )

        if image_viewer.count() > 0:
            expect(image_viewer).to_be_visible(timeout=10000)
            return image_viewer

        # PDF files use the application's document preview modal.
        modal = self.page.locator(
            ".document-preview-modal:visible"
        ).first

        expect(modal).to_be_visible(timeout=10000)
        return modal

    def cabinets_table(self):
        return self.page.locator(
            ".custom-table table"
        ).first

    def cabinet_rows(self):
        return self.cabinets_table().locator(
            "tbody.ant-table-tbody tr.ant-table-row"
        )

    def cabinet_row(self, name: str):
        return self.cabinet_rows().filter(
            has=self.page.locator(
                "a.table-link",
                has_text=re.compile(
                    rf"^\s*{re.escape(name)}\s*\(\d+\)\s*$"
                )
            )
        )

    def open_cabinet(self, name: str):
        row = self.cabinet_row(name)
        expect(row).to_have_count(1)
        row.locator("a.table-link").click()

    def listing_table(self):
        return self.page.locator(
            ".custom-table table"
        ).first

    def listing_rows(self):
        return self.listing_table().locator(
            "tbody.ant-table-tbody tr.ant-table-row"
        )

    def listing_search(self):
        return self.page.get_by_placeholder(
            "Search documents"
        )

    def listing_search_button(self):
        return self.page.locator(
            ".search-box-z button.search-btn"
        )

    def listing_clear_button(self):
        return self.page.locator(
            ".search-box-z button.clear-btn"
        )

    def listing_back(self):
        return self.page.locator(
            "button.back-link"
        ).first
