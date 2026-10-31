
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

