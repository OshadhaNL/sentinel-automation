
import os
import re

import pytest
from playwright.sync_api import (
    Page,
    expect,
    TimeoutError as PlaywrightTimeoutError,
)

from pages.loginPage import LoginPage
from pages.profiles.profilesPage import ProfilesPage


def login_and_open_profiles(
    page: Page,
    base_url: str,
) -> ProfilesPage:
    """Log in and navigate to Profiles > All Files."""

    email = os.getenv("TEST_EMAIL")
    password = os.getenv("TEST_PASSWORD")

    assert email and password, (
        "Set TEST_EMAIL and TEST_PASSWORD environment variables"
    )

    login = LoginPage(page)

    login.open(base_url)
    login.enter_email(email)
    login.enter_password(password)
    login.click_login()

    expect(page).to_have_url(
        re.compile(r".*/nolimit/app/home/?$"),
        timeout=60000,
    )

    profiles = ProfilesPage(page)

    profiles.open_profiles()
    profiles.select_all_files()

    expect(profiles.heading).to_be_visible(timeout=20000)

    return profiles


def open_client_profile(
    page: Page,
    base_url: str,
    client_type: str,
    client_id: str | None = None,
):
    """
    Open an individual or entity profile from All Files.

    Features:
    - Searches by exact client ID when provided.
    - Verifies the client type.
    - Avoids stale indexed row locators.
    - Supports pagination.
    - Retries transient loading failures.
    - Never substitutes another client for an explicit ID.
    """

    profiles = login_and_open_profiles(page, base_url)

    expected_type = client_type.strip().casefold()
    expected_id = client_id.strip() if client_id else None

    max_attempts = 3
    last_error = None

    for attempt in range(1, max_attempts + 1):

        print(
            f"Searching for {client_type} profile "
            f"(attempt {attempt}/{max_attempts})"
        )

        try:
            # Restore All Files after a retry.
            if attempt > 1:
                page.reload(wait_until="domcontentloaded")

                expect(profiles.heading).to_be_visible(
                    timeout=20000
                )

                profiles.select_all_files()

            # Apply the client ID search.
            if expected_id:
                profiles.perform_search(expected_id)

            # Wait for the table itself.
            expect(profiles.table).to_be_visible(
                timeout=20000
            )

            # Wait for search/loading state to finish.
            loading = profiles.table.locator(
                ".ant-spin-spinning"
            )

            expect(loading).to_have_count(
                0,
                timeout=20000,
            )

            # Search results may temporarily be empty.
            try:
                expect(profiles.rows.first).to_be_visible(
                    timeout=15000
                )
            except (AssertionError, PlaywrightTimeoutError):
                raise AssertionError(
                    "No profile records appeared after search"
                )

            # Process the current page, then subsequent pages.
            while True:

                # Locate the row containing the exact client ID.
                if expected_id:
                    matching_rows = profiles.rows.filter(
                        has=page.locator(
                            "td a[href]",
                            has_text=re.compile(
                                rf"^\s*{re.escape(expected_id)}\s*$"
                            ),
                        )
                    )
                else:
                    matching_rows = profiles.rows

                # Use a snapshot of matching IDs rather than
                # iterating through potentially stale row indexes.
                links = matching_rows.locator(
                    "td:first-child a[href]"
                )

                candidate_ids = [
                    value.strip()
                    for value in links.all_text_contents()
                    if value.strip()
                ]

                for found_id in candidate_ids:

                    # Never select the wrong client.
                    if expected_id and found_id != expected_id:
                        continue

                    # Re-locate the row for each candidate.
                    row = profiles.rows.filter(
                        has=page.locator(
                            "td:first-child a[href]",
                            has_text=re.compile(
                                rf"^\s*{re.escape(found_id)}\s*$"
                            ),
                        )
                    ).first

                    if row.count() == 0:
                        continue

                    cells = row.locator("td")

                    if cells.count() < 3:
                        continue

                    try:
                        actual_type = cells.nth(2).inner_text(
                            timeout=5000
                        ).strip().casefold()

                    except PlaywrightTimeoutError:
                        # The table refreshed while reading.
                        # Retry the whole search.
                        raise AssertionError(
                            "Profiles table refreshed during row inspection"
                        )

                    if actual_type != expected_type:
                        continue

                    link = row.locator(
                        "td:first-child a[href]"
                    ).first

                    expect(link).to_be_visible(timeout=10000)

                    # Verify exact client ID before clicking.
                    expect(link).to_have_text(
                        re.compile(
                            rf"^\s*{re.escape(found_id)}\s*$"
                        )
                    )

                    link.click()

                    # Wait for navigation to the profile.
                    expect(page).to_have_url(
                        re.compile(
                            r".*/nolimit/app/profiles/"
                            r"(individual|entity)/process"
                        ),
                        timeout=20000,
                    )

                    print(
                        f"Selected {client_type} profile "
                        f"from UI: {found_id}"
                    )

                    return found_id

                # Stop if no pagination or no next page.
                if (
                    profiles.pagination.count() == 0
                    or profiles.pagination_disabled("next")
                ):
                    break

                profiles.navigate_page("next")

                expect(profiles.table).to_be_visible(
                    timeout=15000
                )

                expect(
                    profiles.table.locator(".ant-spin-spinning")
                ).to_have_count(
                    0,
                    timeout=15000,
                )

        except (
            AssertionError,
            PlaywrightTimeoutError,
        ) as exc:

            last_error = exc

            print(
                f"Profile navigation attempt {attempt} failed: {exc}"
            )

            if attempt < max_attempts:
                continue

        # A profile was not found on this attempt.
        if attempt < max_attempts:
            print("Retrying profile search...")

    pytest.fail(
        f"No matching {client_type} profile found in All Files"
        + (f": {expected_id}" if expected_id else "")
        + (
            f"; last error: {last_error}"
            if last_error
            else ""
        )
    )
