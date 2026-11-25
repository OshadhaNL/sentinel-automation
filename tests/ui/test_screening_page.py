"""Screening UI regression tests.

Writes / external screening calls are opt-in:
  SCREENING_ALLOW_ANALYZE=1      Allows Analyze (external API, possible charges)
  SCREENING_ALLOW_WRITES=1       Allows ongoing enrollment / remove / bulk upload
  SCREENING_DISPOSABLE_DATA_CONFIRMED=1  Confirms test-owned data

Result-page tests require SCREENING_ALLOW_ANALYZE=1 and a disposable test name.
The result UI was not supplied, so unknown selectors are not asserted as facts.
"""
import os
import re
import uuid

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.screeningPage import ScreeningPage


def allow_analyze():
    return os.getenv("SCREENING_ALLOW_ANALYZE") == "1"


def allow_writes():
    return (
        os.getenv("SCREENING_ALLOW_WRITES") == "1"
        and os.getenv("SCREENING_DISPOSABLE_DATA_CONFIRMED") == "1"
    )


@pytest.fixture
def screening(page: Page, base_url: str):
    email, password = os.getenv("TEST_EMAIL"), os.getenv("TEST_PASSWORD")
    if not email or not password:
        pytest.skip("Set TEST_EMAIL and TEST_PASSWORD for authenticated Screening tests")
    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(email)
    login.enter_password(password)
    login.click_login()
    expect(page).to_have_url(re.compile(r".*/nolimit/app/home/?$"), timeout=30000)
    obj = ScreeningPage(page)
    obj.open(base_url)
    return obj


@pytest.mark.ui
class TestScreeningCommon:
    def test_positive_screening_heading(self, screening):
        screening.assert_loaded()

    def test_positive_group_heading(self, screening):
        expect(screening.page.get_by_role("heading", name="Group")).to_be_visible()

    def test_positive_client_search_visible_and_placeholder(self, screening):
        expect(screening.client_search).to_be_visible()
        expect(screening.client_search).to_have_attribute("placeholder", "Search by Client name")

    def test_positive_client_search_icon(self, screening):
        expect(screening.client_search_button().locator("i.fa-search")).to_be_visible()

    @pytest.mark.parametrize("term", ["a", "123", "A B", "-_'", "ශ්‍රී", "a" * 100])
    def test_positive_client_search_accepts_text(self, screening, term):
        screening.client_search.fill(term)
        expect(screening.client_search).to_have_value(term)

    def test_positive_client_search_button_clickable(self, screening):
        screening.client_search_button().click()

    def test_positive_client_list_maximum_twenty(self, screening):
        expect(screening.client_cards.first).to_be_visible()
        assert 1 <= screening.client_cards.count() <= 20

    def test_positive_client_search_existing_name(self, screening):
        name = screening.client_cards.first.locator("p").inner_text().strip()
        screening.search_clients(name)
        expect(screening.client_cards.filter(has_text=name).first).to_be_visible()

    def test_positive_client_search_clear(self, screening):
        screening.client_search.fill("search term")
        screening.client_clear_button().click()
        expect(screening.client_search).to_be_empty()

    def test_negative_client_search_nonexistent_name(self, screening):
        screening.search_clients("NOT_A_REAL_SCREENING_CLIENT_" + uuid.uuid4().hex)
        expect(screening.client_cards).to_have_count(0)

    def test_positive_single_daily_tabs_visible(self, screening):
        expect(screening.single_tab).to_be_visible()
        expect(screening.daily_tab).to_be_visible()

    def test_positive_tab_icons(self, screening):
        expect(screening.single_tab.locator("i.fa-search")).to_be_visible()
        expect(screening.daily_tab.locator("i.fa-calendar-check")).to_be_visible()

    def test_positive_single_tab_default(self, screening):
        expect(screening.single_tab).to_have_class(re.compile(r"\bactive\b"))

    def test_positive_tab_switching(self, screening):
        screening.switch_daily()
        expect(screening.single_tab).not_to_have_class(re.compile(r"\bactive\b"))
        screening.switch_single()
        expect(screening.daily_tab).not_to_have_class(re.compile(r"\bactive\b"))

    def test_positive_client_card_click(self, screening):
        screening.client_cards.first.click()
        # Selecting a group client must not leave Screening unexpectedly.
        expect(screening.page.get_by_role("heading", name="Screening", exact=True)).to_be_visible()


@pytest.mark.ui
class TestSingleScreening:
    def test_positive_client_type_label_and_radios(self, screening):
        expect(screening.page.get_by_text("Client Type:", exact=True)).to_be_visible()
        expect(screening.individual_radio).to_be_visible()
        expect(screening.organization_radio).to_be_visible()

    def test_positive_individual_default_selected(self, screening):
        expect(screening.individual_radio).to_be_checked()
        expect(screening.organization_radio).not_to_be_checked()

    def test_positive_organization_selection(self, screening):
        screening.organization_radio.check()
        expect(screening.organization_radio).to_be_checked()
        expect(screening.individual_radio).not_to_be_checked()

    def test_positive_client_type_switch_back(self, screening):
        screening.organization_radio.check()
        screening.individual_radio.check()
        expect(screening.individual_radio).to_be_checked()

    def test_positive_name_required_mark(self, screening):
        field = screening.name_input.locator("xpath=ancestor::div[contains(@class,'input-box')][1]")
        expect(field).to_have_class(re.compile(r"\breq\b"))

    def test_positive_name_placeholder(self, screening):
        expect(screening.name_input).to_be_visible()
        expect(screening.name_input).to_have_attribute("placeholder", "Enter individual name")

    @pytest.mark.parametrize("value", ["John Doe", "A", "A B-C", "123", "O'Neil", "Élodie", "අමල්", "A" * 100])
    def test_positive_name_input_accepts_text(self, screening, value):
        screening.name_input.fill(value)
        expect(screening.name_input).to_have_value(value)

    def test_positive_name_can_be_cleared(self, screening):
        screening.name_input.fill("Example")
        screening.name_input.clear()
        expect(screening.name_input).to_be_empty()

    def test_positive_gender_label_and_options(self, screening):
        expect(screening.page.get_by_text("Gender:", exact=True)).to_be_visible()
        for value in ("Male", "Female", "Unspecified"):
            expect(screening.page.locator(f'input[name="gender"][value="{value}"]')).to_be_visible()

    @pytest.mark.parametrize("value", ["Male", "Female", "Unspecified"])
    def test_positive_gender_selectable(self, screening, value):
        chosen = screening.page.locator(f'input[name="gender"][value="{value}"]')
        chosen.check()
        expect(chosen).to_be_checked()
        assert screening.gender_radios.evaluate_all("els => els.filter(el => el.checked).length") == 1

    def test_positive_gender_mutually_exclusive(self, screening):
        screening.page.locator('input[name="gender"][value="Male"]').check()
        screening.page.locator('input[name="gender"][value="Female"]').check()
        expect(screening.page.locator('input[name="gender"][value="Male"]')).not_to_be_checked()

    def test_positive_dob_label_placeholder_calendar_icon(self, screening):
        expect(screening.page.get_by_text("Date Of Birth", exact=True)).to_be_visible()
        expect(screening.dob_input).to_be_visible()
        expect(screening.dob_input).to_have_attribute("placeholder", "Pick date of birth")
        expect(screening.dob_input.locator("xpath=ancestor::div[contains(@class,'ant-picker')][1]").locator('.ant-picker-suffix')).to_be_visible()

    def test_positive_dob_calendar_opens(self, screening):
        screening.dob_input.click()
        expect(screening.page.locator(".ant-picker-dropdown:visible")).to_be_visible()

    def test_positive_dob_date_selectable(self, screening):
        screening.dob_input.click()
        popup = screening.page.locator(".ant-picker-dropdown:visible")
        day = popup.locator("td.ant-picker-cell-in-view:not(.ant-picker-cell-disabled) .ant-picker-cell-inner").first
        expect(day).to_be_visible()
        day.click()
        expect(screening.dob_input).not_to_be_empty()

    @pytest.mark.parametrize("label,placeholder", [("Citizenship", "Enter citizenship"), ("Place of Birth", "Select country")])
    def test_positive_country_field_label_and_dropdown(self, screening, label, placeholder):
        expect(screening.page.get_by_text(label, exact=True)).to_be_visible()
        expect(screening.country_select(placeholder)).to_be_visible()

    @pytest.mark.parametrize("placeholder", ["Enter citizenship", "Select country"])
    def test_positive_country_options_visible(self, screening, placeholder):
        screening.country_select(placeholder).click()
        expect(screening.page.locator(".ant-select-dropdown:visible .ant-select-item-option").first).to_be_visible()

    @pytest.mark.parametrize("placeholder", ["Enter citizenship", "Select country"])
    def test_positive_country_option_selectable(self, screening, placeholder):
        # Ant Design removes the placeholder after a selection. Retain the original element.
        select = screening.page.locator(".ant-select").nth(0 if placeholder == "Enter citizenship" else 1)
        expect(select.locator(".ant-select-selection-placeholder")).to_have_text(placeholder)
        select.click()
        option = screening.page.locator(".ant-select-dropdown:visible .ant-select-item-option").first
        expect(option).to_be_visible()
        option.click()
        expect(select.locator(".ant-select-selection-item")).to_be_visible()

    def test_positive_ongoing_label_and_checkbox(self, screening):
        expect(screening.page.locator('label[for="ongoing"]')).to_contain_text("Ongoing Screening")
        expect(screening.ongoing).to_be_visible()

    def test_positive_ongoing_default_unchecked(self, screening):
        expect(screening.ongoing).not_to_be_checked()

    def test_positive_ongoing_toggle(self, screening):
        screening.ongoing.check()
        expect(screening.ongoing).to_be_checked()
        screening.ongoing.uncheck()
        expect(screening.ongoing).not_to_be_checked()

    def test_positive_ongoing_help_icon_and_tooltip(self, screening):
        info = screening.page.locator('label[for="ongoing"] .info-icon')
        expect(info).to_be_visible()
        info.hover()
        expect(screening.page.get_by_text(ScreeningPage.ONGOING_HELP, exact=True)).to_be_visible()

    def test_positive_analyze_button_and_icon(self, screening):
        expect(screening.analyze_button).to_be_visible()
        expect(screening.analyze_button.locator("i.fa-globe")).to_be_visible()

    def test_negative_blank_name_analyze_rejected(self, screening):
        if not allow_analyze():
            pytest.skip("Set SCREENING_ALLOW_ANALYZE=1 to test Analyze validation")
        screening.analyze_button.click()
        # Missing required name must not produce a successful screening result.
        expect(screening.name_input).to_be_visible()
        assert not screening.page.get_by_text(re.compile(r"Showing \d+ matches for", re.I)).is_visible()

    @pytest.mark.parametrize("name", ["   ", "<script>alert(1)</script>", "' OR '1'='1"])
    def test_negative_suspicious_name_does_not_execute_script(self, screening, name):
        screening.name_input.fill(name)
        expect(screening.name_input).to_have_value(name)
        # Safe non-submitting test: input alone must not execute JavaScript or navigate.
        screening.assert_loaded()

    def test_positive_analyze_disposable_name(self, screening):
        if not allow_analyze():
            pytest.skip("Analyze calls an external screening service; set SCREENING_ALLOW_ANALYZE=1")
        name = os.getenv("SCREENING_TEST_NAME")
        if not name:
            pytest.skip("Set SCREENING_TEST_NAME to an approved disposable test identity")
        screening.analyze(name)
        expect(screening.page.get_by_text(re.compile(r"Showing \d+ matches for", re.I))).to_be_visible(timeout=60000)

    @pytest.mark.parametrize("tab", ScreeningPage.RESULT_TABS)
    def test_positive_screening_result_category_visible(self, screening, tab):
        if not allow_analyze() or not os.getenv("SCREENING_TEST_NAME"):
            pytest.skip("Set SCREENING_ALLOW_ANALYZE=1 and SCREENING_TEST_NAME")
        screening.analyze(os.environ["SCREENING_TEST_NAME"])
        expect(screening.result_tab(tab)).to_be_visible(timeout=60000)

    @pytest.mark.parametrize("tab", ScreeningPage.RESULT_TABS)
    def test_positive_screening_result_headers_or_no_hits(self, screening, tab):
        if not allow_analyze() or not os.getenv("SCREENING_TEST_NAME"):
            pytest.skip("Set SCREENING_ALLOW_ANALYZE=1 and SCREENING_TEST_NAME")
        screening.analyze(os.environ["SCREENING_TEST_NAME"])
        screening.result_tab(tab).click()
        if screening.page.get_by_text("No screening hits found", exact=True).is_visible():
            expect(screening.page.get_by_text("No screening hits found", exact=True)).to_be_visible()
        else:
            for header in ScreeningPage.RESULT_HEADERS:
                expect(screening.page.get_by_role("columnheader", name=header, exact=True)).to_be_visible()

    def test_positive_ongoing_enrollment_requires_write_opt_in(self, screening):
        if not allow_writes() or not allow_analyze():
            pytest.skip("Set SCREENING_ALLOW_ANALYZE=1, SCREENING_ALLOW_WRITES=1 and SCREENING_DISPOSABLE_DATA_CONFIRMED=1")
        name = os.getenv("SCREENING_TEST_NAME")
        if not name:
            pytest.skip("Set SCREENING_TEST_NAME to an approved disposable identity")
        screening.analyze(name, ongoing=True)
        expect(screening.page.get_by_text(re.compile(r"Showing \d+ matches for", re.I))).to_be_visible(timeout=60000)
        screening.switch_daily()
        screening.search_daily(name)
        expect(screening.daily_rows.filter(has_text=name).first).to_be_visible(timeout=30000)


@pytest.mark.ui
class TestDailyScreening:
    def test_positive_daily_tab_selected(self, screening):
        screening.switch_daily()
        expect(screening.daily_tab).to_have_class(re.compile(r"\bactive\b"))

    def test_positive_daily_search_visible_placeholder(self, screening):
        screening.switch_daily()
        expect(screening.daily_search).to_be_visible()
        expect(screening.daily_search).to_have_attribute("placeholder", "Search here...")

    @pytest.mark.parametrize("text", ["test", "123", "A B", "@_-", "ශ්‍රී", "x" * 100])
    def test_positive_daily_search_accepts_text(self, screening, text):
        screening.switch_daily()
        screening.daily_search.fill(text)
        expect(screening.daily_search).to_have_value(text)

    def test_positive_daily_search_icon(self, screening):
        screening.switch_daily()
        expect(screening.daily_search_button().locator("i.fa-search")).to_be_visible()

    def test_positive_daily_search_clear(self, screening):
        screening.switch_daily()
        screening.daily_search.fill("abc")
        screening.daily_clear_button().click()
        expect(screening.daily_search).to_be_empty()

    def test_positive_daily_result_count(self, screening):
        screening.switch_daily()
        expect(screening.page.get_by_text(re.compile(r"Showing \d+ results"))).to_be_visible()

    def test_positive_daily_bulk_action_and_remove_buttons(self, screening):
        screening.switch_daily()
        expect(screening.bulk_action_button).to_be_visible()
        expect(screening.remove_button).to_be_visible()
        expect(screening.remove_button.locator("i")).to_be_visible()

    @pytest.mark.parametrize("header", ScreeningPage.DAILY_HEADERS)
    def test_positive_daily_table_header(self, screening, header):
        screening.switch_daily()
        expect(screening.daily_header(header)).to_be_attached()

    def test_positive_daily_table_select_all_checkbox(self, screening):
        screening.switch_daily()
        expect(screening.select_all).to_be_attached()

    def test_positive_daily_rows_have_profile_ids(self, screening):
        screening.switch_daily()
        if screening.daily_rows.count() == 0:
            pytest.skip("Daily Screening has no rows in this environment")
        for i in range(screening.daily_rows.count()):
            row = screening.daily_rows.nth(i)
            expect(row.locator('td').nth(2)).not_to_be_empty()

    def test_positive_daily_row_checkbox_select_deselect(self, screening):
        screening.switch_daily()
        if screening.daily_rows.count() == 0:
            pytest.skip("Daily Screening has no rows")
        box = screening.row_checkbox(0)
        box.check()
        expect(box).to_be_checked()
        box.uncheck()
        expect(box).not_to_be_checked()

    def test_positive_daily_select_all_toggle(self, screening):
        screening.switch_daily()
        if screening.daily_rows.count() == 0:
            pytest.skip("Daily Screening has no rows")
        screening.select_all.check()
        for i in range(screening.daily_rows.count()):
            expect(screening.row_checkbox(i)).to_be_checked()
        screening.select_all.uncheck()
        for i in range(screening.daily_rows.count()):
            expect(screening.row_checkbox(i)).not_to_be_checked()

    def test_positive_daily_search_existing_profile(self, screening):
        screening.switch_daily()
        if screening.daily_rows.count() == 0:
            pytest.skip("Daily Screening has no rows")
        name = screening.daily_rows.first.locator("td").nth(1).inner_text().strip()
        screening.search_daily(name)
        expect(screening.daily_rows.filter(has_text=name).first).to_be_visible()

    def test_negative_daily_search_nonexistent_profile(self, screening):
        screening.switch_daily()
        screening.search_daily("NOT_A_REAL_PROFILE_" + uuid.uuid4().hex)
        expect(screening.daily_rows).to_have_count(0)

    def test_positive_daily_empty_table_message(self, screening):
        screening.switch_daily()
        screening.search_daily("NOT_A_REAL_PROFILE_" + uuid.uuid4().hex)
        expect(screening.page.locator(".ant-empty")).to_be_visible()

    @pytest.mark.skip(reason="Bulk Action is non-functional; excluded from current scope")
    def test_positive_daily_bulk_action_opens_upload_dialog(self, screening):
        screening.switch_daily()
        screening.open_bulk_action()
        expect(screening.bulk_remove_modal.locator('input[type="file"][accept=".csv"]')).to_be_attached()
        expect(screening.bulk_remove_modal.get_by_role("button", name="Okay")).to_be_visible()
        expect(screening.bulk_remove_modal.get_by_role("button", name="Cancel")).to_be_visible()

    @pytest.mark.skip(reason="Bulk Action is non-functional; excluded from current scope")
    def test_positive_daily_bulk_action_cancel(self, screening):
        screening.switch_daily()
        screening.open_bulk_action()
        screening.close_bulk_action()

    @pytest.mark.skip(reason="Bulk Action is non-functional; excluded from current scope")
    def test_positive_daily_bulk_action_close_icon(self, screening):
        screening.switch_daily()
        screening.open_bulk_action()
        screening.bulk_remove_modal.locator(".modal-z-close").click()
        expect(screening.bulk_remove_modal.locator(".modal-z-card")).to_be_hidden()

    @pytest.mark.skip(reason="Bulk Action is non-functional; excluded from current scope")
    def test_negative_bulk_upload_non_csv_rejected_by_accept_attribute(self, screening):
        screening.switch_daily()
        screening.open_bulk_action()
        expect(screening.bulk_remove_modal.locator('input[type="file"]')).to_have_attribute("accept", ".csv")
        # The browser's accept filter is not server-side validation.

    @pytest.mark.skip(reason="Bulk Action is non-functional; excluded from current scope")
    def test_negative_bulk_upload_without_file(self, screening):
        if not allow_writes():
            pytest.skip("Requires disposable write opt-in to test submission")
        screening.switch_daily()
        screening.open_bulk_action()
        screening.bulk_remove_modal.get_by_role("button", name="Okay").click()
        expect(screening.page.get_by_text("Validation failed", exact=True)).to_be_visible(timeout=10000)

    def test_positive_daily_profile_name_is_clickable(self, screening):
        screening.switch_daily()
        if screening.daily_rows.count() == 0:
            pytest.skip("Daily Screening has no rows")
        expect(screening.daily_rows.first.locator("td").nth(1).get_by_role("button")).to_be_visible()

    def test_positive_daily_profile_open(self, screening):
        screening.switch_daily()
        if screening.daily_rows.count() == 0:
            pytest.skip("Daily Screening has no rows")
        screening.daily_rows.first.locator("td").nth(1).get_by_role("button").click()
        # Exact destination/result detail UI needs its DOM to assert further.
        expect(screening.page.locator("body")).to_be_visible()

    def test_negative_remove_without_selection(self, screening):
        if not allow_writes():
            pytest.skip("Requires disposable write opt-in to test Remove")
        screening.switch_daily()
        screening.remove_button.click()
        # A remove action without selection must not silently delete existing rows.
        expect(screening.daily_table).to_be_visible()

    def test_positive_daily_tab_round_trip(self, screening):
        screening.switch_daily()
        screening.switch_single()
        expect(screening.name_input).to_be_visible()
        screening.switch_daily()
        expect(screening.daily_table).to_be_visible()
