import os
import re
import random
import string

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.onboardingPage import OnboardingPage


def generate_random_client_name(prefix: str) -> str:
    """Generate a client name with a random alphabetic suffix."""
    suffix = "".join(
        random.choices(string.ascii_uppercase, k=8)
    )
    return f"{prefix} {suffix}"


@pytest.mark.ui
class TestOnboarding:

    @pytest.fixture(autouse=True)
    def setup_onboarding(self, page: Page, base_url: str):
        self.page = page

        # Get login credentials from environment variables.
        test_email = os.getenv("TEST_EMAIL")
        test_password = os.getenv("TEST_PASSWORD")

        assert test_email, (
            "Please set the TEST_EMAIL environment variable."
        )
        assert test_password, (
            "Please set the TEST_PASSWORD environment variable."
        )

        # Login
        self.login_page = LoginPage(page)
        self.login_page.open(base_url)
        self.login_page.enter_email(test_email)
        self.login_page.enter_password(test_password)
        self.login_page.click_login()

        # Verify successful login
        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$")
        )

        # Navigate to Onboarding
        page.get_by_role(
            "link", name="Onboarding", exact=False
        ).click()

        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/onboarding/?$")
        )

        self.onboarding = OnboardingPage(page)

    # --------------------------------------------------
    # Shared workflow - Individual
    # --------------------------------------------------

    def prepare_individual_onboarding(self):
        self.client_name = generate_random_client_name(
            "Test Individual"
        )

        self.onboarding.enter_client_name(self.client_name)
        self.onboarding.verify_client_name_value(
            self.client_name
        )

        self.onboarding.select_individual_onboarding()

        self.onboarding.verify_client_role_label()
        self.onboarding.verify_client_role_dropdown()

    def prepare_consent_letter(self):
        self.prepare_individual_onboarding()

        self.onboarding.select_client_role("Seller")
        self.onboarding.verify_selected_client_role("Seller")
        self.onboarding.verify_proceed_button_enabled()

        self.onboarding.click_proceed()
        self.onboarding.verify_consent_popup_visible()

    # --------------------------------------------------
    # Main Onboarding page
    # --------------------------------------------------

    def test_onboarding_heading_is_visible(self):
        self.onboarding.verify_onboarding_heading()

    def test_onboarding_description_is_visible(self):
        self.onboarding.verify_onboarding_description()

    def test_new_onboarding_phase_is_visible(self):
        self.onboarding.verify_new_onboarding_phase()

    def test_pending_onboarding_phase_is_visible(self):
        self.onboarding.verify_pending_onboarding_phase()

    def test_client_name_field_is_visible(self):
        self.onboarding.verify_client_name_field()

    def test_client_type_heading_is_visible(self):
        self.onboarding.verify_client_type_heading()

    def test_individual_card_is_visible(self):
        self.onboarding.verify_individual_card()

    def test_entity_card_is_visible(self):
        self.onboarding.verify_entity_card()

    # --------------------------------------------------
    # Individual onboarding and client role
    # --------------------------------------------------

    def test_individual_shows_client_role_dropdown(self):
        self.prepare_individual_onboarding()

    def test_proceed_is_disabled_before_role_selection(self):
        self.prepare_individual_onboarding()
        self.onboarding.verify_proceed_button_initially_disabled()

    def test_all_client_role_options_are_visible(self):
        self.prepare_individual_onboarding()
        self.onboarding.verify_all_client_role_options()

    @pytest.mark.parametrize(
        "role",
        [
            "Seller",
            "Buyer",
            "Lessor",
            "Lessee",
            "Director",
            "Trustee",
            "Beneficial Owner",
            "Solicitor / Power of Attorney",
        ],
    )
    def test_select_role_enables_proceed(self, role):
        self.prepare_individual_onboarding()

        self.onboarding.verify_proceed_button_initially_disabled()

        self.onboarding.select_client_role(role)
        self.onboarding.verify_selected_client_role(role)
        self.onboarding.verify_proceed_button_enabled()

    # --------------------------------------------------
    # Consent Letter content - Individual
    # --------------------------------------------------

    def test_consent_letter_title_is_visible(self):
        self.prepare_consent_letter()
        self.onboarding.verify_consent_title()

    def test_consent_letter_intro_is_visible(self):
        self.prepare_consent_letter()
        self.onboarding.verify_consent_intro()

    def test_all_consent_statements_are_visible(self):
        self.prepare_consent_letter()
        self.onboarding.verify_all_consent_items()

    def test_acknowledgement_text_is_visible(self):
        self.prepare_consent_letter()
        self.onboarding.verify_acknowledgement_text()

    def test_consent_checkbox_is_initially_unchecked(self):
        self.prepare_consent_letter()
        self.onboarding.verify_consent_checkbox_visible()
        self.onboarding.verify_consent_checkbox_unchecked()

    def test_agree_button_is_initially_disabled(self):
        self.prepare_consent_letter()
        self.onboarding.verify_agree_button_disabled()

    def test_cancel_button_is_visible(self):
        self.prepare_consent_letter()
        self.onboarding.verify_cancel_button_visible()

    # --------------------------------------------------
    # Consent acceptance and cancellation - Individual
    # --------------------------------------------------

    def test_checking_checkbox_enables_agree(self):
        self.prepare_consent_letter()

        self.onboarding.check_consent_checkbox()
        self.onboarding.verify_consent_checkbox_checked()
        self.onboarding.verify_agree_button_enabled()

    def test_cancel_closes_consent_popup(self):
        self.prepare_consent_letter()

        self.onboarding.click_cancel()
        self.onboarding.verify_consent_popup_closed()

    def test_agree_accepts_consent(self):
        self.prepare_consent_letter()

        self.onboarding.check_consent_checkbox()
        self.onboarding.verify_consent_checkbox_checked()
        self.onboarding.verify_agree_button_enabled()

        self.onboarding.click_agree()
        self.onboarding.verify_consent_popup_closed()

    # --------------------------------------------------
    # Shared workflow - Entity
    # --------------------------------------------------

    def prepare_entity_onboarding(self):
        self.client_name = generate_random_client_name(
            "Test Entity"
        )

        self.onboarding.enter_client_name(self.client_name)
        self.onboarding.verify_client_name_value(
            self.client_name
        )

        self.onboarding.select_entity_onboarding()

        self.onboarding.verify_customer_role_label()
        self.onboarding.verify_customer_role_dropdown()

    def prepare_entity_consent_letter(self):
        self.prepare_entity_onboarding()

        self.onboarding.select_customer_role("Seller")
        self.onboarding.verify_selected_customer_role("Seller")
        self.onboarding.verify_proceed_button_enabled()

        self.onboarding.click_proceed()

        # Keep the existing popup handler.
        self.onboarding.handle_existing_client_popup()

        self.onboarding.verify_consent_popup_visible()

    # --------------------------------------------------
    # Entity onboarding and customer role
    # --------------------------------------------------

    def test_entity_customer_role_dropdown_is_visible(self):
        self.prepare_entity_onboarding()

    def test_all_entity_customer_role_options_are_visible(self):
        self.prepare_entity_onboarding()
        self.onboarding.verify_all_customer_role_options()

    @pytest.mark.parametrize(
        "role",
        [
            "Seller",
            "Buyer",
            "Lessor",
            "Lessee",
            "Director",
            "Trustee",
            "Beneficial Owner",
            "Solicitor / Power of Attorney",
            "Other",
        ],
    )
    def test_entity_role_selection_enables_proceed(self, role):
        self.prepare_entity_onboarding()

        # Entity Proceed may initially be enabled.
        self.onboarding.select_customer_role(role)
        self.onboarding.verify_selected_customer_role(role)

    # --------------------------------------------------
    # Consent Letter content - Entity
    # --------------------------------------------------

    def test_entity_proceed_opens_consent_letter(self):
        self.prepare_entity_consent_letter()

        self.onboarding.verify_consent_title()
        self.onboarding.verify_consent_intro()
        self.onboarding.verify_all_consent_items()
        self.onboarding.verify_acknowledgement_text()

    def test_entity_consent_checkbox_is_initially_unchecked(self):
        self.prepare_entity_consent_letter()

        self.onboarding.verify_consent_checkbox_visible()
        self.onboarding.verify_consent_checkbox_unchecked()

    def test_entity_consent_checkbox_enables_agree(self):
        self.prepare_entity_consent_letter()

        self.onboarding.check_consent_checkbox()
        self.onboarding.verify_consent_checkbox_checked()
        self.onboarding.verify_agree_button_enabled()

    # --------------------------------------------------
    # Consent acceptance and cancellation - Entity
    # --------------------------------------------------

    def test_entity_cancel_closes_consent_letter(self):
        self.prepare_entity_consent_letter()

        self.onboarding.click_cancel()
        self.onboarding.verify_consent_popup_closed()

    def test_entity_agree_accepts_consent(self):
        self.prepare_entity_consent_letter()

        self.onboarding.check_consent_checkbox()
        self.onboarding.verify_agree_button_enabled()

        self.onboarding.click_agree()
        self.onboarding.verify_consent_popup_closed()

    # --------------------------------------------------
    # Pending Onboarding button and search
    # --------------------------------------------------

    def test_pending_onboarding_button_and_pause_icon(self):
        """Verify Pending Onboarding button and its pause-circle icon."""
        self.onboarding.click_pending_onboarding()
        self.onboarding.verify_pending_onboarding_button_visible()
        self.onboarding.verify_pending_onboarding_pause_icon()

    def test_pending_search_field_is_visible(self):
        """Verify the Pending Onboarding search field is visible."""
        self.onboarding.click_pending_onboarding()
        self.onboarding.verify_pending_search_field_visible()

    def test_pending_search_clear_button_is_hidden_initially(self):
        """Verify clear/cancel is hidden while the search field is empty."""
        self.onboarding.click_pending_onboarding()
        self.onboarding.verify_pending_search_field_visible()
        self.onboarding.verify_pending_search_clear_button_hidden()

    def test_pending_search_clear_button_appears_after_typing(self):
        """Verify clear/cancel appears after entering search text."""
        self.onboarding.click_pending_onboarding()
        self.onboarding.enter_pending_search_text("Test")
        self.onboarding.verify_pending_search_clear_button_visible()

    def test_pending_search_clear_button_clears_text(self):
        """Verify clear/cancel clears the search field."""
        self.onboarding.click_pending_onboarding()
        self.onboarding.enter_pending_search_text("Test")
        self.onboarding.verify_pending_search_clear_button_visible()

        self.onboarding.click_pending_search_clear_button()

        self.onboarding.verify_pending_search_field_empty()
        self.onboarding.verify_pending_search_clear_button_hidden()

    def test_pending_search_button_is_visible_and_clickable(self):
        """Verify the search button is visible and can be clicked."""
        self.onboarding.click_pending_onboarding()
        self.onboarding.verify_pending_search_button_visible()
        self.onboarding.click_pending_search_button()

    # --------------------------------------------------
    # Created By / analyst filter
    # --------------------------------------------------

    def test_created_by_label_and_analyst_filter_are_visible(self):
        """Verify Created By label and analyst dropdown are visible."""
        self.onboarding.click_pending_onboarding()
        self.onboarding.verify_created_by_label_visible()
        self.onboarding.verify_analyst_filter_visible()

    @pytest.mark.parametrize(
        "analyst_name",
        [
            "Oshadha Weerakon",
            "Senith Admin",
        ],
    )
    def test_filter_pending_records_by_analyst(self, analyst_name):
        """Verify records shown after selecting an analyst belong to them."""

        # Refresh only for these analyst filter test cases.
        self.page.reload()
        self.page.reload()
        self.page.wait_for_load_state("domcontentloaded")

        # Open Pending Onboarding after refresh.
        self.onboarding.click_pending_onboarding()

        self.onboarding.select_analyst(analyst_name)
        self.onboarding.verify_selected_analyst_records(analyst_name)

    # --------------------------------------------------
    # Pending Onboarding table
    # --------------------------------------------------

    def test_pending_onboarding_table_is_visible(self):
        """Verify the Pending Onboarding table is visible."""
        self.onboarding.click_pending_onboarding()
        self.onboarding.verify_pending_table_visible()

    def test_pending_onboarding_table_headers(self):
        """Verify all Pending Onboarding table headings and their order."""
        self.onboarding.click_pending_onboarding()
        self.onboarding.verify_pending_table_visible()
        self.onboarding.verify_pending_table_headers()

    # --------------------------------------------------
    # Reference ID navigation
    # --------------------------------------------------

    def test_reference_id_opens_entity_onboarding_process(self):
        """Verify clicking a Reference ID opens its entity process page."""
        self.onboarding.click_pending_onboarding()
        self.onboarding.verify_pending_table_visible()

        reference_id = (
            self.onboarding.pending_table_rows
            .first
            .locator("td")
            .first
            .inner_text()
            .strip()
        )

        assert reference_id, "The first Reference ID is empty."

        self.onboarding.click_reference_id(reference_id)
        self.onboarding.verify_reference_id_navigation(reference_id)