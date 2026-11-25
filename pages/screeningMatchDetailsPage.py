"""WorldCheck match details/report page based on the supplied DOM."""
import re
from playwright.sync_api import Page, expect


class ScreeningMatchDetailsPage:
    RESOLUTIONS = ("Positive Hits", "False Hits", "Possible Hits")
    SECTIONS = ("PERSONAL DETAILS", "BIOGRAPHY", "PEP ROLE DETAILS", "Further Information", "Linked Individuals", "Education", "Linked Companies", "Sources")
    PERSONAL_FIELDS = ("Name", "Record Date", "Category", "Gender", "Date of Birth", "Place of Birth", "Citizenship", "Location Details", "Address", "Special Interest Categories", "Identification Numbers", "Alias", "PEP Type")

    def __init__(self, page: Page):
        self.page = page
        self.report = page.locator("#wc-report")
        self.resolution = page.locator(".listing-toolbar-actions .ant-select")
        self.update = page.locator(".listing-toolbar-actions button.primary-btn")
        self.back = page.locator("button.back-link")
        self.previous = page.locator('button[title="Previous"]')
        self.next = page.locator('button[title="Next"]')

    def assert_loaded(self):
        expect(self.report).to_be_visible(timeout=60000)
        expect(self.report.get_by_role("heading", name="PERSONAL DETAILS")).to_be_visible()
        expect(self.back).to_be_visible()

    def position(self):
        label = self.page.get_by_text(re.compile(r"Showing\s+\d+\s+of\s+\d+\s+Matches", re.I)).first.inner_text()
        match = re.search(r"Showing\s+(\d+)\s+of\s+(\d+)\s+Matches", label, re.I)
        assert match, f"Cannot parse match position: {label!r}"
        return tuple(map(int, match.groups()))

    def profile_id(self):
        value = self.report.locator(".wc-report-profile p").first.inner_text().strip()
        assert value, "Missing WorldCheck profile ID"
        return value

    def detail(self, label):
        row = self.report.locator("table.wc-report-body tbody tr").filter(
            has=self.page.locator("td:first-child b", has_text=re.compile(rf"^{re.escape(label)}$"))
        )
        return row.locator("td").nth(1)

    def options(self):
        self.resolution.click()
        dropdown = self.page.locator(".ant-select-dropdown:visible")
        expect(dropdown).to_be_visible()
        return dropdown

    def choose_resolution(self, value):
        assert value in self.RESOLUTIONS
        dropdown = self.options()
        dropdown.locator(".ant-select-item-option").filter(
            has_text=re.compile(rf"^{re.escape(value)}$", re.I)
        ).click()
        expect(self.resolution.locator(".ant-select-selection-item")).to_have_text(value)

    def section(self, name):
        return self.report.get_by_role("heading", name=name, exact=True)

    def section_table(self, name):
        return self.section(name).locator("xpath=ancestor::div[contains(@class,'wc-report-title')][1]/following-sibling::table[1]")

    def sources(self):
        return self.section_table("Sources").locator('tbody a[href^="http"]')

    def download_pdf(self):
        # PDF export may be a browser download or a new tab; test separately if needed.
        return self.page.locator(".listing-toolbar-actions button.outline-btn")
