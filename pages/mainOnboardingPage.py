
import re
import time

from playwright.sync_api import expect


ROLES = [
    "Seller",
    "Buyer",
    "Lessor",
    "Lessee",
    "Director",
    "Trustee",
    "Beneficial Owner",
    "Solicitor / Power of Attorney",
]

CONSENT_ITEMS = [
    "Identity verification using government-issued identification documents;",
    "Facial biometric verification and facial matching procedures;",
    "Background verification and due diligence checks;",
    "Name screening against sanctions lists, watchlists, politically exposed persons (PEP) databases, adverse media, and other regulatory or compliance databases;",
    "Verification of information provided by me through third-party sources where legally permitted;",
    "Secure storage and retention of my personal data, documents, and verification results in accordance with applicable laws, regulations, and internal compliance requirements.",
]

CONSENT_INTRO = (
    "I understand and agree that the organization may conduct "
    "the following checks and processes as part of its onboarding, "
    "compliance, and risk assessment procedures:"
)

CONSENT_ACK = (
    'I acknowledge that I have read and understood the information '
    'provided above. By clicking "I Agree", I confirm my consent '
    'to the collection, processing, and use of my information in '
    'accordance with the stated terms and conditions.'
)


class MainOnboardingPage:

    def __init__(self, page):
        self.page = page

        # Main page
        self.heading = page.get_by_role(
            "heading", name="Onboarding", exact=True
        )

        self.description = page.get_by_text(
            "Begin onboarding by choosing the appropriate client type below.",
            exact=True,
        )

        self.new_tab = page.locator(
            ".tab-z-option"
        ).filter(has_text="New Onboarding")

        self.pending_tab = page.locator(
            ".tab-z-option"
        ).filter(has_text="Pending Onboarding")

        # New onboarding
        self.name = page.get_by_placeholder(
            "Enter client name", exact=True
        )

        self.individual = page.locator(
            ".onboarding-select-card"
        ).filter(
            has=page.get_by_role(
                "heading",
                name="Onboard Individual",
                exact=True,
            )
        )

        self.entity = page.locator(
            ".onboarding-select-card"
        ).filter(
            has=page.get_by_role(
                "heading",
                name="Onboard Entity",
                exact=True,
            )
        )

        self.proceed = page.get_by_role(
            "button", name="Proceed", exact=True
        )

        # Pending onboarding
        self.search = page.get_by_placeholder(
            "Search by Reference ID or Client name",
            exact=True,
        )

        self.search_button = page.locator(
            ".search-box-z button.search-btn"
        )

        self.clear_button = page.locator(
            ".search-box-z button.clear-btn"
        )

        self.table = page.locator(
            ".ant-table-container table"
        )

        self.rows = self.table.locator(
            "tbody tr.ant-table-row"
        )

        self.pagination = page.locator(
            ".ant-pagination"
        )

        self.page_size = page.locator(
            ".ant-pagination-options-size-changer"
        )

        # Consent popup
        self.consent = page.locator(
            ".modal-z-card:visible"
        ).filter(
            has=page.locator(
                ".modal-z-title h6",
                has_text="Consent Letter",
            )
        )

        # Existing client popup
        self.existing = page.locator(
            ".modal-z-card:visible"
        ).filter(
            has=page.locator(
                ".modal-z-title h6",
                has_text="Existing Client Information",
            )
        )

    # ============================================================
    # MAIN PAGE NAVIGATION
    # ============================================================

    def open_pending(self):
        self.pending_tab.click()
        expect(self.search).to_be_visible()

    def open_new(self):
        self.new_tab.click()
        expect(self.name).to_be_visible()

    # ============================================================
    # CLIENT SELECTION
    # ============================================================

    def choose_client(self, kind, name):
        self.name.fill(name)

        card = (
            self.individual
            if kind == "individual"
            else self.entity
        )

        card.click()

        expect(card).to_have_class(
            re.compile(r"\bactive\b")
        )

    def role_dropdown(self, kind):
        placeholder = (
            "Select client role"
            if kind == "individual"
            else "Select customer role"
        )

        return self.page.locator(
            ".ant-select"
        ).filter(
            has=self.page.locator(
                ".ant-select-selection-placeholder",
                has_text=placeholder,
            )
        ).first

    def select_role(self, kind, role):
        dropdown = self.role_dropdown(kind)

        dropdown.click()

        option = self.page.locator(
            ".ant-select-dropdown:visible "
            ".ant-select-item-option"
        ).filter(
            has=self.page.locator(
                ".ant-select-item-option-content"
            ).get_by_text(role, exact=True)
        )

        expect(option).to_be_visible()
        option.click()

        # Placeholder disappears after selecting a role.
        selected = self.page.locator(
            ".ant-select-selection-item"
        ).filter(has_text=role)

        expect(selected).to_be_visible()

    def client_role_label(self, kind):
        label = (
            "Client Role"
            if kind == "individual"
            else "Customer Role"
        )

        return self.page.get_by_text(
            label, exact=True
        )

    def assert_proceed_disabled_before_role(self, kind):
        expect(self.proceed).to_be_visible()

        if self.proceed.is_enabled():
            selected = self.page.locator(
                ".ant-select-selection-item"
            ).all_inner_texts()

            raise AssertionError(
                f"{kind.title()} Proceed is ENABLED before "
                f"selecting a role. Selected values: {selected!r}. "
                "This violates the expected role-validation behavior."
            )

        expect(self.proceed).to_be_disabled()

    # ============================================================
    # CONSENT LETTER
    # ============================================================

    def open_consent(self, kind, name, role="Seller"):
        self.choose_client(kind, name)

        self.select_role(kind, role)

        expect(self.proceed).to_be_enabled()
        self.proceed.click()

        expect(self.consent).to_be_visible()

    def consent_title(self):
        return self.consent.locator(
            ".modal-z-title h6"
        )

    def consent_checkbox(self):
        return self.consent.locator(
            "input.ant-checkbox-input"
        )

    def consent_agree(self):
        return self.consent.get_by_role(
            "button",
            name="I Agree",
            exact=True,
        )

    def consent_cancel(self):
        return self.consent.get_by_role(
            "button",
            name="Cancel",
            exact=True,
        )

    def consent_close(self):
        return self.consent.locator(
            "button.modal-z-close"
        )

    # ============================================================
    # EXISTING CLIENT POPUP
    # ============================================================

    def existing_title(self):
        return self.existing.locator(
            ".modal-z-title h6"
        )

    def existing_close(self):
        return self.existing.locator(
            "button.modal-z-close"
        )

    def existing_okay(self):
        return self.existing.get_by_role(
            "button",
            name="Okay",
            exact=True,
        )

    def existing_value(self, label):
        row = self.existing.locator(
            ".grid"
        ).filter(
            has=self.page.get_by_text(
                label, exact=True
            )
        ).first

        return row.locator("span").last

    def start_existing_flow(self, kind, name):
        self.choose_client(kind, name)

        self.select_role(kind, "Seller")

        self.proceed.click()

        expect(self.existing).to_be_visible()

    def return_to_onboarding(self):
        base = self.page.url.split(
            "/nolimit/app/"
        )[0]

        self.page.goto(
            base + "/nolimit/app/onboarding"
        )

        expect(self.heading).to_be_visible()

    # ============================================================
    # PENDING ONBOARDING - SEARCH AND PAGINATION
    # ============================================================

    def row_ids(self):
        return [
            value.strip()
            for value in self.rows.locator(
                "td:first-child"
            ).all_inner_texts()
        ]

    def page_size_select(self, size):
        self.page_size.click()

        option = self.page.locator(
            ".ant-select-dropdown:visible "
            f'.ant-select-item-option[title="{size} / page"]'
        )

        option.click()

        expect(
            self.page_size.locator(
                ".ant-select-selection-item"
            )
        ).to_have_text(
            f"{size} / page"
        )

    def wait_for_reference_search(
        self, reference_id, timeout_ms=15000
    ):
        deadline = (
            time.monotonic()
            + timeout_ms / 1000
        )

        actual = []

        while time.monotonic() < deadline:
            actual = self.row_ids()

            if actual and all(
                reference_id.lower() in item.lower()
                for item in actual
            ):
                return actual

            self.page.wait_for_timeout(250)

        raise AssertionError(
            f"Pending search for {reference_id!r} "
            f"did not filter within {timeout_ms}ms. "
            f"Visible IDs: {actual!r}"
        )

    # ============================================================
    # ANALYST DROPDOWN
    # FULL PAGE RELOAD BEFORE OPENING OPTIONS
    # ============================================================

    def analyst_filter(self):
        return self.page.locator(
            ".ant-select"
        ).filter(
            has=self.page.locator(
                ".ant-select-selection-placeholder",
                has_text="Filter by Analyst",
            )
        ).first

    def analyst_options(self):
        return self.page.locator(
            ".ant-select-dropdown:visible "
            ".ant-select-item-option"
        )

    def reload_before_analyst_selection(self):
        """
        Reload the entire Onboarding page.

        After reload:
        - Wait for the main page
        - Open Pending Onboarding
        - Wait for table and analyst dropdown
        """

        self.page.reload(
            wait_until="domcontentloaded",
            timeout=30000,
        )

        expect(
            self.heading
        ).to_be_visible(timeout=15000)

        # The tab may reset to New Onboarding.
        # Open Pending Onboarding after every reload.
        self.open_pending()

        expect(
            self.table
        ).to_be_visible(timeout=15000)

        expect(
            self.analyst_filter()
        ).to_be_visible(timeout=15000)

    def wait_for_analyst_options(
        self, timeout_ms=15000
    ):
        """
        Reload the full page before opening the analyst
        dropdown and waiting for options.
        """

        # Step 1: Reload the full browser page.
        self.reload_before_analyst_selection()

        # Step 2: Locate the analyst dropdown again.
        dropdown = self.analyst_filter()

        expect(dropdown).to_be_visible(
            timeout=15000
        )

        # Step 3: Open the dropdown.
        dropdown.click()

        # Step 4: Wait for analyst options.
        options = self.analyst_options()

        try:
            expect(options.first).to_be_visible(
                timeout=timeout_ms
            )

        except AssertionError:
            empty = self.page.locator(
                ".ant-select-dropdown:visible "
                ".ant-empty-description"
            ).filter(
                has_text=re.compile(r"^No data$")
            ).first

            if (
                empty.count() > 0
                and empty.is_visible()
            ):
                raise AssertionError(
                    "Analyst dropdown still displays "
                    "'No data' after a full page reload. "
                    "Check the analyst data API or "
                    "application permissions."
                ) from None

            raise

        return options

    def select_analyst(self, analyst_name):
        """
        Reload the full page, open Pending Onboarding,
        wait for options, then select the analyst.
        """

        # This method performs the reload internally.
        self.wait_for_analyst_options()

        option = self.analyst_options().filter(
            has=self.page.locator(
                ".ant-select-item-option-content"
            ).get_by_text(
                analyst_name,
                exact=True,
            )
        )

        expect(option).to_be_visible(
            timeout=10000
        )

        option.click()

        # Confirm that the dropdown closes.
        expect(
            self.page.locator(
                ".ant-select-dropdown:visible"
            )
        ).to_have_count(
            0, timeout=10000
        )

    def created_by_values(self):
        return [
            value.strip()
            for value in self.rows.locator(
                "td:nth-child(7)"
            ).all_inner_texts()
        ]

    # ============================================================
    # APPEARANCE AND NOTIFICATIONS
    # ============================================================

    def computed_appearance(self, locator):
        return locator.evaluate(
            """el => {
                const s = getComputedStyle(el);
                return [
                    s.backgroundColor,
                    s.backgroundImage,
                    s.color,
                    s.borderColor
                ].join('|');
            }"""
        )

    def name_required_notification(self):
        return self.page.locator(
            ".ant-notification-notice"
        ).filter(
            has_text="Client name is required"
        )
