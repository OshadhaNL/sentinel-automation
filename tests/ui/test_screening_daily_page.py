import os
import re

import pytest

from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.screeningDailyPage import ScreeningDailyPage


ORGANIZATION_NAME = "Microsoft Corporation"
ORGANIZATION_COUNTRY = "United States of America (USA)"


# ======================================================
# FIXTURES
# ======================================================

@pytest.fixture
def screening(page: Page, base_url: str):

    test_email = os.getenv("TEST_EMAIL")
    test_password = os.getenv("TEST_PASSWORD")

    assert test_email, "Please set TEST_EMAIL"
    assert test_password, "Please set TEST_PASSWORD"

    login = LoginPage(page)

    login.open(base_url)
    login.enter_email(test_email)
    login.enter_password(test_password)
    login.click_login()

    expect(page).to_have_url(
        re.compile(r".*/nolimit/app/home/?$"),
        timeout=60000,
    )

    screening_page = ScreeningDailyPage(page)

    screening_page.open(base_url)

    return screening_page


@pytest.fixture
def daily(screening):

    screening.open_daily()

    return screening


@pytest.fixture
def ongoing_record(screening):

    name = screening.unique_name()
    record = None

    try:

        record = screening.create_ongoing_record(
            name=name
        )

        yield record

    finally:

        # Cleanup is executed even if the test fails.

        if record is not None:

            screening.cleanup_ongoing_record(record)

        else:

            screening.cleanup_ongoing_name(name)


# ======================================================
# ONGOING SCREENING
# 4 TEST CASES
# ======================================================

@pytest.mark.ui
class TestOngoingScreening:

    def test_positive_ongoing_checkbox_visible(
        self,
        screening,
    ):
        screening.choose_individual()

        expect(
            screening.ongoing_checkbox
        ).to_be_visible()

        expect(
            screening.ongoing_checkbox
        ).to_be_enabled()

    def test_positive_ongoing_checkbox_toggle(
        self,
        screening,
    ):
        screening.choose_individual()

        screening.set_ongoing(True)
        screening.set_ongoing(False)
        screening.set_ongoing(True)

    def test_positive_ongoing_screening_added_to_daily(
        self,
        screening,
        ongoing_record,
    ):
        row = screening.find_daily_record(
            ongoing_record["name"]
        )

        expect(row).to_be_visible()

        assert screening.get_daily_profile_id(row) == (
            ongoing_record["profile_id"]
        )

    def test_negative_non_ongoing_screening_not_added(
        self,
        screening,
    ):
        name = screening.unique_name()

        before = screening.collect_daily_records()

        screening.switch_single()

        screening.analyze_screening(
            name=name,
            ongoing=False,
        )

        screening.return_to_screening()

        after = screening.collect_daily_records()

        assert name not in after.values(), (
            "Non-ongoing screening was added "
            "to Daily Screening"
        )

        assert before == after, (
            "Daily Screening records changed after "
            "non-ongoing screening"
        )


# ======================================================
# DAILY SCREENING
# 10 TEST CASES
# ======================================================

@pytest.mark.ui
class TestDailyScreeningFunctional:

    def test_positive_daily_table_headers(
        self,
        daily,
    ):
        daily.assert_daily_headers()

    def test_positive_daily_result_count(
        self,
        daily,
    ):
        records = daily.collect_daily_records()

        count = daily.result_count()

        assert count == len(records)

        print("Displayed result count:", count)
        print("Actual record count:", len(records))

    def test_positive_daily_record_values(
        self,
        screening,
        ongoing_record,
    ):
        row = screening.find_daily_record(
            ongoing_record["name"]
        )

        values = screening.assert_daily_record_values(row)

        assert values["name"] == ongoing_record["name"]

        assert values["profile_id"] == (
            ongoing_record["profile_id"]
        )

        print("Daily record values:", values)

    def test_positive_daily_search_by_name(
        self,
        screening,
        ongoing_record,
    ):
        screening.refresh_daily()

        screening.wait_for_daily_records()

        before = screening.result_count()

        assert before > 1, (
            "At least two records are required "
            "to verify search filtering"
        )

        print("Records before search:", before)

        screening.search_daily_records(
            ongoing_record["name"]
        )

        screening.assert_filtered_record(
            ongoing_record
        )

    def test_positive_daily_search_by_profile_id(
        self,
        screening,
        ongoing_record,
    ):
        screening.refresh_daily()

        screening.wait_for_daily_records()

        before = screening.result_count()

        assert before > 1, (
            "At least two records are required "
            "to verify Profile ID filtering"
        )

        print("Records before search:", before)

        screening.search_daily_records(
            ongoing_record["profile_id"]
        )

        screening.assert_filtered_record(
            ongoing_record
        )

    def test_positive_daily_clear_search(
        self,
        screening,
        ongoing_record,
    ):
        screening.refresh_daily()

        screening.wait_for_daily_records()

        before_count = screening.result_count()

        before_ids = set(
            screening.visible_profile_ids()
        )

        assert before_count > 1

        print("Before search:", before_count)

        screening.search_daily_records(
            ongoing_record["name"]
        )

        # Clear-search validation requires a genuinely
        # filtered table as its starting condition.

        screening.assert_filtered_record(
            ongoing_record
        )

        print(
            "After search:",
            screening.result_count(),
        )

        expect(
            screening.daily_clear_action
        ).to_be_visible()

        screening.clear_daily_search()

        expect(
            screening.daily_search_input
        ).to_have_value("")

        screening.assert_result_count(before_count)

        expect(
            screening.daily_record_rows
        ).to_have_count(
            len(before_ids),
            timeout=30000,
        )

        after_ids = set(
            screening.visible_profile_ids()
        )

        assert after_ids == before_ids, (
            "Original records were not restored "
            "after clearing the search"
        )

        print(
            "After clearing search:",
            screening.result_count(),
        )

    def test_positive_open_daily_screening_record(
        self,
        screening,
        ongoing_record,
    ):
        results = screening.open_daily_record(
            ongoing_record
        )

        results.assert_loaded(
            ongoing_record["name"]
        )

        counts = results.wait_for_counts()

        assert sum(counts.values()) == results.count()

        print("Screening category counts:", counts)

    def test_positive_daily_select_single_record(
        self,
        daily,
    ):
        expect(
            daily.daily_record_rows.first
        ).to_be_visible(timeout=30000)

        daily.clear_all_daily_rows()

        daily.select_daily_row(0)

        daily.assert_selected_daily_count(1)

        daily.deselect_daily_row(0)

        daily.assert_selected_daily_count(0)

    def test_positive_daily_select_multiple_records(
        self,
        daily,
    ):
        expect(
            daily.daily_record_rows.nth(1)
        ).to_be_visible(timeout=30000)

        daily.clear_all_daily_rows()

        daily.select_daily_row(0)
        daily.select_daily_row(1)

        daily.assert_selected_daily_count(2)

        daily.deselect_daily_row(0)

        daily.assert_selected_daily_count(1)

        daily.deselect_daily_row(1)

        daily.assert_selected_daily_count(0)

    def test_positive_daily_select_all_and_clear(
        self,
        daily,
    ):
        expect(
            daily.daily_record_rows.first
        ).to_be_visible(timeout=30000)

        daily.clear_all_daily_rows()

        visible_count = daily.daily_record_rows.count()

        assert visible_count > 0

        daily.select_all_daily_rows()

        daily.assert_selected_daily_count(
            visible_count
        )

        daily.clear_all_daily_rows()

        daily.assert_selected_daily_count(0)


# ======================================================
# REMOVE FUNCTIONALITY
# 3 TEST CASES
# ======================================================

@pytest.mark.ui
class TestDailyScreeningRemove:

    def test_positive_remove_single_ongoing_record(
        self,
        screening,
        ongoing_record,
    ):
        screening.remove_ongoing_records(
            [ongoing_record]
        )

        screening.assert_daily_record_absent(
            ongoing_record["name"]
        )

    def test_positive_remove_multiple_ongoing_records(
        self,
        screening,
    ):
        names = [
            screening.unique_name(),
            screening.unique_name(),
        ]

        records = []

        try:

            for name in names:

                record = screening.create_ongoing_record(
                    name=name
                )

                records.append(record)

            assert records[0]["profile_id"] != (
                records[1]["profile_id"]
            )

            screening.remove_ongoing_records(records)

            for record in records:

                screening.assert_daily_record_absent(
                    record["name"]
                )

        finally:

            # Clean up individually if bulk removal fails.
            # Only generated QA names are eligible.

            for name in names:

                screening.cleanup_ongoing_name(name)

    def test_negative_remove_without_selection(
        self,
        daily,
    ):
        before = daily.collect_daily_records()

        daily.refresh_daily()

        daily.clear_all_daily_rows()

        daily.assert_selected_daily_count(0)

        expect(daily.remove_action).to_be_visible()

        if daily.remove_action.is_disabled():

            print(
                "Remove disabled without selection"
            )

        else:

            daily.remove_action.click()

            daily.wait_daily_loading()

            print(
                "Remove clicked without selection"
            )

        after = daily.collect_daily_records()

        assert before == after, (
            "Daily Screening records changed "
            "without selecting a record"
        )

        print("Records before Remove:", len(before))
        print("Records after Remove:", len(after))

        print(
            "No records removed without selection."
        )


# ======================================================
# ORGANIZATION SCREENING
# 7 TEST CASES
# ======================================================

@pytest.mark.ui
class TestOrganizationScreening:

    def test_positive_organization_radio_selection(
        self,
        screening,
    ):
        screening.choose_organization()

        expect(
            screening.organization_option
        ).to_be_checked()

        expect(
            screening.individual_option
        ).not_to_be_checked()

    def test_positive_organization_form_fields(
        self,
        screening,
    ):
        screening.assert_organization_fields()

    def test_positive_organization_name_input(
        self,
        screening,
    ):
        screening.choose_organization()

        screening.organization_name_input.fill(
            ORGANIZATION_NAME
        )

        expect(
            screening.organization_name_input
        ).to_have_value(
            ORGANIZATION_NAME
        )

    def test_positive_organization_registered_country(
        self,
        screening,
    ):
        screening.choose_registered_country(
            ORGANIZATION_COUNTRY
        )

        expect(
            screening.registered_country_select.locator(
                ".ant-select-selection-item"
            )
        ).to_have_text(
            ORGANIZATION_COUNTRY
        )

    def test_positive_organization_screening_results(
        self,
        screening,
    ):
        results = screening.analyze_screening(
            name=ORGANIZATION_NAME,
            ongoing=False,
            organization=True,
        )

        results.assert_loaded(
            ORGANIZATION_NAME
        )

        results.assert_headers()

        counts = results.wait_for_counts()

        assert sum(counts.values()) == results.count()

        print("Organization matches:", results.count())
        print("Category counts:", counts)

    def test_positive_organization_ongoing_screening(
        self,
        screening,
    ):
        name = screening.unique_name()

        record = None

        try:

            record = screening.create_ongoing_record(
                name=name,
                organization=True,
            )

            row = screening.find_daily_record(
                record["name"]
            )

            expect(row).to_be_visible()

            assert screening.get_daily_profile_id(row) == (
                record["profile_id"]
            )

        finally:

            if record is not None:

                screening.cleanup_ongoing_record(
                    record
                )

            else:

                screening.cleanup_ongoing_name(name)

    def test_negative_organization_analyze_without_name(
        self,
        screening,
    ):
        screening.choose_organization()

        screening.organization_name_input.fill("")

        expect(
            screening.organization_name_input
        ).to_have_value("")

        if screening.analyze_action.is_enabled():

            screening.analyze_action.click()

        expect(
            screening.organization_name_input
        ).to_be_visible()

        expect(
            screening.back_to_screening_button
        ).to_have_count(0)

        expect(
            screening.organization_option
        ).to_be_checked()