
import os
import re

import pytest

from playwright.sync_api import expect

from pages.loginPage import LoginPage
from pages.screeningPage import ScreeningPage
from pages.screeningResultsPage import ScreeningResultsPage


# ======================================================
# HARDCODED SCREENING TEST DATA
# ======================================================

SEARCH_NAMES = (
    "Mahinda Rajapaksa",
    "Gotabaya Rajapaksa",
    "Ranil Wickremesinghe",
    "Vladimir Putin",
    "Narendra Modi",
    "Donald Trump",
    "John Smith",
    "Mohammed Ali",
    "Osama bin Laden",
)


CATEGORIES = (
    "Unresolved Hits",
    "Positive Hits",
    "False Hits",
    "Possible Hits",
)


# ======================================================
# LOGIN AND SCREENING SETUP
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
        re.compile(
            r".*/nolimit/app/home/?$"
        ),
        timeout=30000,
    )

    screen = ScreeningPage(page)

    screen.open(base_url)

    return screen


# ======================================================
# SCREENING TESTS
# ======================================================

@pytest.mark.ui
class TestNamedScreeningCategories:

    # ==================================================
    # TEST 01 - VERIFY DIFFERENT NAMES AND CATEGORIES
    # ==================================================

    @pytest.mark.parametrize(
        "name",
        SEARCH_NAMES,
    )
    def test_positive_real_names_display_in_actual_hit_categories(
        self,
        screening,
        name,
    ):

        screening.analyze(
            name,
            ongoing=False,
        )

        results = ScreeningResultsPage(
            screening.page
        )

        results.assert_loaded(name)

        # Wait until all category counts reconcile.
        counts = results.wait_for_counts()

        total = results.count()

        print("\n" + "=" * 70)
        print(f"SCREENING NAME: {name}")
        print(f"TOTAL MATCHES: {total}")

        for category, count in counts.items():
            print(f"{category}: {count}")

        print("=" * 70)

        assert total > 0, (
            f"No screening matches returned for {name}"
        )

        results.assert_headers()

        matched_search_name = False

        # Validate all four categories.
        for category in CATEGORIES:

            print("\n" + "-" * 60)
            print(f"Checking: {category}")

            # Verify correct active category.
            results.choose_category(category)

            # Read current count after switching.
            count = results.category_count(
                category
            )

            print(f"Category count: {count}")

            # Verify empty and populated categories.
            visible_count = (
                results.assert_category_rows(
                    category
                )
            )

            if visible_count == 0:

                print(
                    f"{category}: "
                    "Empty state verified"
                )

                continue

            # Find the searched name in the category.
            matching = results.matching_rows(
                name
            )

            matching_count = matching.count()

            print(
                f"Matching name rows: "
                f"{matching_count}"
            )

            if matching_count > 0:

                matched_search_name = True

                selected_row = matching.first

            else:

                # Other names can be returned as
                # alternative or false matches.
                selected_row = results.rows.first

                print(
                    "No direct name match in this "
                    "category's visible rows. "
                    "Validating a returned profile."
                )

            # Verify the selected profile name and
            # unique profile ID against the details.
            profile_name, profile_id = (
                results.open_match(selected_row)
            )

            print(
                f"Category: {category}"
            )

            print(
                f"Verified name: {profile_name}"
            )

            print(
                f"Verified ID: {profile_id}"
            )

            # Return to results and wait for
            # counts to finish loading again.
            results.back_to_matches(name)

        assert matched_search_name, (
            f"The searched name '{name}' was not "
            "found in any visible category records."
        )

        print("\n" + "=" * 70)
        print(
            f"Completed category validation "
            f"for {name}"
        )
        print("=" * 70)

    # ==================================================
    # TEST 02 - MAHINDA RAJAPAKSA UNRESOLVED HITS
    # ==================================================

    def test_positive_mahinda_name_displayed_in_unresolved_hits(
        self,
        screening,
    ):

        name = "Mahinda Rajapaksa"

        screening.analyze(
            name,
            ongoing=False,
        )

        results = ScreeningResultsPage(
            screening.page
        )

        results.assert_loaded(name)

        results.wait_for_counts()

        results.choose_category(
            "Unresolved Hits"
        )

        count = results.category_count(
            "Unresolved Hits"
        )

        assert count > 0, (
            f"No Unresolved Hits found for {name}"
        )

        results.assert_category_rows(
            "Unresolved Hits"
        )

        matching = results.matching_rows(
            name
        )

        expect(matching.first).to_be_visible(
            timeout=30000
        )

        profile_name, profile_id = (
            results.open_match(
                matching.first
            )
        )

        assert name.lower() in profile_name.lower()

        print(
            f"\nUnresolved Hits: {count}"
        )

        print(
            f"Verified name: {profile_name}"
        )

        print(
            f"Verified ID: {profile_id}"
        )

        # Verify return navigation.
        results.back_to_matches(name)

        # Confirm category switching works after
        # returning from the details page.
        results.choose_category(
            "Unresolved Hits"
        )

        results.assert_category_rows(
            "Unresolved Hits"
        )

    # ==================================================
    # TEST 03 - CATEGORY COUNT RECONCILIATION
    # ==================================================

    @pytest.mark.parametrize(
        "name",
        (
            "Mahinda Rajapaksa",
            "Vladimir Putin",
            "John Smith",
            "Mohammed Ali",
        ),
    )
    def test_positive_category_totals_reconcile(
        self,
        screening,
        name,
    ):

        screening.analyze(
            name,
            ongoing=False,
        )

        results = ScreeningResultsPage(
            screening.page
        )

        results.assert_loaded(name)

        try:

            counts = results.wait_for_counts(
                timeout=90000
            )

        except Exception as error:

            counts = results.get_category_counts()

            total = results.count()

            pytest.fail(
                f"Category counts did not reconcile "
                f"within 90 seconds for {name}. "
                f"Total matches: {total}. "
                f"Category counts: {counts}. "
                f"Category total: "
                f"{sum(counts.values())}. "
                f"Original error: {error}"
            )

        total = results.count()

        category_total = sum(
            counts.values()
        )

        print("\n" + "=" * 70)
        print(f"SCREENING NAME: {name}")
        print(f"Total matches: {total}")

        for category, count in counts.items():
            print(f"{category}: {count}")

        print(
            f"Category total: {category_total}"
        )

        print(
            f"Difference: "
            f"{total - category_total}"
        )

        print("=" * 70)

        assert category_total == total, (
            f"{name}: "
            f"Total matches={total}, "
            f"Category total={category_total}"
        )
