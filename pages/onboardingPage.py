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

        # Existing Client Information popup
        self.existing_client_modal = self.page.locator(
            ".modal-z-open"
        ).filter(
            has=self.page.get_by_text(
                "Existing Client Information",
                exact=True
            )
        )

        self.existing_client_okay_button = (
            self.existing_client_modal.locator(
                "button.modal-z-primary-btn"
            )
        )

        # Pending Onboarding tab/button
        self.pending_onboarding_button = (
            page.locator("label:has(i.fa-pause-circle)")
            .filter(has_text="Pending Onboarding")
        )

        # Pending Onboarding search field
        self.pending_search_input = page.get_by_placeholder(
            "Search by Reference ID or Client name",
            exact=True
        )

        # Clear/cancel button — appears after typing
        self.pending_search_clear_button = page.locator(
            "button.clear-btn"
        )

        # Search button
        self.pending_search_button = page.locator(
            "button.search-btn"
        )

        # Created By filter label (not the table heading)
        self.created_by_label = page.locator(
            "label.mb-0.whitespace-nowrap"
        ).filter(
            has_text="Created By"
        )

        # Analyst dropdown
        self.analyst_filter = page.locator(
            ".ant-select"
        ).filter(
            has=page.locator(
                ".ant-select-selection-placeholder"
            ).filter(
                has_text="Filter by Analyst"
            )
        )

        self.analyst_filter_placeholder = page.get_by_text(
            "Filter by Analyst",
            exact=True
        )

        # Pending onboarding table
        self.pending_table = page.locator(
            "div.ant-table-container table"
        )

        self.pending_table_headers = self.pending_table.locator(
            "thead th"
        )

        # Only actual data rows; exclude empty/placeholder rows
        self.pending_table_rows = self.pending_table.locator(
            "tbody.ant-table-tbody > tr.ant-table-row"
        )

        # Table columns
        self.reference_id_cells = page.locator(
            "tbody.ant-table-tbody td.ant-table-cell:first-child"
        )

        self.reference_id_links = page.locator(
            "tbody.ant-table-tbody td.ant-table-cell:first-child a"
        )

        self.created_by_cells = page.locator(
            "tbody.ant-table-tbody tr td:nth-child(7)"
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
                ".ant-select-dropdown:visible .ant-select-item-option"
            ).filter(
                has=self.page.locator(
                    ".ant-select-item-option-content"
                ).get_by_text(role, exact=True)
            )
            expect(option).to_be_visible()

    def select_client_role(self, role: str):
        if role not in self.client_role_options:
            raise ValueError(f"Unsupported client role: {role}")

        self.open_client_role_dropdown()

        option = self.page.locator(
            ".ant-select-dropdown:visible .ant-select-item-option"
        ).filter(
            has=self.page.locator(
                ".ant-select-item-option-content"
            ).get_by_text(role, exact=True)
        )

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

    # ==================================================
    # Entity onboarding
    # ==================================================

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
                ".ant-select-dropdown:visible .ant-select-item-option"
            ).filter(
                has=self.page.locator(
                    ".ant-select-item-option-content"
                ).get_by_text(role, exact=True)
            )
            expect(option).to_be_visible()

    def select_customer_role(self, role: str):
        self.open_customer_role_dropdown()

        option = self.page.locator(
            ".ant-select-dropdown:visible .ant-select-item-option"
        ).filter(
            has=self.page.locator(
                ".ant-select-item-option-content"
            ).get_by_text(role, exact=True)
        )

        expect(option).to_be_visible()
        option.click()

    def verify_selected_customer_role(self, role: str):
        selected_role = self.customer_role_dropdown.locator(
            ".ant-select-selection-item"
        )
        expect(selected_role).to_have_text(role)

    # ==================================================
    # Existing Client Information popup
    # ==================================================

    def handle_existing_client_popup(self):
        if self.existing_client_modal.is_visible():
            self.existing_client_okay_button.click()

    def verify_existing_client_popup_visible(self):
        expect(self.existing_client_modal).to_be_visible()

    def dismiss_existing_client_popup(self):
        self.verify_existing_client_popup_visible()
        self.existing_client_okay_button.click()
        expect(self.existing_client_modal).to_be_hidden()

    # ==================================================
    # Pending Onboarding search and controls
    # ==================================================

    def click_pending_onboarding(self):
        """Open Pending Onboarding and wait for its search field."""
        expect(self.pending_onboarding_button).to_be_visible()
        self.pending_onboarding_button.click()
        expect(self.pending_search_input).to_be_visible()

    def verify_pending_onboarding_button_visible(self):
        expect(self.pending_onboarding_button).to_be_visible()

    def verify_pending_onboarding_pause_icon(self):
        expect(
            self.pending_onboarding_button.locator("i.fa-pause-circle")
        ).to_be_visible()

    def verify_pending_search_field_visible(self):
        expect(self.pending_search_input).to_be_visible()

    def enter_pending_search_text(self, search_text: str):
        self.pending_search_input.fill(search_text)

    def verify_pending_search_clear_button_visible(self):
        expect(self.pending_search_clear_button).to_be_visible()

    def verify_pending_search_clear_button_hidden(self):
        expect(self.pending_search_clear_button).to_be_hidden()

    def click_pending_search_clear_button(self):
        self.pending_search_clear_button.click()

    def verify_pending_search_field_empty(self):
        expect(self.pending_search_input).to_have_value("")

    def verify_pending_search_button_visible(self):
        expect(self.pending_search_button).to_be_visible()

    def click_pending_search_button(self):
        self.pending_search_button.click()

    # =========================================
    # CREATED BY / ANALYST FILTER
    # =========================================

    def verify_created_by_label_visible(self):
        expect(self.created_by_label).to_be_visible()
        expect(self.created_by_label).to_have_text("Created By")

    def verify_analyst_filter_visible(self):
        expect(self.analyst_filter).to_be_visible()

    def open_analyst_filter(self):
        analyst_filter = self.page.locator(
            ".ant-select"
        ).filter(
            has=self.page.locator(
                ".ant-select-selection-placeholder"
            ).get_by_text("Filter by Analyst", exact=True)
        )

        expect(analyst_filter).to_be_visible()
        analyst_filter.click()

    def select_analyst(self, analyst_name: str):
        self.open_analyst_filter()

        # Locate the exact analyst option using its HTML title.
        option = self.page.locator(
            ".ant-select-dropdown:visible "
            f'.ant-select-item-option[title="{analyst_name}"]'
        )

        # Verify that the option exists and select it.
        expect(option).to_be_visible()
        option.click()

    def verify_selected_analyst_records(self, analyst_name: str):
        """Verify every visible record belongs to the selected analyst."""
        expect(self.pending_table_rows.first).to_be_visible()

        # Wait for the first record's Created By value to match the filter.
        expect(
            self.pending_table_rows.first.locator("td").nth(6)
        ).to_contain_text(analyst_name)

        row_count = self.pending_table_rows.count()
        assert row_count > 0, (
            f"No records found for analyst: {analyst_name}"
        )

        for index in range(row_count):
            row = self.pending_table_rows.nth(index)
            created_by_cell = row.locator("td").nth(6)
            expect(created_by_cell).to_have_text(analyst_name)

    def verify_records_match_selected_analysts(
        self,
        analyst_names: list[str]
    ):
        """For a multi-select filter, each record must match a selected analyst."""
        expect(self.pending_table_rows.first).to_be_visible()

        row_count = self.pending_table_rows.count()
        assert row_count > 0, "No filtered records were found."

        for index in range(row_count):
            row = self.pending_table_rows.nth(index)
            created_by = row.locator("td").nth(6).inner_text().strip()

            assert any(
                name == created_by for name in analyst_names
            ), (
                f"Unexpected Created By value '{created_by}'. "
                f"Expected one of: {analyst_names}"
            )

    # =========================================
    # TABLE HEADINGS
    # =========================================

    def verify_pending_table_visible(self):
        expect(self.pending_table).to_be_visible()

    def verify_pending_table_headers(self):
        expected_headers = [
            "Reference ID",
            "Name",
            "Type",
            "Status",
            "Created Date",
            "Last Update",
            "Created By",
        ]

        actual_headers = [
            header.strip()
            for header in self.pending_table_headers.all_inner_texts()
        ]

        assert actual_headers == expected_headers, (
            f"Table headers do not match.\n"
            f"Expected: {expected_headers}\n"
            f"Actual:   {actual_headers}"
        )

    # =========================================
    # REFERENCE ID / NAVIGATION
    # =========================================

    def click_reference_id(self, reference_id: str):
        row = self.pending_table_rows.filter(has_text=reference_id)
        expect(row).to_have_count(1)

        # Click the first cell; the Reference ID may not be an <a> element.
        reference_cell = row.locator("td").first
        expect(reference_cell).to_be_visible()
        reference_cell.click()

    def verify_reference_id_navigation(self, reference_id: str):
        expected_url = (
            "https://sentinel-austrac-qa.northlark.com/"
            "nolimit/app/onboarding/entity/process"
            f"?step=documents&client={reference_id}"
        )

        expect(self.page).to_have_url(expected_url)
