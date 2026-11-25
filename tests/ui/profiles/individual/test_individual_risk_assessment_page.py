"""Individual Risk Assessment: UI, risk calculations, and opt-in persistence tests.

Write tests reuse WRITE_CLIENT_ID from config/screening_test_data.py by default.
Set RISK_TEST_ALLOW_CHANGES=1 to opt into modifying the disposable profile.
Use a dedicated disposable individual profile; do not use a shared/read-only client.
"""
import os
import re
import pytest
from playwright.sync_api import expect
from pages.profiles.profileNavigation import open_client_profile
from pages.profiles.individual.individualRiskAssessmentPage import IndividualRiskAssessmentPage as RiskPage
from config.screening_test_data import READ_ONLY_CLIENT_ID, WRITE_CLIENT_ID


@pytest.fixture
def risk(page, base_url):
    client_id = os.getenv('RISK_TEST_READ_CLIENT_ID', READ_ONLY_CLIENT_ID).strip()
    assert client_id, 'Set RISK_TEST_READ_CLIENT_ID or READ_ONLY_CLIENT_ID'
    open_client_profile(page, base_url, 'individual', client_id)
    view = RiskPage(page)
    expect(view.heading).to_be_visible(timeout=15000)
    view.open()
    return view


@pytest.fixture
def risk_write(page, base_url):
    if os.getenv('RISK_TEST_ALLOW_CHANGES') != '1':
        pytest.skip('Set RISK_TEST_ALLOW_CHANGES=1 to run risk write tests')
    client_id = os.getenv('RISK_TEST_WRITE_CLIENT_ID', WRITE_CLIENT_ID).strip()
    read_id = os.getenv('RISK_TEST_READ_CLIENT_ID', READ_ONLY_CLIENT_ID).strip()
    assert client_id, 'Set WRITE_CLIENT_ID in config/screening_test_data.py or RISK_TEST_WRITE_CLIENT_ID'
    assert client_id != read_id, 'Write client must differ from read-only client'
    open_client_profile(page, base_url, 'individual', client_id)
    view = RiskPage(page)
    expect(view.heading).to_be_visible(timeout=15000)
    view.open()
    return view


@pytest.mark.ui
class TestIndividualRiskUI:
    def test_profile_title_and_description(self, risk):
        expect(risk.heading).to_be_visible()
        expect(risk.page.get_by_text("View and manage this client's profile details and compliance information.", exact=True)).to_be_visible()

    def test_risk_tab_active(self, risk):
        expect(risk.page.locator('.tab-z-option.active').filter(has_text='Risk Assessment')).to_be_visible()

    @pytest.mark.parametrize('section', RiskPage.SECTIONS)
    def test_section_heading_visible(self, risk, section):
        expect(risk.section(section)).to_be_visible()

    @pytest.mark.parametrize('factor', list(RiskPage.FACTORS))
    def test_factor_group_visible(self, risk, factor):
        expect(risk.factor_group(factor)).to_be_visible()

    @pytest.mark.parametrize('factor,value', [(f, v) for f, opts in RiskPage.FACTORS.items() for v in opts])
    def test_each_risk_option_visible_and_has_correct_label(self, risk, factor, value):
        option = risk.option(factor, value)
        expect(option).to_be_attached()
        label = option.locator('xpath=ancestor::label[1]')
        expect(label).to_be_visible()
        expected_text = RiskPage.FACTORS[factor][value][0]
        expect(label).to_contain_text(expected_text)

    @pytest.mark.parametrize('factor', list(RiskPage.FACTORS))
    def test_exactly_one_option_selected_per_factor(self, risk, factor):
        group = risk.factor_group(factor)
        expect(group.locator('input[type="radio"]')).to_have_count(len(RiskPage.FACTORS[factor]))
        expect(group.locator('input[type="radio"]:checked')).to_have_count(1)
        assert risk.selected(factor) in RiskPage.FACTORS[factor]

    @pytest.mark.parametrize('factor', list(RiskPage.FACTORS))
    def test_radio_exclusivity_and_switching_without_save(self, risk, factor):
        original = risk.selected(factor)
        alternate = next(v for v in RiskPage.FACTORS[factor] if v != original)
        risk.select(factor, alternate)
        expect(risk.factor_group(factor).locator('input:checked')).to_have_count(1)
        expect(risk.option(factor, original)).not_to_be_checked()
        risk.select(factor, original)
        expect(risk.option(factor, original)).to_be_checked()

    def test_summary_headers(self, risk):
        headers = [h.strip() for h in risk.summary_table().locator('thead th').all_inner_texts()]
        assert headers == list(RiskPage.HEADERS)

    def test_summary_contains_every_risk_attribute_and_score(self, risk):
        for factor, options in RiskPage.FACTORS.items():
            for value, (attribute, score) in options.items():
                row = risk.attribute_row(attribute)
                expect(row).to_have_count(1)
                expect(row.locator('td').last).to_have_text(str(score))

    def test_summary_risk_factors_present(self, risk):
        for label in ('Country / Jurisdiction Risk', 'Individual Risk', 'Australian Residential Status', 'Transfer of Funds', 'Adverse Media'):
            expect(risk.summary_table().locator('tbody td').filter(has_text=re.compile('^' + re.escape(label) + '$'))).to_have_count(1)

    def test_risk_rating_range_headers_and_values(self, risk):
        table = risk.range_table()
        expect(table).to_be_visible()
        for rating, range_text in [('High', '16 and above'), ('Medium', '6 to 15'), ('Low', '0 to 5')]:
            row = table.locator('tbody tr').filter(has=risk.page.get_by_text(rating, exact=True))
            expect(row).to_have_count(1)
            expect(row.locator('td').last).to_have_text(range_text)

    def test_current_saved_selections_match_score_and_classification(self, risk):
        risk.assert_calculation(risk.current_choices())

    def test_total_score_is_sum_of_five_selected_factors(self, risk):
        choices = risk.current_choices()
        assert len(choices) == 5
        assert risk.total_score() == RiskPage.expected_score(choices)

    def test_classification_matches_current_score(self, risk):
        assert risk.classification() == RiskPage.expected_rating(risk.total_score())

    def test_approval_instructions(self, risk):
        expect(risk.page.get_by_text('An authorised approver must review and sign this assessment before it is saved.', exact=True)).to_be_visible()

    def test_approval_table_headers(self, risk):
        assert [h.strip() for h in risk.approval_table().locator('th').all_inner_texts()] == list(RiskPage.APPROVAL_HEADERS)

    def test_approval_record_fields_present(self, risk):
        row = risk.approval_table().locator('tbody tr').first
        expect(row).to_be_visible()
        cells = row.locator('td')
        expect(cells).to_have_count(4)
        assert cells.nth(0).inner_text().strip(), 'Approver name missing'
        assert cells.nth(1).inner_text().strip(), 'Approver role missing'
        assert re.fullmatch(r'\d{2}-\d{2}-\d{4}', cells.nth(2).inner_text().strip()), 'Approval date format unexpected'

    def test_approval_signature_image_visible(self, risk):
        expect(risk.approval_signature()).to_be_visible()
        assert risk.approval_signature().evaluate('(img) => img.complete && img.naturalWidth > 0')

    def test_update_changes_button_visible_and_enabled(self, risk):
        expect(risk.update_button()).to_be_visible()
        expect(risk.update_button()).to_be_enabled()


# Boundary and score scenarios are browser-local changes only; no save is clicked.
CALCULATION_CASES = [
    ('minimum-low-5', {'country': 'low', 'pep': 'nonPep', 'residence': 'residence', 'funds': 'bankTransfer', 'media': 'noHits'}, 5, 'Low'),
    ('medium-7', {'country': 'other', 'pep': 'nonPep', 'residence': 'residence', 'funds': 'bankTransfer', 'media': 'noHits'}, 7, 'Medium'),
    ('medium-9', {'country': 'other', 'pep': 'nonPep', 'residence': 'nonResidence', 'funds': 'bankTransfer', 'media': 'noHits'}, 9, 'Medium'),
    ('medium-15', {'country': 'high', 'pep': 'pep', 'residence': 'nonResidence', 'funds': 'bankTransfer', 'media': 'noHits'}, 15, 'Medium'),
    ('high-17', {'country': 'high', 'pep': 'pep', 'residence': 'nonResidence', 'funds': 'cash', 'media': 'noHits'}, 17, 'High'),
    ('maximum-high-19', {'country': 'high', 'pep': 'pep', 'residence': 'nonResidence', 'funds': 'cash', 'media': 'confirmed'}, 19, 'High'),
]


@pytest.mark.ui
class TestIndividualRiskCalculations:

    def test_debug_risk_reset_with_network(self, risk):
        page = risk.page

        def log_response(response):
            url = response.url.lower()

            if any(term in url for term in (
                    "profile", "risk", "client", "assessment"
            )):
                print(
                    f"API RESPONSE: {response.status} "
                    f"{response.request.method} {response.url}"
                )

        page.on("response", log_response)

        try:
            print("\nINITIAL")
            risk.debug_atomic_risk_snapshot()

            risk.select("country", "high")
            print("\nAFTER COUNTRY")
            risk.debug_atomic_risk_snapshot()

            risk.select("pep", "pep")
            print("\nAFTER PEP")
            risk.debug_atomic_risk_snapshot()

            page.wait_for_timeout(2000)

            print("\nAFTER 2 SECONDS")
            risk.debug_atomic_risk_snapshot()

            assert risk.selected("country") == "high"
            assert risk.selected("pep") == "pep"
            assert risk.total_score() == 15
        finally:
            page.remove_listener("response", log_response)

    def test_debug_risk_initialization_network(self, page, base_url):
        from pages.profiles.profileNavigation import open_client_profile
        from config.screening_test_data import READ_ONLY_CLIENT_ID

        client_id = os.getenv(
            "RISK_TEST_READ_CLIENT_ID",
            READ_ONLY_CLIENT_ID
        ).strip()

        def log_response(response):
            request = response.request

            if request.resource_type in ("fetch", "xhr"):
                print(
                    f"API RESPONSE: {response.status} "
                    f"{request.method} {response.url}"
                )

        page.on("response", log_response)

        try:
            open_client_profile(
                page,
                base_url,
                "individual",
                client_id
            )

            risk = RiskPage(page)
            risk.open()

            print("\nINITIAL STATE")
            risk.debug_atomic_risk_snapshot()

            risk.select("country", "high")
            risk.select("pep", "pep")

            print("\nAFTER SELECTIONS")
            risk.debug_atomic_risk_snapshot()

            page.wait_for_timeout(2000)

            print("\nAFTER 2 SECONDS")
            risk.debug_atomic_risk_snapshot()

            assert risk.selected("country") == "high"
            assert risk.selected("pep") == "pep"
            assert risk.total_score() == 15

        finally:
            page.remove_listener("response", log_response)

    def test_debug_risk_state_reset(self, page, base_url):
        import time

        client_id = os.getenv(
            "RISK_TEST_READ_CLIENT_ID",
            READ_ONLY_CLIENT_ID
        ).strip()

        responses = []

        def on_response(response):
            if "/risk-assessment" in response.url:
                event = (
                    time.monotonic(),
                    response.status,
                    response.request.method
                )
                responses.append(event)
                print("RISK API RESPONSE:", event)

        page.on("response", on_response)

        try:
            open_client_profile(
                page, base_url, "individual", client_id
            )

            risk = RiskPage(page)
            risk.open()

            risk.select("country", "high")
            risk.select("pep", "pep")

            print("START:", risk.current_choices())

            # Diagnostic observation only, not a permanent wait.
            for i in range(20):
                state = risk.current_choices()
                score = risk.total_score()

                print(
                    f"CHECK {i}: "
                    f"country={state['country']}, "
                    f"pep={state['pep']}, "
                    f"score={score}, "
                    f"risk_responses={len(responses)}"
                )

                if (
                        state["country"] != "high"
                        or state["pep"] != "pep"
                        or score != 15
                ):
                    pytest.fail(
                        "Risk state changed unexpectedly: "
                        f"{state}, score={score}, "
                        f"responses={responses}"
                    )

                page.wait_for_timeout(100)

        finally:
            page.remove_listener("response", on_response)

    @pytest.mark.parametrize('case,choices,score,rating', CALCULATION_CASES, ids=[x[0] for x in CALCULATION_CASES])
    def test_risk_score_and_classification(self, risk, case, choices, score, rating):
        assert RiskPage.expected_score(choices) == score
        assert RiskPage.expected_rating(score) == rating
        risk.select_choices(choices)
        risk.assert_calculation(choices)

    @pytest.mark.parametrize('factor,value', [(f, v) for f, opts in RiskPage.FACTORS.items() for v in opts])
    def test_each_choice_recalculates_total_and_highlight(self, risk, factor, value):
        risk.select(factor, value)
        risk.assert_calculation(risk.current_choices())

    @pytest.mark.parametrize('factor', list(RiskPage.FACTORS))
    def test_changing_and_reverting_factor_restores_score(self, risk, factor):
        before = risk.current_choices()
        original_score = risk.total_score()
        alternate = next(v for v in RiskPage.FACTORS[factor] if v != before[factor])
        risk.select(factor, alternate)
        risk.assert_calculation(risk.current_choices())
        risk.select(factor, before[factor])
        risk.assert_calculation(before)
        assert risk.total_score() == original_score

    def test_negative_unsaved_changes_not_persisted_after_reload(self, risk):
        before = risk.current_choices()
        alternate = next(v for v in RiskPage.FACTORS['pep'] if v != before['pep'])
        risk.select('pep', alternate)
        risk.reload_and_open()
        assert risk.current_choices() == before, 'Unsaved risk choices persisted unexpectedly'


@pytest.mark.ui
@pytest.mark.risk_write
class TestIndividualRiskPersistence:

    @pytest.mark.parametrize(
        'case,choices,score,rating',
        CALCULATION_CASES,
        ids=[x[0] for x in CALCULATION_CASES]
    )
    def test_save_risk_scenario_and_verify_after_reload(
            self, risk_write, case, choices, score, rating
    ):
        risk_write.select_choices(choices)
        risk_write.assert_calculation(choices)

        before_save = risk_write.current_choices()

        assert before_save == choices, (
            f"Incorrect selections before saving {case}. "
            f"Expected: {choices}, Actual: {before_save}"
        )

        risk_write.save()
        risk_write.reload_and_open()

        after_reload = risk_write.current_choices()

        print(f"\nPersistence scenario: {case}")
        print(f"Expected: {choices}")
        print(f"After reload: {after_reload}")
        print(f"Expected score: {score}")
        print(f"Actual score: {risk_write.total_score()}")

        assert after_reload == choices, (
            f"Risk choices not persisted for {case}. "
            f"Expected: {choices}, Actual: {after_reload}"
        )

        risk_write.assert_calculation(choices)

        assert risk_write.total_score() == score
        assert risk_write.classification() == rating

    def test_update_single_factor_and_verify_after_reload(self, risk_write):
        before = risk_write.current_choices()
        alternate = next(v for v in RiskPage.FACTORS['media'] if v != before['media'])
        updated = dict(before, media=alternate)
        risk_write.select('media', alternate)
        risk_write.assert_calculation(updated)
        risk_write.save()
        risk_write.reload_and_open()
        assert risk_write.current_choices() == updated
        risk_write.assert_calculation(updated)

    def test_save_existing_values_does_not_change_risk(self, risk_write):
        before = risk_write.current_choices()
        risk_write.save()
        risk_write.reload_and_open()
        assert risk_write.current_choices() == before
        risk_write.assert_calculation(before)

    def test_debug_risk_initialization(self, page, base_url):
        from pages.profiles.profileNavigation import open_client_profile
        from pages.profiles.individual.individualRiskAssessmentPage import (
            IndividualRiskAssessmentPage,
        )

        open_client_profile(
            page,
            base_url,
            "individual",
            "SENTINELE7CE963CAACEA23",
        )

        risk = IndividualRiskAssessmentPage(page)
        risk.open()

        print("\nINITIAL STATE")
        risk.debug_selected_values()

        page.wait_for_timeout(2000)
        print("\nAFTER 2 SECONDS")
        risk.debug_selected_values()

        page.wait_for_timeout(3000)
        print("\nAFTER 5 SECONDS")
        risk.debug_selected_values()

        risk.select("country", "high")
        risk.select("pep", "pep")

        print("\nAFTER INTERACTIONS")
        risk.debug_selected_values()
