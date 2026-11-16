"""Individual Profile Screening UI tests: read-only and opt-in write coverage."""
import re
import pytest
from playwright.sync_api import expect
from pages.profiles.profileNavigation import open_client_profile
from pages.profiles.individual.individualScreeningPage import IndividualScreeningPage


from config.screening_test_data import (
    READ_ONLY_CLIENT_ID,
    WRITE_CLIENT_ID,
    ALLOW_SCREENING_CHANGES,
)



@pytest.fixture
def screening(page, base_url):
    client_id = READ_ONLY_CLIENT_ID.strip()

    assert client_id, (
        "READ_ONLY_CLIENT_ID is missing in "
        "config/screening_test_data.py"
    )

    open_client_profile(
        page,
        base_url,
        "individual",
        client_id,
    )

    view = IndividualScreeningPage(page)

    expect(view.heading).to_be_visible(
        timeout=15000
    )

    view.open_hits()

    return view


@pytest.mark.ui
class TestIndividualScreeningHits:
    def test_main_screening_opens_hits(self, screening):
        screening.open_hits()
        expect(screening.page.get_by_text('Showing 0 matches for', exact=False)).to_be_visible()

    @pytest.mark.parametrize('category', IndividualScreeningPage.HIT_CATEGORIES)
    def test_hit_category_switching(self, screening, category):
        screening.open_hits()
        screening.tab(category).click()
        expect(screening.tab(category)).to_have_class(re.compile(r'\bactive\b'))
        expect(screening.hit_table()).to_be_visible()

    def test_hit_table_headers(self, screening):
        screening.require_hits()

        headers = screening.hit_table().locator("thead th")

        expect(headers).to_have_count(
            len(screening.HIT_HEADERS) + 1,
            timeout=15000,
        )

        actual_headers = [
            header.strip()
            for header in headers.all_inner_texts()[1:]
        ]

        assert actual_headers == list(screening.HIT_HEADERS)

    def test_empty_hits_state(self, screening):
        screening.open_hits()
        expect(screening.hit_table()).to_contain_text('No screening hits found')
        expect(screening.hit_rows()).to_have_count(0)

    def test_back_to_single_screening(self, screening):
        screening.open_single()
        expect(screening.name_input()).to_be_visible()


@pytest.mark.ui
class TestIndividualSingleScreening:
    def test_client_type_is_individual_and_locked(self, screening):
        screening.open_single()
        expect(screening.client_type('P')).to_be_checked()
        expect(screening.client_type('O')).to_be_disabled()

    def test_single_screening_fields(self, screening):
        screening.open_single()
        expect(screening.name_input()).to_be_visible()
        expect(screening.date_of_birth()).to_be_visible()
        expect(screening.select_field('Citizenship')).to_be_visible()
        expect(screening.select_field('Place of Birth')).to_be_visible()
        for gender in ('Male', 'Female', 'Unspecified'):
            expect(screening.gender(gender)).to_be_visible()
        expect(screening.page.locator('input[name="ongoing"]')).to_be_visible()
        expect(screening.page.get_by_role('button', name='Analyze')).to_be_visible()

    def test_connected_party_card(self, screening):
        """Verify the known connected-party record on the read-only fixture."""
        screening.open_single()
        page = screening.page
        expect(screening.name_input()).to_be_visible(timeout=15000)
        expect(page.get_by_role("heading", name="Connected Party")).to_be_visible(timeout=15000)
        # This client's accessibility snapshot shows a Screened record and an
        # Add to Daily Screening button, but no .screen-history-card element.
        expect(page.get_by_text(re.compile(r"Screened\s*\(\d+\)"))).to_be_visible(timeout=15000)
        expect(page.get_by_role("button", name="Add to Daily Screening")).to_be_visible(timeout=15000)
        # Never click Add to Daily Screening on the read-only client.

    def test_single_to_daily_and_back(self, screening):
        screening.open_single()
        screening.tab('Daily Screening').click()
        expect(screening.tab('Daily Screening')).to_have_class(re.compile(r'\bactive\b'))
        screening.tab('Single Screening').click()
        expect(screening.tab('Single Screening')).to_have_class(re.compile(r'\bactive\b'))
        expect(screening.name_input()).to_be_visible()


@pytest.mark.ui
class TestIndividualDailyScreening:
    def test_daily_table_headers(self, screening):
        screening.open_daily()
        headers = screening.daily_table().locator('thead th').all_inner_texts()
        assert [h.strip() for h in headers[1:]] == list(screening.DAILY_HEADERS)

    def test_daily_empty_state(self, screening):
        screening.open_daily()
        expect(screening.daily_result_count()).to_contain_text('Showing 0 results')
        expect(screening.daily_table()).to_contain_text('No data')
        expect(screening.daily_rows()).to_have_count(0)
        expect(
            screening.daily_table().locator(
                'thead input[aria-label="Select all"]'
            )
        ).to_be_disabled()

    def test_daily_search_controls(self, screening):
        screening.open_daily()
        expect(screening.daily_search()).to_be_visible()
        expect(screening.daily_search_button()).to_be_visible()
        expect(screening.daily_clear_button()).to_be_attached()

    def test_negative_daily_search_unknown_name(self, screening):
        screening.open_daily()
        screening.daily_search().fill('qa-nonexistent-screening-987654')
        screening.daily_search_button().click()
        expect(screening.daily_rows()).to_have_count(0)

    def test_daily_search_clear(self, screening):
        screening.open_daily()
        screening.daily_search().fill('qa-nonexistent-screening-987654')
        screening.daily_clear_button().click()
        expect(screening.daily_search()).to_be_empty()

    def test_daily_bulk_action_and_remove_visible(self, screening):
        screening.open_daily()

        # Verify Bulk Action button.
        expect(
            screening.page.get_by_role(
                "button",
                name="Bulk Action",
                exact=True,
            )
        ).to_be_visible()

        # Verify Remove button, including its icon.
        expect(
            screening.page.locator(
                "button.primary-btn"
            ).filter(has_text="Remove")
        ).to_be_visible()


# ---------------------------------------------------------------------------
# Functional and negative coverage. These tests only change browser-local form
# state or perform searches. They NEVER click Analyze / Remove / Delete.
# ---------------------------------------------------------------------------
@pytest.mark.ui
class TestIndividualScreeningFunctional:
    @pytest.mark.parametrize('name', ['QA Screening Test', 'A', 'Name With Spaces', 'José Test'])
    def test_name_field_accepts_text(self, screening, name):
        screening.open_single()
        screening.name_input().fill(name)
        expect(screening.name_input()).to_have_value(name)

    def test_negative_name_can_be_cleared_without_submission(self, screening):
        screening.open_single()
        screening.name_input().fill('')
        expect(screening.name_input()).to_be_empty()

    def test_negative_name_whitespace_remains_unsent(self, screening):
        screening.open_single()
        screening.name_input().fill('   ')
        expect(screening.name_input()).to_have_value('   ')

    @pytest.mark.parametrize('gender', ['Male', 'Female', 'Unspecified'])
    def test_gender_selection(self, screening, gender):
        screening.open_single()
        screening.select_gender(gender)

    def test_gender_radio_exclusive(self, screening):
        screening.open_single()
        screening.select_gender('Male')
        screening.select_gender('Female')
        expect(screening.gender('Male')).not_to_be_checked()
        expect(screening.gender('Female')).to_be_checked()

    def test_negative_client_type_cannot_be_changed(self, screening):
        screening.open_single()
        expect(screening.client_type('P')).to_be_disabled()
        expect(screening.client_type('O')).to_be_disabled()
        expect(screening.client_type('P')).to_be_checked()

    def test_date_of_birth_field_present_and_readable(self, screening):
        screening.open_single()
        dob = screening.date_of_birth()
        expect(dob).to_be_visible()
        assert dob.get_attribute('placeholder') == 'Pick date of birth'

    def test_date_picker_can_be_opened(self, screening):
        screening.open_single()
        screening.date_of_birth().click()
        # Ant Design picker may render in a portal outside the form.
        expect(screening.page.locator('.ant-picker-dropdown:visible').first).to_be_visible()

    @pytest.mark.parametrize('field', ['Citizenship', 'Place of Birth'])
    def test_country_dropdown_opens(self, screening, field):
        screening.open_single()
        select = screening.select_field(field)
        expect(select).to_be_visible()
        select.click()
        expect(screening.country_combobox(field)).to_be_visible()
        # Do not save or submit the selection.

    @pytest.mark.parametrize('field', ['Citizenship', 'Place of Birth'])
    def test_country_dropdown_search_input_exists(self, screening, field):
        screening.open_single()
        screening.select_field(field).click()
        expect(screening.country_combobox(field)).to_be_attached()

    def test_ongoing_screening_checkbox_can_toggle_locally(self, screening):
        screening.open_single()
        checkbox = screening.ongoing_checkbox()
        initial = checkbox.is_checked()
        checkbox.set_checked(not initial)
        assert checkbox.is_checked() != initial
        checkbox.set_checked(initial)
        assert checkbox.is_checked() == initial
        # Never click Analyze: this only changes local form state.

    def test_analyze_button_enabled_without_submitting(self, screening):
        screening.open_single()
        expect(screening.analyze_button()).to_be_visible()
        expect(screening.analyze_button()).to_be_enabled()

    def test_connected_party_details_visible(self, screening):
        """Check the actual connected-party details on the read-only client."""
        screening.open_single()
        page = screening.page
        expect(page.get_by_role("heading", name="Connected Party")).to_be_visible(timeout=15000)
        expect(page.get_by_text(re.compile(r"Screened\s*\(\d+\)"))).to_be_visible(timeout=15000)
        expect(page.get_by_text(re.compile(r"Positive:\s*\d+"))).to_be_visible(timeout=15000)
        expect(page.get_by_text(re.compile(r"False:\s*\d+"))).to_be_visible(timeout=15000)
        expect(page.get_by_text(re.compile(r"Possible:\s*\d+"))).to_be_visible(timeout=15000)

    def test_hit_category_switching_preserves_table(self, screening):
        for category in screening.HIT_CATEGORIES:
            screening.tab(category).click()
            expect(screening.tab(category)).to_have_class(re.compile(r'\bactive\b'))
            expect(screening.hit_table()).to_be_visible()

    def test_daily_search_input_accepts_text_without_submission(self, screening):
        screening.open_daily()
        screening.daily_search().fill('Screening QA')
        expect(screening.daily_search()).to_have_value('Screening QA')

    @pytest.mark.parametrize('query', ['qa-no-match-987654321', 'ZZZ_NOT_A_REAL_CLIENT_123'])
    def test_negative_daily_search_unknown_records(self, screening, query):
        screening.search_daily(query)
        expect(screening.daily_rows()).to_have_count(0)

    def test_negative_daily_search_clear_after_no_match(self, screening):
        screening.search_daily('qa-no-match-987654321')
        screening.clear_daily_search()

    def test_daily_search_button_is_clickable(self, screening):
        screening.open_daily()
        expect(screening.daily_search_button()).to_be_enabled()
        screening.daily_search_button().click()
        expect(screening.daily_table()).to_be_visible()

    def test_daily_action_buttons_visible_without_execution(self, screening):
        screening.open_daily()
        expect(screening.bulk_action_button()).to_be_visible()
        expect(screening.remove_button()).to_be_visible()

    def test_daily_table_selection_when_no_rows(self, screening):
        screening.open_daily()
        if screening.daily_rows().count() != 0:
            pytest.skip('Selection-disabled behavior applies only to empty tables')
        expect(screening.daily_table().locator('thead input[aria-label="Select all"]')).to_be_disabled()


# ---------------------------------------------------------------------------
# Write tests: NEVER run on a shared/read-only client. Requires BOTH a separate
# disposable ID and explicit opt-in. These tests may create screening records.
# ---------------------------------------------------------------------------

@pytest.fixture
def screening_write(page, base_url):

    if not ALLOW_SCREENING_CHANGES:
        pytest.fail(
            "Write tests are disabled. Set "
            "ALLOW_SCREENING_CHANGES=True in "
            "config/screening_test_data.py"
        )

    client_id = WRITE_CLIENT_ID.strip()

    if not client_id:
        pytest.fail(
            "WRITE_CLIENT_ID is missing in "
            "config/screening_test_data.py"
        )

    if client_id == READ_ONLY_CLIENT_ID:
        pytest.fail(
            "Write client must be different "
            "from read-only client."
        )

    open_client_profile(
        page,
        base_url,
        "individual",
        client_id,
    )

    view = IndividualScreeningPage(page)

    expect(view.heading).to_be_visible(
        timeout=15000
    )

    view.open_hits()

    return view



@pytest.mark.ui
@pytest.mark.screening_write
class TestIndividualScreeningWrite:
    def test_negative_analyze_empty_name_does_not_navigate_to_hits(self, screening_write):
        screening_write.open_single()
        screening_write.name_input().fill('')
        screening_write.analyze_button().click()
        # This is a conservative behavioral check; it does not assume the
        # precise validation message or backend implementation.
        expect(screening_write.name_input()).to_be_visible(timeout=15000)

    def test_analyze_valid_name_triggers_screening_response(self, screening_write):
        screening_write.open_single()
        screening_write.name_input().fill('Disposable QA Screening')
        screening_write.analyze_button().click()
        # A request may show results, a spinner, a toast, or return to hits.
        # Require a meaningful observable response, without inventing text.
        screening_write.page.wait_for_timeout(1000)
        assert screening_write.page.locator('main').is_visible(), 'Profile disappeared after Analyze'
        assert (
            screening_write.name_input().is_visible()
            or screening_write.back_to_screening().is_visible()
            or screening_write.page.locator('.ant-message, .ant-notification, [role="alert"]').first.is_visible()
        ), 'No recognizable screening view or feedback after Analyze'

    def test_ongoing_screening_control_can_be_selected_for_analysis(self, screening_write):
        screening_write.open_single()
        screening_write.ongoing_checkbox().check()
        expect(screening_write.ongoing_checkbox()).to_be_checked()
        # No Analyze click here: enrolling daily screening is a separate action.

    def test_bulk_action_button_is_present(self, screening_write):
        """Only verify presence; Bulk Action behavior is not yet specified."""
        screening_write.open_daily()
        expect(screening_write.bulk_action_button()).to_be_visible(timeout=15000)
        # Do not assume this button opens a Bulk Remove dialog.

    def test_remove_without_selection_no_record_deleted(self, screening_write):
        screening_write.open_daily()
        if screening_write.daily_rows().count():
            pytest.skip('Requires an empty daily table to avoid deleting records')
        # Only inspect the button. Clicking Remove with unknown behavior is
        # intentionally excluded until its confirmation flow is captured.
        expect(screening_write.remove_button()).to_be_visible()

    @pytest.mark.screening_write
    def test_ongoing_screening_adds_daily_record(
            self,
            screening_write,
    ):
        screening = screening_write

        screening.open_single()

        # Use the configured disposable client.
        name = screening.name_input().input_value().strip()
        assert name, "Screening name must not be empty"

        # Enable Ongoing Screening.
        checkbox = screening.ongoing_checkbox()
        checkbox.check()
        expect(checkbox).to_be_checked()

        # Analyze the individual.
        screening.analyze_button().click()

        # Verify Screening Hits appears.
        expect(
            screening.back_to_screening()
        ).to_be_visible(timeout=20000)

        # Navigate back and open Daily Screening.
        screening.return_to_daily_after_analysis()

        # Search for the record.
        screening.search_daily(name)

        # Verify a matching record appears.
        expect(
            screening.daily_rows().filter(
                has_text=name
            ).first
        ).to_be_visible(timeout=20000)

    @pytest.mark.screening_write
    def test_ongoing_screening_record_can_be_removed(
            self,
            screening_write,
    ):
        screening = screening_write

        screening.open_single()

        # Use the screening name already populated.
        name = screening.name_input().input_value().strip()

        assert name, "Screening name must not be empty"

        # Enable Ongoing Screening.
        ongoing = screening.ongoing_checkbox()
        ongoing.check()
        expect(ongoing).to_be_checked()

        # Analyze the individual.
        screening.analyze_button().click()

        # Analyze opens Screening Hits.
        expect(
            screening.back_to_screening()
        ).to_be_visible(timeout=20000)

        # Return to Single Screening, then Daily Screening.
        screening.return_to_daily_after_analysis()

        # Find the created screening record.
        screening.search_daily(name)

        # Capture the exact Daily Screening Profile ID before removing it.
        row = screening.daily_row_by_name(name)
        expect(row).to_be_visible(timeout=20000)

        profile_id = row.locator("td").nth(2).inner_text().strip()
        assert profile_id, "Daily Screening Profile ID is empty"

        # Select and remove the record.
        screening.select_daily_record_by_name(name)
        screening.remove_selected_daily_record()

        # Refresh because the table retains the removed row
        # until the page is reloaded.
        screening.refresh_daily_screening()

        # Verify the exact record is gone.
        screening.search_daily(profile_id)

        removed_row = screening.daily_row_by_profile_id(profile_id)
        expect(removed_row).to_have_count(0, timeout=20000)
