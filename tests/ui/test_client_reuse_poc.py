"""Phase 1: prove one verified client can be reopened by Reference ID.

This is a separate test file: existing Individual Onboarding tests are unchanged.
Run on a QA environment using an account permitted to create test clients.
"""

import os
import re
import uuid
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from pages.loginPage import LoginPage
from pages.clientReusePage import ClientReusePage
from pages.individualOnboardingPage import IndividualOnboardingPage


@pytest.mark.ui
def test_poc_reopen_verified_individual_from_pending(page: Page, base_url: str):
    # Preflight: validate inputs BEFORE creating any new client.
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    assert email and password, "Set TEST_EMAIL and TEST_PASSWORD."

    test_data_dir = Path(__file__).resolve().parents[2] / "test_data"
    front = test_data_dir / "doc-front.jpg"
    back = test_data_dir / "doc-back.jpg"
    assert front.is_file(), f"Missing verification fixture: {front}"
    assert back.is_file(), f"Missing verification fixture: {back}"

    # 1. Log in and create exactly one new individual test client.
    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(email)
    login.enter_password(password)
    login.click_login()
    expect(page).to_have_url(
        re.compile(r".*/nolimit/app/home/?$"), timeout=45000
    )

    page.get_by_role("link", name="Onboarding", exact=False).click()
    main = ClientReusePage(page)
    expect(main.heading).to_be_visible(timeout=20000)
    main.open_new()

    created_name = f"Automation Reuse POC {uuid.uuid4().hex[:12]}"
    main.open_consent("individual", created_name, role="Seller")
    main.consent_checkbox().check()
    expect(main.consent_agree()).to_be_enabled()
    main.consent_agree().click()

    individual = IndividualOnboardingPage(page)
    individual.verify_page_loaded()

    # Capture the exact ID while still on the original client.
    reference_id = individual.risk_get_current_client_id()
    assert reference_id.startswith("SENTINEL")
    print(f"Created QA client {reference_id} ({created_name})")

    # 2. Prepare verified state ONCE: photo, documents, review, confirm.
    individual.capture_and_verify_photo()
    individual.select_document_type("Driver Licence")
    individual.upload_document_front(front)
    individual.verify_document_front_uploaded(front.name)
    individual.upload_document_back(back)
    individual.verify_document_back_uploaded(back.name)

    individual.click_verification_submit()
    individual.wait_for_review_extracted_information()
    individual.verify_review_extracted_information_screen()
    individual.select_first_review_dropdown_option("Gender")
    individual.click_review_save_confirm()
    individual.verify_review_submission_successful()
    individual.click_finish_and_view_submitted_documents()
    individual.verify_navigation_after_finish()

    assert individual.risk_get_current_client_id() == reference_id, (
        "Reference ID changed during the verification workflow."
    )
    print("Verification completed once for client:", reference_id)

    # 3. Leave the record and REOPEN the exact ID via Pending Onboarding.
    # No assumption about which row is first; no reliance on client name.
    main.reopen_pending_individual(reference_id)

    resumed = IndividualOnboardingPage(page)
    # Pending Onboarding intentionally opens at step=verification.
    # The Documents view must be selected explicitly after reopening.
    resumed.open_tab("Documents")
    resumed.verify_documents_page_loaded()
    assert resumed.risk_get_current_client_id() == reference_id
    print("PASS: Verified client's Documents stage reopened.")

    # 4. Check that the *same* reopened record can access later stages.
    resumed.open_kyc_form()
    resumed.kyc_assert_loaded()
    assert resumed.risk_get_current_client_id() == reference_id
    print("PASS: KYC available on the same client.")

    resumed.open_risk_assessment()
    assert resumed.risk_get_current_client_id() == reference_id
    print("PASS: Risk Assessment available on the same client.")

    resumed.open_screening_main()
    assert resumed.risk_get_current_client_id() == reference_id
    print("PASS: Screening available on the same client.")

    print("POC SUCCESS - ONE verified client can be reused by exact ID.")


@pytest.mark.ui
def test_poc_reopen_existing_verified_client(page: Page, base_url: str):
    """Fast read-only POC: use the exact QA client created by the first test.

    Set TEST_REUSE_CLIENT_ID before running. This does not create a client,
    use the camera, or upload identification documents.
    """
    reference_id = os.getenv("TEST_REUSE_CLIENT_ID")
    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")
    assert reference_id, "Set TEST_REUSE_CLIENT_ID before running this POC."
    assert email and password, "Set TEST_EMAIL and TEST_PASSWORD."

    login = LoginPage(page)
    login.open(base_url)
    login.enter_email(email)
    login.enter_password(password)
    login.click_login()
    expect(page).to_have_url(
        re.compile(r".*/nolimit/app/home/?$"), timeout=45000
    )

    main = ClientReusePage(page)
    main.reopen_pending_individual(reference_id)
    individual = IndividualOnboardingPage(page)

    individual.open_tab("Documents")
    individual.verify_documents_page_loaded()
    assert individual.risk_get_current_client_id() == reference_id
    print("PASS: Documents")

    individual.open_kyc_form()
    individual.kyc_assert_loaded()
    assert individual.risk_get_current_client_id() == reference_id
    print("PASS: KYC Form")

    individual.open_risk_assessment()
    assert individual.risk_get_current_client_id() == reference_id
    print("PASS: Risk Assessment")

    individual.open_screening_main()
    assert individual.risk_get_current_client_id() == reference_id
    print("PASS: Screening")
    print("CLIENT REUSE POC PASSED - same client in all four stages.")
