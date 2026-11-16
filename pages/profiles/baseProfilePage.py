
import re

from playwright.sync_api import Page, expect


class BaseProfilePage:
    """Shared navigation for Individual and Entity profiles."""

    def __init__(self, page: Page):
        self.page = page

    def tab(self, name: str):
        return self.page.locator(".tab-z-option").filter(
            has=self.page.locator(
                "label",
                has_text=re.compile(
                    rf"^\s*{re.escape(name)}\s*$"
                )
            )
        ).first

    def open_tab(self, name: str):
        tab = self.tab(name)

        expect(tab).to_be_visible(timeout=15000)
        tab.click()

        expect(tab).to_have_class(
            re.compile(r"\bactive\b")
        )

    def go_back(self):
        back_button = self.page.locator(
            "button.back-link"
        ).first

        expect(back_button).to_be_visible()
        back_button.click()
