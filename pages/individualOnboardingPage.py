
import re
from playwright.sync_api import Page, expect
from pathlib import Path

class IndividualOnboardingPage:

    TAB_ICONS = {
        "Verification": "fa-webcam",
        "Documents": "fa-folder-open",
        "Screening": "fa-globe-americas",
        "KYC Form": "fa-user-check",
        "Risk Assessment": "fa-shield-check",
    }

    def __init__(self, page: Page):
        self.page = page

        # =====================================================
        # PAGE HEADER
        # =====================================================

        self.back_button = page.get_by_role(
            "button", name="Back"
        )

        self.page_heading = page.get_by_role(
            "heading",
            name="Individual Onboarding",
            exact=True
        )

        self.page_description = page.get_by_text(
            "Capture and manage individual information to initiate "
            "onboarding and compliance workflows.",
            exact=True
        )

        # =====================================================
        # MAIN NAVIGATION TABS
        # =====================================================

        # Scope to the main Individual Onboarding navigation.
        # This avoids matching nested Screening tabs.
        self.tab_container = page.locator(
            ".tab-z.my-4 > .tab-z-labels"
        )

        self.tabs = self.tab_container.locator(
            ":scope > .tab-z-option"
        )

        self.verification_tab = self.tab("Verification")
        self.documents_tab = self.tab("Documents")
        self.screening_tab = self.tab("Screening")
        self.kyc_tab = self.tab("KYC Form")
        self.risk_assessment_tab = self.tab("Risk Assessment")

        # =====================================================
        # NAVIGATION ICONS
        # =====================================================

        self.verification_icon = self.verification_tab.locator(
            "i.fa-webcam"
        )

        self.documents_icon = self.documents_tab.locator(
            "i.fa-folder-open"
        )

        self.screening_icon = self.screening_tab.locator(
            "i.fa-globe-americas"
        )

        self.kyc_icon = self.kyc_tab.locator(
            "i.fa-user-check"
        )

        self.risk_assessment_icon = (
            self.risk_assessment_tab.locator(
                "i.fa-shield-check"
            )
        )

        # =====================================================
        # LIVE PHOTO - CAMERA WARNING POPUP
        # =====================================================

        self.live_photo_heading = page.get_by_role(
            "heading", name="Live Photo", exact=True
        )

        self.take_photo_heading = page.get_by_role(
            "heading", name="Tap To Take A Photo", exact=True
        )

        self.camera_warning_popup = page.locator(
            ".webcam-card:has(.webcam-denied)"
        )

        self.camera_warning_content = (
            self.camera_warning_popup.locator(".webcam-denied")
        )

        self.camera_warning_heading = (
            self.camera_warning_content.get_by_role(
                "heading", name="Before You Continue", exact=True
            )
        )

        self.camera_warning_message = (
            self.camera_warning_content.locator("p")
        )

        self.camera_warning_icon = (
            self.camera_warning_content.locator(
                "i.fa-exclamation-triangle"
            )
        )

        self.camera_understand_button = (
            self.camera_warning_popup.get_by_role(
                "button", name="I Understand", exact=True
            )
        )

        self.camera_close_button = (
            self.camera_warning_popup.locator("button.close-btn")
        )

        self.camera_close_icon = (
            self.camera_close_button.locator(
                "i.fa-times-circle"
            )
        )

        # =====================================================
        # LIVE CAMERA STREAM
        # =====================================================

        self.camera_stream_popup = page.locator(
            ".webcam-card:not(.doc-webcam-card):has(.webcam-stream)"
        )

        self.camera_stream = (
            self.camera_stream_popup.locator(".webcam-stream")
        )

        self.camera_instruction = (
            self.camera_stream.locator(".note-text")
        )

        self.camera_video = (
            self.camera_stream.locator("video")
        )

        self.camera_positioning_guide = (
            self.camera_stream.locator(".safe-line-wrapper")
        )

        self.camera_positioning_lines = (
            self.camera_positioning_guide.locator(".safe-line")
        )

        self.take_photo_button = (
            self.camera_stream.get_by_role(
                "button"
            ).filter(
                has=page.locator("i.fa-expand")
            )
        )

        self.take_photo_icon = (
            self.take_photo_button.locator("i.fa-expand")
        )

        self.camera_stream_close_button = (
            self.camera_stream_popup.locator("button.close-btn")
        )

        # Captured Live Photo
        self.captured_photo_container = page.locator(
            ".uploader.photo-upload"
        )

        self.captured_photo = (
            self.captured_photo_container.locator("img.user-photo")
        )

        self.invalid_photo_message = page.get_by_text(
            "Random Image Detected. Please upload a valid photo.",
            exact=True
        ).first

        # Live Photo recapture controls
        self.recapture_button = self.captured_photo_container.locator(
            "button.recapture-btn"
        )

        self.recapture_icon = self.recapture_button.locator(
            "i.fa-crosshairs"
        )

        # Document Type section
        self.document_type_heading = page.get_by_role(
            "heading",
            name="Type of Document",
            exact=True
        )

        self.document_type_description = page.get_by_text(
            "Select the type of document you will be uploading",
            exact=True
        )

        self.passport_radio = page.get_by_role(
            "radio",
            name="Passport",
            exact=True
        )

        self.driver_licence_radio = page.get_by_role(
            "radio",
            name="Driver Licence",
            exact=True
        )

        self.proof_of_age_radio = page.get_by_role(
            "radio",
            name="Proof of Age Card",
            exact=True
        )

        # Document Front
        self.document_front_heading = page.get_by_role(
            "heading", name="Document Front", exact=True
        )

        self.document_front_description = page.get_by_text(
            "Upload a clear image of the front side of your document.",
            exact=True
        )

        self.document_front_input = page.locator(
            'input[type="file"][name="doc-front"]'
        )

        self.document_front_wrapper = page.locator(
            'input[name="doc-front"]'
        ).locator("xpath=..")

        self.document_front_upload_icon = (
            self.document_front_wrapper.locator("i.fa-file-upload")
        )

        # Document Back
        self.document_back_heading = page.get_by_role(
            "heading", name="Document Back", exact=True
        )

        self.document_back_description = page.get_by_text(
            "Upload a clear image of the back side of your document.",
            exact=True
        )

        self.document_back_input = page.locator(
            'input[type="file"][name="doc-back"]'
        )

        self.document_back_wrapper = page.locator(
            'input[name="doc-back"]'
        ).locator("xpath=..")

        self.document_back_upload_icon = (
            self.document_back_wrapper.locator("i.fa-file-upload")
        )

        self.document_front_section = page.locator(
            "div.custom-border-bottom"
        ).filter(
            has=page.get_by_role(
                "heading", name="Document Front", exact=True
            )
        )

        self.document_back_section = page.locator(
            "div.custom-border-bottom"
        ).filter(
            has=page.get_by_role(
                "heading", name="Document Back", exact=True
            )
        )

        # Uploaded file cards
        self.document_front_uploaded_file = (
            self.document_front_section.locator(".uploaded-file")
        )

        self.document_back_uploaded_file = (
            self.document_back_section.locator(".uploaded-file")
        )

        # Uploaded filenames
        self.document_front_filename = (
            self.document_front_uploaded_file.locator("h6")
        )

        self.document_back_filename = (
            self.document_back_uploaded_file.locator("h6")
        )

        # File sizes
        self.document_front_file_size = (
            self.document_front_uploaded_file.locator("p")
        )

        self.document_back_file_size = (
            self.document_back_uploaded_file.locator("p")
        )

        # File icons
        self.document_front_file_icon = (
            self.document_front_uploaded_file.locator(
                ".file-icon i.fa-file-upload"
            )
        )

        self.document_back_file_icon = (
            self.document_back_uploaded_file.locator(
                ".file-icon i.fa-file-upload"
            )
        )

        # Remove controls
        self.document_front_remove_button = (
            self.document_front_uploaded_file.locator(".remove-btn")
        )

        self.document_back_remove_button = (
            self.document_back_uploaded_file.locator(".remove-btn")
        )

        # Remove icons
        self.document_front_remove_icon = (
            self.document_front_remove_button.locator("i.fa-times-circle")
        )

        self.document_back_remove_icon = (
            self.document_back_remove_button.locator("i.fa-times-circle")
        )

        # Verification action buttons
        self.verification_reset_button = page.get_by_role(
            "button", name="Reset", exact=True
        )

        self.verification_submit_button = page.get_by_role(
            "button", name="Submit", exact=True
        )

        # Successful verification submission notification
        self.verification_success_notification = page.locator(
            ".ant-notification-notice-success"
        ).filter(
            has_text="Documents submitted successfully"
        )

        # Review Extracted Information screen
        self.review_extracted_information_heading = page.get_by_text(
            "Review Extracted Information",
            exact=True
        )

        self.review_extracted_information_description = page.get_by_text(
            "Please review the information extracted from your document. Correct any errors before proceeding.",
            exact=True
        )

        # Review Extracted Information labels

        self.extracted_first_name_label = page.locator(
            "label"
        ).filter(has_text=re.compile(r"^\s*First Name\s*$"))

        self.extracted_last_name_label = page.locator(
            "label"
        ).filter(has_text=re.compile(r"^\s*Last Name\s*$"))

        self.extracted_dob_label = page.locator(
            "label"
        ).filter(has_text=re.compile(r"^\s*Date of Birth\s*$"))

        self.extracted_gender_label = page.locator(
            "label"
        ).filter(has_text=re.compile(r"^\s*Gender\s*$"))

        self.extracted_nationality_label = page.locator(
            "label"
        ).filter(has_text=re.compile(r"^\s*Nationality\s*$"))

        self.extracted_issuing_country_label = page.locator(
            "label"
        ).filter(has_text=re.compile(r"^\s*Issuing Country\s*$"))


    # =========================================================
    # REUSABLE TAB LOCATOR
    # =========================================================

    def tab(self, tab_name: str):
        if tab_name not in self.TAB_ICONS:
            raise ValueError(
                f"Unknown navigation tab: {tab_name}"
            )

        # Exact text matching prevents Screening from
        # matching Single Screening or Daily Screening.
        return self.tabs.filter(
            has=self.page.locator("label").get_by_text(
                tab_name,
                exact=True
            )
        )

    # =========================================================
    # PAGE LOADED VERIFICATION
    # =========================================================

    def verify_page_loaded(self):
        expect(self.page).to_have_url(
            re.compile(
                r".*/nolimit/app/onboarding/individual/process"
                r"\?(?=[^#]*\bstep=verification(?:&|$)).+"
            ),
            timeout=30000
        )

        expect(self.page_heading).to_be_visible(
            timeout=15000
        )

    # =========================================================
    # PAGE HEADER VERIFICATION
    # =========================================================

    def verify_page_header(self):
        expect(self.back_button).to_be_visible()
        expect(self.page_heading).to_be_visible()
        expect(self.page_description).to_be_visible()

    # =========================================================
    # NAVIGATION TABS VERIFICATION
    # =========================================================

    def verify_navigation_tabs(self):
        expect(self.tabs).to_have_count(5)

        for tab_name in self.TAB_ICONS:
            expect(self.tab(tab_name)).to_be_visible()

    def verify_all_tabs(self):
        self.verify_navigation_tabs()

    # =========================================================
    # NAVIGATION ICONS VERIFICATION
    # =========================================================

    def verify_navigation_icons(self):
        for tab_name, icon_class in self.TAB_ICONS.items():
            icon = self.tab(tab_name).locator(
                f"i.{icon_class}"
            )
            expect(icon).to_be_visible()

    def verify_all_icons(self):
        self.verify_navigation_icons()

    # =========================================================
    # ACTIVE TAB VERIFICATION
    # =========================================================

    def verify_active_tab(self, tab_name: str):
        if tab_name not in self.TAB_ICONS:
            raise ValueError(
                f"Unknown navigation tab: {tab_name}"
            )

        for name in self.TAB_ICONS:
            current_tab = self.tab(name)

            if name == tab_name:
                expect(current_tab).to_have_class(
                    re.compile(r"\bactive\b")
                )
            else:
                expect(current_tab).not_to_have_class(
                    re.compile(r"\bactive\b")
                )

    def verify_default_active_tab(self):
        self.verify_active_tab("Verification")

    # =========================================================
    # NAVIGATION ACTIONS
    # =========================================================

    def open_tab(self, tab_name: str):
        target_tab = self.tab(tab_name)

        expect(target_tab).to_be_visible()
        target_tab.click()

        self.verify_active_tab(tab_name)

    def click_tab(self, tab_name: str):
        self.open_tab(tab_name)

    # =========================================================
    # BACK BUTTON NAVIGATION
    # =========================================================

    def click_back(self):
        expect(self.back_button).to_be_visible()
        self.back_button.click()

        # Application returns to New Onboarding.
        expect(self.page).to_have_url(
            re.compile(
                r".*/nolimit/app/onboarding/?"
                r"(?:\?step=new)?$"
            ),
            timeout=15000
        )

        expect(
            self.page.get_by_role(
                "heading",
                name="Onboarding",
                exact=True
            )
        ).to_be_visible()

    # =========================================================
    # LIVE PHOTO - CAMERA WARNING ACTIONS AND ASSERTIONS
    # =========================================================

    def open_camera_warning(self):
        expect(self.take_photo_heading).to_be_visible()
        self.take_photo_heading.click()

        expect(self.camera_warning_popup).to_be_visible()

    def verify_camera_warning_popup(self):
        expect(self.camera_warning_popup).to_be_visible()
        expect(self.camera_warning_heading).to_be_visible()

        expect(self.camera_warning_message).to_have_text(
            "Please remove any obstacles such as glasses, "
            "hats/caps, and face masks before capturing "
            "your live image."
        )

        expect(self.camera_warning_icon).to_be_visible()
        expect(self.camera_understand_button).to_be_visible()
        expect(self.camera_close_button).to_be_visible()
        expect(self.camera_close_icon).to_be_visible()

    def close_camera_warning(self):
        self.camera_close_button.click()
        expect(self.camera_warning_popup).to_be_hidden()

    def accept_camera_warning(self):
        self.camera_understand_button.click()
        expect(self.camera_warning_content).to_be_hidden()

    # =========================================================
    # LIVE CAMERA STREAM ACTIONS AND ASSERTIONS
    # =========================================================

    def open_live_camera(self):
        self.open_camera_warning()
        self.accept_camera_warning()

        expect(
            self.camera_stream_popup
        ).to_have_count(1)

        expect(
            self.camera_stream_popup
        ).to_be_visible(timeout=15000)

        expect(
            self.camera_video
        ).to_be_visible(timeout=15000)

    def verify_live_camera_interface(self):
        # Verify live camera popup
        expect(self.camera_stream_popup).to_be_visible()

        # Verify camera stream section
        expect(self.camera_stream).to_be_visible()

        # Verify instruction text
        expect(self.camera_instruction).to_have_text(
            "Position your face in the frame"
        )

        # Verify camera video
        expect(self.camera_video).to_be_visible()

        # Verify positioning guide exists in the DOM
        expect(self.camera_positioning_guide).to_have_count(1)

        # Verify four positioning lines exist
        expect(self.camera_positioning_lines).to_have_count(4)

        # Verify capture button
        expect(self.take_photo_button).to_be_visible()
        expect(self.take_photo_button).to_be_enabled()

        # Verify capture icon
        expect(self.take_photo_icon).to_be_visible()

        # Verify close button
        expect(self.camera_stream_close_button).to_be_visible()

    def verify_camera_video_playing(self):
        expect(self.camera_video).to_be_visible()

        expect(self.camera_video).to_have_js_property(
            "paused", False
        )

        expect(self.camera_video).to_have_js_property(
            "ended", False
        )

    def capture_live_photo(self):
        expect(self.take_photo_button).to_be_enabled()
        self.take_photo_button.click()

    def close_live_camera(self):
        self.camera_stream_close_button.click()

        expect(self.camera_stream_popup).to_be_hidden()

    def capture_and_verify_photo(self):
        self.open_live_camera()

        # Verify the real webcam is ready
        self.verify_real_camera_ready()

        # Give the user time to face the camera
        print("\nCamera is ready.")
        print("Look directly at the camera.")
        print("Keep your face centered and still.")
        print("Photo will be captured in 5 seconds.\n")

        self.page.wait_for_timeout(5000)

        # Capture photo
        expect(self.take_photo_button).to_be_visible()
        expect(self.take_photo_button).to_be_enabled()

        self.take_photo_button.click()

        # Verify captured photo
        try:
            expect(self.captured_photo).to_be_visible(
                timeout=30000
            )
        except AssertionError:
            errors = self.get_photo_validation_error()
            raise AssertionError(
                f"Live photo was not accepted by Sentinel. "
                f"Validation errors: {errors}"
            )

        expect(self.captured_photo).to_have_attribute(
            "src",
            re.compile(r"^data:image/jpeg;base64,")
        )

    def verify_captured_photo_loaded(self):
        expect(self.captured_photo).to_be_visible()

        expect(self.captured_photo).to_have_attribute(
            "title", "Click to preview"
        )

        expect(self.captured_photo).to_have_js_property(
            "complete", True
        )

        assert self.captured_photo.evaluate(
            "(img) => img.naturalWidth > 0 && img.naturalHeight > 0"
        ), "Captured photo was not loaded correctly"

    def verify_invalid_photo_rejected(self):
        self.open_live_camera()

        expect(self.take_photo_button).to_be_visible()
        self.take_photo_button.click()

        expect(
            self.invalid_photo_message
        ).to_be_visible(timeout=20000)

        expect(
            self.captured_photo
        ).to_have_count(0)

    def verify_real_camera_ready(self):
        expect(self.camera_video).to_be_visible(timeout=15000)

        expect(self.camera_video).to_have_js_property(
            "paused", False
        )

        self.page.wait_for_function(
            """() => {
                const video = document.querySelector(
                    '.webcam-card:not(.doc-webcam-card) .webcam-stream video'
                );

                return video &&
                    video.readyState >= 2 &&
                    video.videoWidth > 0 &&
                    video.videoHeight > 0 &&
                    video.srcObject &&
                    video.srcObject.getVideoTracks().some(
                        track => track.readyState === 'live'
                    );
            }""",
            timeout=20000
        )

    def click_captured_photo(self):
        expect(self.captured_photo).to_be_visible()
        self.captured_photo.click()

    def verify_captured_photo_preview_attribute(self):
        expect(self.captured_photo).to_have_attribute(
            "title", "Click to preview"
        )

    def get_photo_validation_error(self):
        return self.page.locator(
            "p"
        ).filter(
            has_text=re.compile(
                r"Face is sideways|Random Image Detected|"
                r"Please face the camera"
            )
        ).all_text_contents()

    def verify_recapture_button(self):
        expect(self.captured_photo).to_be_visible()
        expect(self.recapture_button).to_be_visible()
        expect(self.recapture_button).to_be_enabled()
        expect(self.recapture_icon).to_be_visible()

    def click_recapture(self):
        self.verify_recapture_button()
        self.recapture_button.click()

    def verify_document_type_section(self):
        expect(self.document_type_heading).to_be_visible()
        expect(self.document_type_description).to_be_visible()

    def verify_document_type_options(self):
        for radio in [
            self.passport_radio,
            self.driver_licence_radio,
            self.proof_of_age_radio
        ]:
            expect(radio).to_be_visible()
            expect(radio).to_be_enabled()

    def verify_document_type_initially_unselected(self):
        for radio in [
            self.passport_radio,
            self.driver_licence_radio,
            self.proof_of_age_radio
        ]:
            expect(radio).not_to_be_checked()

    def select_document_type(self, document_type):
        options = {
            "Passport": self.passport_radio,
            "Driver Licence": self.driver_licence_radio,
            "Proof of Age Card": self.proof_of_age_radio
        }

        if document_type not in options:
            raise ValueError(
                f"Unsupported document type: {document_type}"
            )

        options[document_type].check()
        expect(options[document_type]).to_be_checked()

    def verify_only_document_type_selected(self, document_type):
        options = {
            "Passport": self.passport_radio,
            "Driver Licence": self.driver_licence_radio,
            "Proof of Age Card": self.proof_of_age_radio
        }

        for name, radio in options.items():
            if name == document_type:
                expect(radio).to_be_checked()
            else:
                expect(radio).not_to_be_checked()

    def verify_document_front_section(self):
        expect(self.document_front_heading).to_be_visible()
        expect(self.document_front_description).to_be_visible()
        expect(self.document_front_wrapper).to_be_visible()
        expect(self.document_front_upload_icon).to_be_visible()

        expect(self.document_front_input).to_have_attribute(
            "accept", "image/*"
        )

        expect(self.document_front_input).to_have_attribute(
            "type", "file"
        )

    def verify_document_back_section(self):
        expect(self.document_back_heading).to_be_visible()
        expect(self.document_back_description).to_be_visible()
        expect(self.document_back_wrapper).to_be_visible()
        expect(self.document_back_upload_icon).to_be_visible()

        expect(self.document_back_input).to_have_attribute(
            "accept", "image/*"
        )

        expect(self.document_back_input).to_have_attribute(
            "type", "file"
        )

    def upload_document_front(self, file_path):
        file_path = Path(file_path).resolve()

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Document Front file not found: {file_path}"
            )

        self.document_front_input.set_input_files(str(file_path))

    def upload_document_back(self, file_path):
        file_path = Path(file_path).resolve()

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Document Back file not found: {file_path}"
            )

        self.document_back_input.set_input_files(str(file_path))

    def verify_document_front_uploaded(self, expected_filename):
        expect(
            self.document_front_uploaded_file
        ).to_be_visible(timeout=15000)

        expect(
            self.document_front_filename
        ).to_have_text(expected_filename)

        expect(
            self.document_front_file_size
        ).to_have_text(
            re.compile(r"^\d+(?:\.\d+)?\s*(?:B|KB|MB)$")
        )

        expect(self.document_front_file_icon).to_be_visible()
        expect(self.document_front_remove_button).to_be_visible()
        expect(self.document_front_remove_icon).to_be_visible()

    def verify_document_back_uploaded(self, expected_filename):
        expect(
            self.document_back_uploaded_file
        ).to_be_visible(timeout=15000)

        expect(
            self.document_back_filename
        ).to_have_text(expected_filename)

        expect(
            self.document_back_file_size
        ).to_have_text(
            re.compile(r"^\d+(?:\.\d+)?\s*(?:B|KB|MB)$")
        )

        expect(self.document_back_file_icon).to_be_visible()
        expect(self.document_back_remove_button).to_be_visible()
        expect(self.document_back_remove_icon).to_be_visible()

    def remove_document_front(self):
        expect(self.document_front_remove_button).to_be_visible()
        self.document_front_remove_button.click()

        expect(self.document_front_uploaded_file).to_have_count(0)
        expect(self.document_front_input).to_have_count(1)

    def remove_document_back(self):
        expect(self.document_back_remove_button).to_be_visible()
        self.document_back_remove_button.click()

        expect(self.document_back_uploaded_file).to_have_count(0)
        expect(self.document_back_input).to_have_count(1)

    def upload_invalid_document_front(self, file_path):
        self.document_front_input.set_input_files(str(file_path))

    def upload_invalid_document_back(self, file_path):
        self.document_back_input.set_input_files(str(file_path))

    def verify_invalid_document_front_rejected(self):
        expect(
            self.document_front_uploaded_file
        ).to_have_count(0)

        expect(
            self.document_front_section.get_by_text(
                "Invalid file type. Allowed types are JPG, PNG, and SVG.",
                exact=True
            )
        ).to_be_visible()

        expect(
            self.document_front_input
        ).to_have_count(1)

    def verify_invalid_document_back_rejected(self):
        expect(
            self.document_back_uploaded_file
        ).to_have_count(0)

        expect(
            self.document_back_section.get_by_text(
                "Invalid file type. Allowed types are JPG, PNG, and SVG.",
                exact=True
            )
        ).to_be_visible()

        expect(
            self.document_back_input
        ).to_have_count(1)

    def verify_verification_action_buttons(self):
        expect(self.verification_reset_button).to_be_visible()
        expect(self.verification_submit_button).to_be_visible()

    def verify_verification_buttons_enabled(self):
        expect(self.verification_reset_button).to_be_enabled()
        expect(self.verification_submit_button).to_be_enabled()

    def click_verification_reset(self):
        expect(self.verification_reset_button).to_be_visible()
        expect(self.verification_reset_button).to_be_enabled()
        self.verification_reset_button.click()

    def verify_document_type_reset(self):
        self.verify_document_type_initially_unselected()

    def verify_document_uploads_reset(self):
        expect(self.document_front_uploaded_file).to_have_count(0)
        expect(self.document_back_uploaded_file).to_have_count(0)

        expect(self.document_front_input).to_have_count(1)
        expect(self.document_back_input).to_have_count(1)

    def click_verification_submit(self):
        expect(self.verification_submit_button).to_be_visible()
        expect(self.verification_submit_button).to_be_enabled()
        self.verification_submit_button.click()

    def get_verification_validation_messages(self):
        return self.page.locator(
            '[role="alert"], .ant-message-notice, '
            '.ant-notification-notice, .Toastify__toast, '
            '.swal2-popup'
        ).all_inner_texts()

    def verify_still_on_verification_page(self):
        expect(self.page).to_have_url(
            re.compile(
                r"/nolimit/app/onboarding/individual/process"
                r"\?(?=[^#]*\bstep=verification\b)[^#]+"
            )
        )

        expect(
            self.page.get_by_role(
                "heading",
                name="Individual Onboarding",
                exact=True
            )
        ).to_be_visible()

        expect(self.live_photo_heading).to_be_visible()
        expect(self.document_type_heading).to_be_visible()

    def verify_documents_submitted_successfully(self):
        expect(
            self.verification_success_notification
        ).to_be_visible(timeout=30000)

        expect(
            self.verification_success_notification
        ).to_contain_text(
            "Documents submitted successfully"
        )

    def verify_review_extracted_information_screen(self):
        # Review screen
        expect(
            self.review_extracted_information_heading
        ).to_be_visible(timeout=30000)

        expect(
            self.review_extracted_information_description
        ).to_be_visible()

        # Extracted personal information
        expect(self.extracted_first_name_label).to_be_visible()
        expect(self.extracted_last_name_label).to_be_visible()
        expect(self.extracted_dob_label).to_be_visible()
        expect(self.extracted_gender_label).to_be_visible()
        expect(self.extracted_nationality_label).to_be_visible()
        expect(self.extracted_issuing_country_label).to_be_visible()

        # Additional document information
        expect(
            self.page.get_by_role(
                "textbox",
                name="Driver Licence Number"
            )
        ).to_be_visible()

        expect(
            self.page.get_by_role(
                "textbox",
                name="Issue Date"
            )
        ).to_be_visible()

        expect(
            self.page.get_by_role(
                "textbox",
                name="Expiry Date"
            )
        ).to_be_visible()

        # Save & Confirm
        expect(
            self.page.get_by_role(
                "button",
                name="Save & Confirm",
                exact=True
            )
        ).to_be_visible()

        # Verify URL without checking old form headings
        self.verify_review_verification_url()

    def verify_review_verification_url(self):
        expect(self.page).to_have_url(
            re.compile(
                r"/nolimit/app/onboarding/individual/process"
                r"\?(?=[^#]*\bstep=verification\b)[^#]+"
            )
        )

        expect(
            self.page.get_by_role(
                "heading",
                name="Individual Onboarding",
                exact=True
            )
        ).to_be_visible()

    def verify_review_media_labels(self):
        for label in [
            "Live Photo",
            "Document Front",
            "Document Back"
        ]:
            expect(
                self.page.get_by_text(label, exact=True)
            ).to_be_visible()

