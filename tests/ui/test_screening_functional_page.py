
import os
import re
import math

import pytest

from playwright.sync_api import expect

from pages.loginPage import LoginPage
from pages.screeningPage import ScreeningPage
from pages.screeningFunctionalPage import (
    ScreeningFunctionalPage,
)


# ======================================================
# HARDCODED TEST DATA
# ======================================================

RESOLUTION_NAME = "Mahinda Rajapaksa"

PAGINATION_NAME = "Vladimir Putin"

DETAILS_NAME = "Vladimir Putin"

PDF_NAME = "Mahinda Rajapaksa"


# ======================================================
# FIXTURES
# ======================================================

@pytest.fixture
def screening(page, base_url):

    email = os.getenv("TEST_EMAIL")

    password = os.getenv("TEST_PASSWORD")

    assert email, "TEST_EMAIL is required"

    assert password, "TEST_PASSWORD is required"

    login = LoginPage(page)

    login.open(base_url)

    login.enter_email(email)

    login.enter_password(password)

    login.click_login()

    expect(page).to_have_url(
        re.compile(r".*/nolimit/app/home/?$"),
        timeout=30000,
    )

    screen = ScreeningPage(page)

    screen.open(base_url)

    return screen


def create_results(screening, name):

    # Always initiate a new one-time screening.
    # Never select an existing client or Daily
    # Screening record.
    screening.analyze(
        name,
        ongoing=False,
    )

    results = ScreeningFunctionalPage(
        screening.page
    )

    results.assert_loaded(name)

    results.wait_for_counts()

    return results


@pytest.fixture
def resolution_results(screening):

    results = create_results(
        screening,
        RESOLUTION_NAME,
    )

    results.choose_category("Unresolved Hits")

    expect(results.rows.first).to_be_visible()

    return results


@pytest.fixture
def pagination_results(screening):

    results = create_results(
        screening,
        PAGINATION_NAME,
    )

    results.choose_category("False Hits")

    expect(results.pagination).to_be_visible(
        timeout=30000
    )

    return results


@pytest.fixture
def details_results(screening):

    results = create_results(
        screening,
        DETAILS_NAME,
    )

    results.choose_category("Unresolved Hits")

    results.open_match(results.rows.first)

    results.assert_details_loaded()

    return results


# ======================================================
# RESOLUTION UPDATE TESTS
# ======================================================

@pytest.mark.ui
class TestScreeningResolution:

    def test_positive_resolution_toolbar_appears(
        self,
        resolution_results,
    ):

        results = resolution_results

        results.select_row(0)

        expect(results.bulk_resolution).to_be_visible()

        expect(results.apply_button).to_be_visible()

        expect(results.clear_button).to_be_visible()

        results.assert_selected_count(1)

    def test_positive_multiple_selection_count(
        self,
        resolution_results,
    ):

        results = resolution_results

        results.select_row(0)

        results.select_row(1)

        results.assert_selected_count(2)

    def test_positive_resolution_dropdown_options(
        self,
        resolution_results,
    ):

        results = resolution_results

        results.select_row(0)

        results.assert_resolution_options()

    @pytest.mark.parametrize(
        "destination",
        (
            "Positive Hits",
            "False Hits",
            "Possible Hits",
        ),
        ids=(
            "positive-hit",
            "false-hit",
            "possible-hit",
        ),
    )
    def test_positive_update_unresolved_resolution(
        self,
        resolution_results,
        destination,
    ):

        results = resolution_results

        profile_ids = results.update_selected_records(
            source="Unresolved Hits",
            destination=destination,
            quantity=1,
        )

        assert len(profile_ids) == 1

        print(
            f"Updated {profile_ids[0]} "
            f"to {destination}"
        )

    def test_positive_update_false_to_positive(
        self,
        resolution_results,
    ):

        resolution_results.update_selected_records(
            source="False Hits",
            destination="Positive Hits",
            quantity=1,
        )

    def test_positive_update_multiple_records(
        self,
        resolution_results,
    ):

        profile_ids = (
            resolution_results.update_selected_records(
                source="Unresolved Hits",
                destination="Possible Hits",
                quantity=2,
            )
        )

        assert len(set(profile_ids)) == 2

    def test_positive_clear_selected_records(
        self,
        resolution_results,
    ):

        results = resolution_results

        results.select_row(0)

        results.select_row(1)

        results.assert_selected_count(2)

        results.clear_selection()

        expect(results.apply_button).to_have_count(0)

    def test_negative_apply_without_resolution(
        self,
        resolution_results,
    ):

        results = resolution_results

        results.select_row(0)

        expect(results.apply_button).to_be_disabled()

    def test_negative_resolution_selection_without_apply(
        self,
        resolution_results,
    ):

        results = resolution_results

        before = results.wait_for_counts()

        profile_id = results.row_id(0)

        results.select_row(0)

        results.choose_bulk_resolution(
            "Positive Hits"
        )

        # Clear the selection without applying.
        results.clear_selection()

        assert results.get_category_counts() == before

        row = results.row_by_id(profile_id)

        expect(row).to_be_visible()

        expect(
            row.locator("td").last
        ).to_have_text(
            re.compile(r"^Unresolved$", re.I)
        )

    def test_positive_update_from_match_details(
        self,
        resolution_results,
    ):

        results = resolution_results

        before = results.wait_for_counts()

        total = results.count()

        profile_id = results.row_id(0)

        results.open_match(results.rows.first)

        results.choose_detail_resolution(
            "Positive Hits"
        )

        results.update_button.click()

        results.assert_update_notification()

        # Handle either supported navigation:
        # staying on details or returning to matches.
        results.page.wait_for_function(
            """
            () => {
                const report = document.querySelector(
                    '#wc-report'
                );

                const summary = document.querySelector(
                    'main .wc-page-header p'
                );

                return (
                    report && report.getClientRects().length
                ) || (
                    summary &&
                    /Showing.*matches for/i.test(
                        summary.innerText
                    )
                );
            }
            """,
            timeout=30000,
        )

        if results.report.is_visible():

            results.back_to_matches(
                RESOLUTION_NAME
            )

        else:

            results.assert_loaded(
                RESOLUTION_NAME
            )

        results.assert_resolution_counts(
            before=before,
            source="Unresolved Hits",
            destination="Positive Hits",
            quantity=1,
            total_before=total,
        )

        results.choose_category("Positive Hits")

        assert results.find_profile_across_pages(
            profile_id
        )

        results.open_match(
            results.row_by_id(profile_id)
        )

        expect(
            results.detail_resolution.locator(
                ".ant-select-selection-item"
            )
        ).to_have_text("Positive Hits")


# ======================================================
# PAGINATION TESTS
# ======================================================

@pytest.mark.ui
class TestScreeningPagination:

    def test_positive_pagination_controls_visible(
        self,
        pagination_results,
    ):

        results = pagination_results

        expect(results.pagination).to_be_visible()

        expect(results.previous_page).to_be_visible()

        expect(results.next_page).to_be_visible()

        expect(
            results.page_size_selector
        ).to_be_visible()

    def test_positive_default_page_size(
        self,
        pagination_results,
    ):

        results = pagination_results

        assert results.page_size() == 15

        expect(results.rows).to_have_count(15)

    def test_positive_next_page_navigation(
        self,
        pagination_results,
    ):

        results = pagination_results

        assert results.current_page() == 1

        results.go_next_page()

        assert results.current_page() == 2

    def test_positive_previous_page_navigation(
        self,
        pagination_results,
    ):

        results = pagination_results

        results.go_next_page()

        results.go_previous_page()

        assert results.current_page() == 1

    def test_positive_specific_page_navigation(
        self,
        pagination_results,
    ):

        results = pagination_results

        results.go_to_page(3)

        assert results.current_page() == 3

    def test_positive_different_records_across_pages(
        self,
        pagination_results,
    ):

        results = pagination_results

        first_page_ids = set(
            results.visible_profile_ids()
        )

        results.go_next_page()

        second_page_ids = set(
            results.visible_profile_ids()
        )

        assert first_page_ids.isdisjoint(
            second_page_ids
        ), "Duplicate profiles across pages"

    def test_positive_last_page_record_count(
        self,
        pagination_results,
    ):

        results = pagination_results

        count = results.category_count(
            "False Hits"
        )

        size = results.page_size()

        expected_last_page = math.ceil(
            count / size
        )

        results.go_last_page("False Hits")

        assert (
            results.current_page()
            == expected_last_page
        )

        expected_rows = (
            count % size
            or size
        )

        expect(results.rows).to_have_count(
            expected_rows
        )

    def test_positive_all_paginated_records_match_count(
        self,
        pagination_results,
    ):

        results = pagination_results

        expected_count = results.category_count(
            "False Hits"
        )

        size = results.page_size()

        total_pages = math.ceil(
            expected_count / size
        )

        collected_ids = []

        for page_number in range(
            1,
            total_pages + 1,
        ):

            assert (
                results.current_page()
                == page_number
            )

            collected_ids.extend(
                results.visible_profile_ids()
            )

            if page_number < total_pages:

                results.go_next_page()

        assert None not in collected_ids

        assert len(collected_ids) == expected_count

        assert (
            len(set(collected_ids))
            == expected_count
        ), "Duplicate profile IDs detected"

        print(
            "Verified paginated records:",
            len(collected_ids),
        )

    def test_negative_previous_disabled_on_first_page(
        self,
        pagination_results,
    ):

        results = pagination_results

        assert results.current_page() == 1

        expect(
            results.previous_page
        ).to_have_class(
            re.compile(
                r"\bant-pagination-disabled\b"
            )
        )

    def test_negative_next_disabled_on_last_page(
        self,
        pagination_results,
    ):

        results = pagination_results

        results.go_last_page("False Hits")

        expect(
            results.next_page
        ).to_have_class(
            re.compile(
                r"\bant-pagination-disabled\b"
            )
        )


# ======================================================
# MATCH DETAILS TESTS
# ======================================================

@pytest.mark.ui
class TestScreeningMatchDetailsFunctional:

    def test_positive_personal_details_fields(
        self,
        details_results,
    ):

        details_results.assert_personal_fields()

    @pytest.mark.parametrize(
        "section",
        (
            "BIOGRAPHY",
            "PEP ROLE DETAILS",
            "Further Information",
            "Linked Individuals",
            "Education",
            "Linked Companies",
            "Sources",
        ),
    )
    def test_positive_report_section_visible(
        self,
        details_results,
        section,
    ):

        details_results.assert_section(section)

    @pytest.mark.parametrize(
        "section,headers",
        (
            (
                "PEP ROLE DETAILS",
                ("Role", "Role Bio", "Status", "Role Term"),
            ),
            (
                "Further Information",
                ("Title", "Description", "Source Link"),
            ),
            (
                "Linked Individuals",
                ("Name", "Connection", "Type", "Category"),
            ),
            (
                "Education",
                ("University", "Term"),
            ),
            (
                "Linked Companies",
                ("Name", "Connection", "Type", "Category"),
            ),
            (
                "Sources",
                ("Date", "Link"),
            ),
        ),
    )
    def test_positive_report_table_headers(
        self,
        details_results,
        section,
        headers,
    ):

        details_results.assert_section_headers(
            section,
            headers,
        )

    def test_positive_next_match_navigation(
        self,
        details_results,
    ):

        results = details_results

        original_id = (
            results.profile_id.inner_text().strip()
        )

        next_id = results.navigate_match("next")

        assert next_id != original_id

    def test_positive_previous_match_navigation(
        self,
        details_results,
    ):

        results = details_results

        original_id = (
            results.profile_id.inner_text().strip()
        )

        results.navigate_match("next")

        previous_id = results.navigate_match(
            "previous"
        )

        assert previous_id == original_id

    def test_positive_match_position_counter(
        self,
        details_results,
    ):

        results = details_results

        position, total = results.position()

        assert position == 1

        assert total > 1

        results.navigate_match("next")

        next_position, next_total = (
            results.position()
        )

        assert next_position == 2

        assert next_total == total

    def test_positive_pep_badge_navigation(
        self,
        details_results,
    ):

        details_results.assert_badge_navigation(
            "PEP",
            "pep",
        )

    def test_positive_adverse_media_badge_navigation(
        self,
        details_results,
    ):

        details_results.assert_badge_navigation(
            "Adverse Media",
            "media",
        )

    def test_positive_missing_information_message(
        self,
        details_results,
    ):

        results = details_results

        empty_sections = results.report.locator(
            ".no-data"
        )

        expect(empty_sections.first).to_be_visible()

        for section in empty_sections.all():

            expect(
                section.get_by_text(
                    "Details are not available",
                    exact=True,
                )
            ).to_be_visible()

    def test_positive_external_source_links(
        self,
        details_results,
    ):

        results = details_results

        sources = results.section_table(
            "Sources"
        ).locator('a[href^="http"]')

        expect(sources.first).to_be_visible()

        for link in sources.all():

            expect(link).to_have_attribute(
                "target",
                "_blank",
            )

            href = link.get_attribute("href")

            assert href.startswith(
                ("https://", "http://")
            )

    def test_negative_previous_disabled_first_match(
        self,
        details_results,
    ):

        results = details_results

        position, total = results.position()

        assert position == 1

        expect(
            results.previous_match
        ).to_be_disabled()

    def test_negative_next_disabled_last_match(
        self,
        screening,
    ):

        results = create_results(
            screening,
            DETAILS_NAME,
        )

        results.choose_category("False Hits")

        if results.pagination.is_visible():

            results.go_last_page("False Hits")

        results.open_match(results.rows.last)

        position, total = results.position()

        # Confirm the selected record really is the
        # final match before checking the button.
        assert position == total, (
            f"Selected position {position} "
            f"is not the final match {total}"
        )

        expect(results.next_match).to_be_disabled()


# ======================================================
# PDF DOWNLOAD TESTS
# ======================================================

@pytest.mark.ui
class TestScreeningPDF:

    def test_positive_pdf_button_visible(
        self,
        details_results,
    ):

        expect(
            details_results.pdf_button
        ).to_be_visible()

        expect(
            details_results.pdf_button
        ).to_be_enabled()

    def test_positive_pdf_download_and_file_validation(
        self,
        screening,
        tmp_path,
    ):

        results = create_results(
            screening,
            PDF_NAME,
        )

        results.choose_category("Unresolved Hits")

        results.open_match(results.rows.first)

        path = results.download_report(tmp_path)

        # Verify extension.
        assert path.suffix.lower() == ".pdf"

        # Verify filename convention.
        assert path.name.lower().startswith(
            "world check report"
        )

        # Verify file content and PDF signature.
        content = path.read_bytes()

        assert len(content) > 0

        assert content.startswith(b"%PDF-"), (
            "Downloaded file has an invalid PDF header"
        )

        assert b"%%EOF" in content[-2048:], (
            "Downloaded PDF appears incomplete"
        )

        print("PDF filename:", path.name)

        print("PDF size:", len(content), "bytes")

        print("PDF file validation completed")
