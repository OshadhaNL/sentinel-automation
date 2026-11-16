
"""Read-only Individual Profile Verification regression tests.

Requires TEST_EMAIL and TEST_PASSWORD.
Uses a dedicated client with processed verification data and two images.
Does not change client records.
"""

import re

import pytest
from playwright.sync_api import Page, expect

from pages.profiles.profileNavigation import open_client_profile
from pages.profiles.individual.individualVerificationPage import IndividualVerificationPage


@pytest.mark.ui
class TestIndividualVerificationReadOnly:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.profile = IndividualVerificationPage(page)

        open_client_profile(
            page,
            base_url,
            "individual",
            self.profile.CLIENT_ID
        )

        expect(self.profile.heading).to_be_visible(timeout=15000)
        self.profile.open()

        expect(self.profile.breadcrumb).to_contain_text(
            self.profile.CLIENT_ID
        )

    def test_verification_tab_is_active(self):
        expect(
            self.profile.tab("Verification")
        ).to_have_class(re.compile(r"\bactive\b"))

    def test_processed_details_breadcrumb(self):
        expect(self.profile.breadcrumb).to_contain_text(
            "Processed Details"
        )

        expect(
            self.profile.breadcrumb.locator(".breadcrumb-badge")
        ).to_contain_text(self.profile.CLIENT_ID)

    def test_all_18_fields_are_present_exactly_once(self):
        expect(
            self.profile.report.locator(".verification-report-item")
        ).to_have_count(18)

        for label in self.profile.LABELS:
            expect(self.profile.item(label)).to_have_count(1)
            expect(self.profile.item(label)).to_be_visible()

    def test_each_field_has_one_badge(self):
        for label in self.profile.LABELS:
            expect(self.profile.badge(label)).to_have_count(1)

    def test_face_match_status_has_correct_styling(self):
        badge = self.profile.badge("Face Match")

        assert self.profile.value("Face Match") == "Not Match"

        expect(badge).to_have_class(
            re.compile(r"\bbadge-error\b")
        )

    @pytest.mark.parametrize(
        "label",
        ["Region", "Expiry Date", "Issue Date"]
    )
    def test_unreadable_values_are_flagged(self, label):
        assert self.profile.value(label) == "Not readable"

        expect(
            self.profile.badge(label)
        ).to_have_class(re.compile(r"\bbadge-error\b"))

    def test_document_type(self):
        assert (
            self.profile.value("Type of Document")
            == "Driver Licence"
        )

    @pytest.mark.parametrize(
        "label",
        [
            "First Name",
            "Last Name",
            "Issuing Country",
            "Nationality",
            "Gender",
            "Occupation",
            "Driver Licence Number",
            "Card Number",
        ]
    )
    def test_processed_values_are_not_empty(self, label):
        assert self.profile.value(label), (
            f"{label} must not be blank for this client"
        )

    def test_missing_values_are_displayed_without_error(self):
        assert self.profile.value("Address") == "N/A"
        assert self.profile.value("Place of Birth") == ""

        expect(
            self.profile.badge("Address")
        ).to_be_visible()

        expect(
            self.profile.badge("Place of Birth")
        ).to_be_visible()

    def test_birth_date_format(self):
        assert re.fullmatch(
            r"[A-Za-z]{3} \d{1,2}, \d{4}",
            self.profile.value("Date of Birth")
        )

    @pytest.mark.parametrize(
        "label",
        ["Face Recognition Time", "Text Extraction Time"]
    )
    def test_processing_time_format(self, label):
        value = self.profile.value(label)

        assert re.fullmatch(
            r"\d+\s*s\s*:\s*\d+\s*ms",
            value
        ), (label, value)

    @pytest.mark.parametrize(
        "title",
        ["Live Photo", "Document Front"]
    )
    def test_verification_images_load(self, title):
        expect(
            self.profile.images.get_by_text(
                title,
                exact=True
            )
        ).to_be_visible()

        self.profile.assert_image_loaded(title)

    def test_images_have_distinct_sources(self):
        live = self.profile.image_for(
            "Live Photo"
        ).get_attribute("src")

        front = self.profile.image_for(
            "Document Front"
        ).get_attribute("src")

        assert live and front and live != front

    def test_verification_survives_reload(self):
        before = {
            label: self.profile.value(label)
            for label in self.profile.LABELS
        }

        self.page.reload(wait_until="domcontentloaded")

        expect(self.profile.heading).to_be_visible(timeout=15000)

        self.profile.open()

        after = {
            label: self.profile.value(label)
            for label in self.profile.LABELS
        }

        assert after == before

    def test_switch_away_and_back(self):
        self.profile.open_tab("Documents")
        self.profile.open()

        expect(self.profile.report).to_be_visible()

        expect(self.profile.breadcrumb).to_contain_text(
            self.profile.CLIENT_ID
        )
