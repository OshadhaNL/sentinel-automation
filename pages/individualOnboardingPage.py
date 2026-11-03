
import re
from playwright.sync_api import Page, expect
from pathlib import Path
from playwright.sync_api import TimeoutError
from urllib.parse import urlparse, parse_qs


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

        # Review Extracted Information - editable fields
        self.review_first_name_input = page.get_by_role(
            "textbox",
            name="First Name",
            exact=True
        )

        self.review_last_name_input = page.get_by_role(
            "textbox",
            name="Last Name",
            exact=True
        )

        self.review_residential_address_checkbox = page.get_by_role(
            "checkbox",
            name="My residential address is different",
            exact=True
        )

        # Review Extracted Information dropdowns
        self.review_gender_dropdown = self.get_review_dropdown("Gender")

        self.review_nationality_dropdown = self.get_review_dropdown("Nationality")

        self.review_issuing_country_dropdown = self.get_review_dropdown("Issuing Country")

        self.review_document_type_dropdown = self.get_review_dropdown("Type of Document")


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
            "paused",
            False,
            timeout=20000
        )

        expect(self.camera_video).to_have_js_property(
            "readyState",
            4,
            timeout=20000
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

    def verify_document_front_uploaded(self, filename):
        front_section = self.page.locator(
            "div.custom-border-bottom"
        ).filter(
            has=self.page.get_by_role(
                "heading",
                name="Document Front",
                exact=True
            )
        )

        expect(front_section).to_be_visible()

        expect(
            front_section.get_by_role(
                "heading",
                name=filename,
                exact=True
            )
        ).to_be_visible(timeout=60000)

        print(f"Document Front uploaded: {filename}")

    def verify_document_back_uploaded(self, expected_filename):
        expect(
            self.document_back_uploaded_file
        ).to_be_visible(timeout=60000)

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
        submit_button = self.verification_submit_button

        expect(submit_button).to_be_visible(timeout=15000)

        try:
            expect(submit_button).to_be_enabled(timeout=60000)
        except AssertionError:
            self.debug_onboarding_blocked(
                "Verification Submit did not become enabled"
            )
            raise

        submit_button.click(timeout=30000)

        print("Verification Submit clicked successfully.")

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
                name=re.compile(
                    r"^(Driver|Driving) Licence Number$"
                )
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

    def verify_review_name_fields(self):
        expect(self.review_first_name_input).to_be_visible()
        expect(self.review_first_name_input).to_be_enabled()

        expect(self.review_last_name_input).to_be_visible()
        expect(self.review_last_name_input).to_be_enabled()

    def edit_review_first_name(self, first_name):
        expect(self.review_first_name_input).to_be_visible()

        self.review_first_name_input.fill(first_name)

        expect(self.review_first_name_input).to_have_value(
            first_name
        )

    def edit_review_last_name(self, last_name):
        expect(self.review_last_name_input).to_be_visible()

        self.review_last_name_input.fill(last_name)

        expect(self.review_last_name_input).to_have_value(
            last_name
        )

    def verify_residential_address_checkbox(self):
        expect(
            self.review_residential_address_checkbox
        ).to_be_visible()

        expect(
            self.review_residential_address_checkbox
        ).to_be_enabled()

    def verify_residential_address_initially_unchecked(self):
        expect(
            self.review_residential_address_checkbox
        ).not_to_be_checked()

    def verify_residential_address_fields_disabled(self):
        for field in ["Street Address", "City", "State", "Postcode"]:
            inputs = self.page.get_by_role(
                "textbox",
                name=field,
                exact=True
            )

            # The second input belongs to Residential Address
            expect(inputs.nth(1)).to_be_disabled()

    def enable_separate_residential_address(self):
        self.review_residential_address_checkbox.check()

        expect(
            self.review_residential_address_checkbox
        ).to_be_checked()

    def verify_residential_address_fields_enabled(self):
        for field in ["Street Address", "City", "State", "Postcode"]:
            inputs = self.page.get_by_role(
                "textbox",
                name=field,
                exact=True
            )

            expect(inputs.nth(1)).to_be_enabled()

    def disable_separate_residential_address(self):
        self.review_residential_address_checkbox.uncheck()

        expect(
            self.review_residential_address_checkbox
        ).not_to_be_checked()

    def get_review_dropdown(self, field_name):
        field = self.page.locator("label").filter(
            has_text=re.compile(
                rf"^\s*{re.escape(field_name)}\s*$"
            )
        )

        return field.locator("xpath=..").locator(".ant-select")

    def verify_review_dropdown_visible(self, field_name):
        dropdown = self.get_review_dropdown(field_name)

        expect(dropdown).to_be_visible()
        expect(dropdown).not_to_have_class(
            re.compile(r"\bant-select-disabled\b")
        )

    def open_review_dropdown(self, field_name):
        dropdown = (
            self.page.locator("label")
            .filter(
                has_text=re.compile(
                    rf"^\s*{re.escape(field_name)}\s*$"
                )
            )
            .locator("..")
            .locator(".ant-select")
        )

        expect(
            self.page.locator(".progress-overlay")
        ).to_be_hidden(timeout=60000)

        selector = dropdown.locator(".ant-select-selector")

        expect(selector).to_be_visible()
        selector.click(timeout=30000)


    def verify_review_dropdown_selected_value(self, field_name, value):
        dropdown = self.get_review_dropdown(field_name)

        expect(
            dropdown.locator(".ant-select-selection-item")
        ).to_have_text(value)

    def verify_review_dropdown_has_options(self, field_name):
        self.open_review_dropdown(field_name)

        options = self.page.locator(
            ".ant-select-dropdown:visible "
            ".ant-select-item-option:not(.ant-select-item-option-disabled)"
        )

        expect(options.first).to_be_visible()

        return options

    def select_first_review_dropdown_option(self, field_name):
        options = self.verify_review_dropdown_has_options(field_name)

        option = options.first
        option_text = option.locator(
            ".ant-select-item-option-content"
        ).inner_text().strip()

        option.click()

        self.verify_review_dropdown_selected_value(
            field_name,
            option_text
        )

        return option_text

    def verify_review_save_confirm_button(self):
        save_button = self.page.get_by_role(
            "button",
            name="Save & Confirm",
            exact=True
        )

        expect(save_button).to_be_visible()
        expect(save_button).to_be_enabled()

    def click_review_save_confirm(self):
        save_button = self.page.get_by_role(
            "button",
            name="Save & Confirm",
            exact=True
        )

        expect(save_button).to_be_visible(timeout=15000)

        try:
            expect(save_button).to_be_enabled(timeout=60000)
        except AssertionError:
            self.debug_onboarding_blocked(
                "Save & Confirm did not become enabled"
            )
            raise

        save_button.click(timeout=30000)

        print("Save & Confirm clicked successfully.")

    def inspect_review_save_result(self):
        # Wait briefly for a save response or navigation.
        try:
            self.page.wait_for_url(
                "**/nolimit/app/onboarding/individual/process?*step=documents*",
                timeout=10000
            )
        except TimeoutError:
            pass

        print("\n========== SAVE RESULT ==========")
        print("Current URL:", self.page.url)

        print("\nVisible notifications:")
        notifications = self.page.locator(
            ".ant-message-notice-content:visible, "
            ".ant-notification-notice:visible, "
            "[role='alert']:visible"
        )

        for i in range(notifications.count()):
            print(notifications.nth(i).inner_text())

        print("\nVisible validation errors:")
        errors = self.page.locator(
            ".ant-form-item-explain-error:visible, "
            ".text-red-500:visible, "
            "[aria-invalid='true']:visible"
        )

        for i in range(errors.count()):
            print(errors.nth(i).inner_text())

        print("\nCurrent page content:")
        print(self.page.locator("main").inner_text()[:5000])

    def verify_review_submission_successful(self):
        success_heading = self.page.get_by_role(
            "heading",
            name="Submission Successful",
            exact=True
        )

        try:
            expect(success_heading.first).to_be_visible(
                timeout=60000
            )

        except AssertionError:
            self.debug_onboarding_blocked(
                "Submission Successful screen did not load"
            )
            raise

        success_message = self.page.get_by_text(
            "Your information has been received and is being "
            "processed for onboarding.",
            exact=True
        )

        expect(success_message.first).to_be_visible(
            timeout=15000
        )

        finish_button = self.page.get_by_role(
            "button",
            name="Finish and View Submitted Documents",
            exact=True
        )

        expect(finish_button.first).to_be_visible(
            timeout=15000
        )

        expect(finish_button.first).to_be_enabled(
            timeout=15000
        )

        print("Submission Successful screen verified.")


    def click_finish_and_view_submitted_documents(self):
        button = self.page.get_by_role(
            "button",
            name="Finish and View Submitted Documents",
            exact=True
        ).first

        expect(button).to_be_visible()
        expect(button).to_be_enabled()

        button.click()

    def verify_navigation_after_finish(self):
        expect(self.page).to_have_url(
            re.compile(r".*step=documents(?:&|$)"),
            timeout=15000
        )

        print("Navigated URL:", self.page.url)

    def wait_for_review_extracted_information(self):
        review_heading = self.page.get_by_role(
            "heading",
            name="Review Extracted Information",
            exact=True
        )

        try:
            expect(review_heading).to_be_visible(timeout=90000)

        except AssertionError:
            self.debug_onboarding_blocked(
                "Review Extracted Information did not load"
            )
            raise

        print("Review Extracted Information screen loaded.")

    def verify_documents_page_loaded(self):
        expect(
            self.page.get_by_text(
                "Uploaded documents",
                exact=True
            )
        ).to_be_visible(timeout=30000)

        expect(
            self.page.get_by_role(
                "heading",
                name=re.compile(r"^Ref ID: SENTINEL")
            )
        ).to_be_visible()

    def verify_documents_upload_categories(self):
        for category in [
            "Passport Copy",
            "Driver Licence",
            "Proof of Age Card",
            "Others"
        ]:
            expect(
                self.page.get_by_text(
                    category,
                    exact=True
                )
            ).to_be_visible()

    def verify_documents_choose_file_buttons(self):
        buttons = self.page.get_by_role(
            "button",
            name="Choose File",
            exact=True
        )

        expect(buttons).to_have_count(4)

        for i in range(4):
            expect(buttons.nth(i)).to_be_visible()
            expect(buttons.nth(i)).to_be_enabled()

    def verify_documents_next_button(self):
        next_button = self.page.get_by_role(
            "button",
            name="Next",
            exact=True
        )

        expect(next_button).to_be_visible()
        expect(next_button).to_be_enabled()

    def get_documents_upload_container(self, category):
        return self.page.locator(
            "div.col-span-1.md\\:col-span-4"
        ).filter(
            has=self.page.locator(
                "label.document-label",
                has_text=category
            )
        )

    def upload_documents_file(self, category, file_path):
        container = self.get_documents_upload_container(category)

        file_input = container.locator('input[type="file"]')
        file_input.set_input_files(str(file_path))

        selected_filename = file_input.evaluate(
            "(element) => element.files?.[0]?.name"
        )

        assert selected_filename == file_path.name, (
            f"Expected {file_path.name}, got {selected_filename}"
        )

        print(f"Selected file for {category}: {selected_filename}")

    def verify_driver_licence_documents(self):
        expect(
            self.page.get_by_text(
                "Driver Licence - Front side",
                exact=False
            )
        ).to_be_visible(timeout=30000)

        expect(
            self.page.get_by_text(
                "Driver Licence - Back side",
                exact=False
            )
        ).to_be_visible(timeout=30000)

        print("Driver Licence front and back sections are visible.")

    def verify_driver_licence_uploaded_files(self):
        expect(
            self.page.get_by_role(
                "heading",
                name="doc-front.jpg",
                exact=True
            )
        ).to_be_visible(timeout=30000)

        expect(
            self.page.get_by_role(
                "heading",
                name="doc-back.jpg",
                exact=True
            )
        ).to_be_visible(timeout=30000)

        print("Driver Licence front and back images are displayed.")

    def verify_documents_uploaded_file(self, category, filename):
        container = self.get_documents_upload_container(category)

        expect(
            container.locator(".uploaded-file h6")
        ).to_have_text(filename, timeout=30000)

    def view_uploaded_document(self, category, filename):
        container = self.get_documents_upload_container(category)

        # Click the View button for the selected document
        container.locator(
            'button[title="View"]'
        ).click()

        # Ant Design image preview dialog
        preview = self.page.get_by_role("dialog")

        expect(preview).to_be_visible(timeout=15000)

        # Verify the correct image is displayed
        expect(
            preview.get_by_role("img", name=filename)
        ).to_be_visible(timeout=15000)

        print(f"Document preview opened successfully: {filename}")


    def close_uploaded_document_preview(self, category):
        preview = self.page.get_by_role("dialog")

        expect(preview).to_be_visible(timeout=10000)

        close_button = self.page.get_by_role(
            "button",
            name="close",
            exact=True
        )

        expect(close_button).to_be_visible(timeout=10000)
        close_button.click()

        expect(preview).to_be_hidden(timeout=10000)

        print("Document preview closed successfully.")


    def download_uploaded_document(self, category, filename):
        container = self.get_documents_upload_container(category)

        with self.page.expect_download(timeout=30000) as download_info:
            container.locator(
                'button[title="Download"]'
            ).click()

        download = download_info.value

        assert download.suggested_filename == filename, (
            f"Expected {filename}, got {download.suggested_filename}"
        )

        print(f"Document downloaded: {download.suggested_filename}")

    def click_documents_verify_tab(self):
        verify_tab = self.page.locator(
            ".tab-z-option"
        ).filter(
            has=self.page.locator("label", has_text="Verify")
        )

        verify_tab.click()

        print("Clicked Documents Verify tab.")

    def verify_documents_verify_tab_active(self):
        verify_tab = self.page.locator(
            ".tab-z-option"
        ).filter(
            has=self.page.locator("label", has_text="Verify")
        )

        expect(verify_tab).to_have_class(
            re.compile(r"\bactive\b"),
            timeout=15000
        )

        print("Documents Verify tab is active.")

    def get_documents_subtab(self, tab_name):
        return self.page.locator(".tab-z-option").filter(
            has=self.page.locator(
                "label",
                has_text=re.compile(rf"^\s*{re.escape(tab_name)}\s*$")
            )
        )

    def click_documents_subtab(self, tab_name):
        tab = self.get_documents_subtab(tab_name)
        expect(tab).to_be_visible()
        tab.click()


    def verify_documents_subtab_active(self, tab_name):
        expect(
            self.get_documents_subtab(tab_name)
        ).to_have_class(re.compile(r"\bactive\b"))

    def verify_documents_reference_id(self):
        reference = self.page.locator(
            "h4.secondary-title"
        ).filter(has_text="Ref ID:")

        expect(reference).to_be_visible()
        expect(reference.locator("span")).not_to_be_empty()

    def verify_documents_client_name_loaded(self):
        client_name = self.page.locator(
            "h4.secondary-title"
        ).filter(has_text="Client Name:")

        expect(client_name).to_be_visible()

        expect(client_name.locator("span")).not_to_have_text(
            re.compile(r"^\s*(Loading\.\.\.|)\s*$"),
            timeout=30000
        )

    def verify_document_cabinets_heading(self):
        expect(
            self.page.get_by_role(
                "heading",
                name="Document Cabinets",
                exact=True
            )
        ).to_be_visible(timeout=15000)

    def verify_document_cabinets_table(self):
        table = self.page.get_by_role("table")

        expect(table).to_be_visible(timeout=15000)

        expected_headers = [
            "Cabinet",
            "Status",
            "Uploaded Date",
            "Date of Expiry",
            "Uploaded By"
        ]

        for header in expected_headers:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True
                )
            ).to_be_visible()

        print("Document Cabinets table and headers verified.")

    def wait_for_document_cabinets_loading(self):
        expect(
            self.page.locator(
                ".ant-table-wrapper .ant-spin-spinning"
            )
        ).to_have_count(0, timeout=30000)

        print("Document Cabinets loading completed.")

    def verify_document_cabinets_empty_or_populated(self):
        self.wait_for_document_cabinets_loading()

        table = self.page.get_by_role("table")

        empty_state = table.locator(".ant-empty-description")

        if empty_state.is_visible():
            expect(empty_state).to_have_text("No data")
            print("Document Cabinets is empty.")
        else:
            rows = table.locator(
                "tbody tr:not(.ant-table-placeholder)"
            )
            assert rows.count() > 0, (
                "Expected document rows or a No data message."
            )
            print(f"Document Cabinets contains {rows.count()} records.")

    def verify_document_reference_matches_url(self):
        reference_id = self.page.locator(
            "h4.secondary-title"
        ).filter(
            has_text="Ref ID:"
        ).locator("span").inner_text().strip()

        assert reference_id, "Reference ID is empty."

        from urllib.parse import urlparse, parse_qs

        query = parse_qs(urlparse(self.page.url).query)

        assert query.get("client", [None])[0] == reference_id

        print(f"Reference ID matches URL: {reference_id}")

    def click_documents_next(self):
        # Ensure the uploaded documents are displayed
        expect(
            self.page.get_by_role("heading", name="doc-front.jpg")
        ).to_be_visible(timeout=30000)

        expect(
            self.page.get_by_role("heading", name="doc-back.jpg")
        ).to_be_visible(timeout=30000)

        # Wait for client details to finish loading
        client_name = self.page.locator(
            "h4.secondary-title"
        ).filter(has_text="Client Name:").locator("span")

        expect(client_name).not_to_have_text(
            "Loading...",
            timeout=30000
        )

        next_button = self.page.get_by_role(
            "button",
            name="Next",
            exact=True
        )

        expect(next_button).to_be_visible(timeout=15000)
        expect(next_button).to_be_enabled(timeout=15000)

        print(f"URL before Next: {self.page.url}")

        next_button.click()

        print("Clicked Documents Next button.")

    def verify_documents_next_opens_verify(self):
        try:
            expect(self.page).to_have_url(
                re.compile(
                    r"[?&]step=documents(?:&|$).*"
                    r"[?&]type=verify(?:&|$)"
                ),
                timeout=30000
            )

            self.verify_documents_subtab_active("Verify")

            print(f"URL after Next: {self.page.url}")
            print("Documents Next navigation passed.")

        except AssertionError:
            print(f"Navigation failed. Current URL: {self.page.url}")

            print("Visible alerts:")
            print(
                self.page.locator(
                    ".ant-message-notice, .ant-notification-notice, "
                    "[role='alert']"
                ).all_inner_texts()
            )

            self.page.screenshot(
                path="documents_next_failure.png",
                full_page=True
            )

            raise


    # ============================================================
    # DOCUMENTS -> VERIFY TAB
    # ============================================================

    def open_documents_verify(self):
        self.click_documents_subtab("Verify")
        self.verify_documents_subtab_active("Verify")

        # Wait for the Verify tab's document data to load.
        expect(
            self.page.locator(".border-box-label")
            .filter(has_text=re.compile(r"^\s*Consent Letter\s*$"))
        ).to_be_visible(timeout=30000)

        expect(
            self.page.locator(".border-box-label")
            .filter(has_text=re.compile(r"^\s*Driver Licence\s*$"))
        ).to_be_visible(timeout=30000)

        expect(
            self.page.locator(".border-box-label")
            .filter(has_text=re.compile(r"^\s*Verification\s*$"))
        ).to_be_visible(timeout=30000)

        print("Documents Verify tab loaded.")


    def get_verify_reference_id(self):
        reference = self.page.locator(
            "h4.secondary-title"
        ).filter(has_text="Ref ID:").locator("span")

        expect(reference).not_to_be_empty(timeout=30000)

        return reference.inner_text().strip()


    def get_verify_expected_documents(self):
        reference_id = self.get_verify_reference_id()

        return {
            "Consent Letter": [
                f"consent-letter-{reference_id}.pdf"
            ],
            "Driver Licence": [
                "doc-front.jpg",
                "doc-back.jpg"
            ],
            "Verification": [
                "photo.jpg",
                f"{reference_id}-Facial Biometrics Verification.pdf"
            ]
        }


    def get_verify_group(self, group_name):
        group = self.page.locator(".border-box").filter(
            has=self.page.locator(
                ".border-box-label",
                has_text=re.compile(
                    rf"^\s*{re.escape(group_name)}\s*$"
                )
            )
        )

        expect(group).to_be_visible(timeout=30000)
        return group


    def get_verify_document_card(self, group_name, filename):
        group = self.get_verify_group(group_name)

        card = group.locator(".w-85").filter(
            has=self.page.get_by_role(
                "heading",
                name=filename,
                exact=True
            )
        )

        expect(card).to_have_count(1, timeout=30000)
        expect(card).to_be_visible(timeout=15000)

        return card


    def verify_all_document_groups(self):
        for group_name in [
            "Consent Letter",
            "Driver Licence",
            "Verification"
        ]:
            self.get_verify_group(group_name)

        print("All three Verify document groups are visible.")


    def verify_all_expected_documents(self):
        expected_documents = self.get_verify_expected_documents()

        for group_name, filenames in expected_documents.items():
            group = self.get_verify_group(group_name)

            for filename in filenames:
                card = self.get_verify_document_card(
                    group_name,
                    filename
                )

                expect(
                    card.locator(".uploaded-file h6")
                ).to_have_text(filename)

                expect(
                    card.locator(".uploaded-file p")
                ).to_contain_text(
                    re.compile(r"\d+\s*(B|KB|MB)")
                )

                print(f"Verified: {group_name} -> {filename}")

            expect(
                group.locator(".w-85")
            ).to_have_count(len(filenames))


    def verify_all_document_action_buttons(self):
        expected_documents = self.get_verify_expected_documents()

        actions = [
            "Reupload",
            "View",
            "Download",
            "Delete",
            "Modify"
        ]

        for group_name, filenames in expected_documents.items():
            for filename in filenames:
                card = self.get_verify_document_card(
                    group_name,
                    filename
                )

                for action in actions:
                    button = card.locator(
                        f'button[title="{action}"]'
                    )

                    expect(button).to_be_visible()
                    expect(button).to_be_enabled()

                print(f"All action buttons verified: {filename}")


    def verify_all_document_expiry_indicators(self):
        expected_documents = self.get_verify_expected_documents()

        for group_name, filenames in expected_documents.items():
            for filename in filenames:
                card = self.get_verify_document_card(
                    group_name,
                    filename
                )

                expect(
                    card.locator(".expire-date")
                ).to_contain_text("Expiry date")

        print("Expiry date indicators verified.")


    def verify_all_document_drag_handles(self):
        expected_documents = self.get_verify_expected_documents()

        for group_name, filenames in expected_documents.items():
            for filename in filenames:
                card = self.get_verify_document_card(
                    group_name,
                    filename
                )

                handle = card.locator("button.drag-btn")

                expect(handle).to_be_visible()
                expect(handle).to_have_attribute(
                    "aria-roledescription",
                    "sortable"
                )
                expect(handle).to_have_attribute(
                    "aria-disabled",
                    "false"
                )

        print("All document drag handles verified.")


    def verify_all_reupload_inputs(self):
        expected_documents = self.get_verify_expected_documents()

        for group_name, filenames in expected_documents.items():
            for filename in filenames:
                card = self.get_verify_document_card(
                    group_name,
                    filename
                )

                file_input = card.locator(
                    ".upload-wrapper input[type='file']"
                )

                expect(file_input).to_have_count(1)
                expect(file_input).to_have_attribute(
                    "accept",
                    re.compile(r"application/pdf")
                )
                expect(file_input).to_have_attribute(
                    "accept",
                    re.compile(r"image/png")
                )
                expect(file_input).to_have_attribute(
                    "accept",
                    re.compile(r"image/jpeg")
                )

                expect(
                    card.locator(".upload-wrapper")
                ).to_contain_text("max. 10MB")

        print("Reupload input formats verified.")


    def verify_pdf_preview(self, group_name, filename):
        card = self.get_verify_document_card(
            group_name,
            filename
        )

        card.locator('button[title="View"]').click()

        preview = self.page.locator(
            ".document-preview-modal"
        ).filter(
            has=self.page.locator(
                ".modal-z-title h6",
                has_text=filename
            )
        )

        expect(preview).to_be_visible(timeout=15000)

        expect(
            preview.locator("iframe")
        ).to_have_attribute("title", filename)

        preview.locator("button.modal-z-close").click()

        expect(preview).to_be_hidden(timeout=15000)

        print(f"PDF preview opened and closed: {filename}")


    def verify_image_preview(self, group_name, filename):
        card = self.get_verify_document_card(
            group_name,
            filename
        )

        card.locator('button[title="View"]').click()

        preview = self.page.get_by_role("dialog")

        expect(preview).to_be_visible(timeout=15000)

        expect(
            preview.get_by_role(
                "img",
                name=filename
            )
        ).to_be_visible(timeout=15000)

        self.page.get_by_role(
            "button",
            name="close",
            exact=True
        ).click()

        expect(preview).to_be_hidden(timeout=15000)

        print(f"Image preview opened and closed: {filename}")


    def verify_document_download(self, group_name, filename):
        card = self.get_verify_document_card(
            group_name,
            filename
        )

        with self.page.expect_download(timeout=30000) as download_info:
            card.locator('button[title="Download"]').click()

        download = download_info.value

        assert download.suggested_filename == filename, (
            f"Expected {filename}, "
            f"got {download.suggested_filename}"
        )

        print(f"Download verified: {filename}")


    def verify_all_document_downloads(self):
        expected_documents = self.get_verify_expected_documents()

        for group_name, filenames in expected_documents.items():
            for filename in filenames:
                self.verify_document_download(
                    group_name,
                    filename
                )


    def verify_modify_dialog_cancel(self, group_name, filename):
        card = self.get_verify_document_card(
            group_name,
            filename
        )

        card.locator('button[title="Modify"]').click()

        dialog = self.page.locator(".modal-z:visible").filter(
            has=self.page.locator(
                ".modal-z-footer button",
                has_text=re.compile(r"^\s*Save\s*$")
            )
        )

        expect(dialog).to_be_visible(timeout=15000)

        expect(
            dialog.get_by_role(
                "button",
                name="Save",
                exact=True
            )
        ).to_be_visible()

        dialog.get_by_role(
            "button",
            name="Cancel",
            exact=True
        ).click()

        expect(dialog).to_be_hidden(timeout=15000)

        print(f"Modify dialog cancelled: {filename}")


    # ============================================================
    # INDIVIDUAL ONBOARDING - SCREENING
    # ============================================================


    def verify_screening_results_header(self):
        results_header = self.page.locator(".wc-page-header")

        # Verify results header is visible
        expect(results_header).to_be_visible(timeout=30000)

        # Verify Back to Screening button
        back_button = results_header.locator("button.back-link")

        expect(back_button).to_be_visible(timeout=15000)
        expect(back_button).to_contain_text("Back to Screening")

        # Verify client reference ID
        expect(
            self.page.get_by_role(
                "heading",
                name=re.compile(r"Ref ID:\s*SENTINEL", re.I)
            )
        ).to_be_visible()

        # Verify client name
        expect(
            self.page.get_by_role(
                "heading",
                name=re.compile(r"Client Name:", re.I)
            )
        ).to_be_visible()

        # Verify match summary
        match_summary = self.page.get_by_text(
            re.compile(r"Showing\s+\d+\s+matches?\s+for", re.I)
        )

        expect(match_summary).to_be_visible(timeout=15000)

        print("Screening Results header verified.")


    # ============================================================
    # INDIVIDUAL ONBOARDING - SCREENING
    # ============================================================

    def get_screening_tab(self, tab_name):
        return self.page.locator(".tab-z-option").filter(
            has=self.page.locator(
                "label",
                has_text=re.compile(
                    rf"^\s*{re.escape(tab_name)}\s*$"
                )
            )
        )
    # ============================================================
    # SCREENING - CORRECT NAVIGATION
    # Individual Onboarding -> Results -> Main Screening
    # ============================================================

    def open_screening_main(self):
        screening_tab = self.get_screening_tab("Screening")

        expect(screening_tab).to_be_visible(timeout=15000)
        screening_tab.click()

        expect(screening_tab).to_have_class(
            re.compile(r"\bactive\b"),
            timeout=15000
        )

        # Screening tab opens the Results page first.
        results_header = self.page.locator(".wc-page-header")

        expect(results_header).to_be_visible(timeout=30000)

        back_button = results_header.locator(
            "button.back-link"
        )

        expect(back_button).to_be_visible(timeout=15000)
        expect(back_button).to_contain_text("Back to Screening")

        print("Screening Results page opened.")

    def open_screening_results(self):
        # Results are already displayed after clicking Screening.
        results_header = self.page.locator(".wc-page-header")

        expect(results_header).to_be_visible(timeout=30000)

        back_button = results_header.locator(
            "button.back-link"
        )

        expect(back_button).to_be_visible()
        expect(back_button).to_contain_text("Back to Screening")

        print("Screening Results page verified.")


    def get_screening_mode_tab(self, mode):
        return self.get_screening_tab(mode)

    def verify_screening_heading_description(self):
        expect(
            self.page.get_by_role(
                "heading", name="Screening", exact=True
            )
        ).to_be_visible()

        expect(
            self.page.get_by_text(
                "Conducts PEP, sanction, and adverse media checks on clients.",
                exact=True
            )
        ).to_be_visible()

    def verify_screening_modes(self):
        single = self.get_screening_mode_tab("Single Screening")
        daily = self.get_screening_mode_tab("Daily Screening")

        expect(single).to_be_visible()
        expect(daily).to_be_visible()
        expect(single).to_have_class(re.compile(r"\bactive\b"))

    def verify_screening_client_type(self):
        individual = self.page.locator(
            'input[name="entityType"][value="P"]'
        )
        organization = self.page.locator(
            'input[name="entityType"][value="O"]'
        )

        expect(individual).to_be_checked()
        expect(individual).to_be_disabled()
        expect(organization).not_to_be_checked()
        expect(organization).to_be_disabled()

    def verify_screening_name_field(self):
        name = self.page.locator('input[name="name"]')

        expect(name).to_be_visible()
        expect(name).to_be_enabled()
        expect(name).to_have_attribute(
            "placeholder", "Enter individual name"
        )
        expect(name).not_to_be_empty(timeout=30000)

        print(f"Screening name: {name.input_value()}")

    def verify_screening_gender_options(self):
        for gender in ["Male", "Female", "Unspecified"]:
            radio = self.page.locator(
                f'input[name="gender"][value="{gender}"]'
            )
            expect(radio).to_be_visible()
            expect(radio).to_be_enabled()

    def verify_screening_gender_selection(self):
        for gender in ["Male", "Female", "Unspecified"]:
            radio = self.page.locator(
                f'input[name="gender"][value="{gender}"]'
            )
            radio.check()
            expect(radio).to_be_checked()

        print("All gender selections verified.")

    def verify_screening_date_of_birth(self):
        dob = self.page.get_by_placeholder(
            "Pick date of birth", exact=True
        )

        expect(dob).to_be_visible()
        expect(dob).to_be_enabled()

        print(f"Screening DOB: {dob.input_value()}")

    def get_screening_select_field(self, label_name):
        container = self.page.locator(".input-box").filter(
            has=self.page.locator(
                "label",
                has_text=re.compile(
                    rf"^\s*{re.escape(label_name)}\s*$"
                )
            )
        )
        return container.locator(".ant-select")

    def verify_screening_country_fields(self):
        for label_name in ["Citizenship", "Place of Birth"]:
            field = self.get_screening_select_field(label_name)

            expect(field).to_be_visible()
            expect(field.locator('[role="combobox"]')).to_be_visible()

        print("Citizenship and Place of Birth fields verified.")

    def verify_screening_ongoing_checkbox(self):
        checkbox = self.page.locator('input[name="ongoing"]')

        expect(checkbox).to_be_visible()
        expect(checkbox).to_be_enabled()

        original_state = checkbox.is_checked()

        checkbox.set_checked(not original_state)
        assert checkbox.is_checked() != original_state

        checkbox.set_checked(original_state)
        assert checkbox.is_checked() == original_state

        print("Ongoing Screening checkbox toggle verified.")

    def verify_screening_analyze_button(self):
        # The main Screening form is opened by open_screening_form().
        # The button's accessible name includes a decorative icon.
        analyze_button = self.page.get_by_role(
            "button",
            name=re.compile(r"Analyze\s*$", re.I)
        )

        expect(analyze_button).to_be_visible(timeout=30000)
        expect(analyze_button).to_be_enabled(timeout=15000)

        print("Analyze button is visible and enabled.")


    def verify_screening_connected_party_section(self):
        expect(
            self.page.get_by_role(
                "heading", name="Connected Party", exact=True
            )
        ).to_be_visible()

        history = self.page.locator(".screen-history")

        expect(history).to_be_visible()

        # Existing history is optional for newly created clients.
        cards = history.locator(".screen-history-card")

        print(f"Existing connected party cards: {cards.count()}")


    def get_screening_result_tab(self, status):
        return self.page.locator(".page-content .tab-z-option").filter(
            has=self.page.locator(
                "label",
                has_text=re.compile(
                    rf"^\s*{re.escape(status)}\s*\(\d+\)\s*$"
                )
            )
        )

    def get_screening_result_count(self, status):
        tab = self.get_screening_result_tab(status)

        expect(tab).to_be_visible(timeout=15000)

        label = tab.locator("label").inner_text()

        match = re.search(r"\((\d+)\)", label)

        assert match is not None, (
            f"Could not extract count from: {label}"
        )

        return int(match.group(1))

    def verify_screening_result_status_tabs(self):
        statuses = [
            "Unresolved Hits",
            "Positive Hits",
            "False Hits",
            "Possible Hits"
        ]

        for status in statuses:
            tab = self.get_screening_result_tab(status)
            expect(tab).to_be_visible()

            count = self.get_screening_result_count(status)

            assert count >= 0

            print(f"{status}: {count}")

        expect(
            self.get_screening_result_tab("Unresolved Hits")
        ).to_have_class(re.compile(r"\bactive\b"))

    def verify_screening_match_counts(self):
        """Verify summary count against the active filter or overall result count.

        Sentinel may show either the selected status count or the aggregate
        count in its "Showing N matches for ..." summary.
        """
        summary = self.page.locator("p").filter(
            has_text=re.compile(
                r"^\s*Showing\s+\d+\s+matches?\s+for\b", re.I
            )
        )
        expect(summary).to_have_count(1, timeout=15000)
        expect(summary).to_be_visible(timeout=15000)

        statuses = [
            "Unresolved Hits",
            "Positive Hits",
            "False Hits",
            "Possible Hits",
        ]
        counts = {
            status: self.get_screening_result_count(status)
            for status in statuses
        }
        categorized_total = sum(counts.values())

        active_statuses = [
            status for status in statuses
            if re.search(
                r"\bactive\b",
                self.get_screening_result_tab(status).get_attribute("class") or ""
            )
        ]
        assert len(active_statuses) == 1, (
            f"Expected one active results tab; found: {active_statuses}"
        )
        active_status = active_statuses[0]
        active_count = counts[active_status]

        # Poll for UI updates rather than reading an intermediate count.
        expect(summary).to_have_text(
            re.compile(
                rf"^\s*Showing\s+(?:{active_count}|{categorized_total})"
                rf"\s+matches?\s+for\b", re.I
            ),
            timeout=30000,
        )
        summary_text = summary.inner_text().strip()
        match = re.search(
            r"Showing\s+(\d+)\s+matches?\s+for\b",
            summary_text,
            re.I,
        )
        assert match is not None, f"Unrecognized summary: {summary_text!r}"
        summary_count = int(match.group(1))

        print(f"Screening summary: {summary_count}")
        print(f"Active status: {active_status} ({active_count})")
        print(f"Total across statuses: {categorized_total}; details: {counts}")
        print("Screening match counts verified.")

    def verify_screening_results_table(self):
        table = self.page.locator(
            ".page-content .ant-table"
        )

        expect(table).to_be_visible(timeout=30000)

        headers = [
            "Name",
            "Match Strength",
            "Type",
            "Gender",
            "Date of Birth",
            "Citizenship",
            "Resolution"
        ]

        for header in headers:
            expect(
                table.get_by_role(
                    "columnheader",
                    name=header,
                    exact=True
                )
            ).to_be_visible()

        print("Screening results table headers verified.")

    def verify_screening_status_table(self, status):
        tab = self.get_screening_result_tab(status)
        tab.click()

        expect(tab).to_have_class(
            re.compile(r"\bactive\b"),
            timeout=15000
        )

        table = self.page.locator(
            ".page-content .ant-table"
        )

        expect(table).to_be_visible(timeout=30000)

        expect(
            self.page.locator(
                ".page-content .ant-spin-spinning"
            )
        ).to_have_count(0, timeout=30000)

        count = self.get_screening_result_count(status)

        if count == 0:
            expect(
                table.locator(".ant-empty-description")
            ).to_have_text("No data", timeout=15000)
        else:
            rows = table.locator(
                "tbody tr:not(.ant-table-placeholder)"
            )

            expect(rows.first).to_be_visible(timeout=30000)

            assert rows.count() > 0, (
                f"{status} has {count} hits but no visible rows."
            )

        print(f"{status} table verified. Count: {count}")


    def click_back_to_screening(self):
        results_header = self.page.locator(".wc-page-header")

        expect(results_header).to_be_visible(timeout=30000)

        back_button = results_header.locator(
            "button.back-link"
        )

        expect(back_button).to_be_visible(timeout=15000)
        back_button.click()

        expect(results_header).to_be_hidden(timeout=30000)

        # Verify the Main Screening form has opened.
        single_screening = self.get_screening_mode_tab(
            "Single Screening"
        )

        expect(single_screening).to_be_visible(timeout=30000)

        expect(
            self.page.locator('input[name="name"]')
        ).to_be_visible(timeout=30000)

        print("Navigated to Main Screening page.")

    def open_screening_form(self):
        # Navigate from Screening Results to Main Screening.
        self.click_back_to_screening()



    # =========================================================
    # KYC FORM - SECTION 01
    # =========================================================

    def open_kyc_form(self):

        # Target only the currently open success modal
        success_modal = self.page.locator(
            ".modal-z.modal-z-open"
        ).filter(
            has_text="Submission Successful"
        )

        if success_modal.count() > 0:
            expect(success_modal).to_be_visible(timeout=15000)

            print("Submission success modal detected.")

            # Complete the existing success workflow
            self.click_finish_and_view_submitted_documents()

            # Verify the modal has closed
            expect(success_modal).to_be_hidden(timeout=15000)

        # Open KYC Form directly
        kyc_tab = self.page.locator(
            ".tab-z-option"
        ).filter(
            has=self.page.get_by_text(
                "KYC Form", exact=True
            )
        )

        expect(kyc_tab).to_be_visible(timeout=15000)

        kyc_tab.click()

        expect(
            self.page.locator(".kyc-form")
        ).to_be_visible(timeout=30000)

        expect(kyc_tab).to_have_class(
            re.compile(r"\bactive\b")
        )

        print("KYC Form opened successfully.")

    def verify_kyc_form_loaded(self):
        expect(
            self.page.get_by_role(
                "heading",
                name="KNOW YOUR CUSTOMER (KYC) FORM - INDIVIDUAL",
                exact=True
            )
        ).to_be_visible(timeout=30000)

        expect(
            self.page.get_by_role(
                "heading",
                name="SECTION 01 - KYC PROFILE OF THE CLIENT",
                exact=True
            )
        ).to_be_visible()

    def verify_kyc_client_id(self):
        client_id = self.page.locator(
            ".kyc-form h4.secondary-title"
        ).filter(has_text="Client ID:").locator("span")

        expect(client_id).to_have_text(
            re.compile(r"^SENTINEL[A-Z0-9]+$")
        )

    def verify_kyc_text_fields(self):
        placeholders = [
            "Enter full name",
            "Enter contact number",
            "Enter email address",
            "Document Number",
            "Enter passport number",
        ]

        for placeholder in placeholders:
            expect(
                self.page.get_by_placeholder(
                    placeholder, exact=True
                )
            ).to_be_visible()

    def verify_kyc_dropdowns(self):
        placeholders = [
            "Select Gender",
            "Select country",
            "Select Occupation",
        ]

        for placeholder in placeholders:
            expect(
                self.page.locator(
                    ".kyc-form .ant-select"
                ).filter(
                    has=self.page.locator(
                        ".ant-select-selection-placeholder",
                        has_text=placeholder
                    )
                ).first
            ).to_be_visible()

    def verify_kyc_date_fields(self):
        expect(
            self.page.locator(
                '.kyc-form .ant-picker input[placeholder="Select date"]'
            )
        ).to_have_count(3)

    def verify_kyc_nationality_options(self):
        nationality = self.page.locator(
            ".kyc-form .border-box"
        ).filter(
            has=self.page.locator(
                ".border-box-label",
                has_text="Nationality"
            )
        )

        for option in ["Single", "Dual", "Multiple"]:
            expect(
                nationality.get_by_role(
                    "radio", name=re.compile(option)
                )
            ).to_be_visible()

    def verify_kyc_single_nationality_default(self):
        nationality = self.page.locator(
            ".kyc-form .border-box"
        ).filter(
            has=self.page.locator(
                ".border-box-label",
                has_text="Nationality"
            )
        )

        expect(
            nationality.locator('input[type="radio"][value="1"]')
        ).to_be_checked()

    def verify_kyc_address_fields(self):
        expect(
            self.page.locator(
                '.kyc-form textarea[placeholder="Enter the address here..."]'
            )
        ).to_have_count(2)

    def verify_kyc_source_of_wealth(self):
        source = self.page.locator(
            ".kyc-form .header-box"
        ).filter(has_text="Source of Wealth")

        expect(source).to_be_visible()

        expect(
            source.locator('input[type="checkbox"]')
        ).to_have_count(16)

    def verify_kyc_save_button(self):
        save_button = self.page.locator(
            ".kyc-form button.primary-btn"
        ).filter(has_text="Save")

        expect(save_button).to_be_visible()
        expect(save_button).to_be_enabled()


    # =========================================================
    # KYC FORM - SECTION 01 FUNCTIONAL ACTIONS
    # Add inside the existing IndividualOnboardingPage class.
    # Do not replace your working open_kyc_form() method.
    # =========================================================

    KYC_WEALTH_OPTIONS = (
        "Employment Income / Salary", "Savings", "Mortgage / Loan",
        "Sale of Property", "Business Income", "Investment Income",
        "Sale of Investments / Shares", "Inheritance", "Gift",
        "Superannuation / Pension", "Trust Distribution", "Insurance Payout",
        "Legal Settlement / Compensation", "Cryptocurrency Assets",
        "Overseas Funds", "Other",
    )

    KYC_TEXT_PLACEHOLDERS = {
        "full_name": "Enter full name",
        "contact": "Enter contact number",
        "email": "Enter email address",
        "document_number": "Document Number",
        "passport_number": "Enter passport number",
    }

    @property
    def kyc_form(self):
        return self.page.locator(".kyc-form")

    def kyc_assert_loaded(self):
        expect(self.kyc_form).to_be_visible(timeout=30000)
        expect(self.kyc_form.locator("h4.secondary-title").filter(
            has_text="KNOW YOUR CUSTOMER (KYC) FORM - INDIVIDUAL"
        )).to_be_visible()

    def kyc_text_input(self, field):
        return self.kyc_form.get_by_placeholder(self.KYC_TEXT_PLACEHOLDERS[field], exact=True).first

    def kyc_fill_text(self, field, value):
        target = self.kyc_text_input(field)
        expect(target).to_be_visible()
        expect(target).to_be_enabled()
        target.fill(value)
        expect(target).to_have_value(value)

    def kyc_clear_text(self, field):
        target = self.kyc_text_input(field)
        target.clear()
        expect(target).to_have_value("")

    def kyc_address(self, index):
        assert index in (0, 1)
        return self.kyc_form.get_by_placeholder("Enter the address here...", exact=True).nth(index)

    def kyc_fill_address(self, index, value):
        target = self.kyc_address(index)
        target.fill(value)
        expect(target).to_have_value(value)

    def kyc_select_for_label(self, label, scope=None):
        """Find an Ant Design select next to the exact field label."""
        container = scope if scope is not None else self.kyc_form
        label_node = container.locator("label").filter(
            has_text=re.compile(r"^\s*" + re.escape(label) + r"\s*$")
        ).first
        expect(label_node).to_be_visible()
        selection = label_node.locator(
            "xpath=following-sibling::div[contains(concat(' ',normalize-space(@class),' '),' ant-select ')]"
        )
        expect(selection).to_be_visible()
        return selection

    def kyc_dropdown_options(self, label, scope=None, search=None):
        """Open an Ant Design select and wait for its actual options."""
        selector = self.kyc_select_for_label(label, scope)
        expect(selector).to_be_visible()
        selector.click()

        if search:
            search_input = selector.locator("input.ant-select-selection-search-input")
            expect(search_input).to_be_visible()
            search_input.fill(search)

        options = self.page.locator(
            ".ant-select-dropdown:visible "
            ".ant-select-item-option:not(.ant-select-item-option-disabled)"
        )

        if search:
            # An earlier Ant dropdown can briefly remain visible during animation.
            # Wait for the option that matches THIS field's search instead of
            # accidentally selecting an old option (e.g., Male).
            matched = options.filter(
                has_text=re.compile(re.escape(search), re.IGNORECASE)
            )
            expect(matched.first).to_be_visible(timeout=15000)
        else:
            expect(options.first).to_be_visible(timeout=15000)

        return selector, options

    def kyc_choose_first_dropdown_option(self, label, scope=None, search=None):

        selector = self.kyc_select_for_label(label, scope)

        expect(selector).to_be_visible(timeout=15000)
        selector.click()

        search_input = selector.locator(
            "input.ant-select-selection-search-input"
        )

        expect(search_input).to_be_attached(timeout=15000)

        # Find the dropdown associated with THIS select,
        # rather than an old dropdown still closing.
        dropdown_id = search_input.get_attribute("aria-controls")

        dropdown = None

        if dropdown_id:
            controlled_list = self.page.locator(
                f'[id="{dropdown_id}"]'
            )

            if controlled_list.count() > 0:
                dropdown = controlled_list.locator(
                    "xpath=ancestor::div[contains("
                    "concat(' ', normalize-space(@class), ' '), "
                    "' ant-select-dropdown ')]"
                ).first

        if dropdown is None or dropdown.count() == 0:
            dropdown = self.page.locator(
                ".ant-select-dropdown:visible"
            ).last

        options = dropdown.locator(
            ".ant-select-item-option"
            ":not(.ant-select-item-option-disabled)"
        )

        if search:
            search_input.fill(search)

            option = options.filter(
                has_text=re.compile(
                    re.escape(search),
                    re.IGNORECASE
                )
            ).first

            expect(option).to_be_visible(timeout=15000)

            expected_text = option.inner_text().strip()

            # Searchable Ant Design selects support Enter.
            search_input.press("Enter")

        else:
            option = options.first

            expect(option).to_be_visible(timeout=15000)

            expected_text = option.inner_text().strip()

            # The first option is already active when the dropdown opens.
            # Do not press ArrowDown because that selects the second option.
            search_input.press("Enter")

            print(f"Selected using keyboard: {expected_text}")

        selected_item = selector.locator(
            ".ant-select-selection-item"
        )

        expect(selected_item).to_have_text(
            expected_text,
            timeout=15000
        )

        print(f"{label} selected: {expected_text}")

        return expected_text


    @property
    def kyc_nationality_box(self):
        return self.kyc_form.locator(".border-box").filter(
            has=self.page.locator(".border-box-label").filter(
                has_text=re.compile(r"^Nationality$")
            )
        )

    def kyc_nationality_radio(self, kind):
        values = {"Single": "1", "Dual": "2", "Multiple": "3"}
        return self.kyc_nationality_box.locator(
            f'input[type="radio"][value="{values[kind]}"]'
        )

    def kyc_choose_nationality_type(self, kind):
        radio = self.kyc_nationality_radio(kind)
        radio.check()
        expect(radio).to_be_checked()
        for other in ("Single", "Dual", "Multiple"):
            if other != kind:
                expect(self.kyc_nationality_radio(other)).not_to_be_checked()

    def kyc_nationality_selects(self):
        return self.kyc_nationality_box.locator(".ant-select")

    def kyc_passport_inputs(self):
        return self.kyc_form.get_by_placeholder("Enter passport number", exact=True)

    def kyc_date_input(self, index):
        assert index in (0, 1, 2), "Date indices: 0 DOB, 1 passport issue, 2 passport expiry"
        return self.kyc_form.locator('.ant-picker input[placeholder="Select date"]').nth(index)

    def kyc_open_date_picker(self, index):
        target = self.kyc_date_input(index)
        expect(target).to_be_visible()
        target.click()
        popup = self.page.locator(
            ".ant-picker-dropdown:not(.ant-picker-dropdown-hidden):visible"
        )
        expect(popup).to_be_visible(timeout=15000)
        return popup

    def kyc_select_calendar_day(self, index):
        popup = self.kyc_open_date_picker(index)
        days = popup.locator(
            ".ant-picker-cell-in-view:not(.ant-picker-cell-disabled) .ant-picker-cell-inner"
        )
        expect(days.first).to_be_visible()
        days.first.click()
        expect(self.kyc_date_input(index)).not_to_have_value("")
        return self.kyc_date_input(index).input_value()

    def kyc_wealth_input(self, name):
        assert name in self.KYC_WEALTH_OPTIONS
        section = self.kyc_form.locator(".header-box").filter(has_text="Source of Wealth")
        return section.locator(f'input[type="checkbox"][value="{name}"]')

    def kyc_set_wealth(self, name, checked=True):
        """Use the real checkbox state; report if the application refuses it."""
        target = self.kyc_wealth_input(name)
        expect(target).to_be_visible()
        expect(target).to_be_enabled()
        if checked:
            if not target.is_checked():
                target.click()
            expect(target).to_be_checked(timeout=5000)
        else:
            if target.is_checked():
                target.click()
            expect(target).not_to_be_checked(timeout=5000)

    def kyc_set_wealth(self, name, checked=True):
        """Use the real checkbox state; report if the application refuses it."""
        target = self.kyc_wealth_input(name)
        expect(target).to_be_visible()
        expect(target).to_be_enabled()
        if checked:
            if not target.is_checked():
                target.click()
            expect(target).to_be_checked(timeout=5000)
        else:
            if target.is_checked():
                target.click()
            expect(target).not_to_be_checked(timeout=5000)

    def kyc_wealth_checked_values(self):
        section = self.kyc_form.locator(".header-box").filter(has_text="Source of Wealth")
        return section.locator('input[type="checkbox"]:checked').evaluate_all(
            "els => els.map(el => el.value)"
        )

    def kyc_save_button(self):
        return self.kyc_form.get_by_role("button", name="Save", exact=True)

    def kyc_click_save(self):
        button = self.kyc_save_button()
        expect(button).to_be_visible()
        expect(button).to_be_enabled()
        button.click()

    def kyc_fill_passport_number(self, index, value):
        """Type into dynamic nationality/passport inputs without a long fill retry."""
        inputs = self.kyc_passport_inputs()
        assert inputs.count() > index, f"Passport input {index + 1} not found"
        target = inputs.nth(index)
        expect(target).to_be_visible(timeout=15000)
        expect(target).to_be_enabled()
        target.click()
        target.press("ControlOrMeta+A")
        target.press_sequentially(value, delay=30)
        expect(inputs.nth(index)).to_have_value(value, timeout=15000)

    # ============================================================
    # RISK ASSESSMENT
    # ============================================================

    RISK_OPTIONS = {
        "Country / Jurisdiction Risk": {
            "low": 1,
            "other": 3,
            "high": 5,
        },
        "Politically Exposed Person (PEP) Status": {
            "nonPep": 1,
            "associate": 3,
            "pep": 5,
        },
        "Australian Residential Status": {
            "residence": 1,
            "nonResidence": 3,
        },
        "Transfer of Funds": {
            "bankTransfer": 1,
            "cash": 3,
        },
        "Adverse Media": {
            "noHits": 1,
            "confirmed": 3,
        },
    }

    def open_risk_assessment(self):

        # Step 1: Handle the Verification submission success modal.
        success_modal = self.page.locator(
            ".modal-z.modal-z-open"
        ).filter(
            has_text="Submission Successful"
        )

        if success_modal.count() > 0:
            expect(success_modal).to_be_visible(timeout=15000)

            print("Submission success modal detected.")

            # Reuse the existing working method from KYC setup.
            self.click_finish_and_view_submitted_documents()

            expect(success_modal).to_be_hidden(timeout=15000)

            print("Submission success modal closed.")

        # Step 2: Locate the Risk Assessment tab.
        risk_tab = self.page.locator(
            ".tab-z-option"
        ).filter(
            has=self.page.get_by_text(
                "Risk Assessment",
                exact=True
            )
        )

        expect(risk_tab).to_be_visible(timeout=15000)

        # Step 3: Click Risk Assessment.
        risk_tab.click()

        # Step 4: Verify the Risk Assessment tab is active.
        expect(risk_tab).to_have_class(
            re.compile(r"\bactive\b"),
            timeout=15000
        )

        # Step 5: Verify the Risk Assessment content loaded.
        expect(
            self.page.get_by_text(
                "Risk Assessment Summary",
                exact=True
            )
        ).to_be_visible(timeout=15000)

        print("Risk Assessment opened successfully.")

    def risk_group(self, group_name):
        group = self.page.locator(".border-box").filter(
            has=self.page.locator(".border-box-label").filter(
                has_text=re.compile(
                    rf"^\s*{re.escape(group_name)}\s*$"
                )
            )
        )

        expect(group).to_have_count(1)
        return group

    def risk_radio(self, group_name, value):
        return self.risk_group(group_name).locator(
            f'input.ant-radio-input[value="{value}"]'
        )

    def risk_select_multiple(self, selections):

        print("\n========== SELECTING RISK FACTORS ==========")

        # Validate the requested selections.
        for group_name, value in selections.items():
            assert group_name in self.RISK_OPTIONS, (
                f"Unknown risk factor: {group_name}"
            )

            assert value in self.RISK_OPTIONS[group_name], (
                f"Invalid option '{value}' for {group_name}"
            )

        max_attempts = 5

        for attempt in range(1, max_attempts + 1):

            print(f"\nVerification attempt {attempt}/{max_attempts}")

            # Select only options that are not currently selected.
            for group_name, expected_value in selections.items():

                actual_values = self.risk_selected_values(group_name)

                if actual_values != [expected_value]:
                    print(
                        f"Updating {group_name}: "
                        f"{actual_values} -> {expected_value}"
                    )

                    self.risk_select(group_name, expected_value)

            # Allow asynchronous frontend updates to settle.
            self.page.wait_for_timeout(700)

            mismatches = {}

            for group_name, expected_value in selections.items():

                actual_values = self.risk_selected_values(group_name)

                print(
                    f"{group_name}: "
                    f"Expected={expected_value}, "
                    f"Actual={actual_values}"
                )

                if actual_values != [expected_value]:
                    mismatches[group_name] = actual_values

            if mismatches:
                print(f"Selections reverted: {mismatches}")
                continue

            # Confirm selections remain stable after another interval.
            self.page.wait_for_timeout(700)

            stable = all(
                self.risk_selected_values(group_name) == [expected_value]
                for group_name, expected_value in selections.items()
            )

            if stable:

                print("\nAll requested risk selections are stable.")

                # Verify the application's displayed calculation.
                self.risk_verify_calculation()

                # For a complete five-factor scenario, verify the
                # score against the intended selections too.
                if len(selections) == len(self.RISK_OPTIONS):
                    expected_score = sum(
                        self.RISK_OPTIONS[group_name][value]
                        for group_name, value in selections.items()
                    )

                    actual_score = self.risk_total_score()

                    assert actual_score == expected_score, (
                        f"Risk score mismatch: "
                        f"Expected {expected_score}, "
                        f"Actual {actual_score}"
                    )

                return

            print("Selections changed during stability verification.")

        final_values = {
            group_name: self.risk_selected_values(group_name)
            for group_name in selections
        }

        raise AssertionError(
            f"Risk selections did not remain stable after "
            f"{max_attempts} attempts. "
            f"Expected: {selections}. "
            f"Actual: {final_values}"
        )

    def risk_select(self, group_name, value):
        assert group_name in self.RISK_OPTIONS
        assert value in self.RISK_OPTIONS[group_name]

        radio = self.risk_radio(group_name, value)

        expect(radio).to_have_count(1)

        # Select the radio through Playwright's radio-specific action.
        radio.check(timeout=15000)

        expect(radio).to_be_checked(timeout=15000)

        print(f"Risk selected: {group_name} = {value}")


    def risk_selected_values(self, group_name):
        group = self.risk_group(group_name)

        return group.locator(
            "input.ant-radio-input:checked"
        ).evaluate_all(
            "(elements) => elements.map(el => el.value)"
        )

    def risk_summary_table(self):
        return self.page.locator(
            "table.signature-table"
        ).first

    def risk_total_score(self):
        total_row = self.risk_summary_table().locator(
            "tbody tr"
        ).filter(
            has=self.page.get_by_text(
                "Total Score",
                exact=True
            )
        )

        expect(total_row).to_have_count(1)

        score_cell = total_row.locator("td").last

        expect(score_cell).to_contain_text(
            re.compile(r"\d+")
        )

        return int(score_cell.inner_text().strip())

    def risk_classification(self):
        classification = self.page.get_by_text(
            re.compile(
                r"^Risk Classification:\s*(Low|Medium|High)$"
            )
        )

        expect(classification).to_be_visible(timeout=15000)

        text = classification.inner_text().strip()

        return text.split(":", 1)[1].strip()

    def risk_expected_score(self):
        total = 0

        for group_name, options in self.RISK_OPTIONS.items():
            selected = self.risk_selected_values(group_name)

            assert len(selected) <= 1, (
                f"Multiple radio selections in {group_name}: "
                f"{selected}"
            )

            if selected:
                total += options[selected[0]]

        return total

    def risk_expected_classification(self, score):
        if score <= 5:
            return "Low"

        if score <= 15:
            return "Medium"

        return "High"

    def risk_verify_calculation(self):
        expected_score = self.risk_expected_score()
        actual_score = self.risk_total_score()

        assert actual_score == expected_score, (
            f"Risk score mismatch: "
            f"expected {expected_score}, "
            f"actual {actual_score}"
        )

        expected_rating = self.risk_expected_classification(
            expected_score
        )

        actual_rating = self.risk_classification()

        assert actual_rating == expected_rating, (
            f"Risk classification mismatch: "
            f"expected {expected_rating}, "
            f"actual {actual_rating}"
        )

        print(
            f"Risk calculation verified: "
            f"Score={actual_score}, "
            f"Classification={actual_rating}"
        )

    def risk_complete_button(self):
        return self.page.get_by_role(
            "button",
            name="Complete Onboarding",
            exact=True
        )

    def risk_debug_all_selections(self):
        print("\n========== RISK SELECTION DEBUG ==========")

        total = 0

        for group_name, options in self.RISK_OPTIONS.items():
            selected = self.risk_selected_values(group_name)

            if selected:
                value = selected[0]
                score = options[value]
                total += score
            else:
                value = "NOT SELECTED"
                score = 0

            print(
                f"{group_name}: "
                f"Selected={value}, Score={score}"
            )

        print(f"Calculated score: {total}")
        print(f"Displayed score: {self.risk_total_score()}")
        print(f"Classification: {self.risk_classification()}")
        print("==========================================\n")

    def risk_update_changes_button(self):
        return self.page.get_by_role(
            "button",
            name="Update Changes",
            exact=True
        )

    def risk_complete_onboarding(self):

        complete_button = self.risk_complete_button()

        expect(complete_button).to_be_visible(timeout=15000)
        expect(complete_button).to_be_enabled()

        complete_button.click()

        print("Complete Onboarding button clicked.")

    def risk_verify_onboarding_completed(self):

        # The original completion button should disappear.
        expect(
            self.risk_complete_button()
        ).to_have_count(0, timeout=15000)

        # Update Changes should replace Complete Onboarding.
        update_button = self.risk_update_changes_button()

        expect(update_button).to_be_visible(timeout=15000)
        expect(update_button).to_be_enabled()

        print(
            "Onboarding completion verified. "
            "Update Changes button is visible."
        )

    def risk_click_update_changes(self):

        update_button = self.risk_update_changes_button()

        expect(update_button).to_be_visible(timeout=15000)
        expect(update_button).to_be_enabled(timeout=15000)

        update_button.click()

        print("Update Changes button clicked.")

    def risk_verify_update_success_notification(self):

        notification = self.page.locator(
            ".ant-notification-notice.ant-notification-notice-success"
        ).filter(
            has_text="Risk assessment updated successfully"
        )

        expect(notification).to_be_visible(timeout=15000)

        print("Risk assessment update success notification verified.")

    def risk_verify_selected_values(self, selections):

        for group_name, expected_value in selections.items():
            actual_values = self.risk_selected_values(group_name)

            assert actual_values == [expected_value], (
                f"{group_name}: "
                f"Expected {expected_value}, "
                f"got {actual_values}"
            )

        print("All updated risk selections verified.")

    def risk_get_current_client_id(self):

        # Capture the unique Client ID before leaving onboarding.
        parsed_url = urlparse(self.page.url)

        client_ids = parse_qs(parsed_url.query).get("client", [])

        assert len(client_ids) == 1 and client_ids[0], (
            f"Could not identify the current client from URL: "
            f"{self.page.url}"
        )

        client_id = client_ids[0]

        print(f"Current Client ID: {client_id}")

        return client_id

    def profiles_open_page(self):

        self.page.get_by_role(
            "link",
            name="Profiles",
            exact=False
        ).click()

        expect(self.page).to_have_url(
            re.compile(r".*/nolimit/app/profiles/?$")
        )

        expect(
            self.page.get_by_role(
                "heading",
                name="Profiles",
                exact=True
            )
        ).to_be_visible(timeout=15000)

        print("Profiles page opened successfully.")

    def profiles_search_client(self, client_id):

        search_input = self.page.get_by_placeholder(
            "Search by client ID or name",
            exact=True
        )

        expect(search_input).to_be_visible()

        search_input.fill(client_id)

        self.page.locator(
            ".search-box-z .search-btn"
        ).click()

        row = self.page.locator(
            "tr.ant-table-row"
        ).filter(
            has=self.page.locator(
                f'a.table-link[href*="client={client_id}"]'
            )
        )

        expect(row).to_have_count(1, timeout=15000)
        expect(row).to_be_visible()

        print(f"Client found in Profiles: {client_id}")

        return row

    def profiles_verify_client_risk(self, client_id, expected_risk):

        row = self.profiles_search_client(client_id)

        # Column 3: Type
        expect(
            row.locator("td").nth(2)
        ).to_contain_text("individual")

        # Column 4: Status
        expect(
            row.locator("td").nth(3)
        ).to_contain_text("Onboarded")

        # Column 6: Risk Rating
        expect(
            row.locator("td").nth(5)
        ).to_contain_text(expected_risk)

        print(
            f"Profiles verified: Client={client_id}, "
            f"Status=Onboarded, Risk={expected_risk}"
        )

    def profiles_open_individual(self, client_id):

        row = self.page.locator(
            "tr.ant-table-row"
        ).filter(
            has=self.page.locator(
                f'a.table-link[href*="client={client_id}"]'
            )
        )

        expect(row).to_have_count(1)

        client_link = row.locator("a.table-link")

        expect(client_link).to_be_visible()

        client_link.click()

        expect(self.page).to_have_url(
            re.compile(
                rf"/nolimit/app/profiles/individual/process"
                rf"\?.*client={re.escape(client_id)}(?:&|$)"
            ),
            timeout=15000
        )

        print(f"Individual profile opened: {client_id}")

    def profile_verify_verification_page(self, client_id):

        expect(
            self.page.get_by_role(
                "heading",
                name="Profile - Individual",
                exact=True
            )
        ).to_be_visible(timeout=15000)

        expect(
            self.page.locator(
                ".tab-z-option.active"
            ).filter(
                has_text="Verification"
            )
        ).to_be_visible()

        expect(
            self.page.locator(
                ".breadcrumb-badge"
            )
        ).to_contain_text(client_id)

        expect(
            self.page.locator(
                ".breadcrumb-text"
            )
        ).to_have_text("Processed Details")

        print(
            f"Profile Verification page loaded: {client_id}"
        )

    def profile_verification_field(self, field_name):

        field = self.page.locator(
            ".verification-report-item"
        ).filter(
            has=self.page.locator(
                "span.label",
                has_text=re.compile(
                    rf"^\s*{re.escape(field_name)}\s*$"
                )
            )
        )

        expect(field).to_have_count(1, timeout=15000)

        return field

    def profile_verification_field_value(self, field_name):

        field = self.profile_verification_field(field_name)

        badge = field.locator("span.custom-badge")

        expect(badge).to_be_visible()

        return badge.inner_text().strip()

    def profile_verify_processed_details(self):

        required_fields = [
            "Face Match",
            "Issuing Country",
            "Region",
            "Type of Document",
            "First Name",
            "Last Name",
            "Date of Birth",
            "Driver Licence Number",
            "Personal Number",
            "Expiry Date",
            "Gender",
            "Nationality",
            "Issue Date",
            "Place of Birth",
            "Address",
            "Residential Address",
            "Face Recognition Time",
            "Text Extraction Time",
        ]

        # This field can legitimately be empty.
        optional_empty_fields = {
            "Place of Birth",
        }

        print("\n========== PROFILE VERIFICATION DETAILS ==========")

        for field_name in required_fields:

            field = self.profile_verification_field(field_name)

            expect(field).to_be_visible()

            value = self.profile_verification_field_value(
                field_name
            )

            print(f"{field_name}: {value}")

            if field_name not in optional_empty_fields:
                assert value, (
                    f"Verification field '{field_name}' "
                    f"has no displayed value."
                )

        print("All expected processed detail fields verified.")

    def profile_verify_document_images(self):

        image_labels = [
            "Live Photo",
            "Document Front",
            "Document Back",
        ]

        print("\n========== PROFILE DOCUMENT IMAGES ==========")

        for label in image_labels:
            image_label = self.page.locator(
                ".document-img .custom-label"
            ).filter(
                has_text=re.compile(
                    rf"^\s*{re.escape(label)}\s*$"
                )
            )

            expect(image_label).to_have_count(1)

            expect(image_label).to_be_visible()

            image = image_label.locator(
                "xpath=following-sibling::div[1]//img"
            )

            expect(image).to_have_count(1)

            expect(image).to_be_visible(timeout=30000)

            expect(image).to_have_attribute(
                "src",
                re.compile(r"^https?://"),
                timeout=30000
            )

            # Wait for the browser to finish loading the image.
            expect(image).to_have_js_property(
                "complete",
                True,
                timeout=30000
            )

            assert image.evaluate(
                "(img) => img.naturalWidth > 0 && img.naturalHeight > 0"
            ), f"{label} image failed to load."

            print(f"{label}: Image loaded successfully.")

        print("All three verification images verified.")

    def verification_capture_review_form_details(self, strict=True):
        """
        Capture extracted document details before Save & Confirm.
        """

        expect(
            self.page.get_by_role(
                "heading",
                name="Review Extracted Information"
            )
        ).to_be_visible(timeout=15000)

        fields = [
            "First Name",
            "Last Name",
            "Date of Birth",
            "Gender",
            "Nationality",
            "Issuing Country",
            "Type of Document",
            "Driver Licence Number",
            "Personal Number",
            "Issue Date",
            "Expiry Date",
            "Place of Birth",
        ]

        details = {}

        for field_name in fields:

            field = self.page.locator(
                "div.col-span-1.md\\:col-span-4"
            ).filter(
                has=self.page.locator(
                    "label",
                    has_text=re.compile(
                        rf"^\s*{re.escape(field_name)}\s*$"
                    )
                )
            )

            if strict:
                expect(field).to_have_count(1)
            else:
                if field.count() == 0:
                    print("Review field not found; skipping optional field.")
                    continue
            selected_option = field.locator(
                ".ant-select-selection-item"
            )

            if selected_option.count() > 0:
                value = selected_option.inner_text().strip()

            else:
                field_input = field.locator(
                    "input:not(.ant-select-selection-search-input)"
                )

                if field_input.count() > 0:
                    value = field_input.first.input_value().strip()
                else:
                    value = ""

            details[field_name] = value

        assert details["First Name"], "First Name was not extracted"
        assert details["Last Name"], "Last Name was not extracted"

        print(
            f"Captured {len(details)} review form fields "
            "before submission."
        )

        return details

    def verification_compare_review_to_profile(
            self,
            original_details,
            saved_details
    ):
        from datetime import datetime

        def normalize(field_name, value):
            value = (value or "").strip()

            if value.lower() in ("", "not readable"):
                return ""

            # Normalize dates.
            if field_name in (
                    "Date of Birth",
                    "Issue Date",
                    "Expiry Date"
            ):
                for date_format in ("%Y-%m-%d", "%b %d, %Y"):
                    try:
                        return datetime.strptime(
                            value, date_format
                        ).strftime("%Y-%m-%d")
                    except ValueError:
                        pass

            # Normalize country names and ISO country codes.
            if field_name in ("Nationality", "Issuing Country"):

                # Example: Sri Lanka (LKA) -> LKA
                country_code = re.search(r"\(([A-Z]{3})\)", value)

                if country_code:
                    return country_code.group(1).casefold()

                # Example: LKA -> lka
                return value.casefold()

            return " ".join(value.split()).casefold()

        mismatches = {}
        skipped = []
        compared = []

        for field_name, original_value in original_details.items():

            assert field_name in saved_details, (
                f"Field '{field_name}' missing from saved profile"
            )

            saved_value = saved_details[field_name]

            original_normalized = normalize(
                field_name, original_value
            )

            saved_normalized = normalize(
                field_name, saved_value
            )

            if not original_normalized:
                skipped.append(field_name)
                print(f"SKIPPED: {field_name} (original value empty)")
                continue

            if original_normalized != saved_normalized:
                mismatches[field_name] = {
                    "original": original_value,
                    "saved": saved_value,
                }
                print(f"MISMATCH: {field_name}")

            else:
                compared.append(field_name)
                print(f"MATCH: {field_name}")

        assert compared, "No populated original fields were compared"

        assert not mismatches, (
            "Verification details do not match after reopening: "
            f"{mismatches}"
        )

        print(
            f"Verification persistence PASSED: "
            f"{len(compared)} fields matched, "
            f"{len(skipped)} blank original fields skipped."
        )

    def verification_capture_processed_details(self):
        """
        Capture saved verification details from the
        completed Individual Profile -> Verification page.
        """

        report = self.page.locator(".verification-report")
        expect(report).to_be_visible(timeout=15000)

        details = {}

        items = report.locator(".verification-report-item")
        expect(items.first).to_be_visible(timeout=15000)

        for index in range(items.count()):
            item = items.nth(index)

            label = item.locator("span.label").inner_text().strip()
            value = item.locator("span.custom-badge").inner_text().strip()

            assert label, f"Missing field label at index {index}"

            assert label not in details, (
                f"Duplicate verification field: {label}"
            )

            details[label] = value

        print(f"Captured {len(details)} saved verification fields.")

        return details


    # ============================================================
    # DOCUMENTS GAP COVERAGE - DELETE, MODIFY, REUPLOAD, VALIDATION
    # Added without changing existing methods or locators.
    # ============================================================

    def docs_gap_open(self, tab="Verify"):
        """Open Documents and the requested Documents subtab."""
        expect(self.documents_tab).to_be_visible(timeout=15000)
        if not re.search(r"\bactive\b", self.documents_tab.get_attribute("class") or ""):
            self.open_tab("Documents")
        self.click_documents_subtab(tab)
        self.verify_documents_subtab_active(tab)
        self.verify_documents_reference_id()

    def docs_gap_resolve_filename(self, file_name):
        """Consent Letter is stored with the generated client ID in its filename."""
        if file_name == "Consent Letter":
            return f"consent-letter-{self.get_verify_reference_id()}.pdf"
        return file_name

    def docs_gap_item(self, file_name, group_name=None):
        """Find a Verify document card using the app's existing .border-box/.w-85 markup."""
        file_name = self.docs_gap_resolve_filename(file_name)
        if group_name is None:
            # Search all groups: the same front/back filenames can belong
            # to Driver Licence or Proof of Age Card workflows.
            matches = self.page.locator(".border-box .w-85").filter(
                has=self.page.get_by_role("heading", name=file_name, exact=True)
            )
            expect(matches).to_have_count(1, timeout=15000)
            expect(matches).to_be_visible()
            return matches
        return self.get_verify_document_card(group_name, file_name)

    def docs_gap_action(self, item, action):
        """Find a document action button and wait for it to be ready."""

        expect(item).to_be_visible(timeout=30000)

        button = item.locator(f'button[title="{action}"]')

        try:
            expect(button).to_be_visible(timeout=15000)

        except AssertionError:
            # Fallback to accessible button name
            button = item.get_by_role(
                "button",
                name=action,
                exact=True
            )

            try:
                expect(button).to_be_visible(timeout=10000)

            except AssertionError:
                print(f"\nDOCUMENT ACTION NOT FOUND: {action}")
                print("Document card HTML:")
                print(item.evaluate("(element) => element.outerHTML"))

                print("Buttons in document card:")
                print(item.locator("button").evaluate_all("""
                    buttons => buttons.map(button => ({
                        title: button.getAttribute("title"),
                        ariaLabel: button.getAttribute("aria-label"),
                        text: button.innerText,
                        disabled: button.disabled
                    }))
                """))

                raise

        expect(button).to_have_count(1)
        expect(button).to_be_enabled(timeout=15000)

        return button

    def docs_gap_modal(self, kind=None):
        """Locate the visible dialog; deletion may use a Popconfirm."""
        if kind == "delete":
            candidates = self.page.locator(
                ".ant-popconfirm:visible, .ant-popover:visible, "
                ".ant-modal:visible, .modal-z:visible, [role='alertdialog']:visible"
            )
        else:
            candidates = self.page.locator(
                ".modal-z:visible, .ant-modal:visible, [role='dialog']:visible"
            )
        expect(candidates.last).to_be_visible(timeout=15000)
        return candidates.last

    def docs_gap_modify(self, file_name, group_name=None):
        self.docs_gap_action(self.docs_gap_item(file_name, group_name), "Modify").click()
        modal = self.docs_gap_modal()
        expect(modal.get_by_role("button", name="Save", exact=True)).to_be_visible()
        return modal

    def docs_gap_delete_decision(self, file_name, group_name=None, confirm=False):
        """Handle a native browser confirm OR a DOM confirmation.

        Without a Playwright dialog listener, native JS confirm is auto-dismissed,
        leaving no HTML popup to locate. Returns the confirmation message.
        """
        observed = []

        def on_dialog(dialog):
            observed.append(dialog.message)
            if confirm:
                dialog.accept()
            else:
                dialog.dismiss()

        self.page.on("dialog", on_dialog)
        try:
            self.docs_gap_action(
                self.docs_gap_item(file_name, group_name), "Delete"
            ).click()
        finally:
            self.page.remove_listener("dialog", on_dialog)

        if observed:
            return observed[0]

        # Fallback for HTML popconfirm implementations. Do not silently
        # pass if neither a native dialog nor an HTML confirmation appears.
        candidates = self.page.locator(
            ".ant-popconfirm:visible, .ant-popover:visible, "
            ".ant-modal:visible, .modal-z:visible, "
            "[role='alertdialog']:visible"
        )
        if candidates.count() == 0:
            raise AssertionError(
                "Delete click opened no native browser dialog or supported "
                "HTML confirmation. Inspect the delete interaction in DevTools."
            )
        modal = candidates.last
        expect(modal).to_be_visible()
        message = modal.inner_text().strip()
        if confirm:
            self.docs_gap_confirm_delete(modal)
        else:
            self.docs_gap_cancel(modal)
        return message

    def docs_gap_delete(self, file_name, group_name=None):
        self.docs_gap_action(self.docs_gap_item(file_name, group_name), "Delete").click()
        return self.docs_gap_modal(kind="delete")

    def docs_gap_cancel(self, modal):
        cancel = modal.get_by_role("button", name=re.compile(r"^cancel$|^no$", re.I))
        expect(cancel.first).to_be_visible()
        cancel.first.click()
        expect(modal).to_be_hidden(timeout=15000)

    def docs_gap_close_modal(self, modal):
        close = modal.locator("button.modal-z-close, button.ant-modal-close")
        if close.count() == 0:
            close = modal.get_by_role("button", name=re.compile(r"^close$", re.I))
        expect(close.first).to_be_visible()
        close.first.click()
        expect(modal).to_be_hidden(timeout=15000)

    def docs_gap_modify_fields(self, modal):
        """Controls observed in the actual Sentinel Modify dialog."""
        for label in ("Document Name", "Uploaded Date", "Expiry Date"):
            expect(modal.get_by_text(label, exact=False).first).to_be_visible()

        name = modal.get_by_placeholder("Enter document name", exact=True)
        expiry = modal.get_by_placeholder("Select expiry date", exact=True)
        uploaded = modal.get_by_placeholder("Select uploaded date", exact=True)
        expect(name).to_have_count(1)
        expect(expiry).to_have_count(1)
        expect(uploaded).to_have_count(1)
        expect(name).to_be_visible()
        expect(expiry).to_be_visible()
        expect(uploaded).to_be_disabled()
        return name, expiry

    def docs_gap_verify_modify_fields(self, modal, expected_filename=None):
        name, expiry = self.docs_gap_modify_fields(modal)
        expect(modal.get_by_role("button", name="Save", exact=True)).to_be_visible()
        expect(modal.get_by_role("button", name="Cancel", exact=True)).to_be_visible()
        expect(name).to_be_editable()
        expect(expiry).to_be_enabled()
        if expected_filename:
            assert name.input_value().strip(), "Document Name was blank in Modify dialog"
        return name, expiry

    def docs_gap_verify_required_name(self, modal):
        expect(modal).to_be_visible()

        # Find the Document Name label
        label = modal.locator("label").filter(
            has_text=re.compile(r"Document\s+Name", re.I)
        ).first

        expect(label).to_be_visible()

        # Inspect CSS-generated required marker
        marker = label.evaluate("""
            (el) => {
                const before = window.getComputedStyle(el, "::before").content;
                const after = window.getComputedStyle(el, "::after").content;

                return {
                    before: before,
                    after: after,
                    html: el.outerHTML
                };
            }
        """)

        print("Document Name marker details:", marker)

        assert (
                "*" in marker["before"]
                or "*" in marker["after"]
                or "*" in label.inner_text()
        ), (
            "Document Name required (*) marker was not found. "
            f"Details: {marker}"
        )


    def docs_gap_verify_uploaded_date_readonly(self, modal):
        expect(modal.get_by_text("Uploaded Date", exact=False).first).to_be_visible()
        uploaded = modal.get_by_placeholder("Select uploaded date", exact=True)
        expect(uploaded).to_be_visible()
        expect(uploaded).to_be_disabled()
        assert uploaded.input_value().strip(), "Uploaded Date should be populated"

    def docs_gap_set_name(self, modal, new_name):
        name, _ = self.docs_gap_modify_fields(modal)
        expect(name).to_be_editable()
        name.fill(new_name)
        expect(name).to_have_value(new_name)

    def docs_gap_set_expiry(self, modal, value="31-12-2030"):
        """Enter an expiry date and verify it survives blur."""

        _, expiry = self.docs_gap_modify_fields(modal)

        expect(expiry).to_be_visible()
        expect(expiry).to_be_enabled()

        print("\nEXPIRY DATE FIELD DETAILS")
        print("Input type:", expiry.get_attribute("type"))
        print("Read-only:", expiry.get_attribute("readonly"))
        print("Input HTML:", expiry.evaluate("(el) => el.outerHTML"))

        expiry.click()

        if not expiry.is_editable():
            raise AssertionError(
                "Expiry Date is picker-only. "
                "Calendar selection must be implemented."
            )

        expiry.fill(value)

        print("Value after fill:", repr(expiry.input_value()))

        expect(expiry).to_have_value(value)

        expiry.press("Tab")

        print("Value after Tab:", repr(expiry.input_value()))

        expect(expiry).to_have_value(
            value,
            timeout=5000
        )


    def docs_gap_save(self, modal):
        expect(modal).to_be_visible()

        save_button = modal.get_by_role(
            "button", name="Save", exact=True
        )

        expect(save_button).to_be_enabled()

        with self.page.expect_response(
                lambda response:
                "/api/v1/documents/update" in response.url
                and response.request.method == "PUT",
                timeout=30000
        ) as response_info:
            save_button.click()

        response = response_info.value

        print("\nDOCUMENT UPDATE API DIAGNOSTICS")
        print("HTTP Status:", response.status)

        # Only print non-sensitive fields from the request.
        payload = response.request.post_data_json

        if isinstance(payload, dict):
            print("Request field names:", list(payload.keys()))
            print("Document name:", payload.get("fileName"))
            print("Expiry date:", payload.get("expiryDate"))

        try:
            response_body = response.json()
            if isinstance(response_body, dict):
                print("Response message:", response_body.get("message"))
                print("Response error:", response_body.get("error"))
            else:
                print("Response type:", type(response_body).__name__)
        except ValueError:
            print("Response was not valid JSON")

        assert response.ok, (
            f"Document update API failed with HTTP {response.status}"
        )

        expect(modal).to_be_hidden(timeout=30000)

    def docs_gap_confirm_delete(self, modal):
        """Confirm deletion and wait for the confirmation to close."""
        expect(modal.get_by_text(re.compile(r"delete|remove|sure", re.I)).first).to_be_visible()
        confirm = modal.get_by_role(
            "button", name=re.compile(r"^(ok|delete|confirm|yes)$", re.I)
        )
        expect(confirm.first).to_be_enabled()
        confirm.first.click()
        expect(modal).to_be_hidden(timeout=30000)

    def docs_gap_verify_deleted(self, file_name, group_name=None):
        """Verify the card disappears; checks the resolved filename and group."""
        resolved = self.docs_gap_resolve_filename(file_name)
        if group_name is None:
            cards = self.page.locator(".border-box .w-85")
        else:
            cards = self.page.locator(".border-box").filter(
                has=self.page.locator(".border-box-label", has_text=re.compile(
                    rf"^\s*{re.escape(group_name)}\s*$"
                ))
            ).locator(".w-85")
        expect(cards.filter(
            has=self.page.get_by_role("heading", name=resolved, exact=True)
        )).to_have_count(0, timeout=30000)

    def docs_gap_reupload(self, file_name, file_path, group_name=None):
        """Replace a document through its own reupload input."""
        file_path = Path(file_path).resolve()
        assert file_path.is_file(), f"Reupload file not found: {file_path}"
        card = self.docs_gap_item(file_name, group_name)
        file_input = card.locator(".upload-wrapper input[type='file']")
        expect(file_input).to_have_count(1)
        file_input.set_input_files(str(file_path))
        # The application may asynchronously upload and rename the document.
        expect(self.page.locator(".ant-message-notice-error:visible")).to_have_count(0)

    def docs_gap_upload_tab_next(self):
        """Assert an empty Upload tab does not advance to Verify."""
        self.docs_gap_open("Upload")
        before_url = self.page.url
        next_button = self.page.get_by_role("button", name="Next", exact=True)
        expect(next_button).to_be_visible()
        if next_button.is_enabled():
            next_button.click()
        self.verify_documents_subtab_active("Upload")
        assert self.page.url == before_url, (
            "Documents advanced even though no documents were uploaded"
        )

    def docs_gap_verify_no_name(self):
        client = self.page.locator("h4.secondary-title").filter(
            has_text="Client Name:"
        )
        expect(client).to_be_visible()
        expect(client.locator("span")).to_have_text("N/A")

    def debug_onboarding_blocked(self, stage):
        print(f"\n===== ONBOARDING DEBUG: {stage} =====")
        print("Current URL:", self.page.url)

        for button_name in ["Submit", "Save & Confirm"]:
            button = self.page.get_by_role(
                "button", name=button_name, exact=False
            )

            if button.count():
                print(
                    f"{button_name}: "
                    f"visible={button.first.is_visible()}, "
                    f"enabled={button.first.is_enabled()}"
                )

        invalid_fields = self.page.locator(
            'input[aria-invalid="true"], '
            'select[aria-invalid="true"], '
            'textarea[aria-invalid="true"]'
        )

        print("Invalid field count:", invalid_fields.count())

        for index in range(invalid_fields.count()):
            field = invalid_fields.nth(index)
            print("Invalid field:", field.evaluate(
                "(el) => el.outerHTML"
            ))

        print("Visible error messages:")
        for selector in [
            ".ant-form-item-explain-error",
            "[role='alert']",
            ".error-message",
        ]:
            matches = self.page.locator(selector + ":visible")
            for index in range(matches.count()):
                print(matches.nth(index).inner_text())

        print("====================================\n")

    def kyc_verify_extracted_full_name(self, expected_full_name):
        """Verify KYC Full Legal Name matches the extracted document name."""

        full_name = self.kyc_text_input("full_name")

        expect(full_name).to_be_visible(timeout=15000)

        expected_full_name = " ".join(expected_full_name.split())

        assert expected_full_name, (
            "Expected extracted full name is empty."
        )

        expect(full_name).to_have_value(
            expected_full_name,
            timeout=15000
        )

        print(
            f"KYC Full Legal Name matches extracted name: "
            f"{expected_full_name}"
        )

    def kyc_verify_calendar_icon(self, index):
        """
        Verify the calendar icon inside a KYC date picker.

        0 = Date of Birth
        1 = Passport Date of Issue
        2 = Passport Date of Expiry
        """

        field_names = {
            0: "Date of Birth",
            1: "Passport Date of Issue",
            2: "Passport Date of Expiry",
        }

        assert index in field_names, (
            f"Unsupported KYC date field index: {index}"
        )

        date_input = self.kyc_date_input(index)

        expect(date_input).to_be_visible(timeout=15000)

        # Find the Ant Design date-picker container
        picker = date_input.locator(
            "xpath=ancestor::*[contains("
            "concat(' ', normalize-space(@class), ' '), "
            "' ant-picker ')][1]"
        )

        expect(picker).to_be_visible()

        # Calendar icon rendered inside the date picker
        calendar_icon = picker.locator(
            ".ant-picker-suffix .anticon-calendar, "
            ".ant-picker-suffix svg"
        ).first

        expect(calendar_icon).to_be_visible(timeout=10000)

        print(
            f"Calendar icon verified: {field_names[index]}"
        )


    # =========================================================
    # RISK RATING RANGE TABLE - EXCEL COVERAGE 17-22
    # =========================================================

    def risk_rating_range_table(self):
        table = self.page.locator("table.signature-table").filter(
            has=self.page.locator("thead th").filter(
                has_text=re.compile(r"^\s*Risk Rating Range\s*$")
            )
        )

        expect(table).to_have_count(1, timeout=15000)
        return table

    def risk_rating_range_row(self, rating):
        if rating not in ("High", "Medium", "Low"):
            raise ValueError(f"Unknown risk rating: {rating}")

        table = self.risk_rating_range_table()

        row = table.locator("tbody tr").filter(
            has=self.page.locator("td:first-child").filter(
                has_text=re.compile(
                    rf"^\s*{re.escape(rating)}\s*$"
                )
            )
        )

        expect(row).to_have_count(1)
        return row

    def risk_verify_rating_range_heading(self):
        heading = self.risk_rating_range_table().locator(
            "thead th"
        )

        expect(heading).to_have_count(1)
        expect(heading).to_have_text("Risk Rating Range")
        expect(heading).to_have_attribute("colspan", "2")
        expect(heading).to_be_visible()

    def risk_verify_rating_column_header(self):
        header = self.risk_rating_range_table().locator(
            "tbody tr:first-child td:first-child"
        )

        expect(header).to_be_visible()
        expect(header).to_have_text("Rating")

    def risk_verify_range_column_header(self):
        header = self.risk_rating_range_table().locator(
            "tbody tr:first-child td:nth-child(2)"
        )

        expect(header).to_be_visible()
        expect(header).to_have_text("Range")

    def risk_verify_all_rating_levels(self):
        for rating in ("High", "Medium", "Low"):
            row = self.risk_rating_range_row(rating)
            expect(row.locator("td").first).to_be_visible()
            expect(row.locator("td").first).to_have_text(rating)

    def risk_verify_rating_score_ranges(self):
        expected_ranges = {
            "High": "16 and above",
            "Medium": "6 to 15",
            "Low": "0 to 5",
        }

        for rating, expected_range in expected_ranges.items():
            row = self.risk_rating_range_row(rating)
            expect(row.locator("td").nth(1)).to_have_text(
                expected_range
            )

    def risk_verify_rating_colors(self):
        expected_classes = {
            "High": ("bg-red-300", "dark:bg-red-950"),
            "Medium": ("bg-yellow-100", "dark:bg-yellow-950"),
            "Low": ("bg-emerald-100", "dark:bg-emerald-950"),
        }

        for rating, (light_class, dark_class) in expected_classes.items():
            cell = self.risk_rating_range_row(rating).locator(
                "td"
            ).first

            expect(cell).to_be_visible()

            classes = cell.get_attribute("class") or ""
            class_tokens = classes.split()

            assert light_class in class_tokens, (
                f"{rating}: missing light-mode class {light_class}. "
                f"Actual classes: {classes}"
            )

            assert dark_class in class_tokens, (
                f"{rating}: missing dark-mode class {dark_class}. "
                f"Actual classes: {classes}"
            )

            # Check that a real background color is rendered,
            # rather than only checking the HTML class names.
            background = cell.evaluate(
                "(element) => getComputedStyle(element).backgroundColor"
            )

            assert background not in (
                "transparent",
                "rgba(0, 0, 0, 0)",
                ""
            ), (
                f"{rating}: background color is not rendered. "
                f"Computed value: {background}"
            )

            print(f"{rating}: background color = {background}")




    # =========================================================
    # KYC - PARTIALLY COVERED EXCEL SCENARIOS
    # =========================================================

    def kyc_partial_form(self):
        form = self.page.locator(".kyc-form")
        expect(form).to_be_visible(timeout=15000)
        return form


    def kyc_partial_verify_active_tab(self):
        """Verify the KYC Form tab is active and inspect its styling."""

        active_tabs = self.page.locator(".tab-z-option.active")

        # Diagnostic: identify all elements marked active
        print(
            "All active tabs:",
            active_tabs.all_text_contents()
        )

        # Select only the active KYC Form tab
        kyc_tab = active_tabs.filter(
            has_text=re.compile(r"KYC\s*Form", re.IGNORECASE)
        )

        expect(kyc_tab).to_have_count(1, timeout=15000)
        expect(kyc_tab).to_be_visible()
        expect(kyc_tab).to_contain_text("KYC Form")

        styles = kyc_tab.evaluate("""
            el => {
                const s = getComputedStyle(el);
                const label = el.querySelector("label");
                const l = label ? getComputedStyle(label) : null;

                return {
                    classes: el.className,
                    background: s.backgroundColor,
                    color: s.color,
                    borderBottom: s.borderBottomColor,
                    boxShadow: s.boxShadow,
                    labelColor: l ? l.color : null,
                    beforeBackground:
                        getComputedStyle(el, "::before").backgroundColor,
                    afterBackground:
                        getComputedStyle(el, "::after").backgroundColor
                };
            }
        """)

        print("KYC active tab styles:", styles)
        print("KYC Form tab verified as active.")


    def kyc_partial_verify_section_01(self):
        section = self.kyc_partial_form().locator(
            ".section-header"
        ).filter(
            has=self.page.locator("h6").filter(
                has_text="SECTION 01 - KYC PROFILE OF THE CLIENT"
            )
        )

        expect(section).to_have_count(1)
        expect(section).to_be_visible()

        expect(section.locator("h6")).to_have_text(
            "SECTION 01 - KYC PROFILE OF THE CLIENT"
        )

        print(
            "KYC Section 01 background:",
            section.evaluate(
                "(el) => getComputedStyle(el).backgroundColor"
            )
        )

        background = section.evaluate(
            "(el) => getComputedStyle(el).backgroundColor"
        )

        assert background == "color(srgb 0.792157 0.207843 0.501961 / 0.3)", (
            f"Unexpected Section 01 background: {background}"
        )

    def kyc_partial_verify_label(self, label_text):
        label = self.kyc_partial_form().locator(
            "label"
        ).get_by_text(
            label_text,
            exact=True
        )

        expect(label).to_have_count(1)
        expect(label).to_be_visible()

        print(f"KYC label verified: {label_text}")

    def kyc_partial_verify_box_heading(self, heading):
        box_label = self.kyc_partial_form().locator(
            ".border-box > .border-box-label"
        ).filter(
            has_text=heading
        )

        expect(box_label).to_have_count(1)
        expect(box_label).to_have_text(heading)
        expect(box_label).to_be_visible()

        print(f"KYC section heading verified: {heading}")

    def kyc_partial_verify_wealth_options(self):
        expected_options = [
            "Employment Income / Salary",
            "Savings",
            "Mortgage / Loan",
            "Sale of Property",
            "Business Income",
            "Investment Income",
            "Sale of Investments / Shares",
            "Inheritance",
            "Gift",
            "Superannuation / Pension",
            "Trust Distribution",
            "Insurance Payout",
            "Legal Settlement / Compensation",
            "Cryptocurrency Assets",
            "Overseas Funds",
            "Other",
        ]

        wealth_section = self.kyc_partial_form().locator(
            ".header-box"
        ).filter(
            has=self.page.locator(
                ".header-box-label"
            ).filter(
                has_text="Source of Wealth"
            )
        )

        expect(wealth_section).to_have_count(1)
        expect(wealth_section).to_be_visible()

        checkboxes = wealth_section.locator(
            ".ant-checkbox-group input[type='checkbox']"
        )

        expect(checkboxes).to_have_count(16)

        actual_options = checkboxes.evaluate_all(
            "elements => elements.map(el => el.value)"
        )

        assert actual_options == expected_options, (
            "Source of Wealth options do not match.\n"
            f"Expected: {expected_options}\n"
            f"Actual: {actual_options}"
        )

        for option in expected_options:
            expect(
                wealth_section.get_by_text(option, exact=True)
            ).to_be_visible()

        print("All 16 Source of Wealth options verified.")



    # =========================================================
    # RISK ASSESSMENT - PARTIAL COVERAGE BATCH 1
    # Excel: 413, 414, 417, 420, 423, 426, 449
    # =========================================================

    def risk_partial_verify_active_tab(self):
        tab = self.page.locator(
            ".tab-z-option.active"
        ).filter(
            has_text=re.compile(
                r"^\s*Risk Assessment\s*$",
                re.IGNORECASE
            )
        )

        expect(tab).to_have_count(1)
        expect(tab).to_be_visible()

        # Record the actual styles before adding an
        # application-specific pink highlight assertion.
        styles = tab.evaluate("""
            el => {
                const s = getComputedStyle(el);
                const label = el.querySelector("label");
                const ls = label ? getComputedStyle(label) : null;

                return {
                    background: s.backgroundColor,
                    color: s.color,
                    borderBottom: s.borderBottomColor,
                    boxShadow: s.boxShadow,
                    labelColor: ls ? ls.color : null,
                    beforeBackground:
                        getComputedStyle(el, "::before").backgroundColor,
                    afterBackground:
                        getComputedStyle(el, "::after").backgroundColor
                };
            }
        """)

        print("Risk Assessment active tab styles:", styles)

    def risk_partial_section_header(self, heading):
        header = self.page.locator(
            ".custom-form .section-header"
        ).filter(
            has=self.page.locator("h6").filter(
                has_text=re.compile(
                    rf"^\s*{re.escape(heading)}\s*$"
                )
            )
        )

        expect(header).to_have_count(1)
        return header

    def risk_partial_verify_pink_heading(self, heading):
        header = self.risk_partial_section_header(heading)

        expect(header).to_be_visible()
        expect(header.locator("h6")).to_have_text(heading)

        # Convert browser CSS colors (including color(srgb))
        # into actual RGBA channels.
        rgba = header.evaluate("""
            el => {
                const color = getComputedStyle(el).backgroundColor;
                const canvas = document.createElement("canvas");
                canvas.width = 1;
                canvas.height = 1;

                const ctx = canvas.getContext("2d");
                ctx.clearRect(0, 0, 1, 1);
                ctx.fillStyle = color;
                ctx.fillRect(0, 0, 1, 1);

                return Array.from(
                    ctx.getImageData(0, 0, 1, 1).data
                );
            }
        """)

        red, green, blue, alpha = rgba

        # Check a visible pink/magenta tint rather than
        # only checking that a background exists.
        assert (
            alpha >= 20
            and red > green * 1.5
            and blue > green * 1.25
        ), (
            f"{heading}: expected pink section background, "
            f"actual RGBA={rgba}"
        )

        print(f"{heading}: pink header verified, RGBA={rgba}")

    def risk_partial_verify_classification_placement(self):
        rating_table = self.risk_rating_range_table()

        # Classification is the next sibling of the rating
        # table inside the right-hand flex column.
        classification = rating_table.locator(
            "xpath=following-sibling::div[1]"
        )

        expect(classification).to_have_count(1)
        expect(classification).to_be_visible()
        expect(classification).to_contain_text(
            re.compile(
                r"Risk Classification:\s*(Low|Medium|High)"
            )
        )

        table_box = rating_table.bounding_box()
        classification_box = classification.bounding_box()

        assert table_box is not None
        assert classification_box is not None

        table_bottom = table_box["y"] + table_box["height"]

        assert classification_box["y"] >= table_bottom - 1, (
            "Risk Classification is not below "
            "the Risk Rating Range table."
        )

        print(
            "Risk Classification verified below "
            "Risk Rating Range table."
        )



    # =========================================================
    # RISK ASSESSMENT - PARTIAL COVERAGE BATCH 2
    # Excel: 430-437
    # =========================================================

    RISK_PARTIAL_GROUPS = [
        ("Country / Jurisdiction Risk",
         "Country / Jurisdiction Risk", [1, 3, 5]),
        ("Individual Risk",
         "Politically Exposed Person (PEP) Status", [1, 3, 5]),
        ("Australian Residential Status",
         "Australian Residential Status", [1, 3]),
        ("Transfer of Funds",
         "Transfer of Funds", [1, 3]),
        ("Adverse Media",
         "Adverse Media", [1, 3]),
    ]

    def risk_partial_summary_rows(self):
        table = self.risk_summary_table()
        expect(table).to_be_visible()

        # Twelve attribute rows, followed by Total Score.
        rows = table.locator("tbody tr")
        expect(rows).to_have_count(13)
        return rows

    def risk_partial_verify_summary_headers(self):
        headers = self.risk_summary_table().locator("thead th")

        expect(headers).to_have_text([
            "Risk Factor",
            "Attribute",
            "Risk Score",
        ])

        print("Risk summary column headers verified.")

    def risk_partial_verify_summary_factors(self):
        rows = self.risk_partial_summary_rows()

        factors = rows.locator("td[rowspan]")

        expect(factors).to_have_text([
            "Country / Jurisdiction Risk",
            "Individual Risk",
            "Australian Residential Status",
            "Transfer of Funds",
            "Adverse Media",
        ])

        print("All five Risk Factors verified.")

    def risk_partial_verify_selected_factor(self, factor_name):
        rows = self.risk_partial_summary_rows()

        offset = 0
        matched = False

        for summary_name, group_name, scores in self.RISK_PARTIAL_GROUPS:
            count = len(scores)

            if summary_name != factor_name:
                offset += count
                continue

            matched = True
            group = self.risk_group(group_name)

            radio_options = group.locator(
                "label.ant-radio-wrapper"
            )
            expect(radio_options).to_have_count(count)

            checked_indexes = [
                index
                for index in range(count)
                if radio_options.nth(index)
                .locator("input[type='radio']")
                .is_checked()
            ]

            assert len(checked_indexes) == 1, (
                f"{factor_name}: expected exactly one "
                f"selected radio option, got {checked_indexes}"
            )

            selected_index = checked_indexes[0]
            selected_radio = radio_options.nth(selected_index)

            selected_text = selected_radio.locator(
                ".ant-radio-label"
            ).inner_text().strip()

            # Country high-risk option contains multiple bullet
            # points, but its summary shows only the first.
            expected_attribute = (
                selected_text.splitlines()[0].strip()
            )

            selected_row = rows.nth(offset + selected_index)

            attribute_cell = selected_row.locator("td").nth(
                1 if selected_index == 0 else 0
            )

            assert (
                attribute_cell.inner_text().strip()
                == expected_attribute
            ), (
                f"{factor_name}: summary attribute does not "
                f"match selected radio option."
            )

            # Verify selected-row styling and pink indicator.
            assert "font-semibold" in (
                selected_row.get_attribute("class") or ""
            ), f"{factor_name}: selected row not highlighted"

            dot = attribute_cell.locator(
                "span[style*='var(--primary)']"
            )
            expect(dot).to_be_visible()

            score_cell = selected_row.locator("td").last
            expect(score_cell.locator("span.font-bold")).to_have_text(
                str(scores[selected_index])
            )

            background = attribute_cell.evaluate(
                "(el) => getComputedStyle(el).backgroundColor"
            )

            print(
                f"{factor_name}: selected={expected_attribute}, "
                f"score={scores[selected_index]}, "
                f"background={background}"
            )
            break

        assert matched, f"Unknown risk factor: {factor_name}"


    def risk_partial_verify_all_scores(self):
        rows = self.risk_partial_summary_rows()

        offset = 0
        expected_total = 0

        # Step 1: Calculate expected total from selected radios.
        for summary_name, group_name, scores in self.RISK_PARTIAL_GROUPS:
            group = self.risk_group(group_name)

            radio_options = group.locator(
                "label.ant-radio-wrapper"
            )

            expect(radio_options).to_have_count(len(scores))

            selected_indexes = [
                i for i in range(len(scores))
                if radio_options.nth(i)
                .locator("input[type='radio']")
                .is_checked()
            ]

            assert len(selected_indexes) == 1, (
                f"{summary_name}: expected exactly one "
                f"selected radio option, got {selected_indexes}"
            )

            selected_index = selected_indexes[0]
            selected_score = scores[selected_index]

            expected_total += selected_score

            print(
                f"Radio selection: {summary_name} "
                f"| index={selected_index} "
                f"| score={selected_score}"
            )

            # Verify every displayed option score.
            for index, expected_score in enumerate(scores):
                row = rows.nth(offset + index)
                score_cell = row.locator("td").last

                assert score_cell.inner_text().strip() == str(
                    expected_score
                ), (
                    f"{summary_name}, option {index}: "
                    f"expected score {expected_score}, "
                    f"got {score_cell.inner_text()}"
                )

            offset += len(scores)

        # Step 2: Read the displayed total after the loop.
        total_row = rows.last

        expect(total_row.locator("td").first).to_have_text(
            "Total Score"
        )

        actual_total = int(
            total_row.locator("td").last.inner_text().strip()
        )

        # Step 3: Independently calculate highlighted total.
        highlighted_total = 0

        print("\n===== RISK SCORE DEBUG =====")
        print("Expected total from radios:", expected_total)
        print("Displayed total:", actual_total)

        for row in rows.all()[:-1]:
            if "font-semibold" not in (
                row.get_attribute("class") or ""
            ):
                continue

            cells = row.locator("td")
            score = cells.last.inner_text().strip()

            attribute_cell = cells.nth(
                1 if cells.count() == 3 else 0
            )

            attribute = attribute_cell.inner_text().strip()

            print(
                f"Highlighted attribute: {attribute} "
                f"| Score: {score}"
            )

            highlighted_total += int(score)

        print(
            "Total from highlighted summary rows:",
            highlighted_total
        )
        print("============================\n")

        # Step 4: Assert both independent calculations.
        assert actual_total == expected_total, (
            f"Radio score total mismatch: "
            f"expected {expected_total}, "
            f"displayed {actual_total}"
        )

        assert actual_total == highlighted_total, (
            f"Highlighted score total mismatch: "
            f"highlighted {highlighted_total}, "
            f"displayed {actual_total}"
        )

        # Step 5: Verify classification.
        expected_classification = (
            "Low" if expected_total <= 5
            else "Medium" if expected_total <= 15
            else "High"
        )


        actual_classification = self.risk_classification()

        assert actual_classification == expected_classification, (
            f"Expected risk classification "
            f"'{expected_classification}', "
            f"got '{actual_classification}'"
        )

        print(
            f"All risk scores verified. "
            f"Total={actual_total}, "
            f"Classification={expected_classification}"
        )


    def risk_partial_verify_country_score_sync(self):
        group = self.risk_group(
            "Country / Jurisdiction Risk"
        )

        radios = group.locator("input[type='radio']")
        expect(radios).to_have_count(3)

        rows = self.risk_partial_summary_rows()

        country_options = [
            ("low", 0, 1),
            ("other", 1, 3),
            ("high", 2, 5),
        ]

        for value, index, expected_score in country_options:
            radio = radios.nth(index)

            radio.check()
            expect(radio).to_be_checked()

            # Verify that the correct country summary row
            # becomes selected after the radio interaction.
            selected_row = rows.nth(index)

            expect(selected_row).to_have_class(
                re.compile(r"\bfont-semibold\b")
            )

            expect(
                selected_row.locator("td").last
            ).to_have_text(str(expected_score))

            # Verify that other country rows are deselected.
            for other_index in range(3):
                if other_index == index:
                    continue

                expect(rows.nth(other_index)).not_to_have_class(
                    re.compile(r"\bfont-semibold\b")
                )

            print(
                f"Country option '{value}' synchronized "
                f"with summary score {expected_score}"
            )


        # Restore Low Risk.
        radios.nth(0).check()

        expect(radios.nth(0)).to_be_checked()

        # Verify the Low Risk row becomes selected.
        expect(rows.nth(0)).to_have_class(
            re.compile(r"\bfont-semibold\b")
        )

        # Inspect all Country / Jurisdiction summary rows.
        print("\n===== COUNTRY RISK RESTORE DEBUG =====")

        for index in range(3):
            row = rows.nth(index)

            print(
                f"Row {index}: "
                f"text={row.inner_text()!r}, "
                f"class={row.get_attribute('class')!r}"
            )

        print(
            "Radio values:",
            [
                {
                    "value": radios.nth(i).get_attribute("value"),
                    "checked": radios.nth(i).is_checked()
                }
                for i in range(3)
            ]
        )

        print("====================================\n")

        # Check that the restored Low Risk row
        # displays its correct score.
        expect(
            rows.nth(0).locator("td").last
        ).to_have_text("1", timeout=10000)

        # Other Country Risk scores should remain unchanged.
        expect(
            rows.nth(1).locator("td").last
        ).to_have_text("3")

        expect(
            rows.nth(2).locator("td").last
        ).to_have_text("5")

        print(
            "Country Risk restored successfully: "
            "Low=1, Other=3, High=5"
        )



    def risk_partial_416_verify_country_radio_options(self):
        group = self.risk_group(
            "Country / Jurisdiction Risk"
        )

        radios = group.locator("input[type='radio']")
        expect(radios).to_have_count(3)

        expected_options = [
            ("low", 1),
            ("other", 3),
            ("high", 5),
        ]

        # Country Risk occupies the first three summary rows.
        rows = self.risk_partial_summary_rows()

        for selected_index, (value, score) in enumerate(
            expected_options
        ):
            radio = radios.nth(selected_index)

            assert radio.get_attribute("value") == value, (
                f"Expected radio value '{value}'"
            )

            radio.check()
            expect(radio).to_be_checked()

            # Exactly one country radio must be checked.
            checked_count = sum(
                radios.nth(i).is_checked()
                for i in range(3)
            )

            assert checked_count == 1, (
                f"Expected one selected Country Risk radio, "
                f"found {checked_count}"
            )

            # Verify other radios are unchecked.
            for other_index in range(3):
                if other_index != selected_index:
                    expect(
                        radios.nth(other_index)
                    ).not_to_be_checked()

            # Verify selected summary row and score.
            selected_row = rows.nth(selected_index)

            expect(selected_row).to_have_class(
                re.compile(r"\bfont-semibold\b")
            )

            expect(
                selected_row.locator("td").last
            ).to_have_text(str(score), timeout=10000)

            # Verify no other Country Risk row is highlighted.
            for other_index in range(3):
                if other_index != selected_index:
                    expect(
                        rows.nth(other_index)
                    ).not_to_have_class(
                        re.compile(r"\bfont-semibold\b")
                    )

            print(
                f"PASS: Country Risk '{value}' selected, "
                f"other options unchecked, summary score={score}"
            )

        # Restore Low Risk for consistency.
        radios.nth(0).check()

        expect(radios.nth(0)).to_be_checked()

        expect(
            rows.nth(0).locator("td").last
        ).to_have_text("1", timeout=10000)

        print(
            "Excel 416: Country Risk radio "
            "mutual exclusivity verified."
        )



    def risk_partial_441_inspect_update_notification(self):
        update_button = self.page.get_by_role(
            "button",
            name="Update Changes",
            exact=True
        )

        complete_button = self.page.get_by_role(
            "button",
            name="Complete Onboarding",
            exact=True
        )

        print("\n===== RISK ASSESSMENT ACTION DEBUG =====")

        print("Current URL:", self.page.url)

        print(
            "Update Changes visible:",
            update_button.is_visible()
        )

        print(
            "Complete Onboarding visible:",
            complete_button.is_visible()
        )

        if update_button.is_visible():
            print(
                "Risk Assessment is displaying "
                "the Update Changes action."
            )

        elif complete_button.is_visible():
            print(
                "Risk Assessment is displaying "
                "the Complete Onboarding action."
            )

        else:
            raise AssertionError(
                "Neither Update Changes nor "
                "Complete Onboarding is visible."
            )

        print("========================================\n")



    def risk_partial_441_verify_update_notification(self):
        update_button = self.page.get_by_role(
            "button",
            name="Update Changes",
            exact=True
        )

        expect(update_button).to_be_visible(timeout=10000)
        expect(update_button).to_be_enabled()

        update_button.click()

        # Ant Design notifications/messages, if used.
        # The exact locator and text should be confirmed
        # against the application's actual notification.
        notification = self.page.locator(
            ".ant-message-success, "
            ".ant-notification-notice-success, "
            "[role='alert']"
        ).filter(
            has_text=re.compile(
                r"success|updated|saved",
                re.IGNORECASE
            )
        ).first

        expect(notification).to_be_visible(timeout=10000)

        print(
            "Excel 441: Update Changes clicked and "
            "success notification verified:",
            notification.inner_text()
        )



    def risk_441_open_existing_client_assessment(self):
        # Navigate to Profiles.
        profiles_link = self.page.get_by_role(
            "link",
            name=re.compile(r"Profiles", re.IGNORECASE)
        )

        expect(profiles_link).to_be_visible()
        profiles_link.click()

        # Open All Files.
        all_files = self.page.get_by_text(
            "All Files",
            exact=True
        )

        expect(all_files).to_be_visible(timeout=10000)
        all_files.click()

        # Open the first available client ID.
        # Adjust this locator if the client IDs use
        # buttons or another HTML structure.
        client_link = self.page.locator(
            "table tbody tr a"
        ).first

        expect(client_link).to_be_visible(timeout=10000)

        print(
            "Opening client:",
            client_link.inner_text().strip()
        )

        client_link.click()

        # Navigate to Risk Assessment.
        risk_tab = self.page.get_by_text(
            "Risk Assessment",
            exact=True
        ).first

        expect(risk_tab).to_be_visible(timeout=10000)
        risk_tab.click()

        # Verify this is the existing-client editing state.
        update_button = self.page.get_by_role(
            "button",
            name="Update Changes",
            exact=True
        )

        expect(update_button).to_be_visible(timeout=10000)

        print(
            "Existing client Risk Assessment opened. "
            "Update Changes button is visible."
        )


    def risk_441_verify_update_notification(self):
        update_button = self.page.get_by_role(
            "button",
            name="Update Changes",
            exact=True
        )

        expect(update_button).to_be_visible(timeout=10000)
        expect(update_button).to_be_enabled()

        # Identify the notification containers.
        notification_selector = (
            ".ant-message-notice, "
            ".ant-notification-notice, "
            "[data-sonner-toast], "
            "[role='alert'], "
            "[role='status']"
        )

        # Capture existing notifications before clicking.
        existing_messages = self.page.locator(
            notification_selector
        ).all_inner_texts()

        print("Notifications before update:", existing_messages)

        # Click Update Changes.
        update_button.click()

        # Inspect notifications appearing after the action.
        # Exclude the known unrelated login success message.
        new_notification = self.page.locator(
            notification_selector
        ).filter(
            has_text=re.compile(
                r"updated|saved|changes.*success|"
                r"successfully updated",
                re.IGNORECASE
            )
        ).first

        expect(new_notification).to_be_visible(timeout=10000)

        message = new_notification.inner_text().strip()

        assert "login" not in message.lower(), (
            "Detected login notification instead of "
            "Risk Assessment update notification."
        )

        print("\n===== EXCEL 441 RESULT =====")
        print("Update Changes clicked successfully.")
        print("Update notification:", message)
        print("============================\n")


    def risk_413_verify_active_tab_pink(self):
        risk_label = self.page.get_by_text(
            "Risk Assessment",
            exact=True
        ).first

        expect(risk_label).to_be_visible(timeout=10000)

        result = risk_label.evaluate("""
            (element) => {
                const canvas = document.createElement("canvas");
                canvas.width = 1;
                canvas.height = 1;
                const ctx = canvas.getContext("2d");

                function toRGBA(color) {
                    ctx.clearRect(0, 0, 1, 1);
                    ctx.fillStyle = color;
                    ctx.fillRect(0, 0, 1, 1);
                    return Array.from(
                        ctx.getImageData(0, 0, 1, 1).data
                    );
                }

                const ancestors = [];
                let node = element;

                for (let i = 0; i < 5 && node; i++) {
                    const style = getComputedStyle(node);

                    ancestors.push({
                        tag: node.tagName,
                        className:
                            typeof node.className === "string"
                                ? node.className
                                : "",
                        background: toRGBA(
                            style.backgroundColor
                        ),
                        textColor: toRGBA(style.color)
                    });

                    node = node.parentElement;
                }

                return ancestors;
            }
        """)

        print("\\n===== EXCEL 413 TAB STYLING =====")

        for item in result:
            print(item)

        print("================================\\n")

        # Verify an ancestor of the label is active.
        active = any(
            "active" in item["className"].split()
            for item in result
        )

        assert active, (
            "Risk Assessment tab does not have "
            "the active CSS class."
        )

        # Expected pink is approximately RGB(202, 53, 126).
        expected_pink = (202, 53, 126)

        def is_pink(rgba):
            return (
                rgba[3] >= 230
                and all(
                    abs(rgba[i] - expected_pink[i]) <= 30
                    for i in range(3)
                )
            )

        pink_found = any(
            is_pink(item["background"])
            for item in result
        )

        assert pink_found, (
            "Active Risk Assessment tab does not "
            "have the expected pink background. "
            f"Computed styles: {result}"
        )

        # Check that the visible label text is white.
        text_color = result[0]["textColor"]

        assert all(
            channel >= 235
            for channel in text_color[:3]
        ), (
            "Risk Assessment tab text is not white. "
            f"Actual RGBA: {text_color}"
        )

        print(
            "Excel 413 PASSED: Risk Assessment tab "
            "is active, pink, and has white text."
        )


    def risk_441_verify_completion_alert(self):
        complete_button = self.page.get_by_role(
            "button",
            name="Complete Onboarding",
            exact=True
        )

        update_button = self.page.get_by_role(
            "button",
            name="Update Changes",
            exact=True
        )

        expect(complete_button).to_be_visible(timeout=10000)
        expect(complete_button).to_be_enabled()

        # Monitor notifications before clicking the button.
        self.page.evaluate("""
            () => {
                const selector = [
                    ".ant-message",
                    ".ant-notification",
                    "[data-sonner-toast]",
                    "[role='alert']",
                    "[role='status']"
                ].join(",");

                const readMessages = () =>
                    [...document.querySelectorAll(selector)]
                        .map(el =>
                            (el.innerText || el.textContent || "").trim()
                        )
                        .filter(Boolean);

                const existing = new Set(readMessages());

                window.__risk441Messages = [];

                if (window.__risk441Observer) {
                    window.__risk441Observer.disconnect();
                }

                const capture = () => {
                    for (const message of readMessages()) {
                        if (
                            !existing.has(message) &&
                            !window.__risk441Messages.includes(message)
                        ) {
                            window.__risk441Messages.push(message);
                        }
                    }
                };

                window.__risk441Observer =
                    new MutationObserver(capture);

                window.__risk441Observer.observe(
                    document.body,
                    {
                        childList: true,
                        subtree: true,
                        characterData: true
                    }
                );
            }
        """)

        # Complete onboarding.
        complete_button.click()

        # Verify the button changes to Update Changes.
        expect(update_button).to_be_visible(timeout=15000)

        # Allow notification updates to be captured.
        self.page.wait_for_timeout(1500)

        messages = self.page.evaluate("""
            () => {
                window.__risk441Observer?.disconnect();
                return window.__risk441Messages || [];
            }
        """)

        print("\n===== EXCEL 441 COMPLETION DEBUG =====")
        print("Complete Onboarding clicked.")
        print("Update Changes button is visible.")
        print("Captured notifications:", messages)
        print("======================================\n")

        # Accept completion-related success wording only.
        completion_messages = [
            message for message in messages
            if re.search(
                r"(risk assessment|onboarding).*complet"
                r"|complet.*(success|risk assessment|onboarding)",
                message,
                re.IGNORECASE
            )
        ]

        assert completion_messages, (
            "Onboarding button changed to Update Changes, "
            "but no completion notification was captured. "
            f"Captured messages: {messages}"
        )

        print(
            "Excel 441 PASSED:",
            completion_messages[0]
        )


    # Excel 432–436 — Selected summary attributes are pink
    def risk_verify_five_selected_attributes_pink(self):
        rows = self.risk_partial_summary_rows()
        offset = 0

        for factor_name, group_name, scores in self.RISK_PARTIAL_GROUPS:
            factor_rows = [
                rows.nth(offset + i)
                for i in range(len(scores))
            ]

            selected_rows = [
                row for row in factor_rows
                if "font-semibold" in (
                    row.get_attribute("class") or ""
                ).split()
            ]

            assert len(selected_rows) == 1, (
                f"{factor_name}: expected one highlighted "
                f"summary row, found {len(selected_rows)}"
            )

            row = selected_rows[0]
            cells = row.locator("td")

            attribute_cell = cells.nth(
                1 if cells.count() == 3 else 0
            )

            pink_dot = attribute_cell.locator(
                "span[style*='background-color']"
            ).first

            expect(pink_dot).to_be_visible()

            colors = attribute_cell.evaluate("""
                (cell) => {
                    const dot = cell.querySelector(
                        "span[style*='background-color']"
                    );

                    const canvas = document.createElement("canvas");
                    canvas.width = 1;
                    canvas.height = 1;

                    const ctx = canvas.getContext("2d");

                    function rgba(color) {
                        ctx.clearRect(0, 0, 1, 1);
                        ctx.fillStyle = color;
                        ctx.fillRect(0, 0, 1, 1);

                        return Array.from(
                            ctx.getImageData(0, 0, 1, 1).data
                        );
                    }

                    return {
                        attribute: cell.innerText.trim(),
                        background: rgba(
                            getComputedStyle(cell).backgroundColor
                        ),
                        indicator: rgba(
                            getComputedStyle(dot).backgroundColor
                        )
                    };
                }
            """)

            def is_pink(color):
                expected = (202, 53, 128)

                return (
                    color[3] >= 20
                    and all(
                        abs(color[i] - expected[i]) <= 35
                        for i in range(3)
                    )
                )

            assert is_pink(colors["background"]), (
                f"{factor_name}: selected attribute "
                f"background is not pink: {colors}"
            )

            assert is_pink(colors["indicator"]), (
                f"{factor_name}: selected indicator "
                f"is not pink: {colors}"
            )

            print(
                f"PASS: {factor_name} | "
                f"{colors['attribute']} | "
                f"background={colors['background']}"
            )

            offset += len(scores)

        print(
            "Excel 432–436 PASSED: "
            "all five selected attributes are pink."
        )

    # Excel 416 — Complete Country Risk options
    def risk_416_verify_complete_country_options(self):
        group = self.risk_group(
            "Country / Jurisdiction Risk"
        )

        options = group.locator(
            "label.ant-radio-wrapper"
        )

        expect(options).to_have_count(3)

        expected_descriptions = [
            [
                "Low risk countries per Basel AML Index",
                "3.33 or lower"
            ],
            [
                "Other countries and jurisdictions"
            ],
            [
                "High risk countries as per Basel AML Index",
                "6.67 or higher",
                "Transparency International Corruption Index",
                "NCCT countries and jurisdictions",
                "Countries subject to sanctions",
                "FATF Grey Listed"
            ]
        ]

        radios = group.locator("input[type='radio']")
        expect(radios).to_have_count(3)

        original_index = next(
            (i for i in range(3) if radios.nth(i).is_checked()),
            None
        )

        assert original_index is not None, (
            "No Country Risk option is initially selected."
        )

        for index, descriptions in enumerate(
            expected_descriptions
        ):
            option = options.nth(index)

            for description in descriptions:
                expect(option).to_contain_text(description)

            radios.nth(index).check()
            expect(radios.nth(index)).to_be_checked()

            checked_count = sum(
                radios.nth(i).is_checked()
                for i in range(3)
            )

            assert checked_count == 1, (
                f"Country option {index}: "
                f"expected one checked radio, got {checked_count}"
            )

            print(
                f"PASS: Country option {index + 1}, "
                "descriptions and exclusivity verified."
            )

        radios.nth(original_index).check()

        print(
            "Excel 416 PASSED: all Country Risk "
            "descriptions and radio exclusivity verified."
        )

    # Excel 437 — Static risk-score weights
    def risk_437_verify_option_score_weights(self):
        rows = self.risk_partial_summary_rows()
        offset = 0

        for factor_name, group_name, scores in self.RISK_PARTIAL_GROUPS:
            for index, expected_score in enumerate(scores):
                row = rows.nth(offset + index)

                expect(
                    row.locator("td").last
                ).to_have_text(str(expected_score))

                print(
                    f"PASS: {factor_name}, "
                    f"option {index + 1}, "
                    f"score={expected_score}"
                )

            offset += len(scores)

        expect(rows.last.locator("td").first).to_have_text(
            "Total Score"
        )

        print(
            "Excel 437 PASSED: all option score "
            "weights and Total Score row verified."
        )




    def risk_450_verify_classification_for_all_levels(self):
        scenarios = [
            {
                "name": "Low",
                "selections": ["low", "nonPep", "residence",
                               "bankTransfer", "noHits"],
                "expected_total": 5,
            },
            {
                "name": "Medium",
                "selections": ["other", "nonPep", "nonResidence",
                               "bankTransfer", "noHits"],
                "expected_total": 9,
            },
            {
                "name": "High",
                "selections": ["high", "pep", "nonResidence",
                               "cash", "confirmed"],
                "expected_total": 19,
            },
        ]

        groups = [
            "Country / Jurisdiction Risk",
            "Politically Exposed Person (PEP) Status",
            "Australian Residential Status",
            "Transfer of Funds",
            "Adverse Media",
        ]

        rows = self.risk_partial_summary_rows()

        for scenario in scenarios:
            print(
                f"\n===== EXCEL 450: {scenario['name']} ====="
            )

            # Select the required options in each risk group.
            for group_name, value in zip(
                groups, scenario["selections"]
            ):
                group = self.risk_group(group_name)

                radio = group.locator(
                    f"input[type='radio'][value='{value}']"
                )

                expect(radio).to_have_count(1)
                radio.check()
                expect(radio).to_be_checked()

            # Wait for the UI to update its total.
            total_cell = rows.last.locator("td").last

            expect(total_cell).to_have_text(
                str(scenario["expected_total"]),
                timeout=10000
            )

            actual_total = int(
                total_cell.inner_text().strip()
            )

            # Calculate expected classification independently.
            expected_classification = (
                "Low" if actual_total <= 5
                else "Medium" if actual_total <= 15
                else "High"
            )

            assert expected_classification == scenario["name"], (
                f"Expected {scenario['name']}, "
                f"calculated {expected_classification}"
            )

            # Existing helper returns classification as a string.
            actual_classification = self.risk_classification()

            assert actual_classification == scenario["name"], (
                f"Score {actual_total}: "
                f"expected classification {scenario['name']}, "
                f"got {actual_classification}"
            )

            print(f"Expected score: {scenario['expected_total']}")
            print(f"Actual score: {actual_total}")
            print(
                f"Classification: {actual_classification}"
            )
            print(f"PASS: {scenario['name']} classification")

        print(
            "\nExcel 450 PASSED: Low, Medium, and High "
            "risk classifications verified."
        )



    # =========================================================
    # KYC - REMAINING 10 PARTIAL EXCEL SCENARIOS
    # =========================================================

    @staticmethod
    def _kyc_is_pink(rgba):
        """Match the application's observed primary pink."""
        if len(rgba) != 4 or rgba[3] < 20:
            return False

        r, g, b, _ = rgba
        return (
            175 <= r <= 230
            and 25 <= g <= 100
            and 90 <= b <= 175
        )

    @staticmethod
    def _kyc_computed_rgba(locator):
        """Resolve CSS colors, including variables and opacity."""
        return locator.evaluate("""
            el => {
                const c = document.createElement('canvas');
                c.width = c.height = 1;

                const ctx = c.getContext('2d');
                ctx.fillStyle = getComputedStyle(el).backgroundColor;
                ctx.fillRect(0, 0, 1, 1);

                return Array.from(
                    ctx.getImageData(0, 0, 1, 1).data
                );
            }
        """)

    # ---------------------------------------------------------
    # EXCEL 350 - ACTIVE KYC TAB IS PINK
    # ---------------------------------------------------------

    def kyc_47_verify_active_tab_pink(self):
        tab = self.page.locator(
            ".tab-z-option.active"
        ).filter(
            has=self.page.get_by_text(
                "KYC Form",
                exact=True
            )
        )

        expect(tab).to_have_count(1)
        expect(tab).to_be_visible()

        rgba = self._kyc_computed_rgba(tab)

        r, g, b, alpha = rgba

        # Pink includes both the primary saturated shade
        # and the lighter pink used by the KYC tab.
        is_pink = (
            alpha >= 20
            and r > g
            and r > b
            and b > g
            and (r - g) >= 20
        )

        assert is_pink, (
            f"Excel 350: Active KYC tab is not pink. "
            f"Actual RGBA: {rgba}"
        )

        print(
            f"Excel 350 PASSED: "
            f"KYC active tab background = {rgba}"
        )

    # ---------------------------------------------------------
    # EXCEL 354 - SECTION 01 PINK RECTANGLE
    # ---------------------------------------------------------

    def kyc_48_verify_section_01_pink(self):
        heading = self.kyc_form.locator(
            ".section-header h6"
        ).filter(
            has_text=re.compile(
                r"^\s*SECTION 01 - "
                r"KYC PROFILE OF THE CLIENT\s*$"
            )
        )

        expect(heading).to_have_count(1)
        expect(heading).to_be_visible()

        container = heading.locator("xpath=..")

        expect(container).to_be_visible()

        rgba = self._kyc_computed_rgba(container)

        assert self._kyc_is_pink(rgba), (
            f"Excel 354: Section 01 "
            f"rectangle is not pink: {rgba}"
        )

        print(
            f"Excel 354 PASSED: "
            f"Section 01 pink rectangle {rgba}"
        )

    # ---------------------------------------------------------
    # EXCEL 359, 379, 386, 399, 400, 403
    # VERIFY SIX REQUIRED LABELS
    # ---------------------------------------------------------

    def kyc_49_verify_six_exact_labels(self):
        requirements = {
            359: "Gender",
            379: "Nationality",
            386: "Passport",
            399: "Address",
            400: "Home Country or Permanent Address",
            403: "Current Residency Address",
        }

        for excel_id, expected in requirements.items():
            label = self.kyc_form.locator(
                "label"
            ).filter(
                has_text=re.compile(
                    r"^\s*"
                    + re.escape(expected)
                    + r"\s*$"
                )
            )

            expect(label).to_have_count(1)
            expect(label).to_be_visible()

            print(
                f"Excel {excel_id} PASSED: {expected}"
            )

    # ---------------------------------------------------------
    # EXCEL 410 - ALL 16 SOURCE OF WEALTH LABELS
    # ---------------------------------------------------------

    def kyc_50_verify_all_16_wealth_labels(self):
        section = self.kyc_form.locator(
            ".header-box"
        ).filter(
            has_text="Source of Wealth"
        )

        expect(section).to_be_visible()

        options = section.locator(
            "label.ant-checkbox-wrapper"
        )

        expect(options).to_have_count(16)

        actual = [
            text.strip()
            for text in options.locator(
                ".ant-checkbox-label"
            ).all_text_contents()
        ]

        expected = list(self.KYC_WEALTH_OPTIONS)

        assert actual == expected, (
            "Excel 410: Source of Wealth "
            "labels or order differ.\n"
            f"Expected: {expected}\n"
            f"Actual: {actual}"
        )

        values = options.locator(
            'input[type="checkbox"]'
        ).evaluate_all(
            "els => els.map(el => el.value)"
        )

        assert values == expected, (
            "Excel 410: Checkbox values "
            f"differ from labels: {values}"
        )

        print(
            "Excel 410 PASSED: "
            "all 16 labels and checkbox values match."
        )

    # ---------------------------------------------------------
    # EXCEL 412 - SAVE KYC AND VERIFY DATA PERSISTENCE
    # ---------------------------------------------------------

    def kyc_51_verify_save_persistence(self):
        from uuid import uuid4

        suffix = uuid4().hex[:8]

        values = {
            "full_name": f"Automation KYC {suffix}",
            "contact": "+94771234567",
            "email": f"kyc.{suffix}@example.com",
            "document_number": f"DOC{suffix.upper()}",
            "passport_number": f"P{suffix.upper()}",
        }

        addresses = (
            f"Home Address {suffix}, Colombo",
            f"Current Address {suffix}, Negombo",
        )

        # Fill text fields.
        for field, value in values.items():
            self.kyc_fill_text(field, value)

        # Fill address fields.
        for i, value in enumerate(addresses):
            self.kyc_fill_address(i, value)

        # Select dropdown values.
        self.kyc_choose_first_dropdown_option(
            "Gender"
        )

        self.kyc_choose_first_dropdown_option(
            "Country of Residency",
            search="Sri"
        )

        self.kyc_choose_first_dropdown_option(
            "Nationality 1",
            scope=self.kyc_nationality_box,
            search="Sri"
        )

        self.kyc_choose_first_dropdown_option(
            "Occupation"
        )

        # Select two Source of Wealth options.
        self.kyc_set_wealth("Savings")
        self.kyc_set_wealth("Inheritance")

        # Capture selected dropdown values.
        dropdowns = (
            ("Gender", None),
            ("Country of Residency", None),
            ("Nationality 1", self.kyc_nationality_box),
            ("Occupation", None),
        )

        selected = {}

        for label, scope in dropdowns:
            select = self.kyc_select_for_label(
                label,
                scope
            )

            item = select.locator(
                ".ant-select-selection-item"
            ).first

            expect(item).to_be_visible()

            selected[label] = item.inner_text().strip()

            assert selected[label], (
                f"{label} has no selected value "
                "before saving"
            )

        # Save the KYC form.
        self.kyc_click_save()

        # Reload to verify data was actually persisted.
        self.page.wait_for_timeout(1500)

        self.page.reload(
            wait_until="domcontentloaded"
        )

        self.open_kyc_form()
        self.kyc_assert_loaded()

        # Verify text field persistence.
        for field, expected in values.items():
            expect(
                self.kyc_text_input(field)
            ).to_have_value(
                expected,
                timeout=15000
            )

            print(f"Persisted: {field}")

        # Verify address persistence.
        for i, expected in enumerate(addresses):
            expect(
                self.kyc_address(i)
            ).to_have_value(
                expected,
                timeout=15000
            )

            print(
                f"Persisted: address {i + 1}"
            )

        # Verify dropdown persistence.
        for label, _ in dropdowns:
            scope = (
                self.kyc_nationality_box
                if label == "Nationality 1"
                else None
            )

            item = self.kyc_select_for_label(
                label,
                scope
            ).locator(
                ".ant-select-selection-item"
            ).first

            expect(item).to_have_text(
                selected[label],
                timeout=15000
            )

            print(
                f"Persisted: {label} = "
                f"{selected[label]}"
            )

        # Verify Source of Wealth persistence.
        for wealth in (
            "Savings",
            "Inheritance"
        ):
            expect(
                self.kyc_wealth_input(wealth)
            ).to_be_checked(
                timeout=15000
            )

            print(
                f"Persisted: Source of Wealth - {wealth}"
            )

        print(
            "Excel 412 PASSED: "
            "saved KYC values survived a page reload."
        )



    def kyc_51_check_address_blur_and_save(self):
        from uuid import uuid4

        marker = f"KYC TEST {uuid4().hex[:8]}"

        address = self.kyc_address(0)

        # Enter the address.
        address.fill(marker)

        expect(address).to_have_value(marker)

        print("After typing:", repr(address.input_value()))

        # Trigger blur/change handling.
        address.press("Tab")

        expect(address).to_have_value(marker)

        print("After blur:", repr(address.input_value()))

        # Capture the Save API request.
        with self.page.expect_response(
            lambda response: (
                response.request.method == "PUT"
                and "/kyc-form" in response.url
            ),
            timeout=30000
        ) as response_info:
            self.kyc_click_save()

        response = response_info.value

        body = response.request.post_data or ""

        print("HTTP status:", response.status)
        print("Edited address sent:", marker in body)

        actual = self.kyc_address(0).input_value()

        print("Address after Save:", repr(actual))

        assert marker in body, (
            "BUG: Edited KYC address is missing "
            "from the Save API request payload."
        )

        assert actual == marker, (
            "BUG: KYC address changed unexpectedly "
            "after Save."
        )

        print("Excel 412 PASSED")
