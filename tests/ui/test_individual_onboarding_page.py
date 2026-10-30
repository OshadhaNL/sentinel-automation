
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

        # Complete verification
        self.individual.capture_and_verify_photo()
        self.individual.select_document_type("Driver Licence")

        self.individual.upload_document_front(front_file)
        self.individual.upload_document_back(back_file)

        self.individual.click_verification_submit()
        self.individual.verify_review_extracted_information_screen()

        # Verify editable personal information
        expect(
            self.page.get_by_role("textbox", name="First Name")
        ).to_be_visible()

        expect(
            self.page.get_by_role("textbox", name="Last Name")
        ).to_be_visible()

        expect(
            self.page.get_by_role("textbox", name="Date of Birth")
        ).to_be_visible()

        # Verify document information
        for field in [
            "Driver Licence Number",
            "Personal Number",
            "Issue Date",
            "Expiry Date",
            "Place of Birth"
        ]:
            expect(
                self.page.get_by_role("textbox", name=field, exact=True)
            ).to_be_visible()

        # Verify residential address checkbox
        expect(
            self.page.get_by_role(
                "checkbox",
                name="My residential address is different"
            )
        ).to_be_visible()

        # Verify Save & Confirm
        expect(
            self.page.get_by_role(
                "button",
                name="Save & Confirm",
                exact=True
            )
        ).to_be_visible()
