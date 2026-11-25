"""WorldCheck profile details tests using controlled search results."""
import os
import re
import pytest
from playwright.sync_api import expect
from pages.loginPage import LoginPage
from pages.screeningPage import ScreeningPage
from pages.screeningResultsPage import ScreeningResultsPage
from pages.screeningMatchDetailsPage import ScreeningMatchDetailsPage

@pytest.fixture
def details(page, base_url):
    if os.getenv("SCREENING_ALLOW_ANALYZE") != "1":
        pytest.skip("Set SCREENING_ALLOW_ANALYZE=1")
    email, password = os.getenv("TEST_EMAIL"), os.getenv("TEST_PASSWORD")
    if not email or not password:
        pytest.skip("Set TEST_EMAIL and TEST_PASSWORD")
    name = os.getenv("SCREENING_MATCH_NAME", "John Smith")
    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(email)
    login.enter_password(password)
    login.click_login()
    expect(page).to_have_url(re.compile(r".*/nolimit/app/home/?$"), timeout=30000)
    screening = ScreeningPage(page)
    screening.open(base_url)
    screening.analyze(name)
    results = ScreeningResultsPage(page)
    results.assert_loaded(name)
    if results.count() == 0:
        pytest.skip(f"No WorldCheck matches returned for {name!r}")
    results.open_first_match()
    obj = ScreeningMatchDetailsPage(page)
    obj.assert_loaded()
    return obj

@pytest.mark.ui
class TestScreeningMatchDetails:
    def test_positive_details_page_loads(self, details):
        details.assert_loaded()

    def test_positive_profile_id_present(self, details):
        assert details.profile_id()

    def test_positive_personal_details_fields(self, details):
        for label in details.PERSONAL_FIELDS:
            expect(details.detail(label)).to_be_attached()

    def test_positive_profile_name_present(self, details):
        expect(details.detail("Name")).not_to_be_empty()

    def test_positive_all_report_sections(self, details):
        for section in details.SECTIONS:
            expect(details.section(section)).to_be_attached()

    def test_positive_report_section_headers(self, details):
        expected = {
            "PEP ROLE DETAILS": ("Role", "Role Bio", "Status", "Role Term"),
            "Further Information": ("Title", "Description", "Source Link"),
            "Linked Individuals": ("Name", "Connection", "Type", "Category"),
            "Education": ("University", "Term"),
            "Linked Companies": ("Name", "Connection", "Type", "Category"),
            "Sources": ("Date", "Link"),
        }
        for section, columns in expected.items():
            table = details.section_table(section)
            for column in columns:
                expect(table.get_by_role("columnheader", name=column, exact=True)).to_be_attached()

    def test_positive_empty_sections_have_placeholder(self, details):
        # Some profiles have populated sections; only assert the placeholder
        # when the section is actually empty.
        for section in ("PEP ROLE DETAILS", "Further Information", "Education", "Linked Companies"):
            table = details.section_table(section)
            if table.locator("tbody .no-data").count():
                expect(table.get_by_text("Details are not available")).to_be_visible()

    def test_positive_source_links_are_valid_urls(self, details):
        for index in range(details.sources().count()):
            link = details.sources().nth(index)
            href = link.get_attribute("href")
            assert href and href.startswith(("https://", "http://"))
            expect(link).to_have_attribute("target", "_blank")

    def test_positive_match_position(self, details):
        current, total = details.position()
        assert 1 <= current <= total

    def test_positive_first_match_previous_disabled(self, details):
        current, _ = details.position()
        if current != 1:
            pytest.skip("Opened match is not first")
        expect(details.previous).to_be_disabled()

    def test_positive_next_previous_navigation(self, details):
        current, total = details.position()
        if total < 2:
            pytest.skip("Only one match")
        original = details.profile_id()
        details.next.click()
        expect(details.report).to_be_visible()
        assert details.position()[0] == current + 1
        details.previous.click()
        assert details.position()[0] == current
        assert details.profile_id() == original

    def test_positive_resolution_options(self, details):
        dropdown = details.options()
        for option in details.RESOLUTIONS:
            expect(dropdown.locator(".ant-select-item-option").filter(has_text=re.compile(rf"^{re.escape(option)}$"))).to_be_visible()

    @pytest.mark.parametrize("resolution", ScreeningMatchDetailsPage.RESOLUTIONS)
    def test_positive_resolution_selectable_without_save(self, details, resolution):
        details.choose_resolution(resolution)
        # Deliberately do not click Update: this is not a disposable match.

    def test_positive_update_and_pdf_controls(self, details):
        expect(details.update).to_be_visible()
        expect(details.download_pdf()).to_be_visible()

    def test_positive_back_to_matches(self, details):
        details.back.click()
        expect(details.page.get_by_text(re.compile(r"Showing\s+\d+\s+matches\s+for", re.I))).to_be_visible(timeout=30000)

    @pytest.mark.skip(reason="Resolution write requires a verified test-owned hit; do not alter WorldCheck classifications on real profiles")
    def test_positive_resolution_update_persists_on_disposable_hit(self, details):
        details.choose_resolution("Possible Hits")
        details.update.click()
        # After a disposable matched record is provided, verify persisted
        # classification and updated counts by reopening that exact profile.
