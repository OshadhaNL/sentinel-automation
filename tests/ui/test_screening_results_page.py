"""Screening result-list tests. External WorldCheck searches are opt-in."""
import os
import re
import uuid
import pytest
from playwright.sync_api import expect
from pages.loginPage import LoginPage
from pages.screeningPage import ScreeningPage
from pages.screeningResultsPage import ScreeningResultsPage

NAMES = ("John Smith", "Mohammed Ali", "Vladimir Putin", "Osama bin Laden")

@pytest.fixture
def screening(page, base_url):
    if os.getenv("SCREENING_ALLOW_ANALYZE") != "1":
        pytest.skip("Set SCREENING_ALLOW_ANALYZE=1 to permit external WorldCheck searches")
    email, password = os.getenv("TEST_EMAIL"), os.getenv("TEST_PASSWORD")
    if not email or not password:
        pytest.skip("Set TEST_EMAIL and TEST_PASSWORD")
    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(email)
    login.enter_password(password)
    login.click_login()
    expect(page).to_have_url(re.compile(r".*/nolimit/app/home/?$"), timeout=30000)
    obj = ScreeningPage(page)
    obj.open(base_url)
    return obj

@pytest.fixture
def one_time_results(screening):
    name = "AutomationScreening_" + uuid.uuid4().hex[:12]
    screening.analyze(name, ongoing=False)
    results = ScreeningResultsPage(screening.page)
    results.assert_loaded(name)
    return results, name

@pytest.mark.ui
class TestScreeningResults:
    def test_positive_one_time_analyze_opens_results(self, one_time_results):
        results, name = one_time_results
        results.assert_loaded(name)

    def test_positive_results_show_total_count(self, one_time_results):
        results, _ = one_time_results
        assert results.count() >= 0

    def test_positive_all_four_categories_display_counts(self, one_time_results):
        results, _ = one_time_results
        for category in results.CATEGORIES:
            assert results.category_count(category) >= 0

    def test_positive_results_headers(self, one_time_results):
        results, _ = one_time_results
        results.assert_headers()

    @pytest.mark.parametrize("category", ScreeningResultsPage.CATEGORIES)
    def test_positive_category_switching(self, one_time_results, category):
        results, _ = one_time_results
        results.choose_category(category)
        expect(results.results_table).to_be_visible()

    def test_positive_category_totals_equal_match_total(self, one_time_results):
        results, _ = one_time_results
        counts = [results.category_count(x) for x in results.CATEGORIES]
        assert sum(counts) == results.count(), f"Category counts {counts} differ from total {results.count()}"

    def test_positive_back_to_screening(self, one_time_results):
        results, _ = one_time_results
        results.back.click()
        expect(results.page.get_by_role("heading", name="Screening", exact=True)).to_be_visible()
        expect(results.page.get_by_placeholder("Enter individual name")).to_be_visible()

    def test_positive_zero_match_empty_state_when_applicable(self, one_time_results):
        results, _ = one_time_results
        if results.count() != 0:
            pytest.skip("This disposable search returned hits; zero-match case unavailable")
        results.assert_empty()

    def test_positive_open_first_match_when_available(self, one_time_results):
        results, _ = one_time_results
        if results.count() == 0:
            pytest.skip("No matches returned for this search")
        results.open_first_match()
        expect(results.page.locator("#wc-report")).to_be_visible(timeout=30000)

    @pytest.mark.parametrize("name", NAMES)
    def test_positive_different_names_result_page(self, screening, name):
        screening.analyze(name)
        results = ScreeningResultsPage(screening.page)
        results.assert_loaded(name)
        assert results.count() >= 0
        for category in results.CATEGORIES:
            assert results.category_count(category) >= 0

    def test_positive_ongoing_analyze_opens_results(self, screening):
        if os.getenv("SCREENING_ALLOW_WRITES") != "1" or os.getenv("SCREENING_DISPOSABLE_DATA_CONFIRMED") != "1":
            pytest.skip("Ongoing enrollment needs SCREENING_ALLOW_WRITES=1 and SCREENING_DISPOSABLE_DATA_CONFIRMED=1")
        name = "AutomationOngoing_" + uuid.uuid4().hex[:12]
        screening.analyze(name, ongoing=True)
        results = ScreeningResultsPage(screening.page)
        results.assert_loaded(name)
        results.back.click()
        screening.switch_daily()
        # Daily search currently has a known defect; verify enrollment without
        # assuming its filtering works. This may need pagination if data grows.
        screening.search_daily(name)
        expect(screening.daily_rows.filter(has_text=name).first).to_be_visible(timeout=30000)
