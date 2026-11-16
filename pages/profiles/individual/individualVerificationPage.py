
import re

from playwright.sync_api import Page, expect

from pages.profiles.individual.individualProfilePage import IndividualProfilePage


class IndividualVerificationPage(IndividualProfilePage):
    """Read-only checks for processed identity verification details."""

    CLIENT_ID = "SENTINELE7CE963CAACEA23"

    LABELS = (
        "Face Match",
        "Issuing Country",
        "Region",
        "Type of Document",
        "First Name",
        "Last Name",
        "Date of Birth",
        "Driver Licence Number",
        "Card Number",
        "Expiry Date",
        "Gender",
        "Nationality",
        "Occupation",
        "Issue Date",
        "Place of Birth",
        "Address",
        "Face Recognition Time",
        "Text Extraction Time",
    )

    def __init__(self, page: Page):
        super().__init__(page)

        self.report = page.locator("ul.verification-report")
        self.breadcrumb = page.locator(".breadcrumb-wrapper")
        self.images = page.locator(".document-img")

    def open(self):
        self.open_tab("Verification")
        expect(self.report).to_be_visible(timeout=15000)

    def item(self, label: str):
        if label == "Driver Licence Number":
            pattern = r"^\s*(?:Driver|Driving) Licence Number\s*$"
        else:
            pattern = rf"^\s*{re.escape(label)}\s*$"

        return self.report.locator(
            ".verification-report-item"
        ).filter(
            has=self.page.locator(
                "span.label",
                has_text=re.compile(pattern, re.I)
            )
        )

    def badge(self, label: str):
        return self.item(label).locator("span.custom-badge")

    def value(self, label: str):
        return self.badge(label).inner_text().strip()

    def image_for(self, title: str):
        label = self.images.locator(
            ".custom-label"
        ).filter(
            has_text=re.compile(
                rf"^\s*{re.escape(title)}\s*$",
                re.I
            )
        )

        return label.locator(
            "xpath=following-sibling::div[1]//img"
        )

    def assert_image_loaded(self, title: str):
        image = self.image_for(title)

        expect(image).to_have_count(1)
        expect(image).to_be_visible(timeout=15000)

        expect(image).to_have_attribute(
            "src",
            re.compile(r"^https?://")
        )

        expect(image).to_have_js_property(
            "complete",
            True,
            timeout=30000
        )

        expect(image).not_to_have_js_property(
            "naturalWidth",
            0,
            timeout=30000
        )
