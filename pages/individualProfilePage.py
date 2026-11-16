
import re
from playwright.sync_api import Page, expect


class IndividualProfilePage:
    """Read-only interactions for Individual Profile. Avoids changing client records."""

    TABS = ("Verification", "Documents", "Screening", "KYC Form", "Risk Assessment", "Activities")
    VERIFICATION_LABELS = (
        "Face Match", "Issuing Country", "Region", "Type of Document", "First Name",
        "Last Name", "Date of Birth", "Driving Licence Number", "Card Number",
        "Expiry Date", "Gender", "Nationality", "Occupation", "Issue Date",
        "Place of Birth", "Address", "Face Recognition Time", "Text Extraction Time",
    )
    RISK_HEADINGS = (
        "Country / Jurisdiction Risk", "Individual Risk", "Australian Residential Status",
        "Transfer of Funds", "Adverse Media", "Risk Assessment Summary", "Approval",
    )

    def __init__(self, page: Page):
        self.page = page
        self.heading = page.get_by_role("heading", name="Profile - Individual", exact=True)
        self.back = page.locator("button.back-link").first

    def tab(self, name: str):
        if name not in self.TABS:
            raise ValueError(f"Unknown profile tab: {name}")
        # Direct child labels prevent collisions with nested tabs.
        return self.page.locator(".tab-z-option").filter(
            has=self.page.locator("label", has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))
        ).first

    def open_tab(self, name: str):
        self.tab(name).click()
        expect(self.tab(name)).to_have_class(re.compile(r"\bactive\b"))

    def verify_shell(self):
        expect(self.heading).to_be_visible()
        expect(self.page.get_by_text(
            "View and manage this client's profile details and compliance information.", exact=True
        )).to_be_visible()
        for name in self.TABS:
            expect(self.tab(name)).to_be_visible()

    def verification_item(self, label: str):
        return self.page.locator(".verification-report-item").filter(
            has=self.page.locator(".label", has_text=re.compile(rf"^\s*{re.escape(label)}\s*$"))
        )

    def open_document_subtab(self, name: str):
        self.open_tab("Documents")
        tab = self.page.locator(".tab-z-option").filter(
            has=self.page.locator("label", has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))
        ).first
        tab.click()
        expect(tab).to_have_class(re.compile(r"\bactive\b"))

    def screening_back_to_form(self):
        self.open_tab("Screening")
        button = self.page.get_by_role("button", name="Back to Screening")
        expect(button).to_be_visible()
        button.click()
        expect(self.page.get_by_text("Single Screening", exact=True)).to_be_visible()

    def activities_table(self):
        return self.page.locator(".ant-table-wrapper").filter(
            has=self.page.locator("th", has_text="Transaction ID")
        ).first

    def activity_search(self):
        return self.page.get_by_placeholder("Search by ID, property, type, status…")



    DOCUMENT_TYPES = (
        "Passport Copy",
        "Driver Licence",
        "Proof of Age Card",
        "Others",
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
