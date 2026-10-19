from playwright.sync_api import Page, expect


class ProfilesPage:
    def __init__(self, page: Page):
        self.page = page

        # Profiles heading
        self.profiles_heading = page.get_by_role(
            "heading", name="Profiles", level=1, exact=True
        )

        # Profiles description
        self.profiles_description = page.get_by_text(
            "View and manage profiles of existing clients.",
            exact=True
        )

        # Search field
        self.search_input = self.page.get_by_placeholder(
            "Search by client ID or name",
            exact=True
        )

        # Cancel / clear button
        self.clear_search_button = self.page.locator(
            "button.clear-btn"
        )

        # Calendar date fields
        self.start_date_input = self.page.get_by_placeholder(
            "Start Date", exact=True
        )

        self.end_date_input = self.page.get_by_placeholder(
            "End Date", exact=True
        )

        # Calendar popup
        self.calendar_popup = self.page.locator(
            ".ant-picker-dropdown"
        )

        # Calendar date cells
        self.calendar_date_cells = self.page.locator(
            ".ant-picker-cell-in-view"
        )

        # Calendar navigation buttons
        self.calendar_previous_month = self.page.locator(
            ".ant-picker-header-prev-btn"
        )

        self.calendar_next_month = self.page.locator(
            ".ant-picker-header-next-btn"
        )

        # Extract button
        self.extract_button = self.page.get_by_role(
            "button", name="Extract", exact=True
        )

        # Profile file tabs
        self.my_files_tab = self.page.get_by_text(
            "My Files", exact=True
        )

        self.all_files_tab = self.page.get_by_text(
            "All Files", exact=True
        )

        # Profiles table
        self.profiles_table = self.page.locator(
            ".ant-table"
        )

        # Table headers
        self.client_id_header = self.page.get_by_role(
            "columnheader", name="Client ID", exact=True
        )

        self.name_header = self.page.get_by_role(
            "columnheader", name="Name", exact=True
        )

        self.type_header = self.page.get_by_role(
            "columnheader", name="Type", exact=True
        )

        self.status_header = self.page.get_by_role(
            "columnheader", name="Status", exact=True
        )

        self.onboarded_date_header = self.page.get_by_role(
            "columnheader", name="Onboarded Date", exact=True
        )

        self.risk_rating_header = self.page.get_by_role(
            "columnheader", name="Risk Rating", exact=True
        )

        self.onboarded_by_header = self.page.get_by_role(
            "columnheader", name="Onboarded By", exact=True
        )

        # Profiles table
        self.profiles_table = self.page.locator(".ant-table")

        self.profiles_table_rows = self.profiles_table.locator(
            "tbody.ant-table-tbody tr.ant-table-row"
        )

        # First Client ID link
        self.first_client_id_link = self.profiles_table_rows.first.locator(
            "td"
        ).first.locator("a.table-link")

        # First row's Client ID
        self.first_client_id = self.first_client_id_link.inner_text

        # Download button in the first row
        self.first_row_download_button = self.profiles_table_rows.first.locator(
            "button.action-btn"
        )

        # Download icon
        self.first_row_download_icon = self.first_row_download_button.locator(
            "i.fa-arrow-to-bottom"
        )





    # Verify the Profiles heading
    def check_profiles_heading(self):
        expect(self.profiles_heading).to_be_visible()

    # Verify the description
    def check_profiles_description(self):
        expect(self.profiles_description).to_be_visible()

    # Verify both elements
    def check_profiles_page_header(self):
        self.check_profiles_heading()
        self.check_profiles_description()

    def check_search_field(self):
        expect(self.search_input).to_be_visible()
        expect(self.search_input).to_be_enabled()

    def check_clear_search_button(self):
        expect(self.clear_search_button).to_be_visible()

    def check_search_button(self):
        expect(self.search_button).to_be_visible()
        expect(self.search_button).to_be_enabled()

    def check_clear_search_functionality(self):
        self.search_input.fill("hj")
        expect(self.search_input).to_have_value("hj")

        self.clear_search_button.click()

        expect(self.search_input).to_have_value("")

    def check_calendar_fields_visible(self):
        expect(self.start_date_input).to_be_visible()
        expect(self.end_date_input).to_be_visible()

    def check_extract_button_visible(self):
        expect(self.extract_button).to_be_visible()
        expect(self.extract_button).to_be_enabled()

    def open_start_date_calendar(self):
        self.start_date_input.click()
        expect(self.calendar_popup).to_be_visible()

    def select_start_date(self, day: str):
        self.start_date_input.click()

        self.calendar_popup.get_by_role(
            "cell", name=day, exact=True
        ).click()

    def select_end_date(self, day: str):
        self.end_date_input.click()

        self.calendar_popup.get_by_role(
            "cell", name=day, exact=True
        ).click()

    def check_file_tabs_visible(self):
        expect(self.my_files_tab).to_be_visible()
        expect(self.all_files_tab).to_be_visible()

    def check_profiles_table_visible(self):
        expect(self.profiles_table).to_be_visible()

    def check_profiles_table_headers(self):
        expect(self.client_id_header).to_be_visible()
        expect(self.name_header).to_be_visible()
        expect(self.type_header).to_be_visible()
        expect(self.status_header).to_be_visible()
        expect(self.onboarded_date_header).to_be_visible()
        expect(self.risk_rating_header).to_be_visible()
        expect(self.onboarded_by_header).to_be_visible()

    def click_my_files_tab(self):
        self.my_files_tab.click()

    def click_all_files_tab(self):
        self.all_files_tab.click()

    def check_profiles_table_displayed(self):
        expect(self.profiles_table).to_be_visible()
        expect(self.profiles_table_rows.first).to_be_visible()

    def check_first_client_id_link(self):
        expect(self.first_client_id_link).to_be_visible()
        expect(self.first_client_id_link).to_have_attribute(
            "href",
            re.compile(
                r"^/nolimit/app/profiles/entity/process\?"
            )
        )

    def click_first_client_id_link(self):
        self.first_client_id_link.click()

    def check_first_client_id_redirection(self):
        expect(self.page).to_have_url(
            re.compile(
                r"/nolimit/app/profiles/entity/process\?"
            )
        )

    def check_first_row_download_button(self):
        expect(self.first_row_download_button).to_be_visible()
        expect(self.first_row_download_icon).to_be_visible()

    def download_first_row_pdf(self, download_folder):
        client_id = self.first_client_id_link.inner_text().strip()

        with self.page.expect_download() as download_info:
            self.first_row_download_button.click()

        download = download_info.value

        expect_filename = download.suggested_filename

        assert expect_filename.lower().endswith(".pdf"), (
            f"Expected a PDF file, but got: {expect_filename}"
        )

        assert client_id.lower() in expect_filename.lower(), (
            f"Expected the downloaded filename '{expect_filename}' "
            f"to contain Client ID '{client_id}'"
        )

        save_path = download_folder / expect_filename
        download.save_as(str(save_path))

        assert save_path.exists(), (
            f"Downloaded file was not saved: {save_path}"
        )

        return save_path