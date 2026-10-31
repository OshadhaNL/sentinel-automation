
import re
from playwright.sync_api import Page, expect
from pathlib import Path
from playwright.sync_api import TimeoutError

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
        dropdown = self.get_review_dropdown(field_name)

        expect(dropdown).to_be_visible()

        dropdown.locator(".ant-select-selector").click()

        expect(
            self.page.locator(".ant-select-dropdown:visible")
        ).to_be_visible()

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
        self.verify_review_save_confirm_button()

        self.page.get_by_role(
            "button",
            name="Save & Confirm",
            exact=True
        ).click()

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

        # Verify at least one matching success heading is visible.
        expect(success_heading.first).to_be_visible(timeout=15000)

        success_message = self.page.get_by_text(
            "Your information has been received and is being processed for onboarding.",
            exact=True
        )

        expect(success_message.first).to_be_visible()

        finish_button = self.page.get_by_role(
            "button",
            name="Finish and View Submitted Documents",
            exact=True
        )

        expect(finish_button.first).to_be_visible()
        expect(finish_button.first).to_be_enabled()

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

        expect(review_heading).to_be_visible(timeout=90000)

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

