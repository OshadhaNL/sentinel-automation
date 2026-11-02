
import os
import re
import uuid
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.mainOnboardingPage import MainOnboardingPage
from pages.individualOnboardingPage import IndividualOnboardingPage



@pytest.mark.ui
class TestIndividualOnboarding:

    @pytest.fixture(autouse=True)
    def setup_individual(self, page: Page, base_url: str):

        self.page = page

        email = os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PASSWORD")

        assert email, "TEST_EMAIL is not configured"
        assert password, "TEST_PASSWORD is not configured"

        # Step 1: Login
        login = LoginPage(page)
        login.open(base_url)
        login.enter_email(email)
        login.enter_password(password)
        login.click_login()

        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$")
        )

        # Step 2: Open main Onboarding
        page.get_by_role(
            "link", name="Onboarding", exact=False
        ).click()

        main = MainOnboardingPage(page)

        expect(main.heading).to_be_visible()
        main.open_new()

        # Step 3: Create unique individual client
        client_name = (
            "Automation Individual "
            + uuid.uuid4().hex[:12]
        )

        main.open_consent(
            "individual",
            client_name,
            role="Seller",
        )

        # Step 4: Accept consent
        main.consent_checkbox().check()

        expect(main.consent_agree()).to_be_enabled()
        main.consent_agree().click()

        # Step 5: Initialize individual page
        self.individual = IndividualOnboardingPage(page)
        self.individual.verify_page_loaded()

    def prepare_documents_step(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.select_first_review_dropdown_option("Gender")

        self.individual.click_review_save_confirm()

        self.individual.verify_review_submission_successful()

        self.individual.click_finish_and_view_submitted_documents()

        self.individual.verify_navigation_after_finish()


    def test_individual_page_header(self):
        self.individual.verify_page_header()

    def test_five_navigation_tabs_visible(self):
        self.individual.verify_all_tabs()

    def test_navigation_tab_icons_visible(self):
        self.individual.verify_all_icons()

    def test_verification_active_by_default(self):
        self.individual.verify_active_tab(
            "Verification"
        )

    @pytest.mark.parametrize(
        "tab_name",
        [
            "Documents",
            "Screening",
            "KYC Form",
            "Risk Assessment",
        ],
    )
    def test_navigation_tab_selection(self, tab_name):
        self.individual.open_tab(tab_name)

    def test_return_to_verification(self):
        self.individual.open_tab("Documents")
        self.individual.open_tab("Verification")

    def test_back_button_navigation(self):
        self.individual.click_back()


    # =========================================================
    # LIVE PHOTO - CAMERA WARNING TESTS
    # =========================================================

    def test_live_photo_heading_visible(self):
        expect(
            self.individual.live_photo_heading
        ).to_be_visible()

    def test_camera_warning_popup_visible(self):
        self.individual.open_camera_warning()
        self.individual.verify_camera_warning_popup()

    def test_camera_warning_close_button(self):
        self.individual.open_camera_warning()
        self.individual.close_camera_warning()

    def test_camera_warning_understand_button(self):
        self.individual.open_camera_warning()
        self.individual.verify_camera_warning_popup()
        self.individual.accept_camera_warning()

    # =========================================================
    # LIVE CAMERA STREAM TESTS
    # =========================================================

    def test_live_camera_interface_visible(self):
        self.individual.open_live_camera()
        self.individual.verify_live_camera_interface()

    def test_live_camera_instruction(self):
        self.individual.open_live_camera()

        expect(
            self.individual.camera_instruction
        ).to_have_text(
            "Position your face in the frame"
        )

    def test_live_camera_positioning_guides(self):
        self.individual.open_live_camera()

        expect(
            self.individual.camera_positioning_lines
        ).to_have_count(4)

    def test_live_camera_video_playing(self):
        self.individual.open_live_camera()
        self.individual.verify_camera_video_playing()

    def test_take_photo_button_visible(self):
        self.individual.open_live_camera()

        expect(
            self.individual.take_photo_button
        ).to_be_visible()

        expect(
            self.individual.take_photo_button
        ).to_be_enabled()

    def test_close_live_camera(self):
        self.individual.open_live_camera()
        self.individual.close_live_camera()

    def test_capture_live_photo(self):
        self.individual.capture_and_verify_photo()

    def test_captured_photo_loaded(self):
        self.individual.capture_and_verify_photo()
        self.individual.verify_captured_photo_loaded()

    def test_invalid_camera_photo_rejected(self):
        self.individual.verify_invalid_photo_rejected()

    def test_captured_photo_preview_attribute(self):
        self.individual.capture_and_verify_photo()
        self.individual.verify_captured_photo_preview_attribute()

    def test_click_captured_photo(self):
        self.individual.capture_and_verify_photo()
        self.individual.click_captured_photo()

    def test_recapture_button_visible(self):
        self.individual.capture_and_verify_photo()
        self.individual.verify_recapture_button()

    def test_click_recapture_button(self):
        self.individual.capture_and_verify_photo()
        self.individual.click_recapture()

    def test_document_type_section_visible(self):
        self.individual.verify_document_type_section()

    def test_document_type_options_visible(self):
        self.individual.verify_document_type_options()

    def test_document_type_initially_unselected(self):
        self.individual.verify_document_type_initially_unselected()

    @pytest.mark.parametrize(
        "document_type",
        [
            "Passport",
            "Driver Licence",
            "Proof of Age Card"
        ]
    )
    def test_select_document_type(self, document_type):
        self.individual.select_document_type(document_type)
        self.individual.verify_only_document_type_selected(
            document_type
        )

    def test_document_type_single_selection(self):
        self.individual.select_document_type("Passport")

        self.individual.select_document_type("Driver Licence")

        self.individual.verify_only_document_type_selected(
            "Driver Licence"
        )

    def test_document_front_section_visible(self):
        self.individual.verify_document_front_section()

    def test_document_back_section_visible(self):
        self.individual.verify_document_back_section()

    def test_document_front_file_input_exists(self):
        expect(
            self.individual.document_front_input
        ).to_have_count(1)

    def test_document_back_file_input_exists(self):
        expect(
            self.individual.document_back_input
        ).to_have_count(1)

    def test_upload_document_front(self):
        file_path = (
                Path(__file__).resolve().parents[2]
                / "test_data"
                / "doc-front.jpg"
        )

        self.individual.upload_document_front(file_path)

        print("Document Front upload action completed")

    def test_upload_document_back(self):
        file_path = (
                Path(__file__).resolve().parents[2]
                / "test_data"
                / "doc-back.jpg"
        )

        self.individual.upload_document_back(file_path)

        print("Document Back upload action completed")

    @pytest.fixture
    def document_files(self):
        root = Path(__file__).resolve().parents[2]

        return {
            "front": root / "test_data" / "doc-front.jpg",
            "back": root / "test_data" / "doc-back.jpg",
        }

    def test_document_front_uploaded_file_visible(self, document_files):
        file_path = document_files["front"]

        self.individual.upload_document_front(file_path)

        self.individual.verify_document_front_uploaded(
            file_path.name
        )

    def test_document_back_uploaded_file_visible(self, document_files):
        file_path = document_files["back"]

        self.individual.upload_document_back(file_path)

        self.individual.verify_document_back_uploaded(
            file_path.name
        )

    def test_both_documents_uploaded(self, document_files):
        front_file = document_files["front"]
        back_file = document_files["back"]

        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

    def test_remove_document_front(self, document_files):
        file_path = document_files["front"]

        self.individual.upload_document_front(file_path)
        self.individual.verify_document_front_uploaded(file_path.name)

        self.individual.remove_document_front()

    def test_remove_document_back(self, document_files):
        file_path = document_files["back"]

        self.individual.upload_document_back(file_path)
        self.individual.verify_document_back_uploaded(file_path.name)

        self.individual.remove_document_back()

    def test_remove_front_keeps_back(self, document_files):
        front_file = document_files["front"]
        back_file = document_files["back"]

        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

        self.individual.remove_document_front()

        self.individual.verify_document_back_uploaded(back_file.name)

    def test_reupload_document_front(self, document_files):
        front_file = document_files["front"]

        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

        self.individual.remove_document_front()

        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

    def test_reupload_document_back(self, document_files):
        back_file = document_files["back"]

        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

        self.individual.remove_document_back()

        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

    def test_remove_back_keeps_front(self, document_files):
        front_file = document_files["front"]
        back_file = document_files["back"]

        # Select document type
        self.individual.select_document_type("Driver Licence")

        # Upload both documents
        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

        # Remove only back
        self.individual.remove_document_back()

        # Front should remain uploaded
        self.individual.verify_document_front_uploaded(front_file.name)

    def test_remove_both_documents(self, document_files):
        front_file = document_files["front"]
        back_file = document_files["back"]

        # Select document type
        self.individual.select_document_type("Driver Licence")

        # Upload both documents
        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

        # Remove both
        self.individual.remove_document_front()
        self.individual.remove_document_back()

        # Verify both upload areas are restored
        expect(
            self.individual.document_front_uploaded_file
        ).to_have_count(0)

        expect(
            self.individual.document_back_uploaded_file
        ).to_have_count(0)

        expect(
            self.individual.document_front_input
        ).to_have_count(1)

        expect(
            self.individual.document_back_input
        ).to_have_count(1)

    def test_invalid_document_front_upload(self):
        file_path = (
                Path(__file__).resolve().parents[2]
                / "test_data"
                / "invalid-document.txt"
        )

        self.individual.select_document_type("Driver Licence")
        self.individual.upload_document_front(file_path)

        self.individual.verify_invalid_document_front_rejected()

    def test_invalid_document_back_upload(self):
        file_path = (
                Path(__file__).resolve().parents[2]
                / "test_data"
                / "invalid-document.txt"
        )

        self.individual.select_document_type("Driver Licence")
        self.individual.upload_document_back(file_path)

        self.individual.verify_invalid_document_back_rejected()

    def test_verification_action_buttons_visible(self):
        self.individual.verify_verification_action_buttons()

    def test_verification_action_buttons_enabled(self):
        self.individual.verify_verification_buttons_enabled()

    def test_reset_selected_document_type(self):
        # Select a document type
        self.individual.select_document_type("Driver Licence")

        # Click Reset
        self.individual.click_verification_reset()

        # Verify document type is cleared
        self.individual.verify_document_type_reset()

    def test_reset_uploaded_documents(self, document_files):
        front_file = document_files["front"]
        back_file = document_files["back"]

        # Select document type
        self.individual.select_document_type("Driver Licence")

        # Upload both documents
        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

        # Click Reset
        self.individual.click_verification_reset()

        # Verify uploads are cleared
        self.individual.verify_document_uploads_reset()

    def test_reset_document_type_and_uploads(self, document_files):
        front_file = document_files["front"]
        back_file = document_files["back"]

        self.individual.select_document_type("Driver Licence")

        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

        self.individual.click_verification_reset()

        self.individual.verify_document_type_reset()
        self.individual.verify_document_uploads_reset()

    def test_submit_without_verification_details(self):
        self.individual.click_verification_submit()

        print(
            "Validation messages:",
            self.individual.get_verification_validation_messages()
        )

        print("Current URL:", self.page.url)

    def test_submit_with_document_type_only(self):
        self.individual.select_document_type("Driver Licence")

        self.individual.click_verification_submit()

        print(
            "Validation messages:",
            self.individual.get_verification_validation_messages()
        )

        print("Current URL:", self.page.url)

    def test_submit_with_documents_but_no_live_photo(self, document_files):
        front_file = document_files["front"]
        back_file = document_files["back"]

        self.individual.select_document_type("Driver Licence")

        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

        self.individual.click_verification_submit()

        print(
            "Validation messages:",
            self.individual.get_verification_validation_messages()
        )

        print("Current URL:", self.page.url)

    def test_submit_without_verification_details(self):
        self.individual.click_verification_submit()

        self.individual.verify_still_on_verification_page()

    def test_submit_with_document_type_only(self):
        self.individual.select_document_type("Driver Licence")

        self.individual.click_verification_submit()

        self.individual.verify_still_on_verification_page()

    def test_submit_with_documents_but_no_live_photo(self, document_files):
        front_file = document_files["front"]
        back_file = document_files["back"]

        self.individual.select_document_type("Driver Licence")

        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

        self.individual.click_verification_submit()

        self.individual.verify_still_on_verification_page()

    def test_successful_verification_submission(self, document_files):
        front_file = document_files["front"]
        back_file = document_files["back"]

        # Capture live photo
        self.individual.capture_and_verify_photo()

        # Select document type
        self.individual.select_document_type("Driver Licence")

        # Upload front document
        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(
            front_file.name
        )

        # Upload back document
        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(
            back_file.name
        )

        # Submit documents
        self.individual.click_verification_submit()

        # Verify success notification
        self.individual.verify_documents_submitted_successfully()

        # Verify extracted information screen
        self.individual.verify_review_extracted_information_screen()

        # Verify media section labels
        self.individual.verify_review_media_labels()

        def test_review_extracted_information_fields(self, document_files):
            front_file = document_files["front"]
            back_file = document_files["back"]

            # Capture live photo
            self.individual.capture_and_verify_photo()

            # Select document type
            self.individual.select_document_type("Driver Licence")

            # Upload Document Front
            self.individual.upload_document_front(front_file)
            self.individual.verify_document_front_uploaded(front_file.name)

            # Upload Document Back
            self.individual.upload_document_back(back_file)
            self.individual.verify_document_back_uploaded(back_file.name)

            # IMPORTANT: Verify Front still exists after Back upload
            self.individual.verify_document_front_uploaded(front_file.name)

            # Submit
            self.individual.click_verification_submit()

            # Verify success notification
            self.individual.verify_documents_submitted_successfully()

            # Verify review screen
            self.individual.verify_review_extracted_information_screen()

            # Verify uploaded media labels
            self.individual.verify_review_media_labels()

            # Verify extracted fields
            for field in [
                "First Name",
                "Last Name",
                "Date of Birth",
                "Driver Licence Number",
                "Personal Number",
                "Issue Date",
                "Expiry Date",
                "Place of Birth"
            ]:
                expect(
                    self.page.get_by_role(
                        "textbox",
                        name=field,
                        exact=True
                    )
                ).to_be_visible()

            expect(
                self.page.get_by_role(
                    "checkbox",
                    name="My residential address is different"
                )
            ).to_be_visible()

            expect(
                self.page.get_by_role(
                    "button",
                    name="Save & Confirm",
                    exact=True
                )
            ).to_be_visible()

    def test_review_extracted_information_fields(self, document_files):
        front_file = document_files["front"]
        back_file = document_files["back"]

        # Capture live photo
        self.individual.capture_and_verify_photo()

        # Select document type
        self.individual.select_document_type("Driver Licence")

        # Upload Document Front
        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

        # Upload Document Back
        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

        # Ensure both documents remain uploaded
        self.individual.verify_document_front_uploaded(front_file.name)

        # Submit documents
        self.individual.click_verification_submit()

        # Verify success notification
        self.individual.verify_documents_submitted_successfully()

        # Verify Review Extracted Information screen
        self.individual.verify_review_extracted_information_screen()

        # Verify extracted information fields
        for field in [
            "First Name",
            "Last Name",
            "Date of Birth",
            "Driver Licence Number",
            "Personal Number",
            "Issue Date",
            "Expiry Date",
            "Place of Birth"
        ]:
            expect(
                self.page.get_by_role(
                    "textbox",
                    name=field,
                    exact=True
                )
            ).to_be_visible()

        # Verify residential address checkbox
        expect(
            self.page.get_by_role(
                "checkbox",
                name="My residential address is different"
            )
        ).to_be_visible()

        # Verify Save & Confirm button
        expect(
            self.page.get_by_role(
                "button",
                name="Save & Confirm",
                exact=True
            )
        ).to_be_visible()

    def prepare_review_extracted_information(self, document_files):
        front_file = document_files["front"]
        back_file = document_files["back"]

        self.individual.capture_and_verify_photo()
        self.individual.select_document_type("Driver Licence")

        self.individual.upload_document_front(front_file)
        self.individual.verify_document_front_uploaded(front_file.name)

        self.individual.upload_document_back(back_file)
        self.individual.verify_document_back_uploaded(back_file.name)

        self.individual.verify_document_front_uploaded(front_file.name)

        self.individual.click_verification_submit()
        self.individual.wait_for_review_extracted_information()
        self.individual.verify_review_extracted_information_screen()

        # Capture values from the review form before Save & Confirm.
        self.original_verification_details = (
            self.individual.verification_capture_review_form_details(strict=False)
        )

    def test_review_first_last_name_fields(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.verify_review_name_fields()

    def test_review_first_last_name_fields(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.verify_review_name_fields()

    def test_edit_extracted_first_name(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.edit_review_first_name(
            "AutomationFirstName"
        )

    def test_edit_extracted_last_name(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.edit_review_last_name(
            "AutomationLastName"
        )

    def test_review_residential_address_checkbox_visible(
            self, document_files
    ):
        self.prepare_review_extracted_information(document_files)

        self.individual.verify_residential_address_checkbox()

    def test_residential_address_initially_disabled(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.verify_residential_address_initially_unchecked()
        self.individual.verify_residential_address_fields_disabled()

    def test_enable_separate_residential_address(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.enable_separate_residential_address()
        self.individual.verify_residential_address_fields_enabled()

    def test_disable_separate_residential_address(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.enable_separate_residential_address()
        self.individual.verify_residential_address_fields_enabled()

        self.individual.disable_separate_residential_address()
        self.individual.verify_residential_address_fields_disabled()

    def test_review_gender_dropdown_visible(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.verify_review_dropdown_visible("Gender")

    def test_review_gender_dropdown_options(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.verify_review_dropdown_has_options("Gender")

    def test_review_select_gender(self, document_files):
        self.prepare_review_extracted_information(document_files)

        selected_gender = (
            self.individual.select_first_review_dropdown_option("Gender")
        )

        print(f"Selected Gender: {selected_gender}")

    def test_review_nationality_dropdown(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.verify_review_dropdown_visible("Nationality")

        self.individual.verify_review_dropdown_selected_value(
            "Nationality",
            "Sri Lanka (LKA)"
        )

    def test_review_issuing_country_dropdown(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.verify_review_dropdown_visible("Issuing Country")

        self.individual.verify_review_dropdown_selected_value(
            "Issuing Country",
            "Sri Lanka (LKA)"
        )

    def test_review_document_type_dropdown(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.verify_review_dropdown_visible("Type of Document")

        self.individual.verify_review_dropdown_selected_value(
            "Type of Document",
            "Driver Licence"
        )

    def test_review_save_confirm_button_visible(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.verify_review_save_confirm_button()

    def test_review_save_confirm_action(self, document_files):
        self.prepare_review_extracted_information(document_files)

        # Gender was unselected in the supplied HTML.
        self.individual.select_first_review_dropdown_option("Gender")

        # Click Save & Confirm.
        self.individual.click_review_save_confirm()

        # Inspect the resulting state.
        self.individual.inspect_review_save_result()

    def test_review_save_confirm_action(self, document_files):
        self.prepare_review_extracted_information(document_files)

        # Select Gender, which was initially empty.
        self.individual.select_first_review_dropdown_option("Gender")

        # Save the extracted information.
        self.individual.click_review_save_confirm()

        # Verify actual submission success.
        self.individual.verify_review_submission_successful()

    def test_finish_and_view_submitted_documents(self, document_files):
        self.prepare_review_extracted_information(document_files)

        self.individual.select_first_review_dropdown_option("Gender")

        self.individual.click_review_save_confirm()

        self.individual.verify_review_submission_successful()

        self.individual.click_finish_and_view_submitted_documents()

        self.individual.verify_navigation_after_finish()

    def test_documents_step_navigation(self, document_files):
        self.prepare_documents_step(document_files)

        print("\n========== DOCUMENTS PAGE ==========")
        print(self.page.locator("main").inner_text()[:8000])

        print("\n========== ARIA SNAPSHOT ==========")
        print(self.page.locator("main").aria_snapshot())

    def test_documents_page_elements(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_page_loaded()
        self.individual.verify_documents_upload_categories()

    def test_documents_choose_file_buttons(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_page_loaded()
        self.individual.verify_documents_choose_file_buttons()

    def test_documents_next_button_visible(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_page_loaded()
        self.individual.verify_documents_next_button()

    def test_inspect_documents_upload_inputs(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_page_loaded()

        file_inputs = self.page.locator('input[type="file"]')

        print("\n========== DOCUMENT FILE INPUTS ==========")
        print("Total file inputs:", file_inputs.count())

        for i in range(file_inputs.count()):
            print(f"\nFile Input {i + 1}:")
            print(file_inputs.nth(i).evaluate("(element) => element.outerHTML"))

        print("\n========== UPLOAD SECTION HTML ==========")

        for category in [
            "Passport Copy",
            "Driver Licence",
            "Proof of Age Card",
            "Others"
        ]:
            label = self.page.get_by_text(category, exact=True).first

            print(f"\n{category}:")
            print(label.locator("xpath=..").evaluate("(element) => element.outerHTML"))

    def test_upload_passport_copy(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.upload_documents_file(
            "Passport Copy",
            document_files["front"]
        )

        self.individual.verify_documents_uploaded_file(
            "Passport Copy",
            document_files["front"].name
        )

    def test_upload_driver_licence(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.upload_documents_file(
            "Driver Licence",
            document_files["front"]
        )

        self.individual.verify_documents_uploaded_file(
            "Driver Licence",
            document_files["front"].name
        )

    def test_upload_proof_of_age_card(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.upload_documents_file(
            "Proof of Age Card",
            document_files["front"]
        )

        self.individual.verify_documents_uploaded_file(
            "Proof of Age Card",
            document_files["front"].name
        )

    def test_upload_others(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.upload_documents_file(
            "Others",
            document_files["front"]
        )

        self.individual.verify_documents_uploaded_file(
            "Others",
            document_files["front"].name
        )

    def test_inspect_passport_upload_result(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_page_loaded()

        self.individual.upload_documents_file(
            "Passport Copy",
            document_files["front"]
        )

        container = self.individual.get_documents_upload_container(
            "Passport Copy"
        )

        print("\n========== PASSPORT UPLOAD RESULT ==========")
        print(container.aria_snapshot())

        print("\n========== PASSPORT UPLOAD HTML ==========")
        print(container.inner_html())

        print("\n========== PAGE ALERTS ==========")
        print(self.page.get_by_role("alert").all_text_contents())

    def test_driver_licence_documents_visible(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_page_loaded()
        self.individual.verify_driver_licence_documents()

    def test_driver_licence_uploaded_images_visible(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_page_loaded()
        self.individual.verify_driver_licence_uploaded_files()

    def test_inspect_driver_licence_actions(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_page_loaded()
        self.individual.verify_driver_licence_uploaded_files()

        for filename in ["doc-front.jpg", "doc-back.jpg"]:
            document = self.page.get_by_role(
                "heading",
                name=filename,
                exact=True
            )

            print(f"\n========== {filename} ==========")

            print(
                document.evaluate("""
                                  element => {
                                      const card = element.closest('.uploader-z');
                                      return card
                                          ? card.outerHTML
                                          : element.parentElement.parentElement.parentElement.outerHTML;
                                  }
                                  """)
            )

        print("\n========== DOCUMENTS ARIA SNAPSHOT ==========")
        print(self.page.locator("main").aria_snapshot())

    def test_view_driver_licence_front(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.view_uploaded_document(
            "Driver Licence - Front side",
            "doc-front.jpg"
        )

        self.individual.close_uploaded_document_preview(
            "Driver Licence - Front side"
        )

    def test_view_driver_licence_back(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.view_uploaded_document(
            "Driver Licence - Back side",
            "doc-back.jpg"
        )

        self.individual.close_uploaded_document_preview(
            "Driver Licence - Back side"
        )

    def test_download_driver_licence_front(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.download_uploaded_document(
            "Driver Licence - Front side",
            "doc-front.jpg"
        )

    def test_download_driver_licence_back(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.download_uploaded_document(
            "Driver Licence - Back side",
            "doc-back.jpg"
        )

    def test_documents_verify_tab(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_page_loaded()
        self.individual.click_documents_verify_tab()
        self.individual.verify_documents_verify_tab_active()

        # Wait until client information finishes loading
        client_name = self.page.locator(
            "h4.secondary-title"
        ).filter(
            has_text="Client Name:"
        ).locator("span")

        expect(client_name).not_to_have_text(
            "Loading...",
            timeout=30000
        )

        print("\n========== VERIFY TAB CONTENT ==========")
        print(self.page.locator("main").aria_snapshot())

        print("\n========== VERIFY TAB TEXT ==========")
        print(self.page.locator("main").inner_text())

        print("\n========== VERIFY FORM HTML ==========")
        print(self.page.locator("main .custom-form").first.inner_html())

    def test_documents_upload_tab_active(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_subtab_active("Upload")

    def test_documents_verify_tab_active(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.click_documents_subtab("Verify")
        self.individual.verify_documents_subtab_active("Verify")

    def test_documents_cabinets_tab_active(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.click_documents_subtab("Cabinets")
        self.individual.verify_documents_subtab_active("Cabinets")

    def test_documents_switch_between_tabs(self, document_files):
        self.prepare_documents_step(document_files)

        for tab_name in ["Verify", "Cabinets", "Upload"]:
            self.individual.click_documents_subtab(tab_name)
            self.individual.verify_documents_subtab_active(tab_name)

    def test_documents_reference_id_visible(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_reference_id()

    def test_documents_client_name_visible(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_documents_client_name_loaded()

    def test_inspect_remaining_documents_and_screening(self, document_files):
        self.prepare_documents_step(document_files)

        for tab_name in ["Verify", "Cabinets"]:
            self.individual.click_documents_subtab(tab_name)
            self.individual.verify_documents_subtab_active(tab_name)

            # Wait for client information to load
            expect(
                self.page.locator("h4.secondary-title")
                .filter(has_text="Client Name:")
                .locator("span")
            ).not_to_have_text(
                "Loading...",
                timeout=30000
            )

            print(f"\n========== {tab_name.upper()} TAB SNAPSHOT ==========")
            print(self.page.locator("main").aria_snapshot())

            print(f"\n========== {tab_name.upper()} TAB HTML ==========")
            print(self.page.locator("main").inner_html())

        # Return to Upload to inspect the Next button
        self.individual.click_documents_subtab("Upload")

        next_button = self.page.get_by_role(
            "button",
            name="Next",
            exact=True
        )

        expect(next_button).to_be_visible(timeout=15000)
        next_button.click()

        print("\n========== SCREENING URL ==========")
        print(self.page.url)

        print("\n========== SCREENING SNAPSHOT ==========")
        print(self.page.locator("main").aria_snapshot())

        print("\n========== SCREENING HTML ==========")
        print(self.page.locator("main").inner_html())

    def test_document_cabinets_heading_visible(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.click_documents_subtab("Cabinets")
        self.individual.verify_document_cabinets_heading()

    def test_document_cabinets_table_headers(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.click_documents_subtab("Cabinets")
        self.individual.verify_document_cabinets_table()

    def test_document_cabinets_data_state(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.click_documents_subtab("Cabinets")
        self.individual.verify_document_cabinets_empty_or_populated()

    def test_documents_reference_matches_url(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.verify_document_reference_matches_url()

    def test_documents_next_opens_verify(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.click_documents_next()
        self.individual.verify_documents_next_opens_verify()


    # ============================================================
    # DOCUMENTS -> VERIFY TESTS
    # ============================================================

    def test_verify_document_groups_visible(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_documents_verify()
        self.individual.verify_all_document_groups()


    def test_verify_all_uploaded_documents(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_documents_verify()
        self.individual.verify_all_expected_documents()


    def test_verify_document_action_buttons(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_documents_verify()
        self.individual.verify_all_document_action_buttons()


    def test_verify_document_expiry_indicators(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_documents_verify()
        self.individual.verify_all_document_expiry_indicators()


    def test_verify_document_drag_handles(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_documents_verify()
        self.individual.verify_all_document_drag_handles()


    def test_verify_document_reupload_formats(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_documents_verify()
        self.individual.verify_all_reupload_inputs()


    def test_verify_pdf_document_previews(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_documents_verify()

        documents = self.individual.get_verify_expected_documents()

        self.individual.verify_pdf_preview(
            "Consent Letter",
            documents["Consent Letter"][0]
        )

        self.individual.verify_pdf_preview(
            "Verification",
            documents["Verification"][1]
        )


    def test_verify_image_document_previews(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_documents_verify()

        for filename in ["doc-front.jpg", "doc-back.jpg"]:
            self.individual.verify_image_preview(
                "Driver Licence",
                filename
            )

        self.individual.verify_image_preview(
            "Verification",
            "photo.jpg"
        )


    def test_verify_all_document_downloads(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_documents_verify()
        self.individual.verify_all_document_downloads()


    def test_verify_modify_dialog_cancel(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_documents_verify()

        self.individual.verify_modify_dialog_cancel(
            "Driver Licence",
            "doc-front.jpg"
        )




    # ============================================================
    # DOCUMENTS GAP TESTS - ADDITIONAL COVERAGE
    # Uses docs_gap_* methods in individualOnboardingPage.py.
    # Every test creates its own client through setup_individual.
    # ============================================================

    @pytest.fixture
    def docs_gap_ready(self, document_files):
        """Finish verification and open Documents > Verify for this client."""
        self.prepare_documents_step(document_files)
        self.individual.docs_gap_open("Verify")

    @staticmethod
    def _docs_gap_samples():
        """Documents created by prepare_documents_step()."""
        return (
            ("Consent Letter", "Consent Letter"),
            ("Driver Licence", "doc-front.jpg"),
            ("Driver Licence", "doc-back.jpg"),
        )

    def _docs_gap_card(self, group, filename):
        return self.individual.docs_gap_item(filename, group)

    def _docs_gap_modified_card(self, group, original, new_name):
        """A metadata rename may or may not rename the stored file heading."""
        group_locator = self.individual.get_verify_group(group)
        for candidate in (new_name, original):
            resolved = self.individual.docs_gap_resolve_filename(candidate)
            card = group_locator.locator(".w-85").filter(
                has=self.page.get_by_role("heading", name=resolved, exact=True)
            )
            if card.count() == 1:
                return card
        raise AssertionError(
            f"Document card disappeared after modification: {group} / {original}"
        )

    # 01 - A delete action requests confirmation. Dismiss to preserve data.
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_01_delete_confirmation_visible(self, docs_gap_ready, group, filename):
        message = self.individual.docs_gap_delete_decision(filename, group, confirm=False)
        assert message.strip(), "Delete confirmation had no message"
        expect(self._docs_gap_card(group, filename)).to_be_visible()

    # 02 - Cancel deletion keeps the original document.
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_02_cancel_delete_preserves_document(self, docs_gap_ready, group, filename):
        self.individual.docs_gap_delete_decision(filename, group, confirm=False)
        expect(self._docs_gap_card(group, filename)).to_be_visible()

    # 03 - Confirm deletion removes the card (destructive; isolated client).
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_03_confirm_delete_removes_document(self, docs_gap_ready, group, filename):
        self.individual.docs_gap_delete_decision(filename, group, confirm=True)
        self.individual.docs_gap_verify_deleted(filename, group)

    # 04 - Modify popup shows name, upload date, expiry date, and actions.
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_04_modify_dialog_fields(self, docs_gap_ready, group, filename):
        modal = self.individual.docs_gap_modify(filename, group)
        self.individual.docs_gap_verify_modify_fields(modal, filename)
        self.individual.docs_gap_cancel(modal)

    # 05 - X close button dismisses Modify popup without changing file.
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_05_modify_close_x(self, docs_gap_ready, group, filename):
        modal = self.individual.docs_gap_modify(filename, group)
        self.individual.docs_gap_close_modal(modal)
        expect(self._docs_gap_card(group, filename)).to_be_visible()

    # 06 - Document Name is editable; change is not saved yet.
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_06_edit_document_name(self, docs_gap_ready, group, filename):
        modal = self.individual.docs_gap_modify(filename, group)
        updated = "Automation Document " + uuid.uuid4().hex[:8]
        self.individual.docs_gap_set_name(modal, updated)
        self.individual.docs_gap_cancel(modal)

    # 07 - Upload Date is not editable.
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_07_uploaded_date_readonly(self, docs_gap_ready, group, filename):
        modal = self.individual.docs_gap_modify(filename, group)
        self.individual.docs_gap_verify_uploaded_date_readonly(modal)
        self.individual.docs_gap_cancel(modal)

    # 08 - Expiry Date input or calendar control is available.
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_08_expiry_date_control(self, docs_gap_ready, group, filename):
        modal = self.individual.docs_gap_modify(filename, group)
        _, expiry = self.individual.docs_gap_modify_fields(modal)
        expect(expiry).to_be_enabled()
        expiry.click()
        # The picker may be read-only; only verify opening here.
        expect(expiry).to_be_visible()
        self.individual.docs_gap_cancel(modal)

    # 09 - Edit expiry date and save it (picker-only UI needs locator update).
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_09_save_expiry_date(self, docs_gap_ready, group, filename):
        modal = self.individual.docs_gap_modify(filename, group)
        self.individual.docs_gap_set_expiry(modal, "2030-12-31")
        _, expiry = self.individual.docs_gap_modify_fields(modal)
        assert expiry.input_value().strip(), "Expiry Date did not accept a value"
        self.individual.docs_gap_save(modal)

    # 10 - Save document name, reopen Modify, verify persistence.
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_10_name_persists_after_save(self, docs_gap_ready, group, filename):
        new_name = "Automation Document " + uuid.uuid4().hex[:8]
        modal = self.individual.docs_gap_modify(filename, group)
        self.individual.docs_gap_set_name(modal, new_name)
        self.individual.docs_gap_save(modal)
        self.page.reload(wait_until="domcontentloaded")
        self.individual.docs_gap_open("Verify")
        card = self._docs_gap_modified_card(group, filename, new_name)
        self.individual.docs_gap_action(card, "Modify").click()
        reopened = self.individual.docs_gap_modal()
        name, _ = self.individual.docs_gap_modify_fields(reopened)
        expect(name).to_have_value(new_name)
        self.individual.docs_gap_cancel(reopened)

    # 11 - Required indicator for Document Name.
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_11_name_required_marker(self, docs_gap_ready, group, filename):
        modal = self.individual.docs_gap_modify(filename, group)
        self.individual.docs_gap_verify_required_name(modal)
        self.individual.docs_gap_cancel(modal)

    # 12 - Cancel after editing does not persist the unsaved name.
    @pytest.mark.parametrize("group,filename", [
        ("Consent Letter", "Consent Letter"),
        ("Driver Licence", "doc-front.jpg"),
        ("Driver Licence", "doc-back.jpg"),
    ])
    def test_docs_gap_12_cancel_modify_discards_changes(self, docs_gap_ready, group, filename):
        modal = self.individual.docs_gap_modify(filename, group)
        name, _ = self.individual.docs_gap_modify_fields(modal)
        original = name.input_value()
        self.individual.docs_gap_set_name(modal, "Unsaved " + uuid.uuid4().hex[:8])
        self.individual.docs_gap_cancel(modal)
        reopened = self.individual.docs_gap_modify(filename, group)
        name, _ = self.individual.docs_gap_modify_fields(reopened)
        expect(name).to_have_value(original)
        self.individual.docs_gap_cancel(reopened)

    # 13 - Reupload via the existing document card's input.
    @pytest.mark.parametrize("group,filename,file_key", [
        ("Driver Licence", "doc-front.jpg", "front"),
        ("Driver Licence", "doc-back.jpg", "back"),
    ])
    def test_docs_gap_13_reupload_document(self, docs_gap_ready, document_files, group, filename, file_key):
        file_path = document_files[file_key]
        self.individual.docs_gap_reupload(filename, file_path, group)
        expect(self._docs_gap_card(group, filename)).to_be_visible()

    # 14 - Ref ID shown on the Documents page matches the current URL.
    def test_docs_gap_14_reference_id_matches_url(self, docs_gap_ready):
        self.individual.verify_document_reference_matches_url()

    # 15 - Empty-document navigation needs a client with no uploaded files.
    # Existing prepare_documents_step uploads verification documents, so
    # asserting an empty state here would produce a false result.
    def test_docs_gap_15_next_blocked_when_no_documents(self, docs_gap_ready):
        pytest.skip(
            "Needs a separate Documents client with zero uploaded documents; "
            "the existing setup always uploads a photo and licence."
        )

    # 16 - Proof of Age Card front/back need a proof-of-age onboarding fixture.
    @pytest.mark.parametrize("filename", ["doc-front.jpg", "doc-back.jpg"])
    def test_docs_gap_16_proof_of_age_card_modify(self, docs_gap_ready, filename):
        group = self.page.locator(".border-box").filter(
            has=self.page.locator(".border-box-label", has_text=re.compile(r"^\s*Proof of Age Card\s*$"))
        )
        if group.count() == 0:
            pytest.skip(
                "Proof of Age Card documents are not produced by the Driver Licence setup; "
                "a Proof of Age Card verification fixture is required."
            )
        modal = self.individual.docs_gap_modify(filename, "Proof of Age Card")
        self.individual.docs_gap_verify_modify_fields(modal, filename)
        self.individual.docs_gap_verify_uploaded_date_readonly(modal)
        self.individual.docs_gap_cancel(modal)

    # 17 - Missing-name N/A requires a deliberately nameless client record.
    def test_docs_gap_17_missing_client_name_displays_na(self, docs_gap_ready):
        pytest.skip(
            "Needs a fixture for an existing client whose name is actually missing; "
            "the normal setup always creates a named client."
        )

    # ============================================================
    # SCREENING - MAIN PAGE
    # ============================================================

    def test_screening_01_heading_and_description(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_form()
        self.individual.verify_screening_heading_description()

    def test_screening_02_single_and_daily_tabs(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_form()
        self.individual.verify_screening_modes()

    def test_screening_03_client_type_locked(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_form()
        self.individual.verify_screening_client_type()

    def test_screening_04_name_field(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_form()
        self.individual.verify_screening_name_field()

    def test_screening_05_gender_options_and_selection(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_form()

        self.individual.verify_screening_gender_options()
        self.individual.verify_screening_gender_selection()

    def test_screening_06_date_of_birth(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_form()
        self.individual.verify_screening_date_of_birth()

    def test_screening_07_citizenship_and_birthplace(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_form()
        self.individual.verify_screening_country_fields()

    def test_screening_08_ongoing_screening_checkbox(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_form()
        self.individual.verify_screening_ongoing_checkbox()

    def test_screening_09_analyze_button(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_form()
        self.individual.verify_screening_analyze_button()

    def test_screening_10_connected_party_section(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_form()
        self.individual.verify_screening_connected_party_section()

    # ============================================================
    # SCREENING - RESULTS PAGE
    # ============================================================

    def test_screening_11_results_header(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_results()
        self.individual.verify_screening_results_header()

    def test_screening_12_result_status_tabs(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_results()
        self.individual.verify_screening_result_status_tabs()

    def test_screening_13_match_count_consistency(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_results()
        self.individual.verify_screening_match_counts()

    def test_screening_14_result_tables_and_filters(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_results()

        self.individual.verify_screening_results_table()

        for status in [
            "Unresolved Hits",
            "Positive Hits",
            "False Hits",
            "Possible Hits"
        ]:
            self.individual.verify_screening_status_table(status)

    # ============================================================
    # SCREENING - BACK NAVIGATION
    # ============================================================

    def test_screening_15_back_to_screening(self, document_files):
        self.prepare_documents_step(document_files)

        self.individual.open_screening_main()
        self.individual.open_screening_results()
        self.individual.click_back_to_screening()


    @pytest.fixture
    def kyc_verification_complete(self, document_files):
        """Complete Verification and review before opening KYC directly."""
        self.prepare_review_extracted_information(document_files)
        self.individual.select_first_review_dropdown_option("Gender")
        self.individual.click_review_save_confirm()
        self.individual.verify_review_submission_successful()

    # =========================================================
    # KYC FORM - SECTION 01 TESTS
    # =========================================================

    def test_kyc_01_form_loaded(self, kyc_verification_complete):
        self.individual.open_kyc_form()
        self.individual.verify_kyc_form_loaded()

    def test_kyc_02_client_id(self, kyc_verification_complete):
        self.individual.open_kyc_form()
        self.individual.verify_kyc_client_id()

    def test_kyc_03_text_fields(self, kyc_verification_complete):
        self.individual.open_kyc_form()
        self.individual.verify_kyc_text_fields()

    def test_kyc_04_dropdowns(self, kyc_verification_complete):
        self.individual.open_kyc_form()
        self.individual.verify_kyc_dropdowns()

    def test_kyc_05_date_fields(self, kyc_verification_complete):
        self.individual.open_kyc_form()
        self.individual.verify_kyc_date_fields()

    def test_kyc_06_nationality_options(self, kyc_verification_complete):
        self.individual.open_kyc_form()
        self.individual.verify_kyc_nationality_options()

    def test_kyc_07_default_nationality(self, kyc_verification_complete):
        self.individual.open_kyc_form()
        self.individual.verify_kyc_single_nationality_default()

    def test_kyc_08_address_fields(self, kyc_verification_complete):
        self.individual.open_kyc_form()
        self.individual.verify_kyc_address_fields()

    def test_kyc_09_source_of_wealth(self, kyc_verification_complete):
        self.individual.open_kyc_form()
        self.individual.verify_kyc_source_of_wealth()

    def test_kyc_10_save_button(self, kyc_verification_complete):
        self.individual.open_kyc_form()
        self.individual.verify_kyc_save_button()


    # =========================================================
    # KYC FORM - SECTION 01: FUNCTIONAL TESTS (11-46)
    # =========================================================
    # Existing 01-10 tests remain unchanged.

    @pytest.fixture
    def kyc_ready(self, kyc_verification_complete):
        """Reuses successful Verification setup; opens KYC directly."""
        self.individual.open_kyc_form()
        self.individual.kyc_assert_loaded()

    def test_kyc_11_full_legal_name_entry(self, kyc_ready):
        self.individual.kyc_fill_text("full_name", "Automation Test Individual")

    def test_kyc_12_full_name_edit(self, kyc_ready):
        self.individual.kyc_fill_text("full_name", "Original Test Name")
        self.individual.kyc_fill_text("full_name", "Updated Test Name")

    def test_kyc_13_contact_number_entry(self, kyc_ready):
        self.individual.kyc_fill_text("contact", "+94771234567")

    def test_kyc_14_email_address_entry(self, kyc_ready):
        self.individual.kyc_fill_text("email", "kyc.automation@example.com")

    def test_kyc_15_document_number_entry(self, kyc_ready):
        self.individual.kyc_fill_text("document_number", "DOC123456789")

    def test_kyc_16_passport_number_entry(self, kyc_ready):
        self.individual.kyc_fill_text("passport_number", "N12345678")

    @pytest.mark.parametrize("field", [
        "full_name", "contact", "email", "document_number", "passport_number"
    ])
    def test_kyc_17_text_fields_can_be_cleared(self, kyc_ready, field):
        self.individual.kyc_fill_text(field, "Sample123")
        self.individual.kyc_clear_text(field)

    def test_kyc_18_both_addresses_accept_text(self, kyc_ready):
        self.individual.kyc_fill_address(0, "123 Main Street, Colombo, Sri Lanka")
        self.individual.kyc_fill_address(1, "45 Park Road, Kandy, Sri Lanka")

    def test_kyc_19_addresses_are_independent(self, kyc_ready):
        permanent = "Permanent Address Test"
        current = "Current Address Test"
        self.individual.kyc_fill_address(0, permanent)
        self.individual.kyc_fill_address(1, current)
        self.individual.kyc_address(0).clear()
        expect(self.individual.kyc_address(0)).to_have_value("")
        expect(self.individual.kyc_address(1)).to_have_value(current)

    def test_kyc_20_gender_dropdown_options(self, kyc_ready):
        _, options = self.individual.kyc_dropdown_options("Gender")
        assert options.count() >= 2, "Expected multiple Gender options"

    def test_kyc_21_gender_can_be_selected(self, kyc_ready):
        self.individual.kyc_choose_first_dropdown_option("Gender")

    def test_kyc_22_residency_country_options(self, kyc_ready):
        _, options = self.individual.kyc_dropdown_options("Country of Residency")
        assert options.count() > 0

    def test_kyc_23_residency_country_selection(self, kyc_ready):
        self.individual.kyc_choose_first_dropdown_option("Country of Residency", search="Sri")

    def test_kyc_24_nationality_country_selection(self, kyc_ready):
        self.individual.kyc_choose_first_dropdown_option(
            "Nationality 1", scope=self.individual.kyc_nationality_box, search="Sri"
        )

    def test_kyc_25_occupation_dropdown_options(self, kyc_ready):
        _, options = self.individual.kyc_dropdown_options("Occupation")
        assert options.count() > 0

    def test_kyc_26_occupation_can_be_selected(self, kyc_ready):
        self.individual.kyc_choose_first_dropdown_option("Occupation")

    def test_kyc_27_single_nationality_fields(self, kyc_ready):
        self.individual.kyc_choose_nationality_type("Single")
        expect(self.individual.kyc_nationality_selects()).to_have_count(1)
        expect(self.individual.kyc_passport_inputs()).to_have_count(1)

    def test_kyc_28_dual_nationality_fields(self, kyc_ready):
        self.individual.kyc_choose_nationality_type("Dual")
        expect(self.individual.kyc_nationality_selects()).to_have_count(2)
        expect(self.individual.kyc_passport_inputs()).to_have_count(2)

    def test_kyc_29_multiple_nationality_fields(self, kyc_ready):
        self.individual.kyc_choose_nationality_type("Multiple")
        assert self.individual.kyc_nationality_selects().count() >= 3
        assert self.individual.kyc_passport_inputs().count() >= 3

    def test_kyc_30_switch_nationality_back_to_single(self, kyc_ready):
        self.individual.kyc_choose_nationality_type("Dual")
        self.individual.kyc_choose_nationality_type("Single")
        expect(self.individual.kyc_nationality_selects()).to_have_count(1)
        expect(self.individual.kyc_passport_inputs()).to_have_count(1)

    def test_kyc_31_nationality_radio_exclusivity(self, kyc_ready):
        for kind in ("Dual", "Multiple", "Single"):
            self.individual.kyc_choose_nationality_type(kind)

    def test_kyc_32_dual_passport_numbers_independent(self, kyc_ready):
        self.individual.kyc_choose_nationality_type("Dual")
        inputs = self.individual.kyc_passport_inputs()
        inputs.nth(0).fill("P11111111")
        inputs.nth(1).fill("P22222222")
        expect(inputs.nth(0)).to_have_value("P11111111")
        expect(inputs.nth(1)).to_have_value("P22222222")

    def test_kyc_33_multiple_passport_numbers_independent(self, kyc_ready):
        self.individual.kyc_choose_nationality_type("Multiple")
        inputs = self.individual.kyc_passport_inputs()
        assert inputs.count() >= 3
        for index in range(3):
            inputs.nth(index).fill(f"P12345{index:03d}")
        for index in range(3):
            expect(inputs.nth(index)).to_have_value(f"P12345{index:03d}")

    @pytest.mark.parametrize("index", [0, 1, 2], ids=["dob", "issue", "expiry"])
    def test_kyc_34_date_calendar_opens(self, kyc_ready, index):
        self.individual.kyc_open_date_picker(index)

    @pytest.mark.parametrize("index", [0, 1, 2], ids=["dob", "issue", "expiry"])
    def test_kyc_35_date_can_be_selected(self, kyc_ready, index):
        chosen = self.individual.kyc_select_calendar_day(index)
        assert chosen, f"Date field {index} remained empty"

    def test_kyc_36_wealth_checkboxes_initially_clear(self, kyc_ready):
        assert self.individual.kyc_wealth_checked_values() == []

    def test_kyc_37_all_16_wealth_options_toggle(self, kyc_ready):

        for name in self.individual.KYC_WEALTH_OPTIONS:
            print(f"Testing Source of Wealth: {name}")

            # Select this option
            self.individual.kyc_set_wealth(name, True)

            expect(
                self.individual.kyc_wealth_input(name)
            ).to_be_checked()

            # Deselect this option
            self.individual.kyc_set_wealth(name, False)

            expect(
                self.individual.kyc_wealth_input(name)
            ).not_to_be_checked()

        # No options should remain checked
        assert self.individual.kyc_wealth_checked_values() == []

        print("All 16 Source of Wealth options toggled successfully.")

    def test_kyc_38_multiple_wealth_selections(self, kyc_ready):
        selected = ("Savings", "Business Income", "Investment Income")
        for name in selected:
            self.individual.kyc_set_wealth(name)
        assert set(self.individual.kyc_wealth_checked_values()) == set(selected)

    def test_kyc_39_uncheck_preserves_other_wealth(self, kyc_ready):
        self.individual.kyc_set_wealth("Savings")
        self.individual.kyc_set_wealth("Inheritance")
        self.individual.kyc_set_wealth("Savings", False)
        assert self.individual.kyc_wealth_checked_values() == ["Inheritance"]

    def test_kyc_40_other_wealth_option(self, kyc_ready):
        self.individual.kyc_set_wealth("Other")
        expect(self.individual.kyc_wealth_input("Other")).to_be_checked()

    def test_kyc_41_save_button_enabled(self, kyc_ready):
        expect(self.individual.kyc_save_button()).to_be_visible()
        expect(self.individual.kyc_save_button()).to_be_enabled()

    def test_kyc_42_save_action_on_populated_form(self, kyc_ready):
        # Save is intentionally last. Exact success/validation feedback
        # requires a captured post-save DOM snapshot to assert correctly.
        self.individual.kyc_fill_text("full_name", "Automation KYC Test")
        self.individual.kyc_fill_text("contact", "+94771234567")
        self.individual.kyc_fill_text("email", "kyc.automation@example.com")
        self.individual.kyc_fill_text("document_number", "DOC123456789")
        self.individual.kyc_fill_text("passport_number", "P12345678")
        self.individual.kyc_fill_address(0, "123 Main Street, Colombo")
        self.individual.kyc_fill_address(1, "123 Main Street, Colombo")
        self.individual.kyc_choose_first_dropdown_option("Gender")
        self.individual.kyc_choose_first_dropdown_option("Country of Residency", search="Sri")
        self.individual.kyc_choose_first_dropdown_option(
            "Nationality 1", scope=self.individual.kyc_nationality_box, search="Sri"
        )
        self.individual.kyc_choose_first_dropdown_option("Occupation")
        self.individual.kyc_set_wealth("Employment Income / Salary")
        self.individual.kyc_click_save()
        print("KYC save URL:", self.page.url)
        print("KYC save alerts:", self.page.get_by_role("alert").all_text_contents())
        print("KYC save page snapshot:", self.page.locator("main").aria_snapshot()[:5000])
        # Do not assert success until the actual application's Save response
        # (toast, modal, inline validation, or navigation) is confirmed.

    # ============================================================
    # RISK ASSESSMENT TESTS
    # ============================================================

    @pytest.fixture
    def risk_ready(self, kyc_verification_complete):
        self.individual.open_risk_assessment()

    def test_risk_01_page_loaded(self, risk_ready):
        expect(
            self.page.get_by_text(
                "Risk Assessment Summary",
                exact=True
            )
        ).to_be_visible()

        expect(
            self.individual.risk_complete_button()
        ).to_be_visible()

    def test_risk_02_all_five_groups_visible(self, risk_ready):
        for group_name in self.individual.RISK_OPTIONS:
            expect(
                self.individual.risk_group(group_name)
            ).to_be_visible()

    @pytest.mark.parametrize(
        "group_name",
        [
            "Country / Jurisdiction Risk",
            "Politically Exposed Person (PEP) Status",
            "Australian Residential Status",
            "Transfer of Funds",
            "Adverse Media",
        ]
    )
    def test_risk_03_radio_options_visible(
            self,
            risk_ready,
            group_name
    ):
        for value in self.individual.RISK_OPTIONS[group_name]:
            expect(
                self.individual.risk_radio(
                    group_name,
                    value
                )
            ).to_be_attached()

    def test_risk_04_initial_selections(self, risk_ready):
        expected = {
            "Country / Jurisdiction Risk": ["low"],
            "Politically Exposed Person (PEP) Status": ["nonPep"],
            "Australian Residential Status": [],
            "Transfer of Funds": ["bankTransfer"],
            "Adverse Media": ["noHits"],
        }

        for group_name, values in expected.items():
            assert (
                    self.individual.risk_selected_values(group_name)
                    == values
            )

    def test_risk_05_initial_score_and_rating(self, risk_ready):
        assert self.individual.risk_total_score() == 4
        assert self.individual.risk_classification() == "Low"

        self.individual.risk_verify_calculation()

    @pytest.mark.parametrize(
        "group_name,value",
        [
            ("Country / Jurisdiction Risk", "low"),
            ("Country / Jurisdiction Risk", "other"),
            ("Country / Jurisdiction Risk", "high"),
            ("Politically Exposed Person (PEP) Status", "nonPep"),
            ("Politically Exposed Person (PEP) Status", "associate"),
            ("Politically Exposed Person (PEP) Status", "pep"),
            ("Australian Residential Status", "residence"),
            ("Australian Residential Status", "nonResidence"),
            ("Transfer of Funds", "bankTransfer"),
            ("Transfer of Funds", "cash"),
            ("Adverse Media", "noHits"),
            ("Adverse Media", "confirmed"),
        ]
    )
    def test_risk_06_each_option_updates_score(
            self,
            risk_ready,
            group_name,
            value
    ):
        self.individual.risk_select(group_name, value)

        assert self.individual.risk_selected_values(
            group_name
        ) == [value]

        self.individual.risk_verify_calculation()

    @pytest.mark.parametrize(
        "group_name",
        [
            "Country / Jurisdiction Risk",
            "Politically Exposed Person (PEP) Status",
            "Australian Residential Status",
            "Transfer of Funds",
            "Adverse Media",
        ]
    )
    def test_risk_07_radio_selection_is_exclusive(
            self,
            risk_ready,
            group_name
    ):
        for value in self.individual.RISK_OPTIONS[group_name]:
            self.individual.risk_select(group_name, value)

            assert self.individual.risk_selected_values(
                group_name
            ) == [value]

    def test_risk_08_low_classification(self, risk_ready):

        selections = {
            "Country / Jurisdiction Risk": "low",
            "Politically Exposed Person (PEP) Status": "nonPep",
            "Australian Residential Status": "residence",
            "Transfer of Funds": "bankTransfer",
            "Adverse Media": "noHits",
        }

        print("\n========== BEFORE SELECTION ==========")

        for group_name in selections:
            print(
                f"{group_name}: "
                f"{self.individual.risk_selected_values(group_name)}"
            )

        print(
            f"Initial score: "
            f"{self.individual.risk_total_score()}"
        )

        print("\n========== SELECTING OPTIONS ==========")

        for group_name, value in selections.items():
            self.individual.risk_select(group_name, value)

            print(
                f"After selecting {group_name}: "
                f"Score={self.individual.risk_total_score()}"
            )

        print("\n========== FINAL SELECTIONS ==========")

        for group_name, expected_value in selections.items():
            actual_values = self.individual.risk_selected_values(
                group_name
            )

            print(
                f"{group_name}: "
                f"Expected={expected_value}, "
                f"Actual={actual_values}"
            )

            assert actual_values == [expected_value], (
                f"{group_name} changed unexpectedly: "
                f"{actual_values}"
            )

        expected_score = sum(
            self.individual.RISK_OPTIONS[group_name][value]
            for group_name, value in selections.items()
        )

        actual_score = self.individual.risk_total_score()

        print("\n========== FINAL CALCULATION ==========")
        print(f"Expected score: {expected_score}")
        print(f"Actual score: {actual_score}")
        print(
            f"Classification: "
            f"{self.individual.risk_classification()}"
        )

        assert actual_score == expected_score, (
            f"Incorrect risk calculation: "
            f"Expected {expected_score}, got {actual_score}"
        )

        assert self.individual.risk_classification() == "Low"

    def test_risk_09_medium_classification(self, risk_ready):

        self.individual.risk_select_multiple({
            "Australian Residential Status": "residence",
            "Transfer of Funds": "bankTransfer",
            "Adverse Media": "noHits",
            "Politically Exposed Person (PEP) Status": "associate",
            "Country / Jurisdiction Risk": "other",
        })

        assert self.individual.risk_total_score() == 9

        assert self.individual.risk_classification() == "Medium"

    def test_risk_10_high_classification(self, risk_ready):

        self.individual.risk_select_multiple({
            "Politically Exposed Person (PEP) Status": "pep",
            "Australian Residential Status": "nonResidence",
            "Transfer of Funds": "cash",
            "Adverse Media": "confirmed",
            "Country / Jurisdiction Risk": "high",
        })

        self.individual.risk_debug_all_selections()

        assert self.individual.risk_total_score() == 19
        assert self.individual.risk_classification() == "High"

    def test_risk_11_complete_onboarding_button_visible(
            self,
            risk_ready
    ):
        expect(
            self.individual.risk_complete_button()
        ).to_be_visible()

    def test_risk_11_complete_onboarding(self, risk_ready):

        # Verify Complete Onboarding is available.
        expect(
            self.individual.risk_complete_button()
        ).to_be_visible()

        expect(
            self.individual.risk_complete_button()
        ).to_be_enabled()

        # Complete onboarding.
        self.individual.risk_complete_onboarding()

        # Verify the button changes to Update Changes.
        self.individual.risk_verify_onboarding_completed()

    def test_risk_12_update_changes_after_completion(
            self,
            risk_ready
    ):

        # Step 1: Complete onboarding.
        self.individual.risk_complete_onboarding()

        # Step 2: Verify Update Changes appears.
        self.individual.risk_verify_onboarding_completed()

        # Step 3: Change all risk factors to Low.
        low_risk_selections = {
            "Australian Residential Status": "residence",
            "Transfer of Funds": "bankTransfer",
            "Adverse Media": "noHits",
            "Politically Exposed Person (PEP) Status": "nonPep",
            "Country / Jurisdiction Risk": "low",
        }

        self.individual.risk_select_multiple(
            low_risk_selections
        )

        # Step 4: Verify score and classification before saving.
        self.individual.risk_verify_selected_values(
            low_risk_selections
        )

        assert self.individual.risk_total_score() == 5
        assert self.individual.risk_classification() == "Low"

        # Step 5: Click Update Changes.
        self.individual.risk_click_update_changes()

        # Step 6: Verify success notification.
        self.individual.risk_verify_update_success_notification()

        # Step 7: Verify the updated values remain correct.
        self.individual.risk_verify_selected_values(
            low_risk_selections
        )

        assert self.individual.risk_total_score() == 5
        assert self.individual.risk_classification() == "Low"

        # Step 8: Verify Update Changes remains available.
        expect(
            self.individual.risk_update_changes_button()
        ).to_be_visible()

        print(
            "Risk 12 PASSED: Risk assessment changes "
            "saved successfully."
        )

    def test_risk_13_update_low_to_high_classification(
            self,
            risk_ready
    ):
        # Step 1: Set the initial risk assessment to Low.
        low_risk_selections = {
            "Australian Residential Status": "residence",
            "Transfer of Funds": "bankTransfer",
            "Adverse Media": "noHits",
            "Politically Exposed Person (PEP) Status": "nonPep",
            "Country / Jurisdiction Risk": "low",
        }

        self.individual.risk_select_multiple(low_risk_selections)

        self.individual.risk_verify_selected_values(
            low_risk_selections
        )

        assert self.individual.risk_total_score() == 5
        assert self.individual.risk_classification() == "Low"

        print("Initial risk assessment verified: Score=5, Low")

        # Step 2: Complete onboarding.
        self.individual.risk_complete_onboarding()

        self.individual.risk_verify_onboarding_completed()

        print("Onboarding completed successfully.")

        # Step 3: Change the risk assessment to High.
        high_risk_selections = {
            "Australian Residential Status": "nonResidence",
            "Transfer of Funds": "cash",
            "Adverse Media": "confirmed",
            "Politically Exposed Person (PEP) Status": "pep",
            "Country / Jurisdiction Risk": "high",
        }

        self.individual.risk_select_multiple(high_risk_selections)

        # Step 4: Verify all High-risk selections.
        self.individual.risk_verify_selected_values(
            high_risk_selections
        )

        # Step 5: Verify updated score and classification.
        assert self.individual.risk_total_score() == 19
        assert self.individual.risk_classification() == "High"

        print("Updated risk assessment verified: Score=19, High")

        # Step 6: Save the changes using Update Changes.
        self.individual.risk_click_update_changes()

        # Step 7: Verify success notification.
        self.individual.risk_verify_update_success_notification()

        # Step 8: Verify values remain correct after update.
        self.individual.risk_verify_selected_values(
            high_risk_selections
        )

        assert self.individual.risk_total_score() == 19
        assert self.individual.risk_classification() == "High"

        # Step 9: Verify Update Changes remains available.
        expect(
            self.individual.risk_update_changes_button()
        ).to_be_visible(timeout=15000)

        print(
            "Risk 13 PASSED: Risk assessment updated "
            "from Low (5) to High (19) successfully."
        )

    def test_risk_14_saved_risk_persists_after_reopening(
            self,
            risk_ready
    ):

        # Step 1: Capture the Client ID.
        client_id = self.individual.risk_get_current_client_id()

        # Step 2: Set all risk factors to Low.
        low_risk_selections = {
            "Australian Residential Status": "residence",
            "Transfer of Funds": "bankTransfer",
            "Adverse Media": "noHits",
            "Politically Exposed Person (PEP) Status": "nonPep",
            "Country / Jurisdiction Risk": "low",
        }

        self.individual.risk_select_multiple(low_risk_selections)

        assert self.individual.risk_total_score() == 5
        assert self.individual.risk_classification() == "Low"

        # Step 3: Complete onboarding.
        self.individual.risk_complete_onboarding()

        self.individual.risk_verify_onboarding_completed()

        # Step 4: Change risk factors to High.
        high_risk_selections = {
            "Australian Residential Status": "nonResidence",
            "Transfer of Funds": "cash",
            "Adverse Media": "confirmed",
            "Politically Exposed Person (PEP) Status": "pep",
            "Country / Jurisdiction Risk": "high",
        }

        self.individual.risk_select_multiple(high_risk_selections)

        self.individual.risk_verify_selected_values(
            high_risk_selections
        )

        assert self.individual.risk_total_score() == 19
        assert self.individual.risk_classification() == "High"

        # Step 5: Save using Update Changes.
        self.individual.risk_click_update_changes()

        self.individual.risk_verify_update_success_notification()

        print("High-risk assessment saved successfully.")

        # Step 6: Navigate to Profiles.
        self.individual.profiles_open_page()

        # Step 7: Verify the same client appears with High risk.
        self.individual.profiles_verify_client_risk(
            client_id,
            "High"
        )

        # Step 8: Open the individual.
        self.individual.profiles_open_individual(client_id)

        # Step 9: Navigate to Risk Assessment.
        self.individual.open_risk_assessment()

        # Step 10: Verify saved selections after reopening.
        self.individual.risk_verify_selected_values(
            high_risk_selections
        )

        # Step 11: Verify saved score and classification.
        assert self.individual.risk_total_score() == 19

        assert self.individual.risk_classification() == "High"

        self.individual.risk_verify_calculation()

        print(
            f"Risk 14 PASSED: Client {client_id} retained "
            f"High-risk selections and score 19 after reopening."
        )

    def test_risk_15_profile_verification_details_after_onboarding(
            self,
            risk_ready
    ):

        # Step 1: Capture the current Client ID.
        client_id = self.individual.risk_get_current_client_id()

        # Step 2: Complete onboarding.
        self.individual.risk_complete_onboarding()

        # Step 3: Verify onboarding completed.
        self.individual.risk_verify_onboarding_completed()

        print("Individual onboarding completed successfully.")

        # Step 4: Navigate to Profiles.
        self.individual.profiles_open_page()

        # Step 5: Search for the newly onboarded client.
        self.individual.profiles_search_client(client_id)

        # Step 6: Open the individual profile.
        self.individual.profiles_open_individual(client_id)

        # Step 7: Verify Profile - Individual page.
        self.individual.profile_verify_verification_page(
            client_id
        )

        # Step 8: Verify all processed details.
        self.individual.profile_verify_processed_details()

        # Step 9: Verify uploaded images.
        self.individual.profile_verify_document_images()

        print(
            f"Risk 15 PASSED: Verification details and "
            f"images displayed after reopening client {client_id}."
        )

    def test_risk_16_verification_details_persist(
            self,
            risk_ready
    ):
        client_id = self.individual.risk_get_current_client_id()

        original_details = self.original_verification_details

        assert original_details, (
            "Original extracted verification details were not captured."
        )

        # Complete onboarding.
        self.individual.risk_complete_onboarding()
        self.individual.risk_verify_onboarding_completed()

        # Reopen the same individual through Profiles.
        self.individual.profiles_open_page()
        self.individual.profiles_search_client(client_id)
        self.individual.profiles_open_individual(client_id)

        self.individual.profile_verify_verification_page(client_id)

        # Capture the saved values.
        saved_details = (
            self.individual.verification_capture_processed_details()
        )

        # Compare original and saved values.
        self.individual.verification_compare_processed_details(
            original_details,
            saved_details
        )

        print(
            f"Risk 16 PASSED: Original and saved verification "
            f"details match for client {client_id}."
        )

    def test_risk_16_verification_details_persist(
            self,
            risk_ready
    ):
        # Original values were captured during
        # prepare_review_extracted_information().
        original_details = self.original_verification_details

        assert original_details, (
            "Original extracted verification details were not captured."
        )

        client_id = self.individual.risk_get_current_client_id()

        # Complete onboarding.
        self.individual.risk_complete_onboarding()
        self.individual.risk_verify_onboarding_completed()

        # Navigate to Profiles.
        self.individual.profiles_open_page()

        # Find and open the same individual.
        self.individual.profiles_search_client(client_id)
        self.individual.profiles_open_individual(client_id)

        # Verify the saved profile's Verification page.
        self.individual.profile_verify_verification_page(client_id)

        # Capture saved processed details.
        saved_details = (
            self.individual.verification_capture_processed_details()
        )

        # Compare original and saved values.
        self.individual.verification_compare_review_to_profile(
            original_details,
            saved_details
        )

        print("Risk 16 PASSED: Verification details persisted.")

