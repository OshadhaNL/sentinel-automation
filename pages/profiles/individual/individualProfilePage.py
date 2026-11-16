
import re
from playwright.sync_api import Page, expect
from pages.profiles.individual.individualDocumentsPage import IndividualDocumentsPage


class IndividualProfilePage(IndividualDocumentsPage):
    """Read-only interactions for Individual Profile. Avoids changing client records."""

    TABS = ("Verification", "Documents", "Screening", "KYC Form", "Risk Assessment", "Activities")
    VERIFICATION_LABELS = (
        "Face Match", "Issuing Country", "Region", "Type of Document", "First Name",
        "Last Name", "Date of Birth", "Driver Licence Number", "Card Number",
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



