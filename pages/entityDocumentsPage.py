"""Entity Documents: Upload, Verify and Cabinets page object.

Only locators observed in the supplied HTML are used. Methods that change
server data are intentionally separate from read-only verification methods.
"""

import re
from pathlib import Path
from playwright.sync_api import Page, expect
from pages.entityOnboardingPage import EntityOnboardingPage


class EntityDocumentsPage(EntityOnboardingPage):
    DOCUMENT_TAB_ICONS = {
        "Upload": "fa-cloud-upload",
        "Verify": "fa-file-check",
        "Cabinets": "fa-folder-tree",
    }
    DOCUMENT_CATEGORIES = (
        "Commercial Registration (ASIC Extract)",
        "National ID / Driving Licence",
        "Passport",
        "Financial Statements (6 Months)",
        "Power of Attorney",
        "Ownership",
        "Others",
    )
    ACCEPTED_FILE_TYPES = "application/pdf,image/png,image/jpeg,image/jpg"

    def __init__(self, page: Page):
        super().__init__(page)
        # Find the nested Documents tab group by its Upload option; the main
        # navigation and the other nested tab groups do not contain Upload.
        documents_tab_group = page.locator(".onboarding-page .tab-z").filter(
            has=page.locator(".tab-z-option").filter(
                has_text=re.compile(r"^\s*Upload\s*$")
            )
        )
        self.document_tabs = documents_tab_group.locator(
            ".tab-z-labels > .tab-z-option"
        )
        self.bulk_upload_input = page.locator(".uploader-z .upload-wrapper input#dealCsv")
        self.category_cards = page.locator(".bulk-documents-wrapper > .grid > div")
        self.validated_counter = page.locator(".bulk-documents-wrapper > h5")
        # Match the accessible button name without assuming DOM parent structure.
        # Font Awesome icons can prefix the name, e.g. " Upload All".
        self.upload_all_button = page.get_by_role(
            "button", name=re.compile(r"Upload All\s*$")
        )
        self.verify_groups = page.locator(".custom-form .border-box")
        self.cabinets_table = page.locator(".onboarding-page .custom-table table")

    def document_tab(self, name: str):
        if name not in self.DOCUMENT_TAB_ICONS:
            raise ValueError(f"Unknown Documents tab: {name}")
        return self.document_tabs.filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")
        )

    def open_document_tab(self, name: str):
        self.open_main_tab("Documents")
        tab = self.document_tab(name)
        tab.click()
        expect(tab).to_have_class(re.compile(r"(?:^|\s)active(?:\s|$)"))
        return tab

    def verify_document_navigation(self):
        self.open_main_tab("Documents")
        expect(self.document_tabs).to_have_count(3)
        for name, icon_class in self.DOCUMENT_TAB_ICONS.items():
            tab = self.document_tab(name)
            expect(tab).to_be_visible()
            expect(tab.locator(f"i.{icon_class}")).to_have_count(1)

    def verify_upload_section(self):
        self.open_document_tab("Upload")
        expect(self.page.get_by_role("heading", name="Bulk Upload", exact=True)).to_be_visible()
        expect(self.page.locator(".uploader-z .upload-wrapper")).to_be_visible()
        expect(self.bulk_upload_input).to_have_count(1)
        expect(self.bulk_upload_input).to_have_attribute(
            "accept", self.ACCEPTED_FILE_TYPES
        )
        expect(self.bulk_upload_input).to_have_attribute("multiple", "")
        expect(self.category_cards).to_have_count(len(self.DOCUMENT_CATEGORIES))
        expect(self.validated_counter).to_have_text(
            re.compile(r"^\s*\d+\s*/\s*\d+\s+Documents Validated\s*$")
        )
        expect(self.upload_all_button).to_be_visible()

    def category_card(self, category: str):
        if category not in self.DOCUMENT_CATEGORIES:
            raise ValueError(f"Unknown document category: {category}")
        return self.category_cards.filter(
            has=self.page.get_by_role("button", name=category, exact=True)
        )

    def category_upload_button(self, category: str):
        return self.category_card(category).locator(
            'button[aria-label^="Upload documents to "]'
        )

    def category_file_input(self, category: str):
        return self.category_card(category).locator('input[type="file"]')

    def verify_category(self, category: str):
        card = self.category_card(category)
        expect(card).to_be_visible()
        expect(card.get_by_role("button", name=category, exact=True)).to_be_visible()
        expect(self.category_upload_button(category)).to_be_visible()
        expect(self.category_file_input(category)).to_have_attribute(
            "accept", self.ACCEPTED_FILE_TYPES
        )
        expect(card.get_by_text(re.compile(r"\d+ Files Uploaded"))).to_be_visible()

    def upload_bulk_file(self, path: str | Path):
        """Select a file; does not click Upload All or submit the entity."""
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(path)
        self.open_document_tab("Upload")
        self.bulk_upload_input.set_input_files(str(path.resolve()))

    def upload_category_file(self, category: str, path: str | Path):
        """Select a file in a category. The application may upload immediately."""
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(path)
        self.open_document_tab("Upload")
        self.category_file_input(category).set_input_files(str(path.resolve()))

    def verify_group(self, name: str):
        return self.verify_groups.filter(
            has=self.page.locator(".border-box-label").filter(
                has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")
            )
        )

    def verify_file_action(self, group_name: str, title: str):
        return self.verify_group(group_name).locator(
            f'.uploaded.show-file button[title="{title}"]'
        )

    def cabinet_row(self, name: str):
        return self.cabinets_table.locator("tbody tr").filter(has_text=name)

    def consent_letter_cabinet_row(self):
        return self.cabinets_table.locator('tbody tr[data-row-key="consent-letter"]')

    # Phase 2: reusable actions. The visible modal selectors are deliberately
    # scoped because the app keeps closed modal elements in the DOM.

    def verify_uploaded_file(self, group_name: str, filename: str | None = None):
        files = self.verify_group(group_name).locator(".uploaded.show-file")
        if filename is not None:
            files = files.filter(has_text=filename)
        return files

    def visible_preview_modal(self):
        return self.page.locator(".modal-z.document-preview-modal:visible")

    def visible_named_modal(self, title: str):
        return self.page.locator(".modal-z:visible").filter(
            has=self.page.locator(".modal-z-title").filter(
                has_text=re.compile(rf"^\s*{re.escape(title)}\s*$")
            )
        )

    def visible_modify_modal(self):
        # The captured Modify dialog has an empty/dynamic title, but a Save
        # button in its footer. Avoid generated modal IDs and empty headings.
        return self.page.locator(".modal-z:visible").filter(
            has=self.page.locator(".modal-z-footer button.modal-z-primary-btn").filter(
                has_text=re.compile(r"^\s*Save\s*$")
            )
        )

    def click_verify_file_action(self, group_name: str, title: str,
                                 filename: str | None = None):
        file_card = self.verify_uploaded_file(group_name, filename)
        expect(file_card).to_be_visible(timeout=15000)
        action = file_card.locator(f'button[title="{title}"]')
        expect(action).to_be_visible()
        action.click()

    def wait_for_consent_letter_cabinet(self, timeout: int = 15000):
        self.open_document_tab("Cabinets")
        expect(self.cabinets_table).to_be_visible(timeout=timeout)
        row = self.consent_letter_cabinet_row()
        # Do not use row.count() as a readiness check: it returns immediately.
        expect(row).to_be_visible(timeout=timeout)
        return row
