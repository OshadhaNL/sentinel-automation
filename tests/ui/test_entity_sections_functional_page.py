
import os
import re
from urllib.parse import quote, urlsplit

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.entitySectionsPage import EntitySectionsPage


def _open_entity(page: Page, base_url: str, client_id: str):
    email = os.getenv("TEST_EMAIL", "").strip()
    password = os.getenv("TEST_PASSWORD", "")

    assert email and password, "Set TEST_EMAIL and TEST_PASSWORD"

    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(email)
    login.enter_password(password)
    login.click_login()

    expect(page).to_have_url(
        re.compile(r".*/nolimit/app/home/?$"),
        timeout=45000
    )

    parsed = urlsplit(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    page.goto(
        f"{origin}/nolimit/app/onboarding/entity/process"
        f"?step=documents&client={quote(client_id, safe='')}",
        wait_until="domcontentloaded"
    )

    entity = EntitySectionsPage(page)
    entity.verify_page_loaded()

    expect(entity.reference_id).to_have_text(
        client_id,
        timeout=15000
    )

    return entity


@pytest.fixture
def read_entity(page: Page, base_url: str):
    client_id = os.getenv(
        "TEST_ENTITY_CLIENT_ID", ""
    ).strip()

    if not client_id:
        pytest.skip("Set TEST_ENTITY_CLIENT_ID")

    return _open_entity(page, base_url, client_id)


@pytest.fixture
def risk_entity(page: Page, base_url: str):
    if os.getenv("TEST_ENTITY_ALLOW_RISK_CHANGES") != "1":
        pytest.skip(
            "Set TEST_ENTITY_ALLOW_RISK_CHANGES=1"
        )

    if os.getenv("PYTEST_XDIST_WORKER"):
        pytest.fail("Run risk tests with -n 0")

    write_id = os.getenv(
        "TEST_ENTITY_WRITE_CLIENT_ID", ""
    ).strip()

    read_id = os.getenv(
        "TEST_ENTITY_CLIENT_ID", ""
    ).strip()

    if not re.fullmatch(
        r"SENTINEL[A-Za-z0-9_-]+",
        write_id
    ):
        pytest.fail(
            "Set a real TEST_ENTITY_WRITE_CLIENT_ID"
        )

    if not read_id or write_id == read_id:
        pytest.fail(
            "Write entity must differ from read-only entity"
        )

    return _open_entity(page, base_url, write_id)


# ==========================================================
# SCREENING FUNCTIONAL TESTS
# ==========================================================

@pytest.mark.ui
class TestEntityScreeningInteractions:

    def test_switch_client_type_and_restore(self, read_entity):
        e = read_entity
        e.open_screening()

        e.screening_individual.check(force=True)

        expect(
            e.screening_individual
        ).to_be_checked()

        expect(
            e.page.get_by_placeholder(
                "Enter individual name",
                exact=True
            )
        ).to_be_visible()

        e.screening_organization.check(force=True)

        expect(
            e.screening_organization
        ).to_be_checked()

        expect(
            e.page.get_by_placeholder(
                "Enter organisation name",
                exact=True
            )
        ).to_be_visible()

    def test_enter_and_clear_organization_name(self, read_entity):
        e = read_entity
        e.open_screening()

        field = e.page.get_by_placeholder(
            "Enter organisation name",
            exact=True
        )

        field.fill("QA AUTOMATION TEST ENTITY")

        expect(field).to_have_value(
            "QA AUTOMATION TEST ENTITY"
        )

        field.fill("")

        expect(field).to_be_empty()

    def test_registered_country_dropdown_opens(self, read_entity):
        e = read_entity
        e.open_screening()

        e.page.locator(".ant-select").first.click()

        expect(
            e.page.locator(
                ".ant-select-dropdown:visible"
            ).first
        ).to_be_visible()

        e.page.keyboard.press("Escape")

    def test_ongoing_screening_checkbox_toggle(self, read_entity):
        e = read_entity
        e.open_screening()

        checkbox = e.screening_ongoing
        original = checkbox.is_checked()

        checkbox.set_checked(
            not original,
            force=True
        )

        assert checkbox.is_checked() is not original

        checkbox.set_checked(
            original,
            force=True
        )

        assert checkbox.is_checked() is original


# ==========================================================
# KYC FUNCTIONAL TESTS
# ==========================================================

@pytest.mark.ui
class TestEntityKYCInteractions:

    def test_edit_multiple_fields_without_saving(self, read_entity):
        e = read_entity
        e.open_kyc()

        values = {
            "Enter legal name": "QA AUTOMATION UNSAVED ENTITY",
            "Enter email address": "qa-automation@example.com",
            "Enter AUD": "100000",
        }

        for placeholder, value in values.items():
            field = e.page.get_by_placeholder(
                placeholder,
                exact=True
            )

            field.fill(value)

            expect(field).to_have_value(value)

        # Do not click Save.

    def test_legal_form_dropdown_opens(self, read_entity):
        e = read_entity
        e.open_kyc()

        e.kyc_form.locator(
            ".ant-select"
        ).first.click()

        expect(
            e.page.locator(
                ".ant-select-dropdown:visible"
            ).first
        ).to_be_visible()

        e.page.keyboard.press("Escape")

    def test_incorporated_date_picker_opens(self, read_entity):
        e = read_entity
        e.open_kyc()

        e.page.get_by_placeholder(
            "Select incorporated date",
            exact=True
        ).click()

        expect(
            e.page.locator(
                ".ant-picker-dropdown:visible"
            ).first
        ).to_be_visible()

        e.page.keyboard.press("Escape")

    def test_incomplete_kyc_save_disabled(self, read_entity):
        e = read_entity
        e.open_kyc()

        legal_name = e.page.get_by_placeholder(
            "Enter legal name",
            exact=True
        )

        if legal_name.input_value().strip():
            pytest.skip(
                "Entity already has a legal name"
            )

        save = e.page.get_by_role(
            "button",
            name="Save",
            exact=True
        )

        expect(save).to_be_disabled()


# ==========================================================
# OWNERSHIP FUNCTIONAL TESTS
# ==========================================================

@pytest.mark.ui
class TestEntityOwnershipInteractions:

    def test_existing_profile_search(self, read_entity):
        e = read_entity
        e.open_ownership("Profiles")
        expect(
            e.profile_cards.first
        ).to_be_visible(timeout=15000)

        name = (
            e.profile_cards.first
            .locator("h6")
            .first
            .inner_text()
            .strip()
        )

        if not name:
            pytest.skip("Profile name unavailable")

        e.profile_search.fill(name)

        e.page.locator(
            "button.search-btn"
        ).click()

        expect(
            e.profile_cards.filter(
                has_text=name
            )
        ).to_be_visible(timeout=15000)

        e.profile_search.fill("")

        e.page.locator(
            "button.search-btn"
        ).click()

    def test_search_nonexistent_profile(self, read_entity):
        e = read_entity
        e.open_ownership("Profiles")

        e.profile_search.fill(
            "qa-auto-nonexistent-profile-987654321"
        )

        e.page.locator(
            "button.search-btn"
        ).click()

        expect(
            e.profile_cards
        ).to_have_count(
            0,
            timeout=15000
        )

        e.profile_search.fill("")

        e.page.locator(
            "button.search-btn"
        ).click()

    def test_cancel_profile_draft_does_not_create_profile(
            self, read_entity
    ):
        e = read_entity

        e.open_ownership("Profiles")

        # Wait for the existing profile to load.
        expect(
            e.profile_cards.first
        ).to_be_visible(timeout=15000)

        # Capture existing profile names.
        before_names = sorted(
            e.profile_cards.locator(
                ".profile-name"
            ).all_inner_texts()
        )

        before_count = len(before_names)

        assert before_count > 0, (
            "Expected an existing profile for this QA entity"
        )

        # Open Create Profile.
        modal = e.open_create_profile()

        expect(
            modal.locator(
                'input[name="profileId"]'
            )
        ).to_be_disabled()

        # Enter draft data.
        modal.locator(
            'input[name="shares"]'
        ).fill("10")

        modal.locator(
            'input[name="percentage"]'
        ).fill("10")

        # Cancel without saving.
        modal.get_by_role(
            "button",
            name="Cancel",
            exact=True
        ).click()

        expect(modal).not_to_be_visible()

        # Verify the number of profiles is unchanged.
        expect(
            e.profile_cards
        ).to_have_count(
            before_count,
            timeout=15000
        )

        after_names = sorted(
            e.profile_cards.locator(
                ".profile-name"
            ).all_inner_texts()
        )

        assert after_names == before_names, (
            "Profile list changed after cancelling"
        )

        # Reload to verify the persisted state.
        e.page.reload(
            wait_until="domcontentloaded"
        )

        e.open_ownership("Profiles")

        expect(
            e.profile_cards
        ).to_have_count(
            before_count,
            timeout=15000
        )

        persisted_names = sorted(
            e.profile_cards.locator(
                ".profile-name"
            ).all_inner_texts()
        )

        assert persisted_names == before_names, (
            "Profile data changed after cancellation"
        )

    def test_additional_role_checkboxes(self, read_entity):
        e = read_entity

        modal = e.open_create_profile()

        for role in ("director", "signatory"):
            checkbox = modal.locator(
                f'input[name="roles"][value="{role}"]'
            )

            label = modal.locator(
                f'label[for="{role}"]'
            )

            expect(checkbox).to_have_count(1)
            expect(label).to_be_visible()

            # Click the actual visible label.
            label.click()

            # Verify checkbox becomes checked.
            expect(checkbox).to_be_checked(
                timeout=5000
            )

            # Click again and verify it becomes unchecked.
            label.click()

            expect(checkbox).not_to_be_checked(
                timeout=5000
            )

        # Close without saving.
        modal.get_by_role(
            "button",
            name="Cancel",
            exact=True
        ).click()

        expect(modal).not_to_be_visible()


    def test_structure_zoom_controls(self, read_entity):
        e = read_entity

        e.open_ownership("Ownership Structure")

        for icon in (
            "fa-search-plus",
            "fa-search-minus",
            "fa-times-circle"
        ):
            e.structure_controls.locator(
                f"button:has(i.{icon})"
            ).click()

            expect(
                e.structure_canvas
            ).to_be_visible()


# ==========================================================
# RISK ASSESSMENT FUNCTIONAL TESTS
# Disposable entity ONLY
# ==========================================================

RISK_CASES = [
    pytest.param(
        ("low", "notPep", "low", "bankTransfer", "noHits"),
        5,
        "Low",
        id="low-5"
    ),
    pytest.param(
        ("high", "pepIdentified", "medium", "bankTransfer", "noHits"),
        15,
        "Medium",
        id="medium-15"
    ),
    pytest.param(
        ("high", "pepIdentified", "high", "bankTransfer", "noHits"),
        17,
        "High",
        id="high-17"
    ),
]


@pytest.mark.ui
class TestEntityRiskCalculations:

    @pytest.mark.parametrize(
        "choices, expected_score, expected_rating",
        RISK_CASES
    )
    def test_risk_score_and_classification(
        self,
        risk_entity,
        choices,
        expected_score,
        expected_rating
    ):
        e = risk_entity
        e.open_risk()

        selected_radios = []

        for title, value in zip(e.RISK_OPTIONS, choices):

            group = e.risk_group(title)

            radio = group.locator(
                f'input[type="radio"][value="{value}"]'
            )

            wrapper = radio.locator("xpath=..")

            print(f"\nAttempting: {title} = {value}", flush=True)

            wrapper.click()

            import time

            print(f"\nCLICKED: {title} = {value}", flush=True)

            for delay in [0, 0.2, 0.5, 1.0, 2.0]:
                if delay:
                    time.sleep(delay)

                checked_values = group.locator(
                    'input[type="radio"]:checked'
                ).evaluate_all(
                    "(els) => els.map(el => el.value)"
                )

                print(
                    f"After additional {delay}s | "
                    f"Group: {title} | "
                    f"Checked: {checked_values} | "
                    f"Score: {e.risk_total_score.inner_text()}",
                    flush=True
                )

            expect(
                radio,
                f"Selection failed: {title} = {value}"
            ).to_be_checked(timeout=5000)

            selected_radios.append((title, value))

            print(f"Selected: {title} = {value}", flush=True)

            for previous_title, previous_value in selected_radios:

                previous_radio = e.risk_group(
                    previous_title
                ).locator(
                    f'input[type="radio"][value="{previous_value}"]'
                )

                if not previous_radio.is_checked():
                    checked_values = e.risk_group(
                        previous_title
                    ).locator(
                        'input[type="radio"]:checked'
                    ).evaluate_all(
                        "(els) => els.map(el => el.value)"
                    )

                    print(
                        f"RESET DETECTED after selecting {title}={value}. "
                        f"Previous selection {previous_title}={previous_value}. "
                        f"Currently checked: {checked_values}",
                        flush=True
                    )

                expect(
                    previous_radio,
                    f"Selection reset after {title}: "
                    f"{previous_title}={previous_value}"
                ).to_be_checked(timeout=5000)

            print(f"Selected: {title} = {value}")

        print(
            "Actual total score:",
            e.risk_total_score.inner_text()
        )

        print(
            "Actual classification:",
            e.risk_classification.inner_text()
        )

        expect(
            e.risk_total_score
        ).to_have_text(
            str(expected_score),
            timeout=15000
        )

        expect(
            e.risk_classification
        ).to_contain_text(expected_rating)