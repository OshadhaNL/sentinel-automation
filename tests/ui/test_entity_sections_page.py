
import os
import re
from urllib.parse import quote, urlsplit

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.entitySectionsPage import EntitySectionsPage


class _EntitySetup:

    @pytest.fixture(autouse=True)
    def open_entity(self, page: Page, base_url: str):

        client_id = os.getenv(
            "TEST_ENTITY_CLIENT_ID", ""
        ).strip()

        if not client_id:
            pytest.skip(
                "Set TEST_ENTITY_CLIENT_ID to an existing QA entity"
            )

        email = os.getenv("TEST_EMAIL", "").strip()
        password = os.getenv("TEST_PASSWORD", "")

        assert email, "Set TEST_EMAIL"
        assert password, "Set TEST_PASSWORD"

        login = LoginPage(page)
        login.open(base_url)
        login.enter_email(email)
        login.enter_password(password)
        login.click_login()

        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$"),
            timeout=45000
        )

        parsed = urlsplit(base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"

        entity_url = (
            f"{origin}/nolimit/app/onboarding/entity/process"
            f"?step=documents&client={quote(client_id, safe='')}"
        )

        page.goto(
            entity_url,
            wait_until="domcontentloaded"
        )

        self.entity = EntitySectionsPage(page)
        self.entity.verify_page_loaded()

        expect(
            self.entity.reference_id
        ).to_have_text(
            client_id,
            timeout=15000
        )

        self.page = page
        self.client_id = client_id


# ============================================================
# SCREENING
# ============================================================

@pytest.mark.ui
class TestEntityScreening(_EntitySetup):

    def test_screening_tabs(self):
        self.entity.open_screening()

        for name in ("Single Screening", "Daily Screening"):
            expect(
                self.entity.subtab(name)
            ).to_be_visible()

        self.entity.open_subtab("Daily Screening")
        self.entity.open_subtab("Single Screening")

    def test_organization_is_selected(self):
        self.entity.open_screening()

        expect(
            self.entity.screening_organization
        ).to_be_checked()

        expect(
            self.entity.screening_individual
        ).not_to_be_checked()

    def test_organization_name_field(self):
        self.entity.open_screening()

        expect(
            self.page.get_by_placeholder(
                "Enter organisation name",
                exact=True
            )
        ).to_be_visible()

    def test_registered_country_selector(self):
        self.entity.open_screening()

        expect(
            self.page.locator(".ant-select").first
        ).to_be_visible()

    def test_analyze_action_available(self):
        self.entity.open_screening()

        expect(
            self.page.get_by_role(
                "button",
                name=re.compile(r"Analyze\s*$")
            )
        ).to_be_visible()

    def test_ongoing_screening_checkbox(self):
        self.entity.open_screening()

        expect(
            self.entity.screening_ongoing
        ).to_have_count(1)

    def test_connected_party_and_history(self):
        self.entity.open_screening()

        expect(
            self.page.get_by_role(
                "heading",
                name="Connected Party",
                exact=True
            )
        ).to_be_visible()

        expect(
            self.entity.screening_history
        ).to_be_visible()


# ============================================================
# KYC FORM
# ============================================================

@pytest.mark.ui
class TestEntityKYC(_EntitySetup):

    def test_kyc_heading_and_client_id(self):
        self.entity.open_kyc()

        expect(
            self.entity.kyc_client_id
        ).to_contain_text(self.client_id)

    def test_kyc_sections(self):
        self.entity.open_kyc()

        sections = (
            "SECTION 01 - KYC PROFILE OF THE CLIENT",
            "SECTION 2 - Connected Parties",
        )

        for name in sections:
            expect(
                self.page.get_by_role(
                    "heading",
                    name=name
                )
            ).to_be_visible()

    def test_kyc_field_labels(self):
        self.entity.open_kyc()

        for label in self.entity.KYC_FIELDS:
            locator = self.entity.kyc_form.locator(
                "label"
            ).filter(
                has_text=re.compile(
                    rf"^\s*{re.escape(label)}\s*$"
                )
            )

            expect(locator).to_be_visible()

    def test_kyc_text_inputs(self):
        self.entity.open_kyc()

        placeholders = (
            "Enter legal name",
            "Select incorporated date",
            "Enter incorporation number",
            "Enter contact number",
            "Enter email address",
            "Enter AUD",
        )

        for placeholder in placeholders:
            expect(
                self.page.get_by_placeholder(
                    placeholder,
                    exact=True
                )
            ).to_be_visible()

    def test_kyc_textareas(self):
        self.entity.open_kyc()

        expect(
            self.page.get_by_placeholder(
                "Enter the address here...",
                exact=True
            )
        ).to_be_visible()

        expect(
            self.entity.kyc_form.locator(
                'textarea[placeholder="Type here..."]'
            )
        ).to_have_count(2)

    def test_kyc_dropdowns(self):
        self.entity.open_kyc()

        expect(
            self.entity.kyc_form.locator(".ant-select")
        ).to_have_count(2)

    def test_connected_party_table_columns(self):
        self.entity.open_kyc()

        table = self.entity.kyc_table
        expect(table).to_be_visible()

        for heading in self.entity.CONNECTED_PARTY_COLUMNS:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=heading,
                    exact=True
                ).first
            ).to_be_visible()

    def test_kyc_buttons_without_submitting(self):
        self.entity.open_kyc()

        expect(
            self.page.get_by_role(
                "button",
                name=re.compile(r"Add parent party\s*$", re.I)
            )
        ).to_be_visible()

        expect(
            self.page.get_by_role(
                "button",
                name="Save",
                exact=True
            )
        ).to_be_visible()
# ============================================================
# RISK ASSESSMENT
# ============================================================

@pytest.mark.ui
class TestEntityRiskAssessment(_EntitySetup):

    def test_risk_heading_and_client_id(self):
        self.entity.open_risk()

        client_heading = self.page.locator(
            "h4.secondary-title"
        ).filter(
            has_text=re.compile(r"^\s*Client ID:")
        )

        expect(
            client_heading
        ).to_contain_text(self.client_id)

    def test_five_risk_groups_and_options(self):
        self.entity.open_risk()

        for title, options in self.entity.RISK_OPTIONS.items():

            group = self.entity.risk_group(title)
            expect(group).to_be_visible()

            for value in options:
                expect(
                    group.locator(
                        f'input[type="radio"][value="{value}"]'
                    )
                ).to_have_count(1)

            expect(
                group.locator('input[type="radio"]')
            ).to_have_count(len(options))

    def test_risk_radio_groups_are_independent(self):
        self.entity.open_risk()

        names = []

        for title in self.entity.RISK_OPTIONS:
            radios = self.entity.risk_group(
                title
            ).locator('input[type="radio"]')

            group_names = radios.evaluate_all(
                "(nodes) => [...new Set(nodes.map(n => n.name))]"
            )

            assert len(group_names) == 1, (
                f"{title} has mixed radio names"
            )

            names.append(group_names[0])

        assert len(set(names)) == 5, (
            "Different risk factors share a radio group"
        )

    def test_risk_summary_headers(self):
        self.entity.open_risk()

        expect(
            self.page.get_by_role(
                "heading",
                name="Risk Assessment Summary"
            )
        ).to_be_visible()

        for header in (
            "Risk Factor",
            "Attribute",
            "Risk Score"
        ):
            expect(
                self.entity.risk_tables.first.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True
                )
            ).to_be_visible()

    def test_risk_rating_ranges(self):
        self.entity.open_risk()

        rating_table = self.entity.risk_tables.nth(1)

        expect(rating_table).to_contain_text(
            "16 and above"
        )
        expect(rating_table).to_contain_text(
            "6 to 15"
        )
        expect(rating_table).to_contain_text(
            "0 to 5"
        )

    def test_risk_classification_matches_score(self):
        self.entity.open_risk()

        score_text = (
            self.entity.risk_total_score.inner_text()
        )

        score = int(score_text.strip())

        expected = (
            "Low" if score <= 5
            else "Medium" if score <= 15
            else "High"
        )

        expect(
            self.entity.risk_classification
        ).to_contain_text(expected)

    def test_complete_onboarding_button_visible_only(self):
        self.entity.open_risk()

        expect(
            self.page.get_by_role(
                "button",
                name="Complete Onboarding",
                exact=True
            )
        ).to_be_visible()


# ============================================================
# OWNERSHIP
# ============================================================

@pytest.mark.ui
class TestEntityOwnership(_EntitySetup):

    def test_ownership_subnavigation(self):
        self.entity.open_main_tab("Ownership")

        for name in (
            "Profiles",
            "Ownership Structure",
            "Ownership Chart"
        ):
            expect(
                self.entity.subtab(name)
            ).to_be_visible()

            self.entity.open_subtab(name)

    def test_profile_search_field(self):
        self.entity.open_ownership()

        expect(
            self.entity.profile_search
        ).to_be_visible()

        self.entity.profile_search.fill(
            "qa-nonexistent-profile"
        )

        expect(
            self.entity.profile_search
        ).to_have_value("qa-nonexistent-profile")

        self.entity.profile_search.fill("")

        expect(
            self.entity.profile_search
        ).to_have_value("")

    def test_client_id_read_only(self):
        self.entity.open_ownership()

        expect(
            self.entity.ownership_client_id
        ).to_have_value(self.client_id)

        expect(
            self.entity.ownership_client_id
        ).to_be_disabled()

    def test_entity_name_and_update_action(self):
        self.entity.open_ownership()

        expect(
            self.entity.ownership_entity_name
        ).to_be_visible()

        expect(
            self.page.get_by_role(
                "button",
                name=re.compile(r"Update\s*$")
            )
        ).to_be_visible()


    def test_add_profile_modal_opens_and_cancels(self):
        modal = self.entity.open_create_profile()

        expect(
            modal.locator('input[name="profileId"]')
        ).to_be_visible()

        expect(
            modal.locator('input[name="shares"]')
        ).to_be_visible()

        expect(
            modal.locator('input[name="percentage"]')
        ).to_be_visible()

        dropdowns = modal.locator(".ant-select")

        assert dropdowns.count() >= 3, (
            "Expected at least 3 dropdowns in Create Profile modal"
        )

        for role in ("director", "signatory"):
            expect(
                modal.locator(
                    f'input[name="roles"][value="{role}"]'
                )
            ).to_have_count(1)

        expect(
            modal.get_by_role(
                "button",
                name="Save",
                exact=True
            )
        ).to_be_visible()

        modal.get_by_role(
            "button",
            name="Cancel",
            exact=True
        ).click()

        expect(modal).not_to_be_visible()

    def test_existing_profiles_if_any(self):
        self.entity.open_ownership()

        expect(
            self.entity.profile_add
        ).to_be_visible()

        cards = self.entity.profile_cards

        if cards.count() > 0:
            expect(cards.first).to_be_visible()

    def test_ownership_structure_canvas(self):
        self.entity.open_ownership(
            "Ownership Structure"
        )

        expect(
            self.entity.structure_canvas
        ).to_be_visible(timeout=15000)

    def test_ownership_structure_controls(self):
        self.entity.open_ownership(
            "Ownership Structure"
        )

        icons = (
            "fa-search-plus",
            "fa-search-minus",
            "fa-times-circle",
            "fa-compress"
        )

        for icon in icons:
            expect(
                self.entity.structure_controls.locator(
                    f"button:has(i.{icon})"
                )
            ).to_be_visible()

    def test_ownership_chart_search_and_exports(self):
        self.entity.open_ownership(
            "Ownership Chart"
        )

        expect(
            self.page.get_by_placeholder(
                "Search by client ID or name",
                exact=True
            )
        ).to_be_visible()

        for label in ("Download CSV", "Download PDF"):
            expect(
                self.entity.ownership_chart.locator(
                    f'button:has(img[alt="{label}"])'
                )
            ).to_be_visible()

    def test_ownership_chart_columns(self):
        self.entity.open_ownership(
            "Ownership Chart"
        )

        table = self.entity.ownership_chart.locator(
            ".table-scroll-wrapper table"
        )

        expect(table).to_be_visible()

        for heading in self.entity.OWNERSHIP_CHART_COLUMNS:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=heading,
                    exact=True
                )
            ).to_be_visible()
