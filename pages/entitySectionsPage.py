
import re

from playwright.sync_api import Page, expect
from pages.entityOnboardingPage import EntityOnboardingPage


class EntitySectionsPage(EntityOnboardingPage):

    RISK_OPTIONS = {
        "Country / Jurisdiction Risk": ("low", "other", "high"),
        "Politically Exposed Person (PEP) Involvement": (
            "notPep", "stateOwned", "pepIdentified"
        ),
        "Entity Legal Form / Type": ("low", "medium", "high"),
        "Transfer of Funds": ("bankTransfer", "cash"),
        "Adverse Media": ("noHits", "confirmed"),
    }

    KYC_FIELDS = (
        "Full Legal Name (as per Trade license / CR)",
        "Entity Legal Form / Type",
        "Country of Incorporation",
        "Incorporated Date",
        "Incorporation Number",
        "Contact Number",
        "Email",
        "Home Country or Permanent Address",
        "Annual Business Turnover (AUD)",
        "Nature of Business",
        "Source of Funds (SOF)",
    )

    CONNECTED_PARTY_COLUMNS = (
        "Full Name",
        "Client Type",
        "Client ID",
        "Date of Birth (DD/MM/YY)",
        "Nationality / Country of incorporation",
        "Position / Role in Entity",
        "Share %",
        "Client Verification",
        "Action",
    )

    OWNERSHIP_CHART_COLUMNS = (
        "Profile ID",
        "Name",
        "Type",
        "Nationality",
        "Ownership",
        "Role",
        "Ownership Percentage",
    )

    def __init__(self, page: Page):
        super().__init__(page)

        # Screening
        self.screening_name = page.locator('input[name="name"]')
        self.screening_organization = page.locator(
            'input[name="entityType"][value="O"]'
        )
        self.screening_individual = page.locator(
            'input[name="entityType"][value="P"]'
        )
        self.screening_ongoing = page.locator(
            'input[name="ongoing"]'
        )
        self.screening_history = page.locator(".screen-history")

        # KYC
        self.kyc_form = page.locator(".custom-form.my-5")
        self.kyc_heading = page.locator(
            "h4.secondary-title"
        ).filter(
            has_text="KNOW YOUR CUSTOMER (KYC) FORM - ENTITY"
        )
        self.kyc_client_id = page.locator(
            "h4.secondary-title"
        ).filter(
            has_text=re.compile(r"^\s*Client ID:")
        )
        self.kyc_table = page.locator("table").filter(
            has=page.get_by_role(
                "columnheader",
                name="Full Name",
                exact=True
            )
        )

        # Risk Assessment
        self.risk_title = page.locator(
            "h4.secondary-title"
        ).filter(has_text="Risk Assessment - Entity")

        self.risk_tables = page.locator(
            "table.signature-table"
        )

        self.risk_total_score = (
            self.risk_tables.first
            .locator("tbody tr")
            .filter(has_text="Total Score")
            .locator("td")
            .last
        )

        self.risk_classification = page.get_by_text(
            re.compile(
                r"^Risk Classification:\s*(Low|Medium|High)$"
            )
        )

        # Ownership
        self.profile_search = page.get_by_placeholder(
            "Search by profile name",
            exact=True
        )
        self.ownership_client_id = page.locator(
            'input[name="clientId"]'
        )
        self.ownership_entity_name = page.locator(
            'input[name="entityName"]'
        )
        self.profile_add = page.locator(".profile-add")
        self.profile_cards = page.locator(".profile-card")

        self.structure_canvas = page.locator(
            ".react-transform-component .reactOrgChart"
        )
        self.structure_controls = page.locator(
            ".control-tools"
        )
        self.ownership_chart = page.locator("#chart-pdf")

    # Common nested navigation
    def subtab(self, name: str):
        return self.page.locator(
            ".onboarding-page .tab-z-option"
        ).filter(
            has=self.page.locator("label").filter(
                has_text=re.compile(
                    rf"^\s*{re.escape(name)}\s*$"
                )
            )
        )

    def open_subtab(self, name: str):
        tab = self.subtab(name)

        expect(tab).to_have_count(1)
        tab.click()

        expect(tab).to_have_class(
            re.compile(r"(?:^|\s)active(?:\s|$)")
        )
        return tab

    # Screening
    def open_screening(self):
        self.open_main_tab("Screening")
        expect(
            self.subtab("Single Screening")
        ).to_be_visible(timeout=15000)

    # KYC
    def open_kyc(self):
        self.open_main_tab("KYC Form")
        expect(
            self.kyc_heading
        ).to_be_visible(timeout=15000)

    # Risk Assessment
    def open_risk(self):
        self.open_main_tab("Risk Assessment")
        expect(
            self.risk_title
        ).to_be_visible(timeout=15000)

    def risk_group(self, title: str):
        return self.page.locator(".border-box").filter(
            has=self.page.locator(
                ".border-box-label"
            ).filter(
                has_text=re.compile(
                    rf"^\s*{re.escape(title)}\s*$"
                )
            )
        )

    # Ownership
    def open_ownership(self, subtab="Profiles"):
        self.open_main_tab("Ownership")
        return self.open_subtab(subtab)

    def create_profile_modal(self):
        return self.page.locator(
            ".modal-z:visible"
        ).filter(
            has=self.page.locator(
                ".modal-z-title"
            ).filter(has_text="Create Profile")
        )

    def open_create_profile(self):
        self.open_ownership("Profiles")

        expect(self.profile_add).to_be_visible()
        self.profile_add.click()

        modal = self.create_profile_modal()
        expect(modal).to_be_visible(timeout=10000)

        return modal
