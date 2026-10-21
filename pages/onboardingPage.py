
from playwright.sync_api import Page, expect
import re

class OnboardingPage:
    def __init__(self, page: Page):
        self.page = page

        # Main Onboarding page
        self.onboarding_heading = page.get_by_role(
            "heading", name="Onboarding", exact=True
        )
        self.onboarding_description = page.get_by_text(
            "Begin onboarding by choosing the appropriate client type below.",
            exact=True,
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

        # Client type
        self.client_type_heading = page.get_by_role(
            "heading", name="Select Client Type", exact=True
        )
        self.individual_card_heading = page.get_by_role(
            "heading", name="Onboard Individual", exact=True
        )
        self.entity_card_heading = page.get_by_role(
            "heading", name="Onboard Entity", exact=True
        )

        self.individual_card = self.individual_card_heading.locator(
            "xpath=../.."
        )
        self.entity_card = self.entity_card_heading.locator(
            "xpath=../.."
        )

        # Client Role label and custom Ant Design dropdown
        self.client_role_label = page.get_by_role(
            "heading", name="Client Role", exact=True
        )

        self.client_role_dropdown = page.locator(
            ".ant-select"
        ).filter(
            has=page.locator(
                ".ant-select-selection-placeholder"
            ).filter(
                has_text="Select client role"
            )
        )

        self.client_role_options = [
            "Seller",
            "Buyer",
            "Lessor",
            "Lessee",
            "Director",
            "Trustee",
            "Beneficial Owner",
            "Solicitor / Power of Attorney",
            "Other",
        ]

        # Proceed
        self.proceed_button = page.get_by_role(
            "button", name="Proceed", exact=True
        )

        # Consent Letter modal
        self.consent_modal = page.locator(
            ".modal-z"
        ).filter(
            has=page.get_by_text("Consent Letter", exact=True)
        )

        self.consent_title = self.consent_modal.get_by_text(
            "Consent Letter", exact=True
        )

        self.consent_intro_text = (
            "I understand and agree that the organization may conduct "
            "the following checks and processes as part of its onboarding, "
            "compliance, and risk assessment procedures:"
        )

        self.consent_intro = self.consent_modal.get_by_text(
            self.consent_intro_text, exact=True
        )

        self.consent_items = [
            "Identity verification using government-issued identification documents;",
            "Facial biometric verification and facial matching procedures;",
            "Background verification and due diligence checks;",
            "Name screening against sanctions lists, watchlists, politically exposed persons (PEP) databases, adverse media, and other regulatory or compliance databases;",
            "Verification of information provided by me through third-party sources where legally permitted;",
            "Secure storage and retention of my personal data, documents, and verification results in accordance with applicable laws, regulations, and internal compliance requirements.",
        ]

        self.consent_acknowledgement = (
            'I acknowledge that I have read and understood the information '
            'provided above. By clicking "I Agree", I confirm my consent to '
            "the collection, processing, and use of my information in "
            "accordance with the stated terms and conditions."
        )

        self.consent_checkbox = self.consent_modal.locator(
            'input.ant-checkbox-input[type="checkbox"]'
        )

        self.agree_button = self.consent_modal.get_by_role(
            "button", name="I Agree", exact=True
        )

        self.cancel_button = self.consent_modal.get_by_role(
            "button", name="Cancel", exact=True
        )

        # Entity Customer Role label
        self.customer_role_label = page.get_by_role(
            "heading",
            name="Customer Role",
            exact=True
        )

        # Entity Customer Role dropdown
        self.customer_role_dropdown = self.page.get_by_text(
            "Customer Role", exact=True
        ).locator(
            "xpath=following::div[contains(@class, 'ant-select')][1]"
        )

        self.existing_client_okay_button = self.page.get_by_role(
            "button", name="Okay"
        )

        # Existing Client Information popup
        self.existing_client_modal = self.page.locator(
            ".modal-z"
        ).filter(
            has=self.page.get_by_role(
                "heading",
                name="Existing Client Information"
            )
        )

        self.existing_client_okay_button = self.existing_client_modal.get_by_role(
            "button",
            name="Okay",
            exact=True
        )

    # ==================================================
    # Main page verifications
    # ==================================================

    def verify_onboarding_heading(self):
        expect(self.onboarding_heading).to_be_visible()

    def verify_onboarding_description(self):
        expect(self.onboarding_description).to_be_visible()

    def verify_new_onboarding_phase(self):
        expect(self.new_onboarding_phase).to_be_visible()

    def verify_pending_onboarding_phase(self):
        expect(self.pending_onboarding_phase).to_be_visible()

    def select_new_onboarding_phase(self):
        self.new_onboarding_phase.click()

    def select_pending_onboarding_phase(self):
        self.pending_onboarding_phase.click()

    # ==================================================
    # Client name
    # ==================================================

    def verify_client_name_field(self):
        expect(self.client_name_input).to_be_visible()
        expect(self.client_name_input).to_be_enabled()

    def enter_client_name(self, client_name: str):
        expect(self.client_name_input).to_be_visible()
        expect(self.client_name_input).to_be_enabled()
        self.client_name_input.fill(client_name)

    def verify_client_name_value(self, client_name: str):
        expect(self.client_name_input).to_have_value(client_name)

    # ==================================================
    # Client type cards
    # ==================================================

    def verify_client_type_heading(self):
        expect(self.client_type_heading).to_be_visible()

    def verify_individual_card(self):
        expect(self.individual_card_heading).to_be_visible()
        expect(self.individual_card).to_be_visible()

    def verify_entity_card(self):
        expect(self.entity_card_heading).to_be_visible()
        expect(self.entity_card).to_be_visible()

    def select_individual_onboarding(self):
        self.individual_card_heading.click()
        self.verify_client_role_label()
        self.verify_client_role_dropdown()

    def select_entity_onboarding(self):
        self.entity_card_heading.click()

    # ==================================================
    # Client Role dropdown
    # ==================================================

    def verify_client_role_label(self):
        expect(self.client_role_label).to_be_visible()

    def verify_client_role_dropdown(self):
        expect(self.client_role_dropdown).to_be_visible()
        expect(self.client_role_dropdown).to_be_enabled()

    def open_client_role_dropdown(self):
        self.verify_client_role_dropdown()
        self.client_role_dropdown.click()

    def verify_all_client_role_options(self):
        self.open_client_role_dropdown()

        for role in self.client_role_options:
            option = self.page.locator(
                ".ant-select-item-option"
            ).filter(
                has=self.page.locator(
                    ".ant-select-item-option-content"
                ).get_by_text(role, exact=True)
            )

            expect(option).to_be_visible()

    def select_client_role(self, role: str):
        if role not in self.client_role_options:
            raise ValueError(f"Unsupported client role: {role}")

        option = self.page.locator(
            f'.ant-select-item-option[title="{role}"]'
        )

        if not option.is_visible():
            self.open_client_role_dropdown()

        expect(option).to_be_visible()
        option.click()

    def verify_selected_client_role(self, role: str):
        # After selection, the custom dropdown displays the chosen value.
        expect(
            self.page.locator(".ant-select-selection-item").filter(
                has_text=role
            )
        ).to_be_visible()

    # ==================================================
    # Proceed button
    # ==================================================

    def verify_proceed_button(self):
        expect(self.proceed_button).to_be_visible()

    def verify_proceed_button_initially_disabled(self):
        expect(self.proceed_button).to_be_visible()
        expect(self.proceed_button).to_be_disabled()

    def verify_proceed_button_enabled(self):
        expect(self.proceed_button).to_be_enabled()

    def click_proceed(self):
        expect(self.proceed_button).to_be_enabled()
        self.proceed_button.click()

    # ==================================================
    # Consent Letter popup
    # ==================================================

    def verify_consent_popup_visible(self):
        expect(self.consent_modal).to_be_visible()

    def verify_consent_title(self):
        expect(self.consent_title).to_be_visible()

    def verify_consent_intro(self):
        expect(self.consent_intro).to_be_visible()

    def verify_all_consent_items(self):
        for item in self.consent_items:
            expect(
                self.consent_modal.get_by_text(item, exact=True)
            ).to_be_visible()

    def verify_acknowledgement_text(self):
        expect(
            self.consent_modal.get_by_text(
                self.consent_acknowledgement, exact=True
            )
        ).to_be_visible()

    def verify_consent_checkbox_visible(self):
        expect(self.consent_checkbox).to_be_visible()

    def verify_consent_checkbox_unchecked(self):
        expect(self.consent_checkbox).not_to_be_checked()

    def check_consent_checkbox(self):
        self.consent_checkbox.check()

    def verify_consent_checkbox_checked(self):
        expect(self.consent_checkbox).to_be_checked()

    def verify_agree_button_disabled(self):
        expect(self.agree_button).to_be_visible()
        expect(self.agree_button).to_have_class(
            re.compile(r"cursor-not-allowed")
        )

    def verify_agree_button_enabled(self):
        expect(self.agree_button).to_be_enabled()

    def verify_cancel_button_visible(self):
        expect(self.cancel_button).to_be_visible()
        expect(self.cancel_button).to_be_enabled()

    def click_agree(self):
        expect(self.agree_button).to_be_enabled()
        self.agree_button.click()

    def click_cancel(self):
        self.cancel_button.click()

    def verify_consent_popup_closed(self):
        expect(self.consent_modal).to_be_hidden()

    # Entity onboarding
    def select_entity_onboarding(self):
        self.entity_card_heading.click()
        self.verify_customer_role_label()
        self.verify_customer_role_dropdown()

    def verify_customer_role_label(self):
        expect(self.customer_role_label).to_be_visible()

    def verify_customer_role_dropdown(self):
        expect(self.customer_role_dropdown).to_be_visible()
        expect(self.customer_role_dropdown).to_be_enabled()

    def open_customer_role_dropdown(self):
        self.verify_customer_role_dropdown()
        self.customer_role_dropdown.click()

    def verify_all_customer_role_options(self):
        self.open_customer_role_dropdown()

        for role in self.client_role_options:
            option = self.page.locator(
                ".ant-select-item-option"
            ).filter(
                has=self.page.locator(
                    ".ant-select-item-option-content"
                ).get_by_text(role, exact=True)
            )
            expect(option).to_be_visible()

    def select_customer_role(self, role: str):
        self.customer_role_dropdown.click()

        # Select the requested option from the open dropdown.
        self.page.locator(
            ".ant-select-item-option"
        ).filter(
            has=self.page.locator(
                ".ant-select-item-option-content"
            ).get_by_text(role, exact=True)
        ).click()

    def verify_selected_customer_role(self, role: str):
        selected_role = self.customer_role_dropdown.locator(
            ".ant-select-selection-item"
        )
        expect(selected_role).to_have_text(role)

    def handle_existing_client_popup(self):
        if self.existing_client_okay_button.is_visible():
            self.existing_client_okay_button.click()

    def handle_existing_client_popup(self):
        existing_client_modal = self.page.locator(".modal-z-open").filter(
            has=self.page.get_by_text(
                "Existing Client Information",
                exact=True
            )
        )

        okay_button = existing_client_modal.locator(
            "button.modal-z-primary-btn"
        )

        if existing_client_modal.is_visible():
            okay_button.click()
            print("Clicked Okay on Existing Client Information popup")

        def verify_existing_client_popup_visible(self):
            expect(self.existing_client_modal).to_be_visible()

        def dismiss_existing_client_popup(self):
            self.verify_existing_client_popup_visible()
            self.existing_client_okay_button.click()
            expect(self.existing_client_modal).to_be_hidden()

    def dismiss_existing_client_popup(self):
        expect(self.existing_client_modal).to_be_visible()

        self.existing_client_okay_button.click()

        expect(self.existing_client_modal).to_be_hidden()