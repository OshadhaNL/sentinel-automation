"""Sentinel Screening page object (Playwright synchronous API)."""
import re
from playwright.sync_api import Page, expect


class ScreeningPage:
    PATH = "/nolimit/app/screening"
    DESCRIPTION = "Conducts PEP, sanction, and adverse media checks on clients."
    DAILY_HEADERS = (
        "Name", "Profile ID", "Mandatory Actions", "Resolved Hits", "Total Hits",
        "Review Required", "Last Modified By", "Created Date", "Last Screened Date",
    )
    RESULT_HEADERS = (
        "Name", "Match Strength", "Type", "Gender", "DOB", "Citizenship", "Resolution",
    )
    RESULT_TABS = ("Unresolved Hits", "Positive Hits", "False Hits", "Possible Hits")
    ONGOING_HELP = (
        "Ongoing screening will add the screening name to the daily screening list "
        "and run a background check on a daily basis"
    )

    def __init__(self, page: Page):
        self.page = page

    def open(self, base_url: str):
        from urllib.parse import urlsplit
        parts = urlsplit(base_url)
        root = f"{parts.scheme}://{parts.netloc}"
        self.page.goto(root + self.PATH, wait_until="domcontentloaded")
        self.assert_loaded()

    def assert_loaded(self):
        expect(self.page.get_by_role("heading", name="Screening", exact=True)).to_be_visible()
        expect(self.page.get_by_text(self.DESCRIPTION, exact=True)).to_be_visible()

    @property
    def client_search(self):
        return self.page.get_by_placeholder("Search by Client name")

    @property
    def client_cards(self):
        return self.page.locator(".clients-list .client-card")

    @property
    def single_tab(self):
        return self.page.locator(".tab-z-option").filter(has_text="Single Screening")

    @property
    def daily_tab(self):
        return self.page.locator(".tab-z-option").filter(has_text="Daily Screening")

    def switch_single(self):
        self.single_tab.click()
        expect(self.single_tab).to_have_class(re.compile(r"\bactive\b"))

    def switch_daily(self):
        self.daily_tab.click()
        expect(self.daily_tab).to_have_class(re.compile(r"\bactive\b"))

    def client_search_button(self):
        return self.client_search.locator("xpath=..").locator("button.search-btn")

    def client_clear_button(self):
        return self.client_search.locator("xpath=..").locator("button.clear-btn")

    def search_clients(self, term: str):
        self.client_search.fill(term)
        self.client_search_button().click()

    def choose_client(self, name: str, index: int = 0):
        card = self.client_cards.filter(has=self.page.locator("p", has_text=re.compile(rf"^{re.escape(name)}$")))
        card.nth(index).click()

    @property
    def individual_radio(self):
        return self.page.locator('input[name="entityType"][value="P"]')

    @property
    def organization_radio(self):
        return self.page.locator('input[name="entityType"][value="O"]')

    @property
    def name_input(self):
        return self.page.locator('input[name="name"]')

    @property
    def gender_radios(self):
        return self.page.locator('input[name="gender"]')

    @property
    def dob_input(self):
        return self.page.get_by_placeholder("Pick date of birth")

    def country_select(self, placeholder: str):
        return self.page.locator(".ant-select").filter(
            has=self.page.locator(".ant-select-selection-placeholder", has_text=placeholder)
        )

    def choose_country(self, placeholder: str, country: str):
        select = self.page.locator(".ant-select").nth(0 if placeholder == "Enter citizenship" else 1)
        select.click()
        select.locator('input[role="combobox"]').fill(country)
        option = self.page.locator('.ant-select-dropdown:visible .ant-select-item-option').filter(
            has_text=re.compile(rf"^{re.escape(country)}$", re.I)
        )
        expect(option.first).to_be_visible(timeout=10000)
        option.first.click()

    @property
    def ongoing(self):
        return self.page.locator('input[name="ongoing"]')

    @property
    def analyze_button(self):
        return self.page.get_by_role("button", name="Analyze")

    def analyze(self, name: str, *, ongoing: bool = False):
        self.name_input.fill(name)
        if ongoing:
            self.ongoing.check()
        self.analyze_button.click()

    @property
    def daily_search(self):
        return self.page.get_by_placeholder("Search here...")

    @property
    def daily_table(self):
        return self.page.locator("main table").first

    @property
    def daily_rows(self):
        return self.daily_table.locator("tbody tr").filter(has=self.page.locator("td"))

    def daily_search_button(self):
        return self.daily_search.locator("xpath=..").locator("button.search-btn")

    def daily_clear_button(self):
        return self.daily_search.locator("xpath=..").locator("button.clear-btn")

    def search_daily(self, term: str):
        self.daily_search.fill(term)
        self.daily_search_button().click()

    def daily_header(self, text: str):
        return self.daily_table.locator("thead th").filter(has_text=re.compile(rf"^{re.escape(text)}$"))

    @property
    def select_all(self):
        return self.daily_table.get_by_role("checkbox", name="Select all")

    def row_checkbox(self, index: int):
        return self.daily_rows.nth(index).locator('input[type="checkbox"]')

    @property
    def bulk_action_button(self):
        return self.page.get_by_role("button", name="Bulk Action")

    @property
    def remove_button(self):
        return self.page.get_by_role("button", name=re.compile(r"Remove\s*$"))

    @property
    def bulk_remove_modal(self):
        return self.page.locator(".modal-z").filter(has=self.page.locator(".modal-z-title", has_text="Bulk Remove"))

    def open_bulk_action(self):
        self.bulk_action_button.click()
        expect(self.bulk_remove_modal.locator(".modal-z-card")).to_be_visible(timeout=10000)

    def close_bulk_action(self):
        self.bulk_remove_modal.get_by_role("button", name="Cancel").click()
        expect(self.bulk_remove_modal.locator(".modal-z-card")).to_be_hidden()

    def result_tab(self, title: str):
        return self.page.get_by_text(title, exact=True)
