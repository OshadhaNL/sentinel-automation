"""Deterministic client-reuse navigation for the Sentinel QA automation suite.

Phase 1 proof of concept. Extends the existing MainOnboardingPage without
changing any existing page objects, tests, or fixture scopes.
"""

import re
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect
from pages.mainOnboardingPage import MainOnboardingPage


class ClientReusePage(MainOnboardingPage):
    def reopen_pending_individual(self, reference_id: str) -> str:
        """Open a pending Individual by exact Reference ID, not table position.

        Raises a clear assertion when the record is no longer in Pending.
        If that happens, later stages may need to reopen it from Profiles.
        """
        if not re.fullmatch(r"SENTINEL[A-Za-z0-9]+", reference_id):
            raise ValueError(f"Invalid client reference ID: {reference_id!r}")

        self.return_to_onboarding()
        self.open_pending()
        expect(self.table).to_be_visible(timeout=20000)

        # Explicit search avoids selecting somebody else's newest row.
        self.search.fill(reference_id)
        self.search_button.click()
        self.wait_for_reference_search(reference_id, timeout_ms=30000)

        exact_link = self.page.locator(
            "td:first-child a.table-link"
        ).filter(
            has_text=re.compile(rf"^\s*{re.escape(reference_id)}\s*$")
        )
        matching_rows = self.rows.filter(has=exact_link)
        expect(matching_rows).to_have_count(1, timeout=20000)
        row = matching_rows.first
        expect(row).to_be_visible()

        actual_reference = row.locator("td").nth(0).inner_text().strip()
        actual_type = row.locator("td").nth(2).inner_text().strip()
        assert actual_reference == reference_id, (
            f"Wrong pending record: {actual_reference!r} != {reference_id!r}"
        )
        assert actual_type.casefold() == "individual", (
            f"Reference {reference_id} is {actual_type!r}, not Individual"
        )

        # The extracted identity may replace the original name. ID is stable.
        link = row.locator("td:first-child a.table-link")
        href = link.get_attribute("href")
        assert href, f"Pending record {reference_id} has no link"
        parsed = urlsplit(href)
        assert (
            parsed.path.endswith("/onboarding/individual/process")
            and parse_qs(parsed.query).get("client") == [reference_id]
        ), f"Unexpected pending record link: {href!r}"

        link.click()
        self.page.wait_for_url(
            lambda url: (
                urlsplit(str(url)).path.endswith(
                    "/onboarding/individual/process"
                )
                and parse_qs(urlsplit(str(url)).query).get("client")
                == [reference_id]
            ),
            timeout=30000,
        )
        expect(
            self.page.get_by_role(
                "heading", name="Individual Onboarding", exact=True
            )
        ).to_be_visible(timeout=20000)

        print(f"Reopened exact Pending Individual: {reference_id}")
        return reference_id
