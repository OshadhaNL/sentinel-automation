import re
import pytest
from pathlib import Path
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.profilesPage import ProfilesPage

@pytest.mark.ui
@pytest.mark.smoke
class TestProfiles:

    @pytest.fixture(autouse=True)
    def setup_profiles(
        self,
        page: Page,
        base_url: str,
    ):
        self.page = page

        # Login
        self.login_page = LoginPage(page)
        self.login_page.open(base_url)

        self.login_page.enter_email("Oshadha@northlark.com")
        self.login_page.enter_password("5e11Piwu")
        self.login_page.click_login()

        # Verify successful login and landing on Home
        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/home/?$")
        )

        # Navigate to Profiles from the sidebar
        profiles_sidebar = page.get_by_role(
            "link", name="Profiles", exact=False
        )

        expect(profiles_sidebar).to_be_visible()
        profiles_sidebar.click()

        # Verify navigation to Profiles
        expect(page).to_have_url(
            re.compile(r".*/nolimit/app/profiles/?$")
        )

        self.profiles = ProfilesPage(page)

    def test_profiles_heading_is_displayed(self):
        self.profiles.check_profiles_heading()

    def test_profiles_description_is_displayed(self):
        self.profiles.check_profiles_description()

    def test_profiles_search_field_is_displayed(self):
        self.profiles.check_search_field()

    def test_profiles_clear_search_functionality(self):
        self.profiles.check_clear_search_functionality()

    def test_profiles_calendar_fields_are_displayed(self):
        self.profiles.check_calendar_fields_visible()

    def test_profiles_extract_button_is_displayed(self):
        self.profiles.check_extract_button_visible()

    def test_profiles_file_tabs_are_displayed(self):
        self.profiles.check_file_tabs_visible()

    def test_my_files_tab(self):
        self.profiles.click_my_files_tab()
        self.profiles.check_profiles_table_visible()
        self.profiles.check_profiles_table_headers()

    def test_all_files_tab(self):
        self.profiles.click_all_files_tab()
        self.profiles.check_profiles_table_visible()
        self.profiles.check_profiles_table_headers()

    def test_profiles_table_headers_are_displayed(self):
        self.profiles.check_profiles_table_visible()
        self.profiles.check_profiles_table_headers()

    def test_profiles_table_contains_rows(self):
        self.profiles.check_profiles_table_displayed()

    def test_first_client_id_link_is_displayed_with_expected_url(self):
        self.profiles.check_first_client_id_link()

    def test_first_client_id_link_redirects_to_entity_page(self):
        expected_href = self.profiles.first_client_id_link.get_attribute(
            "href"
        )
        assert expected_href, "The first Client ID link has no href."

        self.profiles.click_first_client_id_link()

        expect(self.page).to_have_url(
            re.compile(re.escape(expected_href))
        )

    def test_first_row_downloads_pdf(self, tmp_path: Path):
        self.profiles.check_profiles_table_displayed()
        self.profiles.check_first_row_download_button()

        saved_file = self.profiles.download_first_row_pdf(tmp_path)

        assert saved_file.exists()
        assert saved_file.suffix.lower() == ".pdf"
