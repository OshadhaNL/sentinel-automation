
from playwright.sync_api import Page, expect


class OnboardingPage:
    def __init__(self, page: Page):
        self.page = page

        # Main page
        self.onboarding_heading = page.get_by_role(
            "heading", name="Onboarding", exact=True
        )
        self.onboarding_description = page.get_by_text(
            "Begin onboarding by choosing the appropriate client type below.",
            exact=True
        )

        # Onboarding phases
        self.new_onboarding_phase = page.get_by_text(
            "New Onboarding", exact=True
        )
        self.pending_onboarding_phase = page.get_by_text(
            "Pending Onboarding", exact=True
        )

        # Client name
        self.client_name_input = page.get_by_placeholder(
            "Enter client name", exact=True
        )

        # Client type section
        self.client_type_heading = page.get_by_role(
            "heading", name="Select Client Type", exact=True
        )

        # Client type cards — headings visible in your screenshot
        self.individual_card_heading = page.get_by_role(
            "heading", name="Onboard Individual", exact=True
        )
        self.entity_card_heading = page.get_by_role(
            "heading", name="Onboard Entity", exact=True
        )

        # Parent card containers
        self.individual_card = self.individual_card_heading.locator(
            "xpath=../.."
        )
        self.entity_card = self.entity_card_heading.locator(
            "xpath=../.."
        )

    # --------------------------------------------------
    # Page verifications
    # --------------------------------------------------

    def verify_onboarding_heading(self):
        expect(self.onboarding_heading).to_be_visible()

    def verify_onboarding_description(self):
        expect(self.onboarding_description).to_be_visible()

    # --------------------------------------------------
    # Phase verifications and actions
    # --------------------------------------------------

    def verify_new_onboarding_phase(self):
        expect(self.new_onboarding_phase).to_be_visible()

    def verify_pending_onboarding_phase(self):
        expect(self.pending_onboarding_phase).to_be_visible()

    def select_new_onboarding_phase(self):
        self.new_onboarding_phase.click()

    def select_pending_onboarding_phase(self):
        self.pending_onboarding_phase.click()

    # --------------------------------------------------
    # Client name
    # --------------------------------------------------

    def verify_client_name_field(self):
        expect(self.client_name_input).to_be_visible()

    def enter_client_name(self, client_name: str):
        expect(self.client_name_input).to_be_enabled()
        self.client_name_input.fill(client_name)

    def verify_client_name_value(self, client_name: str):
        expect(self.client_name_input).to_have_value(client_name)

    # --------------------------------------------------
    # Client type verification
    # --------------------------------------------------

    def verify_client_type_heading(self):
        expect(self.client_type_heading).to_be_visible()

    def verify_individual_card(self):
        expect(self.individual_card_heading).to_be_visible()
        expect(self.individual_card).to_be_visible()

    def verify_entity_card(self):
        expect(self.entity_card_heading).to_be_visible()
        expect(self.entity_card).to_be_visible()

    # --------------------------------------------------
    # Client type selection
    # --------------------------------------------------

    def select_individual_onboarding(self, client_name: str):
        self.enter_client_name(client_name)
        self.individual_card.click()

    def select_entity_onboarding(self, client_name: str):
        self.enter_client_name(client_name)
        self.entity_card.click()
