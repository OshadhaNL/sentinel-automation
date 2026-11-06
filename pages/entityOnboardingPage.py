"""Common Entity Onboarding navigation, grounded in the supplied DOM snapshots."""

import re
from playwright.sync_api import Page, expect


class EntityOnboardingPage:
    MAIN_TAB_ICONS = {
        "Documents": "fa-folder-open",
        "Screening": "fa-globe-americas",
        "KYC Form": "fa-user-check",
        "Risk Assessment": "fa-shield-check",
        "Ownership": "fa-percent",
    }

    def __init__(self, page: Page):
        self.page = page
        # The five top-level tabs are DIVs, not <button> elements.
        # This scope excludes nested Upload/Verify/Cabinets and Generic tabs.
        self.main_tabs = page.locator(
            ".onboarding-page > div > .tab-z.my-4 > "
            ".tab-z-labels > .tab-z-option"
        )
        self.heading = page.get_by_role("heading", name="Onboarding Entity", exact=True)
        self.reference_id = (
            page.locator("h4.secondary-title")
            .filter(has_text=re.compile(r"^\s*Ref ID:"))
            .locator("span.text-primary")
        )
        self.client_name = (
            page.locator("h4.secondary-title")
            .filter(has_text=re.compile(r"^\s*Client Name:"))
            .locator("span.text-primary")
        )

    def main_tab(self, name: str):
        if name not in self.MAIN_TAB_ICONS:
            raise ValueError(f"Unknown entity tab: {name}")
        return self.main_tabs.filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")
        )

    def verify_page_loaded(self):
        expected_tabs = [
            "Documents",
            "Screening",
            "KYC Form",
            "Risk Assessment",
            "Ownership",
        ]

        # Wait for the required tabs to become available.
        for tab_name in expected_tabs:
            expect(
                self.main_tabs.filter(
                    has_text=re.compile(
                        rf"^\s*{re.escape(tab_name)}\s*$"
                    )
                )
            ).to_be_visible(timeout=15000)

        actual_tabs = [
            name.strip()
            for name in self.main_tabs.all_inner_texts()
        ]

        print(
            f"Entity tabs ({len(actual_tabs)}): {actual_tabs}",
            flush=True
        )

        unexpected_tabs = [
            name for name in actual_tabs
            if name not in expected_tabs
        ]

        if unexpected_tabs:
            print(
                f"Additional entity tabs detected: {unexpected_tabs}",
                flush=True
            )

    def verify_main_navigation(self):
        self.verify_page_loaded()
        for name, icon_class in self.MAIN_TAB_ICONS.items():
            tab = self.main_tab(name)
            expect(tab).to_be_visible()
            expect(tab.locator(f"i.{icon_class}")).to_have_count(1)

    def open_main_tab(self, name: str):
        tab = self.main_tab(name)
        tab.click()
        expect(tab).to_have_class(re.compile(r"(?:^|\s)active(?:\s|$)"))
        return tab
